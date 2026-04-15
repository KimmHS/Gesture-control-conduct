from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


def _require_cv2() -> Any:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("OpenCV is required. Install dependencies with `pip install -r requirements.txt`.") from exc
    return cv2


@dataclass(slots=True)
class FramePacket:
    frame: Any
    timestamp: float
    frame_index: int
    width: int
    height: int


class CameraStream:
    """Small OpenCV webcam wrapper."""

    def __init__(
        self,
        index: int,
        frame_width: int,
        frame_height: int,
        mirror: bool,
    ) -> None:
        self.index = index
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.mirror = mirror
        self.is_open = False
        self._cv2: Any | None = None
        self._capture: Any | None = None
        self._frame_index = 0

    def open(self) -> None:
        cv2 = _require_cv2()
        self._cv2 = cv2
        self._capture = cv2.VideoCapture(self.index)
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        if not self._capture.isOpened():
            raise RuntimeError(f"Could not open webcam device {self.index}.")
        self.is_open = True

    def read(self) -> FramePacket:
        if not self.is_open or self._capture is None or self._cv2 is None:
            raise RuntimeError("CameraStream.read() called before opening the camera.")

        ok, frame = self._capture.read()
        if not ok or frame is None:
            raise RuntimeError("Failed to read a frame from the webcam.")

        if self.mirror:
            frame = self._cv2.flip(frame, 1)

        self._frame_index += 1
        height, width = frame.shape[:2]
        return FramePacket(
            frame=frame,
            timestamp=time.monotonic(),
            frame_index=self._frame_index,
            width=width,
            height=height,
        )

    def close(self) -> None:
        if self._capture is not None:
            self._capture.release()
        self._capture = None
        self.is_open = False

    def describe(self) -> str:
        return (
            f"device={self.index} "
            f"size={self.frame_width}x{self.frame_height} "
            f"mirror={self.mirror} "
            f"open={self.is_open}"
        )
