from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from statistics import mean


@dataclass(slots=True)
class MotionSample:
    x: float
    y: float
    timestamp: float
    confidence: float
    raw_x: float
    raw_y: float
    is_live: bool = True


class MotionBuffer:
    """Rolling wrist-trajectory buffer."""

    def __init__(self, maxlen: int = 120) -> None:
        self.maxlen = maxlen
        self._samples: deque[MotionSample] = deque(maxlen=maxlen)

    def append(self, sample: MotionSample) -> None:
        self._samples.append(sample)

    def clear(self) -> None:
        self._samples.clear()

    def latest(self) -> MotionSample | None:
        return self._samples[-1] if self._samples else None

    def samples(self, limit: int | None = None) -> list[MotionSample]:
        items = list(self._samples)
        if limit is not None:
            items = items[-limit:]
        return items

    def recent_samples(self, now: float, window_seconds: float) -> list[MotionSample]:
        threshold = now - max(window_seconds, 0.0)
        return [sample for sample in self._samples if sample.is_live and sample.timestamp >= threshold]

    def points(self, limit: int | None = None) -> list[tuple[int, int]]:
        return [(int(sample.x), int(sample.y)) for sample in self.samples(limit=limit)]

    def average_confidence(self, limit: int | None = None) -> float:
        samples = self.samples(limit=limit)
        if not samples:
            return 0.0
        return float(mean(sample.confidence for sample in samples))

    def __len__(self) -> int:
        return len(self._samples)

    def describe(self) -> str:
        return (
            f"motion buffer: {len(self._samples)}/{self.maxlen} samples "
            f"avg_conf={self.average_confidence(limit=30):.2f}"
        )
