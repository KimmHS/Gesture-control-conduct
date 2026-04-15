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
        self._backend_name = "default"

    def open(self, retries: int = 1, retry_delay_seconds: float = 0.0) -> None:
        cv2 = _require_cv2()
        self._cv2 = cv2
        last_error: RuntimeError | None = None
        attempts = max(retries, 1)

        for attempt in range(attempts):
            self.close()
            capture, backend_name = self._open_with_backends(cv2)
            if capture is not None:
                self._capture = capture
                self._backend_name = backend_name
                self.is_open = True
                return

            last_error = RuntimeError(f"Could not open webcam device {self.index}.")
            if attempt < attempts - 1 and retry_delay_seconds > 0:
                time.sleep(retry_delay_seconds)

        raise last_error or RuntimeError(f"Could not open webcam device {self.index}.")

    def reopen(self, retries: int = 2, retry_delay_seconds: float = 0.25) -> None:
        self.open(retries=retries, retry_delay_seconds=retry_delay_seconds)

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
        self._backend_name = "default"

    def describe(self) -> str:
        return (
            f"device={self.index} "
            f"size={self.frame_width}x{self.frame_height} "
            f"mirror={self.mirror} "
            f"backend={self._backend_name} "
            f"open={self.is_open}"
        )

    def _open_with_backends(self, cv2: Any) -> tuple[Any | None, str]:
        backends: list[tuple[str, int | None]] = []
        if hasattr(cv2, "CAP_DSHOW"):
            backends.append(("dshow", cv2.CAP_DSHOW))
        backends.append(("default", None))

        for backend_name, backend_id in backends:
            if backend_id is None:
                capture = cv2.VideoCapture(self.index)
            else:
                capture = cv2.VideoCapture(self.index, backend_id)
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            if capture.isOpened():
                return capture, backend_name
            capture.release()
        return None, "default"
