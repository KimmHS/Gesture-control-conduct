from __future__ import annotations

import logging
import time
from typing import Any

import numpy as np

from conductor_demo.app.state import (
    AppState,
    CalibrationState,
    DynamicsState,
    HandRoleState,
    PlaybackState,
    TempoState,
)
from conductor_demo.config.defaults import AppConfig
from conductor_demo.cueing.selector import CueSelector
from conductor_demo.motion.buffer import MotionBuffer, MotionSample
from conductor_demo.motion.calibration import CalibrationManager
from conductor_demo.motion.dynamics import DynamicsEstimator
from conductor_demo.motion.tempo import TempoEstimator
from conductor_demo.music.controller import MusicController
from conductor_demo.ui.controls import FallbackControls
from conductor_demo.ui.overlay import OverlayRenderer
from conductor_demo.vision.camera import CameraStream
from conductor_demo.vision.tracker import HandTracker, TrackingResult, TrackedHand


LOGGER = logging.getLogger(__name__)


def _require_cv2() -> Any:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("OpenCV is required. Install dependencies with `pip install -r requirements.txt`.") from exc
    return cv2


class AppRunner:
    """Run the webcam conducting demo with split hand roles."""

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
            swap_left_right_labels=config.vision.swap_left_right_labels,
        )
        self.tempo_motion = MotionBuffer(maxlen=config.motion.buffer_size)
        self.dynamics_motion = MotionBuffer(maxlen=config.motion.buffer_size)
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
            tempo_window_seconds=config.calibration.tempo_window_seconds,
        )
        self.tempo = TempoEstimator(
            window_seconds=config.tempo.window_seconds,
            min_samples=config.tempo.min_samples,
            smoothing_alpha=config.tempo.smoothing_alpha,
            idle_smoothing_alpha=config.tempo.idle_smoothing_alpha,
            confidence_floor=config.tempo.confidence_floor,
            motion_floor_hand_scales=config.tempo.motion_floor_hand_scales,
            motion_ceiling_hand_scales=config.tempo.motion_ceiling_hand_scales,
            output_deadband=config.tempo.output_deadband,
            min_rate=config.music.min_rate,
            neutral_rate=1.0,
            max_rate=config.music.max_rate,
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
        self.last_tempo = self.tempo.current()
        self.last_dynamics = self.dynamics.current()
        self.manual_tempo_bias = 0.0
        self.controls = FallbackControls(config.controls.keymap())
        self.cue_selector = CueSelector(
            enabled=config.cueing.enabled,
            slot_count=config.cueing.slot_count,
            labels=config.cueing.labels,
            selection_hold_seconds=config.cueing.selection_hold_seconds,
            boundary_margin_ratio=config.cueing.boundary_margin_ratio,
        )
        self.last_cue = self.cue_selector.current()
        self.last_cue.active_indices = self.music.active_group_indices
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
        timestamp = time.monotonic()
        frame = np.zeros(
            (self.config.vision.frame_height, self.config.vision.frame_width, 3),
            dtype=np.uint8,
        )
        tracking = self.tracker.process(frame, timestamp=timestamp)
        self._update_motion_controls(tracking=tracking, timestamp=timestamp)
        self.last_cue = self.cue_selector.update(
            hand=tracking.cue_hand,
            frame_width=frame.shape[1],
            timestamp=timestamp,
        )
        self.last_cue.active_indices = self.music.active_group_indices
        app_state = self._snapshot_state(tracking)
        debug_frame = self.overlay.draw_debug(
            frame=frame,
            tracking=tracking,
            app_state=app_state,
            trail_length=self.config.motion.trail_length,
            tempo_motion_buffer=self.tempo_motion,
            dynamics_motion_buffer=self.dynamics_motion,
        )
        LOGGER.info(
            "\n%s",
            self.overlay.render_status(
                app_state=app_state,
                camera_status="self-test synthetic frame",
                tracker_status=self.tracker.describe(),
                motion_status=self._motion_status(),
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
            self._append_live_samples(tracking=tracking, timestamp=packet.timestamp)
            self._update_motion_controls(tracking=tracking, timestamp=packet.timestamp)
            self.last_cue = self.cue_selector.update(
                hand=tracking.cue_hand,
                frame_width=packet.width,
                timestamp=packet.timestamp,
            )
            self.last_cue.active_indices = self.music.active_group_indices
            app_state = self._snapshot_state(tracking)
            debug_frame = self.overlay.draw_debug(
                frame=packet.frame,
                tracking=tracking,
                app_state=app_state,
                trail_length=self.config.motion.trail_length,
                tempo_motion_buffer=self.tempo_motion,
                dynamics_motion_buffer=self.dynamics_motion,
            )
            cv2.imshow(self.config.ui.window_name, debug_frame)

            action = self.controls.resolve_keycode(cv2.waitKey(1) & 0xFF)
            if action is not None and self._handle_action(action):
                break

            frame_count += 1
            if self.max_frames is not None and frame_count >= self.max_frames:
                break
        return 0

    def _append_live_samples(self, tracking: TrackingResult, timestamp: float) -> None:
        self._append_hand_sample(self.tempo_motion, tracking.tempo_hand, timestamp)
        self._append_hand_sample(self.dynamics_motion, tracking.tempo_hand, timestamp)

    def _append_hand_sample(
        self,
        motion_buffer: MotionBuffer,
        hand: TrackedHand | None,
        timestamp: float,
    ) -> None:
        if hand is None or hand.mode != "live" or not hand.tracking_ok:
            return
        if hand.wrist_px is None or hand.raw_wrist_px is None:
            return

        motion_buffer.append(
            MotionSample(
                x=hand.wrist_px[0],
                y=hand.wrist_px[1],
                timestamp=timestamp,
                confidence=hand.confidence,
                raw_x=hand.raw_wrist_px[0],
                raw_y=hand.raw_wrist_px[1],
                is_live=True,
            )
        )

    def _update_motion_controls(self, tracking: TrackingResult, timestamp: float) -> None:
        tempo_hand = tracking.tempo_hand
        calibration_completed = self.calibration.update(
            timestamp=timestamp,
            tempo_tracking_ok=bool(tempo_hand and tempo_hand.tracking_ok),
            tempo_wrist_px=tempo_hand.wrist_px if tempo_hand is not None else None,
            tempo_hand_scale_px=tempo_hand.hand_scale_px if tempo_hand is not None else None,
            dynamics_tracking_ok=bool(tempo_hand and tempo_hand.tracking_ok),
            dynamics_wrist_px=tempo_hand.wrist_px if tempo_hand is not None else None,
            dynamics_hand_scale_px=tempo_hand.hand_scale_px if tempo_hand is not None else None,
        )
        if calibration_completed:
            self.tempo_motion.clear()
            self.dynamics_motion.clear()
            self.tempo.reset()
            self.dynamics.reset()
            LOGGER.info(
                "Calibration complete: tempo_gate=%.1f-%.1f px dynamics_span=%.1f dyn_ref=%.1f",
                self.calibration.tempo_motion_floor_px or 0.0,
                self.calibration.tempo_motion_ceiling_px or 0.0,
                self.calibration.comfortable_motion_span_px or 0.0,
                self.calibration.dynamics_reference_span_px or 0.0,
            )

        self.last_tempo = self.tempo.update(
            motion_buffer=self.tempo_motion,
            timestamp=timestamp,
            tracking_ok=bool(tempo_hand and tempo_hand.tracking_ok),
            hand_scale_px=tempo_hand.hand_scale_px if tempo_hand is not None else None,
            baseline_hand_scale_px=self.calibration.tempo_baseline_hand_scale,
            motion_floor_px_override=self.calibration.tempo_motion_floor_px,
            motion_ceiling_px_override=self.calibration.tempo_motion_ceiling_px,
            freeze_output=self.calibration.active or bool(tempo_hand and tempo_hand.mode == "hold"),
        )
        self.last_dynamics = self.dynamics.update(
            motion_buffer=self.dynamics_motion,
            timestamp=timestamp,
            tracking_ok=bool(tempo_hand and tempo_hand.tracking_ok),
            hand_scale_px=tempo_hand.hand_scale_px if tempo_hand is not None else None,
            baseline_hand_scale_px=self.calibration.baseline_hand_scale,
            reference_span_px_override=self.calibration.dynamics_reference_span_px,
            freeze_output=self.calibration.active or bool(tempo_hand and tempo_hand.mode == "hold"),
        )

        self.music.set_rate(self.last_tempo.rate + self.manual_tempo_bias)
        self.music.set_volume(self.last_dynamics.volume)

    def _handle_action(self, action: str) -> bool:
        if action == "quit":
            return True
        if action == "reset":
            self.tempo_motion.clear()
            self.dynamics_motion.clear()
            self.tracker.reset()
            self.cue_selector.reset()
            self.last_cue = self.cue_selector.current()
            self.music.activate_all_groups()
            self.last_cue.active_indices = self.music.active_group_indices
            self.tempo.reset()
            self.dynamics.reset()
            self.manual_tempo_bias = 0.0
            self.music.reset()
            self.calibration.cancel_active()
            LOGGER.info("Reset tracking, tempo bias, and playback state while preserving the last completed calibration.")
            return False
        if action == "calibrate":
            self.calibration.start()
            LOGGER.info("Calibration started. Show your right hand, hold still briefly, then conduct naturally.")
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
        if action == "cue_toggle_selected":
            selected_index = self.last_cue.selected_index
            if selected_index is None:
                LOGGER.info("Cue toggle skipped: no left-hand target is currently selected.")
                return False
            active = self.music.toggle_group(selected_index)
            self.last_cue.active_indices = self.music.active_group_indices
            if active is None:
                LOGGER.info("Cue toggle skipped: current track does not support grouped cue control.")
                return False
            LOGGER.info(
                "Cue target %s %s.",
                self.last_cue.selected_label,
                "enabled" if active else "muted",
            )
            return False
        if action == "cue_enable_all":
            result = self.music.activate_all_groups()
            self.last_cue.active_indices = self.music.active_group_indices
            if result is None:
                LOGGER.info("Enable-all skipped: current track does not support grouped cue control.")
                return False
            LOGGER.info("All cue groups enabled.")
            return False
        if action == "tempo_down":
            self.manual_tempo_bias -= self.config.music.rate_step
            self.music.set_rate(self.last_tempo.rate + self.manual_tempo_bias)
            LOGGER.info(
                "Tempo trim decreased: bias=%.2f effective_rate=%.2f",
                self.manual_tempo_bias,
                self.music.playback_rate,
            )
            return False
        if action == "tempo_up":
            self.manual_tempo_bias += self.config.music.rate_step
            self.music.set_rate(self.last_tempo.rate + self.manual_tempo_bias)
            LOGGER.info(
                "Tempo trim increased: bias=%.2f effective_rate=%.2f",
                self.manual_tempo_bias,
                self.music.playback_rate,
            )
            return False
        return False

    def _snapshot_state(self, tracking: TrackingResult) -> AppState:
        right_hand_state = self._role_state(tracking.tempo_hand, fallback_label="Right")
        cue_hand_state = self._role_state(tracking.cue_hand, fallback_label="Left")
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
        tempo = TempoState(
            rate=self.last_tempo.rate,
            raw_rate=self.last_tempo.raw_rate,
            motion_energy_px=self.last_tempo.motion_energy_px,
            floor_px=self.last_tempo.floor_px,
            ceiling_px=self.last_tempo.ceiling_px,
            normalized_motion=self.last_tempo.normalized_motion,
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
            tempo_hand=right_hand_state,
            dynamics_hand=self._role_state(tracking.tempo_hand, fallback_label="Right"),
            cue_hand=cue_hand_state,
            playback=playback,
            tempo=tempo,
            dynamics=dynamics,
            cue=self.last_cue,
            calibration=calibration,
            fallback_hint=self.controls.describe(),
        )

    def _role_state(self, hand: TrackedHand | None, fallback_label: str) -> HandRoleState:
        if hand is None:
            return HandRoleState(label=fallback_label)
        return HandRoleState(
            label=hand.label,
            mode=hand.mode,
            tracking_ok=hand.tracking_ok,
            confidence=hand.confidence,
            status_text=self._hand_status_text(hand),
        )

    def _hand_status_text(self, hand: TrackedHand) -> str:
        if hand.mode == "live" and hand.tracking_ok:
            return "TRACKING"
        if hand.mode == "hold":
            return "HOLD"
        if hand.mode == "live":
            return "LOW CONF"
        return "SEARCHING"

    def _motion_status(self) -> str:
        return (
            f"tempo buffer: {self.tempo_motion.describe()} | "
            f"dynamics buffer: {self.dynamics_motion.describe()}"
        )
