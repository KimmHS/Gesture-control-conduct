from __future__ import annotations

import logging
import time
from typing import Any

import numpy as np

from conductor_demo.app.state import AppState, CalibrationState, DynamicsState, PlaybackState
from conductor_demo.config.defaults import AppConfig
from conductor_demo.motion.buffer import MotionBuffer, MotionSample
from conductor_demo.motion.calibration import CalibrationManager
from conductor_demo.motion.dynamics import DynamicsEstimator
from conductor_demo.music.controller import MusicController
from conductor_demo.ui.controls import FallbackControls
from conductor_demo.ui.overlay import OverlayRenderer
from conductor_demo.vision.camera import CameraStream
from conductor_demo.vision.tracker import HandTracker, TrackingResult


LOGGER = logging.getLogger(__name__)


def _require_cv2() -> Any:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("OpenCV is required. Install dependencies with `pip install -r requirements.txt`.") from exc
    return cv2


class AppRunner:
    """Run the current webcam and tracking layer."""

    def __init__(self, config: AppConfig, max_frames: int | None = None, self_test: bool = False) -> None:
        self.config = config
        self.max_frames = max_frames
        self.self_test = self_test
        self.camera = CameraStream(
            index=config.vision.camera_index,
            frame_width=config.vision.frame_width,
            frame_height=config.vision.frame_height,
            mirror=config.vision.mirror,
        )
        self.tracker = HandTracker(
            detection_confidence=config.vision.detection_confidence,
            tracking_confidence=config.vision.tracking_confidence,
            smoothing_alpha=config.motion.smoothing_alpha,
            hold_seconds=config.motion.lost_tracking_hold_seconds,
            max_num_hands=config.vision.max_num_hands,
            model_complexity=config.vision.model_complexity,
            hand_confidence_threshold=config.vision.hand_confidence_threshold,
            min_hand_scale_px=config.vision.min_hand_scale_px,
        )
        self.motion = MotionBuffer(maxlen=config.motion.buffer_size)
        self.calibration = CalibrationManager(
            enabled=config.calibration.enabled,
            hold_seconds=config.calibration.hold_seconds,
            motion_seconds=config.calibration.motion_seconds,
            min_hold_samples=config.calibration.min_hold_samples,
            min_motion_samples=config.calibration.min_motion_samples,
            min_motion_span_px=config.calibration.min_motion_span_px,
            min_motion_span_hand_scales=config.calibration.min_motion_span_hand_scales,
            dynamics_span_multiplier=config.calibration.dynamics_span_multiplier,
            tempo_motion_floor_ratio=config.calibration.tempo_motion_floor_ratio,
            tempo_motion_ceiling_ratio=config.calibration.tempo_motion_ceiling_ratio,
        )
        self.dynamics = DynamicsEstimator(
            window_seconds=config.dynamics.window_seconds,
            min_samples=config.dynamics.min_samples,
            smoothing_alpha=config.dynamics.smoothing_alpha,
            idle_smoothing_alpha=config.dynamics.idle_smoothing_alpha,
            confidence_floor=config.dynamics.confidence_floor,
            reference_span_hand_scales=config.dynamics.reference_span_hand_scales,
            output_deadband=config.dynamics.output_deadband,
            default_volume=config.music.default_volume,
            min_volume=config.music.min_volume,
            max_volume=config.music.max_volume,
        )
        self.music = MusicController(
            base_bpm=config.music.base_bpm,
            default_volume=config.music.default_volume,
            min_volume=config.music.min_volume,
            max_volume=config.music.max_volume,
            min_rate=config.music.min_rate,
            max_rate=config.music.max_rate,
            demo_track_path=config.music.demo_track_path,
        )
        self.last_dynamics = self.dynamics.current()
        self.controls = FallbackControls(config.controls.keymap())
        self.overlay = OverlayRenderer(
            app_name=config.app_name,
            show_landmarks=config.ui.show_landmarks,
            show_help=config.ui.show_help_overlay,
        )
        self._camera_failures = 0

    def run(self) -> int:
        LOGGER.info("Starting %s", self.config.app_name)
        try:
            self.tracker.start()
            if self.self_test:
                self._run_self_test()
                LOGGER.info("Self-test completed.")
                return 0

            return self._run_camera_loop()
        except RuntimeError as exc:
            LOGGER.error("%s", exc)
            return 1
        finally:
            try:
                cv2 = _require_cv2()
                cv2.destroyAllWindows()
            except RuntimeError:
                pass
            self.music.close()
            self.tracker.stop()
            self.camera.close()

    def _run_self_test(self) -> None:
        frame = np.zeros(
            (self.config.vision.frame_height, self.config.vision.frame_width, 3),
            dtype=np.uint8,
        )
        tracking = self.tracker.process(frame, timestamp=time.monotonic())
        self.calibration.update(
            timestamp=time.monotonic(),
            tracking_ok=tracking.tracking_ok,
            wrist_px=tracking.wrist_px,
            hand_scale_px=tracking.hand_scale_px,
        )
        self.last_dynamics = self.dynamics.update(
            motion_buffer=self.motion,
            timestamp=time.monotonic(),
            tracking_ok=tracking.tracking_ok,
            hand_scale_px=tracking.hand_scale_px,
            baseline_hand_scale_px=self.calibration.baseline_hand_scale,
            reference_span_px_override=self.calibration.dynamics_reference_span_px,
        )
        self.music.set_volume(self.last_dynamics.volume)
        app_state = self._snapshot_state(tracking)
        debug_frame = self.overlay.draw_debug(
            frame=frame,
            tracking=tracking,
            motion_buffer=self.motion,
            app_state=app_state,
            trail_length=self.config.motion.trail_length,
        )
        LOGGER.info(
            "\n%s",
            self.overlay.render_status(
                app_state=app_state,
                camera_status="self-test synthetic frame",
                tracker_status=self.tracker.describe(),
                motion_status=self.motion.describe(),
            ),
        )
        LOGGER.debug("Rendered synthetic debug frame with shape %s", debug_frame.shape)

    def _run_camera_loop(self) -> int:
        cv2 = _require_cv2()
        self.camera.open(
            retries=self.config.vision.camera_open_retries,
            retry_delay_seconds=self.config.vision.camera_retry_delay_seconds,
        )
        cv2.namedWindow(self.config.ui.window_name, cv2.WINDOW_NORMAL)

        frame_count = 0
        while True:
            try:
                packet = self.camera.read()
                self._camera_failures = 0
            except RuntimeError as exc:
                self._camera_failures += 1
                LOGGER.warning("Camera read failed (%d): %s", self._camera_failures, exc)
                if self._camera_failures > self.config.vision.camera_reopen_retries:
                    raise RuntimeError(
                        "Camera feed could not be recovered. Check camera access, then restart the demo."
                    ) from exc
                self.camera.reopen(
                    retries=self.config.vision.camera_reopen_retries,
                    retry_delay_seconds=self.config.vision.camera_retry_delay_seconds,
                )
                LOGGER.info("Camera reopened successfully.")
                continue

            tracking = self.tracker.process(packet.frame, timestamp=packet.timestamp)

            if (
                tracking.mode == "live"
                and tracking.tracking_ok
                and tracking.wrist_px is not None
                and tracking.raw_wrist_px is not None
            ):
                self.motion.append(
                    MotionSample(
                        x=tracking.wrist_px[0],
                        y=tracking.wrist_px[1],
                        timestamp=packet.timestamp,
                        confidence=tracking.confidence,
                        raw_x=tracking.raw_wrist_px[0],
                        raw_y=tracking.raw_wrist_px[1],
                        is_live=tracking.mode == "live",
                    )
                )

            self._update_motion_controls(tracking=tracking, timestamp=packet.timestamp)
            app_state = self._snapshot_state(tracking)
            debug_frame = self.overlay.draw_debug(
                frame=packet.frame,
                tracking=tracking,
                motion_buffer=self.motion,
                app_state=app_state,
                trail_length=self.config.motion.trail_length,
            )
            cv2.imshow(self.config.ui.window_name, debug_frame)

            action = self.controls.resolve_keycode(cv2.waitKey(1) & 0xFF)
            if action is not None:
                if self._handle_action(action, tracking):
                    break

            frame_count += 1
            if self.max_frames is not None and frame_count >= self.max_frames:
                break
        return 0

    def _update_motion_controls(self, tracking: TrackingResult, timestamp: float) -> None:
        calibration_completed = self.calibration.update(
            timestamp=timestamp,
            tracking_ok=tracking.tracking_ok,
            wrist_px=tracking.wrist_px,
            hand_scale_px=tracking.hand_scale_px,
        )
        if calibration_completed:
            self.motion.clear()
            self.dynamics.reset()
            LOGGER.info(
                "Calibration complete: baseline_scale=%.1f span=%.1f dyn_ref=%.1f tempo_gate=%.1f-%.1f px",
                self.calibration.baseline_hand_scale or 0.0,
                self.calibration.comfortable_motion_span_px or 0.0,
                self.calibration.dynamics_reference_span_px or 0.0,
                self.calibration.tempo_motion_floor_px or 0.0,
                self.calibration.tempo_motion_ceiling_px or 0.0,
            )

        freeze_motion_response = self.calibration.active or tracking.mode == "hold"
        self.last_dynamics = self.dynamics.update(
            motion_buffer=self.motion,
            timestamp=timestamp,
            tracking_ok=tracking.tracking_ok,
            hand_scale_px=tracking.hand_scale_px,
            baseline_hand_scale_px=self.calibration.baseline_hand_scale,
            reference_span_px_override=self.calibration.dynamics_reference_span_px,
            freeze_output=freeze_motion_response,
        )
        self.music.set_volume(self.last_dynamics.volume)

    def _handle_action(self, action: str, tracking: TrackingResult) -> bool:
        if action == "quit":
            return True
        if action == "reset":
            self.motion.clear()
            self.tracker.reset()
            self.dynamics.reset()
            self.music.reset()
            self.calibration.cancel_active()
            LOGGER.info("Reset tracking and playback state while preserving the last completed calibration.")
            return False
        if action == "calibrate":
            self.calibration.start()
            LOGGER.info("Calibration started. Hold still briefly, then move in a comfortable conducting range.")
            return False
        if action == "play_from_start":
            self.music.play()
            LOGGER.info("Playback start: %s", self.music.describe())
            return False
        if action == "pause":
            self.music.pause()
            LOGGER.info("Playback pause: %s", self.music.describe())
            return False
        if action == "resume":
            self.music.resume()
            LOGGER.info("Playback resume: %s", self.music.describe())
            return False
        if action == "pause_resume_toggle":
            self.music.toggle_pause_resume()
            LOGGER.info("Playback toggle: %s", self.music.describe())
            return False
        if action == "tempo_down":
            self.music.adjust_rate(-self.config.music.rate_step)
            LOGGER.info("Playback rate decreased: %.2f", self.music.playback_rate)
            return False
        if action == "tempo_up":
            self.music.adjust_rate(self.config.music.rate_step)
            LOGGER.info("Playback rate increased: %.2f", self.music.playback_rate)
            return False
        return False

    def _snapshot_state(self, tracking: TrackingResult) -> AppState:
        playback = PlaybackState(
            mode=self.music.state,
            is_playing=self.music.is_playing,
            bpm=self.music.current_bpm,
            rate=self.music.playback_rate,
            volume=self.music.volume,
            track_name=self.music.track_name,
            position_seconds=self.music.position_seconds,
            duration_seconds=self.music.duration_seconds,
            status_text=self.music.status_text,
            status_detail=self.music.status_detail,
        )
        dynamics = DynamicsState(
            intensity=self.last_dynamics.intensity,
            raw_intensity=self.last_dynamics.raw_intensity,
            span_px=self.last_dynamics.span_px,
            reference_span_px=self.last_dynamics.reference_span_px,
        )
        calibration = CalibrationState(
            enabled=self.calibration.enabled,
            active=self.calibration.active,
            calibrated=self.calibration.calibrated,
            stage=self.calibration.stage,
            progress=self.calibration.progress,
            status_text=self.calibration.status_text,
            status_detail=self.calibration.status_detail,
            baseline_wrist_px=self.calibration.baseline_wrist_px,
            baseline_hand_scale=self.calibration.baseline_hand_scale,
            comfortable_motion_span_px=self.calibration.comfortable_motion_span_px,
            dynamics_reference_span_px=self.calibration.dynamics_reference_span_px,
            tempo_motion_floor_px=self.calibration.tempo_motion_floor_px,
            tempo_motion_ceiling_px=self.calibration.tempo_motion_ceiling_px,
        )
        return AppState(
            tracking_ok=tracking.tracking_ok,
            active_hand=tracking.active_hand,
            playback=playback,
            dynamics=dynamics,
            calibration=calibration,
            fallback_hint=self.controls.describe(),
        )
