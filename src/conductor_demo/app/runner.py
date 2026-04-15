from __future__ import annotations

import logging
import time
from typing import Any

import numpy as np

from conductor_demo.app.state import AppState, CalibrationState, PlaybackState
from conductor_demo.config.defaults import AppConfig
from conductor_demo.motion.buffer import MotionBuffer, MotionSample
from conductor_demo.motion.calibration import CalibrationManager
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
        )
        self.motion = MotionBuffer(maxlen=config.motion.buffer_size)
        self.calibration = CalibrationManager(enabled=True)
        self.music = MusicController(
            base_bpm=config.music.base_bpm,
            default_volume=config.music.default_volume,
        )
        self.controls = FallbackControls(config.controls.keymap())
        self.overlay = OverlayRenderer(
            app_name=config.app_name,
            show_landmarks=config.ui.show_landmarks,
        )

    def run(self) -> int:
        LOGGER.info("Starting %s", self.config.app_name)
        self.tracker.start()

        try:
            if self.self_test:
                self._run_self_test()
                LOGGER.info("Self-test completed.")
                return 0

            return self._run_camera_loop()
        finally:
            try:
                cv2 = _require_cv2()
                cv2.destroyAllWindows()
            except RuntimeError:
                pass
            self.tracker.stop()
            self.camera.close()

    def _run_self_test(self) -> None:
        frame = np.zeros(
            (self.config.vision.frame_height, self.config.vision.frame_width, 3),
            dtype=np.uint8,
        )
        tracking = self.tracker.process(frame, timestamp=time.monotonic())
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
        self.camera.open()
        cv2.namedWindow(self.config.ui.window_name, cv2.WINDOW_NORMAL)

        frame_count = 0
        while True:
            packet = self.camera.read()
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

    def _handle_action(self, action: str, tracking: TrackingResult) -> bool:
        if action == "quit":
            return True
        if action == "reset":
            self.motion.clear()
            self.tracker.reset()
            self.music.reset()
            self.calibration.reset()
            LOGGER.info("Reset tracking, calibration, and playback state.")
            return False
        if action == "calibrate":
            if tracking.hand_scale_px is not None:
                self.calibration.complete(tracking.hand_scale_px)
                LOGGER.info("Calibration placeholder updated with baseline hand scale %.1f px.", tracking.hand_scale_px)
            else:
                self.calibration.start()
                LOGGER.info("Calibration placeholder armed. Show the conducting hand to complete later.")
            return False
        if action == "play_pause":
            self.music.toggle_play_pause()
            LOGGER.info("Playback placeholder toggled: playing=%s", self.music.is_playing)
            return False
        return False

    def _snapshot_state(self, tracking: TrackingResult) -> AppState:
        playback = PlaybackState(
            is_playing=self.music.is_playing,
            rate=self.music.playback_rate,
            volume=self.music.volume,
        )
        calibration = CalibrationState(
            enabled=self.calibration.enabled,
            calibrated=self.calibration.calibrated,
            baseline_hand_scale=self.calibration.baseline_hand_scale,
        )
        return AppState(
            tracking_ok=tracking.tracking_ok,
            active_hand=tracking.active_hand,
            playback=playback,
            calibration=calibration,
            fallback_hint=self.controls.describe(),
        )
