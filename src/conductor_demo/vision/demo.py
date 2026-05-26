from __future__ import annotations

import argparse
import logging
import time
from typing import Any

import numpy as np

from conductor_demo.app.state import AppState, CalibrationState, DynamicsState, HandRoleState, PlaybackState, TempoState
from conductor_demo.config.defaults import ControlsConfig, DynamicsConfig, MotionConfig, MusicConfig, UIConfig, VisionConfig
from conductor_demo.motion.buffer import MotionBuffer, MotionSample
from conductor_demo.motion.dynamics import DynamicsEstimator
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


class TrackingDemo:
    """Standalone webcam tracker demo."""

    def __init__(
        self,
        vision: VisionConfig,
        motion: MotionConfig,
        dynamics: DynamicsConfig,
        music: MusicConfig,
        controls: ControlsConfig,
        ui: UIConfig,
        max_frames: int | None = None,
        self_test: bool = False,
    ) -> None:
        self.vision = vision
        self.motion_config = motion
        self.rate_step = music.rate_step
        self.ui = ui
        self.max_frames = max_frames
        self.self_test = self_test
        self.camera = CameraStream(
            index=vision.camera_index,
            frame_width=vision.frame_width,
            frame_height=vision.frame_height,
            mirror=vision.mirror,
        )
        self.tracker = HandTracker(
            detection_confidence=vision.detection_confidence,
            tracking_confidence=vision.tracking_confidence,
            smoothing_alpha=motion.smoothing_alpha,
            hold_seconds=motion.lost_tracking_hold_seconds,
            max_num_hands=vision.max_num_hands,
            model_complexity=vision.model_complexity,
            hand_confidence_threshold=vision.hand_confidence_threshold,
            min_hand_scale_px=vision.min_hand_scale_px,
            swap_left_right_labels=vision.swap_left_right_labels,
        )
        self.motion = MotionBuffer(maxlen=motion.buffer_size)
        self.dynamics = DynamicsEstimator(
            window_seconds=dynamics.window_seconds,
            min_samples=dynamics.min_samples,
            smoothing_alpha=dynamics.smoothing_alpha,
            idle_smoothing_alpha=dynamics.idle_smoothing_alpha,
            confidence_floor=dynamics.confidence_floor,
            reference_span_hand_scales=dynamics.reference_span_hand_scales,
            output_deadband=dynamics.output_deadband,
            default_volume=music.default_volume,
            min_volume=music.min_volume,
            max_volume=music.max_volume,
        )
        self.music = MusicController(
            base_bpm=music.base_bpm,
            default_volume=music.default_volume,
            min_volume=music.min_volume,
            max_volume=music.max_volume,
            min_rate=music.min_rate,
            max_rate=music.max_rate,
            demo_track_path=music.demo_track_path,
        )
        self.last_dynamics = self.dynamics.current()
        demo_keymap = {
            key: action
            for key, action in controls.keymap().items()
            if action != "calibrate"
        }
        self.controls = FallbackControls(demo_keymap)
        self.overlay = OverlayRenderer(
            app_name="Conductor Tracking Demo",
            show_landmarks=ui.show_landmarks,
            show_help=ui.show_help_overlay,
        )
        self.camera_open_retries = vision.camera_open_retries
        self.camera_retry_delay_seconds = vision.camera_retry_delay_seconds
        self.camera_reopen_retries = vision.camera_reopen_retries
        self._camera_failures = 0

    def run(self) -> int:
        LOGGER.info("Starting Conductor Tracking Demo")
        try:
            self.tracker.start()
            if self.self_test:
                self._run_self_test()
                return 0
            return self._run_loop()
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
        frame = np.zeros((self.vision.frame_height, self.vision.frame_width, 3), dtype=np.uint8)
        tracking = self.tracker.process(frame, timestamp=time.monotonic())
        source_hand = self._motion_source_hand(tracking)
        self.last_dynamics = self.dynamics.update(
            motion_buffer=self.motion,
            timestamp=time.monotonic(),
            tracking_ok=bool(source_hand and source_hand.tracking_ok),
            hand_scale_px=source_hand.hand_scale_px if source_hand is not None else None,
        )
        self.music.set_volume(self.last_dynamics.volume)
        debug_frame = self.overlay.draw_debug(
            frame=frame,
            tracking=tracking,
            motion_buffer=self.motion,
            app_state=self._snapshot_state(tracking),
            trail_length=self.motion_config.trail_length,
        )
        LOGGER.info("Self-test tracker status: %s", self.tracker.describe())
        LOGGER.info("Self-test frame rendered: %s", debug_frame.shape)

    def _run_loop(self) -> int:
        cv2 = _require_cv2()
        self.camera.open(
            retries=self.camera_open_retries,
            retry_delay_seconds=self.camera_retry_delay_seconds,
        )
        cv2.namedWindow(self.ui.window_name, cv2.WINDOW_NORMAL)

        frame_count = 0
        while True:
            try:
                packet = self.camera.read()
                self._camera_failures = 0
            except RuntimeError as exc:
                self._camera_failures += 1
                LOGGER.warning("Camera read failed (%d): %s", self._camera_failures, exc)
                if self._camera_failures > self.camera_reopen_retries:
                    raise RuntimeError("Camera feed could not be recovered in tracking demo.") from exc
                self.camera.reopen(
                    retries=self.camera_reopen_retries,
                    retry_delay_seconds=self.camera_retry_delay_seconds,
                )
                LOGGER.info("Camera reopened successfully.")
                continue
            tracking = self.tracker.process(packet.frame, timestamp=packet.timestamp)
            source_hand = self._motion_source_hand(tracking)
            if (
                source_hand is not None
                and source_hand.mode == "live"
                and source_hand.tracking_ok
                and source_hand.wrist_px
                and source_hand.raw_wrist_px
            ):
                self.motion.append(
                    MotionSample(
                        x=source_hand.wrist_px[0],
                        y=source_hand.wrist_px[1],
                        timestamp=packet.timestamp,
                        confidence=source_hand.confidence,
                        raw_x=source_hand.raw_wrist_px[0],
                        raw_y=source_hand.raw_wrist_px[1],
                        is_live=True,
                    )
                )

            self.last_dynamics = self.dynamics.update(
                motion_buffer=self.motion,
                timestamp=packet.timestamp,
                tracking_ok=bool(source_hand and source_hand.tracking_ok),
                hand_scale_px=source_hand.hand_scale_px if source_hand is not None else None,
                freeze_output=bool(source_hand and source_hand.mode == "hold"),
            )
            self.music.set_volume(self.last_dynamics.volume)
            frame = self.overlay.draw_debug(
                frame=packet.frame,
                tracking=tracking,
                motion_buffer=self.motion,
                app_state=self._snapshot_state(tracking),
                trail_length=self.motion_config.trail_length,
            )
            cv2.imshow(self.ui.window_name, frame)

            action = self.controls.resolve_keycode(cv2.waitKey(1) & 0xFF)
            if action is not None and self._handle_action(action):
                break

            frame_count += 1
            if self.max_frames is not None and frame_count >= self.max_frames:
                break

        return 0

    def _handle_action(self, action: str) -> bool:
        if action == "quit":
            return True
        if action == "reset":
            self.motion.clear()
            self.tracker.reset()
            self.dynamics.reset()
            self.music.reset()
            LOGGER.info("Tracking and playback reset.")
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
            self.music.adjust_rate(-self.rate_step)
            LOGGER.info("Playback rate decreased: %.2f", self.music.playback_rate)
            return False
        if action == "tempo_up":
            self.music.adjust_rate(self.rate_step)
            LOGGER.info("Playback rate increased: %.2f", self.music.playback_rate)
            return False
        return False

    def _snapshot_state(self, tracking: TrackingResult) -> AppState:
        right_hand_state = self._role_state(tracking.tempo_hand, "Right")
        cue_hand_state = self._role_state(tracking.cue_hand, "Left")
        return AppState(
            tracking_ok=tracking.tracking_ok,
            active_hand=tracking.active_hand,
            tempo_hand=right_hand_state,
            dynamics_hand=self._role_state(tracking.tempo_hand, "Right"),
            cue_hand=cue_hand_state,
            playback=PlaybackState(
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
            ),
            tempo=TempoState(
                rate=self.music.playback_rate,
                raw_rate=self.music.playback_rate,
            ),
            dynamics=DynamicsState(
                intensity=self.last_dynamics.intensity,
                raw_intensity=self.last_dynamics.raw_intensity,
                span_px=self.last_dynamics.span_px,
                reference_span_px=self.last_dynamics.reference_span_px,
            ),
            calibration=CalibrationState(
                enabled=False,
                status_text="DISABLED",
                status_detail="Calibration is available in the full demo",
            ),
            fallback_hint=self.controls.describe(),
        )

    def _motion_source_hand(self, tracking: TrackingResult) -> TrackedHand | None:
        if tracking.tempo_hand is not None and tracking.tempo_hand.mode != "lost":
            return tracking.tempo_hand
        if tracking.cue_hand is not None and tracking.cue_hand.mode != "lost":
            return tracking.cue_hand
        return None

    def _role_state(self, hand: TrackedHand | None, fallback_label: str) -> HandRoleState:
        if hand is None:
            return HandRoleState(label=fallback_label)
        if hand.mode == "live" and hand.tracking_ok:
            status = "TRACKING"
        elif hand.mode == "hold":
            status = "HOLD"
        elif hand.mode == "live":
            status = "LOW CONF"
        else:
            status = "SEARCHING"
        return HandRoleState(
            label=hand.label,
            mode=hand.mode,
            tracking_ok=hand.tracking_ok,
            confidence=hand.confidence,
            status_text=status,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Standalone webcam tracking demo")
    parser.add_argument("--camera-index", type=int, default=0, help="OpenCV webcam index")
    parser.add_argument("--frame-width", type=int, default=1280, help="Requested webcam width")
    parser.add_argument("--frame-height", type=int, default=720, help="Requested webcam height")
    parser.add_argument("--max-frames", type=int, help="Run for a fixed number of frames")
    parser.add_argument("--self-test", action="store_true", help="Run one synthetic frame without opening the webcam")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument("--no-mirror", action="store_true", help="Disable mirror mode")
    parser.add_argument(
        "--no-swap-hands",
        action="store_true",
        help="Keep MediaPipe's original left/right labels without swapping them",
    )
    parser.add_argument("--hide-landmarks", action="store_true", help="Hide landmark dots in the debug overlay")
    return parser


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def main() -> int:
    args = build_parser().parse_args()
    configure_logging(args.verbose)

    vision = VisionConfig(
        camera_index=args.camera_index,
        frame_width=args.frame_width,
        frame_height=args.frame_height,
        mirror=not args.no_mirror,
        swap_left_right_labels=not args.no_swap_hands,
    )
    motion = MotionConfig()
    dynamics = DynamicsConfig()
    music = MusicConfig()
    controls = ControlsConfig()
    ui = UIConfig(
        window_name="Conductor Tracking Demo",
        show_landmarks=not args.hide_landmarks,
    )
    return TrackingDemo(
        vision=vision,
        motion=motion,
        dynamics=dynamics,
        music=music,
        controls=controls,
        ui=ui,
        max_frames=args.max_frames,
        self_test=args.self_test,
    ).run()


if __name__ == "__main__":
    raise SystemExit(main())
