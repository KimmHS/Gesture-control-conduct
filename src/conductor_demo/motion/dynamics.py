from __future__ import annotations

from dataclasses import dataclass
from math import hypot

from conductor_demo.motion.buffer import MotionBuffer


@dataclass(slots=True)
class DynamicsReading:
    intensity: float
    raw_intensity: float
    span_px: float
    reference_span_px: float
    volume: float


class DynamicsEstimator:
    """Estimate conducting intensity from recent wrist-motion span."""

    def __init__(
        self,
        window_seconds: float,
        min_samples: int,
        smoothing_alpha: float,
        idle_smoothing_alpha: float,
        confidence_floor: float,
        reference_span_hand_scales: float,
        output_deadband: float,
        default_volume: float,
        min_volume: float,
        max_volume: float,
    ) -> None:
        if max_volume <= min_volume:
            raise ValueError("max_volume must be greater than min_volume")

        self.window_seconds = window_seconds
        self.min_samples = min_samples
        self.smoothing_alpha = smoothing_alpha
        self.idle_smoothing_alpha = idle_smoothing_alpha
        self.confidence_floor = confidence_floor
        self.reference_span_hand_scales = reference_span_hand_scales
        self.output_deadband = output_deadband
        self.min_volume = min_volume
        self.max_volume = max_volume
        self.idle_intensity = self._volume_to_intensity(default_volume)

        self._reference_hand_scale_px: float | None = None
        self._current_intensity = self.idle_intensity
        self._last_raw_intensity = self.idle_intensity
        self._last_span_px = 0.0
        self._last_reference_span_px = 1.0

    def reset(self) -> None:
        self._reference_hand_scale_px = None
        self._current_intensity = self.idle_intensity
        self._last_raw_intensity = self.idle_intensity
        self._last_span_px = 0.0
        self._last_reference_span_px = 1.0

    def current(self) -> DynamicsReading:
        return DynamicsReading(
            intensity=self._current_intensity,
            raw_intensity=self._last_raw_intensity,
            span_px=self._last_span_px,
            reference_span_px=self._last_reference_span_px,
            volume=self._intensity_to_volume(self._current_intensity),
        )

    def update(
        self,
        motion_buffer: MotionBuffer,
        timestamp: float,
        tracking_ok: bool,
        hand_scale_px: float | None = None,
        baseline_hand_scale_px: float | None = None,
        reference_span_px_override: float | None = None,
        freeze_output: bool = False,
    ) -> DynamicsReading:
        if freeze_output:
            return self.current()

        reference_hand_scale_px = self._resolve_reference_hand_scale(
            hand_scale_px=hand_scale_px,
            baseline_hand_scale_px=baseline_hand_scale_px,
        )
        recent_samples = motion_buffer.recent_samples(now=timestamp, window_seconds=self.window_seconds)
        span_px = self._estimate_span(recent_samples)
        if reference_span_px_override is not None and reference_span_px_override > 0:
            reference_span_px = float(reference_span_px_override)
        else:
            reference_span_px = max(reference_hand_scale_px * self.reference_span_hand_scales, 1.0)
        raw_intensity = self._clip(span_px / reference_span_px)

        avg_confidence = 0.0
        if recent_samples:
            avg_confidence = sum(sample.confidence for sample in recent_samples) / len(recent_samples)

        target_intensity = self.idle_intensity
        alpha = self.idle_smoothing_alpha
        if (
            tracking_ok
            and len(recent_samples) >= self.min_samples
            and avg_confidence >= self.confidence_floor
        ):
            target_intensity = raw_intensity
            alpha = self.smoothing_alpha

        if abs(target_intensity - self._current_intensity) < self.output_deadband:
            target_intensity = self._current_intensity

        self._current_intensity += alpha * (target_intensity - self._current_intensity)
        self._current_intensity = self._clip(self._current_intensity)
        self._last_raw_intensity = raw_intensity
        self._last_span_px = span_px
        self._last_reference_span_px = reference_span_px
        return self.current()

    def _resolve_reference_hand_scale(
        self,
        hand_scale_px: float | None,
        baseline_hand_scale_px: float | None,
    ) -> float:
        candidate = baseline_hand_scale_px or hand_scale_px
        if candidate is not None and candidate > 0:
            if self._reference_hand_scale_px is None:
                self._reference_hand_scale_px = candidate
            else:
                self._reference_hand_scale_px += 0.12 * (candidate - self._reference_hand_scale_px)
        return self._reference_hand_scale_px or 1.0

    def _estimate_span(self, recent_samples: list) -> float:
        if len(recent_samples) < 2:
            return 0.0

        xs = [sample.x for sample in recent_samples]
        ys = [sample.y for sample in recent_samples]
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        return hypot(width, height)

    def _intensity_to_volume(self, intensity: float) -> float:
        return self.min_volume + self._clip(intensity) * (self.max_volume - self.min_volume)

    def _volume_to_intensity(self, volume: float) -> float:
        return self._clip((volume - self.min_volume) / (self.max_volume - self.min_volume))

    def _clip(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))
