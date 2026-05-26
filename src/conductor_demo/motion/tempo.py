from __future__ import annotations

from dataclasses import dataclass
from math import hypot

from conductor_demo.motion.buffer import MotionBuffer


@dataclass(slots=True)
class TempoReading:
    rate: float
    raw_rate: float
    motion_energy_px: float
    floor_px: float
    ceiling_px: float
    normalized_motion: float


class TempoEstimator:
    """Estimate playback rate from recent conducting motion energy."""

    def __init__(
        self,
        window_seconds: float,
        min_samples: int,
        smoothing_alpha: float,
        idle_smoothing_alpha: float,
        confidence_floor: float,
        motion_floor_hand_scales: float,
        motion_ceiling_hand_scales: float,
        output_deadband: float,
        min_rate: float,
        neutral_rate: float,
        max_rate: float,
    ) -> None:
        if max_rate <= min_rate:
            raise ValueError("max_rate must be greater than min_rate")
        if not min_rate <= neutral_rate <= max_rate:
            raise ValueError("neutral_rate must sit between min_rate and max_rate")

        self.window_seconds = window_seconds
        self.min_samples = min_samples
        self.smoothing_alpha = smoothing_alpha
        self.idle_smoothing_alpha = idle_smoothing_alpha
        self.confidence_floor = confidence_floor
        self.motion_floor_hand_scales = motion_floor_hand_scales
        self.motion_ceiling_hand_scales = motion_ceiling_hand_scales
        self.output_deadband = output_deadband
        self.min_rate = min_rate
        self.neutral_rate = neutral_rate
        self.max_rate = max_rate

        self._reference_hand_scale_px: float | None = None
        self._current_rate = self.neutral_rate
        self._last_raw_rate = self.neutral_rate
        self._last_motion_energy_px = 0.0
        self._last_floor_px = 0.0
        self._last_ceiling_px = 1.0
        self._last_normalized_motion = 0.0

    def reset(self) -> None:
        self._reference_hand_scale_px = None
        self._current_rate = self.neutral_rate
        self._last_raw_rate = self.neutral_rate
        self._last_motion_energy_px = 0.0
        self._last_floor_px = 0.0
        self._last_ceiling_px = 1.0
        self._last_normalized_motion = 0.0

    def current(self) -> TempoReading:
        return TempoReading(
            rate=self._current_rate,
            raw_rate=self._last_raw_rate,
            motion_energy_px=self._last_motion_energy_px,
            floor_px=self._last_floor_px,
            ceiling_px=self._last_ceiling_px,
            normalized_motion=self._last_normalized_motion,
        )

    def update(
        self,
        motion_buffer: MotionBuffer,
        timestamp: float,
        tracking_ok: bool,
        hand_scale_px: float | None = None,
        baseline_hand_scale_px: float | None = None,
        motion_floor_px_override: float | None = None,
        motion_ceiling_px_override: float | None = None,
        freeze_output: bool = False,
    ) -> TempoReading:
        if freeze_output:
            return self.current()

        reference_hand_scale_px = self._resolve_reference_hand_scale(
            hand_scale_px=hand_scale_px,
            baseline_hand_scale_px=baseline_hand_scale_px,
        )
        recent_samples = motion_buffer.recent_samples(now=timestamp, window_seconds=self.window_seconds)
        motion_energy_px = self._estimate_motion_energy(recent_samples)
        floor_px, ceiling_px = self._resolve_motion_gate(
            reference_hand_scale_px=reference_hand_scale_px,
            motion_floor_px_override=motion_floor_px_override,
            motion_ceiling_px_override=motion_ceiling_px_override,
        )
        normalized_motion = self._clip((motion_energy_px - floor_px) / max(ceiling_px - floor_px, 1.0))
        raw_rate = self.min_rate + normalized_motion * (self.max_rate - self.min_rate)

        avg_confidence = 0.0
        if recent_samples:
            avg_confidence = sum(sample.confidence for sample in recent_samples) / len(recent_samples)

        tracking_ready = (
            tracking_ok
            and len(recent_samples) >= self.min_samples
            and avg_confidence >= self.confidence_floor
        )

        target_rate = self.neutral_rate
        alpha = self.idle_smoothing_alpha
        if tracking_ready:
            target_rate = raw_rate
            alpha = self.smoothing_alpha

        if abs(target_rate - self._current_rate) < self.output_deadband:
            target_rate = self._current_rate

        self._current_rate += alpha * (target_rate - self._current_rate)
        self._current_rate = self._clip_rate(self._current_rate)
        self._last_raw_rate = self._clip_rate(raw_rate if tracking_ready else self.neutral_rate)
        self._last_motion_energy_px = motion_energy_px
        self._last_floor_px = floor_px
        self._last_ceiling_px = ceiling_px
        self._last_normalized_motion = normalized_motion
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

    def _resolve_motion_gate(
        self,
        reference_hand_scale_px: float,
        motion_floor_px_override: float | None,
        motion_ceiling_px_override: float | None,
    ) -> tuple[float, float]:
        floor_px = float(motion_floor_px_override) if motion_floor_px_override and motion_floor_px_override > 0 else 0.0
        if floor_px <= 0:
            floor_px = max(reference_hand_scale_px * self.motion_floor_hand_scales, 1.0)

        ceiling_px = (
            float(motion_ceiling_px_override)
            if motion_ceiling_px_override and motion_ceiling_px_override > floor_px
            else 0.0
        )
        if ceiling_px <= floor_px:
            ceiling_px = max(
                reference_hand_scale_px * self.motion_ceiling_hand_scales,
                floor_px + reference_hand_scale_px * 1.2,
            )
        return floor_px, ceiling_px

    def _estimate_motion_energy(self, recent_samples: list) -> float:
        if len(recent_samples) < 2:
            return 0.0

        energy = 0.0
        for previous, current in zip(recent_samples, recent_samples[1:]):
            energy += hypot(current.x - previous.x, current.y - previous.y)
        return float(energy)

    def _clip(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def _clip_rate(self, value: float) -> float:
        return max(self.min_rate, min(self.max_rate, float(value)))
