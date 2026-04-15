from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from statistics import median


@dataclass(slots=True)
class CalibrationSample:
    x: float
    y: float
    timestamp: float
    hand_scale_px: float


@dataclass(slots=True)
class CalibrationProfile:
    baseline_wrist_px: tuple[float, float] | None = None
    baseline_hand_scale: float | None = None
    comfortable_motion_span_px: float | None = None
    dynamics_reference_span_px: float | None = None
    tempo_motion_floor_px: float | None = None
    tempo_motion_ceiling_px: float | None = None


class CalibrationManager:
    """Short, robust calibration flow for baseline pose and motion range."""

    def __init__(
        self,
        enabled: bool = True,
        hold_seconds: float = 1.0,
        motion_seconds: float = 2.0,
        min_hold_samples: int = 12,
        min_motion_samples: int = 20,
        min_motion_span_px: float = 90.0,
        min_motion_span_hand_scales: float = 4.2,
        dynamics_span_multiplier: float = 1.05,
        tempo_motion_floor_ratio: float = 0.18,
        tempo_motion_ceiling_ratio: float = 0.68,
        tracking_loss_reset_seconds: float = 0.5,
    ) -> None:
        self.enabled = enabled
        self.hold_seconds = hold_seconds
        self.motion_seconds = motion_seconds
        self.min_hold_samples = min_hold_samples
        self.min_motion_samples = min_motion_samples
        self.min_motion_span_px = min_motion_span_px
        self.min_motion_span_hand_scales = min_motion_span_hand_scales
        self.dynamics_span_multiplier = dynamics_span_multiplier
        self.tempo_motion_floor_ratio = tempo_motion_floor_ratio
        self.tempo_motion_ceiling_ratio = tempo_motion_ceiling_ratio
        self.tracking_loss_reset_seconds = tracking_loss_reset_seconds

        self.active = False
        self.calibrated = False
        self.stage = "idle"
        self.progress = 0.0
        self.status_text = "READY"
        self.status_detail = "Press C to run a quick calibration"

        self.profile = CalibrationProfile()

        self._stage_start_timestamp: float | None = None
        self._hold_samples: list[CalibrationSample] = []
        self._motion_samples: list[CalibrationSample] = []
        self._pending_baseline_wrist_px: tuple[float, float] | None = None
        self._pending_baseline_hand_scale: float | None = None
        self._last_visible_timestamp: float | None = None

    def start(self) -> None:
        self.active = True
        self.stage = "waiting"
        self.progress = 0.0
        self.status_text = "SHOW HAND"
        self.status_detail = "Show one clear conducting hand to begin calibration"
        self._stage_start_timestamp = None
        self._hold_samples.clear()
        self._motion_samples.clear()
        self._pending_baseline_wrist_px = None
        self._pending_baseline_hand_scale = None
        self._last_visible_timestamp = None

    def update(
        self,
        timestamp: float,
        tracking_ok: bool,
        wrist_px: tuple[float, float] | None,
        hand_scale_px: float | None,
    ) -> bool:
        if not self.enabled or not self.active:
            return False

        if not tracking_ok or wrist_px is None or hand_scale_px is None:
            if (
                self._last_visible_timestamp is not None
                and timestamp - self._last_visible_timestamp >= self.tracking_loss_reset_seconds
            ):
                self._restart_current_calibration()
            if self.stage == "waiting":
                self.status_text = "SHOW HAND"
                self.status_detail = "Show one clear conducting hand to begin calibration"
            elif self.stage == "hold":
                self.status_text = "HOLD STILL"
                self.status_detail = "Keep your hand visible while holding a neutral pose"
            else:
                self.status_text = "MOVE NATURALLY"
                self.status_detail = "Keep your hand visible while moving through your demo range"
            return False

        self._last_visible_timestamp = timestamp
        sample = CalibrationSample(
            x=wrist_px[0],
            y=wrist_px[1],
            timestamp=timestamp,
            hand_scale_px=hand_scale_px,
        )

        if self.stage == "waiting":
            self.stage = "hold"
            self._stage_start_timestamp = timestamp
            self._hold_samples.clear()

        if self.stage == "hold":
            return self._update_hold_stage(sample)
        if self.stage == "move":
            return self._update_motion_stage(sample)
        return False

    def reset(self) -> None:
        self.active = False
        self.calibrated = False
        self.stage = "idle"
        self.progress = 0.0
        self.status_text = "READY"
        self.status_detail = "Press C to run a quick calibration"
        self.profile = CalibrationProfile()
        self._stage_start_timestamp = None
        self._hold_samples.clear()
        self._motion_samples.clear()
        self._pending_baseline_wrist_px = None
        self._pending_baseline_hand_scale = None
        self._last_visible_timestamp = None

    def cancel_active(self) -> None:
        if not self.active:
            return

        self.active = False
        self.stage = "done" if self.calibrated else "idle"
        self.progress = 1.0 if self.calibrated else 0.0
        if self.calibrated:
            self.status_text = "CALIBRATED"
            span = self.comfortable_motion_span_px or 0.0
            self.status_detail = f"Range {span:.0f}px ready. Press C any time to recalibrate"
        else:
            self.status_text = "READY"
            self.status_detail = "Press C to run a quick calibration"
        self._stage_start_timestamp = None
        self._hold_samples.clear()
        self._motion_samples.clear()
        self._pending_baseline_wrist_px = None
        self._pending_baseline_hand_scale = None
        self._last_visible_timestamp = None

    @property
    def baseline_wrist_px(self) -> tuple[float, float] | None:
        return self.profile.baseline_wrist_px

    @property
    def baseline_hand_scale(self) -> float | None:
        return self.profile.baseline_hand_scale

    @property
    def comfortable_motion_span_px(self) -> float | None:
        return self.profile.comfortable_motion_span_px

    @property
    def dynamics_reference_span_px(self) -> float | None:
        return self.profile.dynamics_reference_span_px

    @property
    def tempo_motion_floor_px(self) -> float | None:
        return self.profile.tempo_motion_floor_px

    @property
    def tempo_motion_ceiling_px(self) -> float | None:
        return self.profile.tempo_motion_ceiling_px

    def _update_hold_stage(self, sample: CalibrationSample) -> bool:
        self._hold_samples.append(sample)
        elapsed = self._elapsed(sample.timestamp)
        time_progress = min(elapsed / max(self.hold_seconds, 0.01), 1.0)
        sample_progress = min(len(self._hold_samples) / max(self.min_hold_samples, 1), 1.0)
        self.progress = 0.45 * min(max(time_progress, sample_progress), 1.0)
        self.status_text = "HOLD STILL"
        self.status_detail = "Relax your hand at a comfortable neutral pose"

        if elapsed < self.hold_seconds or len(self._hold_samples) < self.min_hold_samples:
            return False

        xs = [item.x for item in self._hold_samples]
        ys = [item.y for item in self._hold_samples]
        scales = [item.hand_scale_px for item in self._hold_samples]
        self._pending_baseline_wrist_px = (float(median(xs)), float(median(ys)))
        self._pending_baseline_hand_scale = float(median(scales))
        self.stage = "move"
        self._stage_start_timestamp = sample.timestamp
        self._motion_samples.clear()
        self.progress = 0.45
        self.status_text = "MOVE NATURALLY"
        self.status_detail = "Conduct for a moment in the range you want to use live"
        return False

    def _update_motion_stage(self, sample: CalibrationSample) -> bool:
        self._motion_samples.append(sample)
        elapsed = self._elapsed(sample.timestamp)
        time_progress = min(elapsed / max(self.motion_seconds, 0.01), 1.0)
        sample_progress = min(len(self._motion_samples) / max(self.min_motion_samples, 1), 1.0)
        self.progress = 0.45 + 0.55 * min(max(time_progress, sample_progress), 1.0)
        self.status_text = "MOVE NATURALLY"
        self.status_detail = "Use your comfortable demo-sized conducting motion"

        enough_time = elapsed >= self.motion_seconds
        enough_samples = len(self._motion_samples) >= self.min_motion_samples
        if not enough_time or not enough_samples:
            return False

        self._complete_profile()
        return True

    def _complete_profile(self) -> None:
        if self._pending_baseline_wrist_px is None or self._pending_baseline_hand_scale is None:
            return

        xs = [item.x for item in self._motion_samples]
        ys = [item.y for item in self._motion_samples]

        width = self._percentile(xs, 0.9) - self._percentile(xs, 0.1)
        height = self._percentile(ys, 0.9) - self._percentile(ys, 0.1)
        comfortable_motion_span_px = hypot(width, height)
        min_span = max(
            self.min_motion_span_px,
            self._pending_baseline_hand_scale * self.min_motion_span_hand_scales,
        )
        comfortable_motion_span_px = max(float(comfortable_motion_span_px), float(min_span))
        dynamics_reference_span_px = max(
            comfortable_motion_span_px * self.dynamics_span_multiplier,
            self._pending_baseline_hand_scale * 2.8,
        )
        tempo_motion_floor_px = max(
            comfortable_motion_span_px * self.tempo_motion_floor_ratio,
            self._pending_baseline_hand_scale * 0.9,
        )
        tempo_motion_ceiling_px = max(
            comfortable_motion_span_px * self.tempo_motion_ceiling_ratio,
            tempo_motion_floor_px + self._pending_baseline_hand_scale * 1.2,
        )

        self.profile = CalibrationProfile(
            baseline_wrist_px=self._pending_baseline_wrist_px,
            baseline_hand_scale=self._pending_baseline_hand_scale,
            comfortable_motion_span_px=comfortable_motion_span_px,
            dynamics_reference_span_px=dynamics_reference_span_px,
            tempo_motion_floor_px=tempo_motion_floor_px,
            tempo_motion_ceiling_px=tempo_motion_ceiling_px,
        )
        self.calibrated = True
        self.active = False
        self.stage = "done"
        self.progress = 1.0
        self.status_text = "CALIBRATED"
        self.status_detail = (
            f"Range {comfortable_motion_span_px:.0f}px ready. Press C any time to recalibrate"
        )
        self._stage_start_timestamp = None
        self._hold_samples.clear()
        self._motion_samples.clear()
        self._pending_baseline_wrist_px = None
        self._pending_baseline_hand_scale = None

    def _elapsed(self, timestamp: float) -> float:
        if self._stage_start_timestamp is None:
            self._stage_start_timestamp = timestamp
            return 0.0
        return max(timestamp - self._stage_start_timestamp, 0.0)

    def _restart_current_calibration(self) -> None:
        self.stage = "waiting"
        self.progress = 0.0
        self.status_text = "SHOW HAND"
        self.status_detail = "Tracking was lost. Show your hand again to restart calibration"
        self._stage_start_timestamp = None
        self._hold_samples.clear()
        self._motion_samples.clear()
        self._pending_baseline_wrist_px = None
        self._pending_baseline_hand_scale = None
        self._last_visible_timestamp = None

    def _percentile(self, values: list[float], quantile: float) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        if len(ordered) == 1:
            return float(ordered[0])

        clamped = max(0.0, min(1.0, quantile))
        index = clamped * (len(ordered) - 1)
        lower = int(index)
        upper = min(lower + 1, len(ordered) - 1)
        blend = index - lower
        return float(ordered[lower] + blend * (ordered[upper] - ordered[lower]))
