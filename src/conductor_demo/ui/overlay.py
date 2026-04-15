from __future__ import annotations

from typing import Any

import numpy as np

from conductor_demo.app.state import AppState
from conductor_demo.motion.buffer import MotionBuffer
from conductor_demo.vision.tracker import TrackingResult


def _require_cv2() -> Any:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("OpenCV is required. Install dependencies with `pip install -r requirements.txt`.") from exc
    return cv2


class OverlayRenderer:
    """Lightweight debug overlay for the webcam tracking layer."""

    def __init__(self, app_name: str, show_landmarks: bool = True) -> None:
        self.app_name = app_name
        self.show_landmarks = show_landmarks

    def render_status(
        self,
        app_state: AppState,
        camera_status: str,
        tracker_status: str,
        motion_status: str,
    ) -> str:
        lines = [
            f"{self.app_name}",
            f"camera: {camera_status}",
            f"tracker: {tracker_status}",
            motion_status,
            f"playback: playing={app_state.playback.is_playing} rate={app_state.playback.rate:.2f} volume={app_state.playback.volume:.2f}",
            f"calibration: enabled={app_state.calibration.enabled} calibrated={app_state.calibration.calibrated}",
            f"fallback: {app_state.fallback_hint}",
        ]
        return "\n".join(lines)

    def draw_debug(
        self,
        frame: Any,
        tracking: TrackingResult,
        motion_buffer: MotionBuffer,
        app_state: AppState,
        trail_length: int,
    ) -> Any:
        cv2 = _require_cv2()
        canvas = frame.copy()

        if self.show_landmarks and tracking.landmarks_px:
            for point in tracking.landmarks_px:
                cv2.circle(canvas, point, 2, (120, 120, 120), -1)

        if tracking.bbox is not None:
            x1, y1, x2, y2 = tracking.bbox
            cv2.rectangle(canvas, (x1, y1), (x2, y2), self._status_color(tracking.mode), 2)

        points = motion_buffer.points(limit=trail_length)
        if len(points) > 1:
            polyline = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(canvas, [polyline], False, (0, 200, 255), 2)

        if tracking.wrist_px is not None:
            wrist = (int(tracking.wrist_px[0]), int(tracking.wrist_px[1]))
            cv2.circle(canvas, wrist, 8, self._status_color(tracking.mode), 2)
            cv2.circle(canvas, wrist, 3, (255, 255, 255), -1)

        info_lines = [
            self.app_name,
            f"tracking: {tracking.mode} | hand={tracking.active_hand or '-'} | conf={tracking.confidence:.2f} | hands={tracking.hand_count}",
            f"buffer: {len(motion_buffer)} samples | avg_conf={motion_buffer.average_confidence(limit=trail_length):.2f}",
            f"debug: {tracking.debug_message}",
            app_state.fallback_hint,
        ]
        for idx, line in enumerate(info_lines):
            y = 28 + idx * 26
            cv2.putText(canvas, line, (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (20, 20, 20), 1)
            cv2.putText(canvas, line, (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        return canvas

    def _status_color(self, mode: str) -> tuple[int, int, int]:
        if mode == "live":
            return (40, 220, 40)
        if mode == "hold":
            return (0, 215, 255)
        return (40, 40, 220)
