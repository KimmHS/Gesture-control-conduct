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
    baseline_dynamics_wrist_px: tuple[float, float] | None = None
    baseline_dynamics_hand_scale: float | None = None
    baseline_tempo_wrist_px: tuple[float, float] | None = None
    baseline_tempo_hand_scale: float | None = None
    dynamics_comfortable_motion_span_px: float | None = None
    dynamics_reference_span_px: float | None = None
    tempo_motion_floor_px: float | None = None
    tempo_motion_ceiling_px: float | None = None


class CalibrationManager:
    """Short calibration flow for right-hand tempo and dynamics control."""

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
        tempo_window_seconds: float = 0.45,
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
        self.tempo_window_seconds = tempo_window_seconds
        self.tracking_loss_reset_seconds = tracking_loss_reset_seconds

        self.active = False
        self.calibrated = False
        self.stage = "idle"
        self.progress = 0.0
        self.status_text = "READY"
        self.status_detail = "Press C to calibrate right-hand tempo and dynamics"

        self.profile = CalibrationProfile()

        self._stage_start_timestamp: float | None = None
        self._hold_samples: dict[str, list[CalibrationSample]] = {"tempo": [], "dynamics": []}
        self._motion_samples: dict[str, list[CalibrationSample]] = {"tempo": [], "dynamics": []}
        self._pending_baseline_wrist_px: dict[str, tuple[float, float] | None] = {
            "tempo": None,
            "dynamics": None,
        }
        self._pending_baseline_hand_scale: dict[str, float | None] = {"tempo": None, "dynamics": None}
        self._last_visible_timestamp: float | None = None

    def start(self) -> None:
        self.active = True
        self.stage = "waiting"
        self.progress = 0.0
        self.status_text = "SHOW RIGHT HAND"
        self.status_detail = "Show your right hand clearly. Left hand can stay free for cue target selection."
        self._stage_start_timestamp = None
        self._clear_pending_samples()
        self._last_visible_timestamp = None

    def update(
        self,
        timestamp: float,
        tempo_tracking_ok: bool,
        tempo_wrist_px: tuple[float, float] | None,
        tempo_hand_scale_px: float | None,
        dynamics_tracking_ok: bool,
        dynamics_wrist_px: tuple[float, float] | None,
        dynamics_hand_scale_px: float | None,
    ) -> bool:
        if not self.enabled or not self.active:
            return False

        tempo_ready = tempo_tracking_ok and tempo_wrist_px is not None and tempo_hand_scale_px is not None
        dynamics_ready = (
            dynamics_tracking_ok and dynamics_wrist_px is not None and dynamics_hand_scale_px is not None
        )
        if not tempo_ready or not dynamics_ready:
            if (
                self._last_visible_timestamp is not None
                and timestamp - self._last_visible_timestamp >= self.tracking_loss_reset_seconds
            ):
                self._restart_current_calibration()
            self._set_visibility_status(tempo_ready=tempo_ready, dynamics_ready=dynamics_ready)
            return False

        self._last_visible_timestamp = timestamp
        tempo_sample = CalibrationSample(
            x=tempo_wrist_px[0],
            y=tempo_wrist_px[1],
            timestamp=timestamp,
            hand_scale_px=tempo_hand_scale_px,
        )
        dynamics_sample = CalibrationSample(
            x=dynamics_wrist_px[0],
            y=dynamics_wrist_px[1],
            timestamp=timestamp,
            hand_scale_px=dynamics_hand_scale_px,
        )

        if self.stage == "waiting":
            self.stage = "hold"
            self._stage_start_timestamp = timestamp
            self._hold_samples["tempo"].clear()
            self._hold_samples["dynamics"].clear()

        if self.stage == "hold":
            return self._update_hold_stage(tempo_sample=tempo_sample, dynamics_sample=dynamics_sample)
        if self.stage == "move":
            return self._update_motion_stage(tempo_sample=tempo_sample, dynamics_sample=dynamics_sample)
        return False

    def reset(self) -> None:
        self.active = False
        self.calibrated = False
        self.stage = "idle"
        self.progress = 0.0
        self.status_text = "READY"
        self.status_detail = "Press C to calibrate right-hand tempo and dynamics"
        self.profile = CalibrationProfile()
        self._stage_start_timestamp = None
        self._clear_pending_samples()
        self._last_visible_timestamp = None

    def cancel_active(self) -> None:
        if not self.active:
            return

        self.active = False
        self.stage = "done" if self.calibrated else "idle"
        self.progress = 1.0 if self.calibrated else 0.0
        if self.calibrated:
            span = self.comfortable_motion_span_px or 0.0
            self.status_text = "CALIBRATED"
            self.status_detail = (
                f"Right-hand range {span:.0f}px and tempo gate are ready. Press C to recalibrate"
            )
        else:
            self.status_text = "READY"
            self.status_detail = "Press C to calibrate right-hand tempo and dynamics"
        self._stage_start_timestamp = None
        self._clear_pending_samples()
        self._last_visible_timestamp = None

    @property
    def baseline_wrist_px(self) -> tuple[float, float] | None:
        return self.profile.baseline_dynamics_wrist_px

    @property
    def baseline_hand_scale(self) -> float | None:
        return self.profile.baseline_dynamics_hand_scale

    @property
    def tempo_baseline_wrist_px(self) -> tuple[float, float] | None:
        return self.profile.baseline_tempo_wrist_px

    @property
    def tempo_baseline_hand_scale(self) -> float | None:
        return self.profile.baseline_tempo_hand_scale

    @property
    def comfortable_motion_span_px(self) -> float | None:
        return self.profile.dynamics_comfortable_motion_span_px

    @property
    def dynamics_reference_span_px(self) -> float | None:
        return self.profile.dynamics_reference_span_px

    @property
    def tempo_motion_floor_px(self) -> float | None:
        return self.profile.tempo_motion_floor_px

    @property
    def tempo_motion_ceiling_px(self) -> float | None:
        return self.profile.tempo_motion_ceiling_px

    def _update_hold_stage(
        self,
        tempo_sample: CalibrationSample,
        dynamics_sample: CalibrationSample,
    ) -> bool:
        self._hold_samples["tempo"].append(tempo_sample)
        self._hold_samples["dynamics"].append(dynamics_sample)
        elapsed = self._elapsed(tempo_sample.timestamp)
        time_progress = min(elapsed / max(self.hold_seconds, 0.01), 1.0)
        sample_progress = min(
            min(
                len(self._hold_samples["tempo"]) / max(self.min_hold_samples, 1),
                len(self._hold_samples["dynamics"]) / max(self.min_hold_samples, 1),
            ),
            1.0,
        )
        self.progress = 0.45 * min(max(time_progress, sample_progress), 1.0)
        self.status_text = "HOLD STILL"
        self.status_detail = "Keep your right hand visible in a comfortable neutral pose"

        enough_time = elapsed >= self.hold_seconds
        enough_samples = (
            len(self._hold_samples["tempo"]) >= self.min_hold_samples
            and len(self._hold_samples["dynamics"]) >= self.min_hold_samples
        )
        if not enough_time or not enough_samples:
            return False

        self._pending_baseline_wrist_px["tempo"] = self._median_wrist(self._hold_samples["tempo"])
        self._pending_baseline_wrist_px["dynamics"] = self._median_wrist(self._hold_samples["dynamics"])
        self._pending_baseline_hand_scale["tempo"] = self._median_scale(self._hold_samples["tempo"])
        self._pending_baseline_hand_scale["dynamics"] = self._median_scale(self._hold_samples["dynamics"])
        self.stage = "move"
        self._stage_start_timestamp = tempo_sample.timestamp
        self._motion_samples["tempo"].clear()
        self._motion_samples["dynamics"].clear()
        self.progress = 0.45
        self.status_text = "MOVE NATURALLY"
        self.status_detail = "Conduct naturally with your right hand in your comfortable demo range"
        return False

    def _update_motion_stage(
        self,
        tempo_sample: CalibrationSample,
        dynamics_sample: CalibrationSample,
    ) -> bool:
        self._motion_samples["tempo"].append(tempo_sample)
        self._motion_samples["dynamics"].append(dynamics_sample)
        elapsed = self._elapsed(tempo_sample.timestamp)
        time_progress = min(elapsed / max(self.motion_seconds, 0.01), 1.0)
        sample_progress = min(
            min(
                len(self._motion_samples["tempo"]) / max(self.min_motion_samples, 1),
                len(self._motion_samples["dynamics"]) / max(self.min_motion_samples, 1),
            ),
            1.0,
        )
        self.progress = 0.45 + 0.55 * min(max(time_progress, sample_progress), 1.0)
        self.status_text = "MOVE NATURALLY"
        self.status_detail = "Keep your right hand visible while conducting in your demo-sized range"

        enough_time = elapsed >= self.motion_seconds
        enough_samples = (
            len(self._motion_samples["tempo"]) >= self.min_motion_samples
            and len(self._motion_samples["dynamics"]) >= self.min_motion_samples
        )
        if not enough_time or not enough_samples:
            return False

        self._complete_profile()
        return True

    def _complete_profile(self) -> None:
        tempo_scale = self._pending_baseline_hand_scale["tempo"]
        dynamics_scale = self._pending_baseline_hand_scale["dynamics"]
        tempo_wrist = self._pending_baseline_wrist_px["tempo"]
        dynamics_wrist = self._pending_baseline_wrist_px["dynamics"]
        if tempo_scale is None or dynamics_scale is None or tempo_wrist is None or dynamics_wrist is None:
            return

        dynamics_motion_span_px = self._estimate_comfortable_span(
            samples=self._motion_samples["dynamics"],
            baseline_hand_scale=dynamics_scale,
        )
        tempo_motion_span_px = self._estimate_comfortable_span(
            samples=self._motion_samples["tempo"],
            baseline_hand_scale=tempo_scale,
        )
        dynamics_reference_span_px = max(
            dynamics_motion_span_px * self.dynamics_span_multiplier,
            dynamics_scale * 2.8,
        )
        tempo_motion_floor_px = max(
            tempo_motion_span_px * self.tempo_motion_floor_ratio,
            tempo_scale * 0.9,
        )
        tempo_motion_ceiling_px = max(
            tempo_motion_span_px * self.tempo_motion_ceiling_ratio,
            tempo_motion_floor_px + tempo_scale * 1.2,
        )
        tempo_motion_floor_px, tempo_motion_ceiling_px = self._stabilize_tempo_gate(
            floor_px=tempo_motion_floor_px,
            ceiling_px=tempo_motion_ceiling_px,
            samples=self._motion_samples["tempo"],
            baseline_hand_scale=tempo_scale,
        )

        self.profile = CalibrationProfile(
            baseline_dynamics_wrist_px=dynamics_wrist,
            baseline_dynamics_hand_scale=dynamics_scale,
            baseline_tempo_wrist_px=tempo_wrist,
            baseline_tempo_hand_scale=tempo_scale,
            dynamics_comfortable_motion_span_px=dynamics_motion_span_px,
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
            f"Right-hand range {dynamics_motion_span_px:.0f}px and tempo gate are ready. Press C to recalibrate"
        )
        self._stage_start_timestamp = None
        self._clear_pending_samples()

    def _estimate_comfortable_span(
        self,
        samples: list[CalibrationSample],
        baseline_hand_scale: float,
    ) -> float:
        xs = [item.x for item in samples]
        ys = [item.y for item in samples]
        width = self._percentile(xs, 0.9) - self._percentile(xs, 0.1)
        height = self._percentile(ys, 0.9) - self._percentile(ys, 0.1)
        comfortable_motion_span_px = hypot(width, height)
        min_span = max(
            self.min_motion_span_px,
            baseline_hand_scale * self.min_motion_span_hand_scales,
        )
        return max(float(comfortable_motion_span_px), float(min_span))

    def _stabilize_tempo_gate(
        self,
        floor_px: float,
        ceiling_px: float,
        samples: list[CalibrationSample],
        baseline_hand_scale: float,
    ) -> tuple[float, float]:
        energies = self._tempo_motion_energies(samples)
        if not energies:
            return floor_px, ceiling_px

        observed_floor = max(self._percentile(energies, 0.2), baseline_hand_scale * 0.9)
        observed_ceiling = max(
            self._percentile(energies, 0.85),
            observed_floor + baseline_hand_scale * 1.2,
        )
        floor_px = max(floor_px, observed_floor * 0.75)
        ceiling_px = max(ceiling_px, observed_ceiling)
        return floor_px, max(ceiling_px, floor_px + baseline_hand_scale * 1.2)

    def _tempo_motion_energies(self, samples: list[CalibrationSample]) -> list[float]:
        if len(samples) < 2:
            return []

        energies: list[float] = []
        for index, current in enumerate(samples):
            start_index = index
            while (
                start_index > 0
                and current.timestamp - samples[start_index - 1].timestamp <= self.tempo_window_seconds
            ):
                start_index -= 1

            energy = 0.0
            window_samples = samples[start_index : index + 1]
            for previous, later in zip(window_samples, window_samples[1:]):
                energy += hypot(later.x - previous.x, later.y - previous.y)
            if energy > 0:
                energies.append(float(energy))
        return energies

    def _median_wrist(self, samples: list[CalibrationSample]) -> tuple[float, float]:
        xs = [item.x for item in samples]
        ys = [item.y for item in samples]
        return float(median(xs)), float(median(ys))

    def _median_scale(self, samples: list[CalibrationSample]) -> float:
        return float(median(item.hand_scale_px for item in samples))

    def _elapsed(self, timestamp: float) -> float:
        if self._stage_start_timestamp is None:
            self._stage_start_timestamp = timestamp
            return 0.0
        return max(timestamp - self._stage_start_timestamp, 0.0)

    def _restart_current_calibration(self) -> None:
        self.stage = "waiting"
        self.progress = 0.0
        self.status_text = "SHOW RIGHT HAND"
        self.status_detail = "Tracking was lost. Show your right hand again for tempo and dynamics."
        self._stage_start_timestamp = None
        self._clear_pending_samples()
        self._last_visible_timestamp = None

    def _set_visibility_status(self, tempo_ready: bool, dynamics_ready: bool) -> None:
        missing_text = "your right hand" if not tempo_ready or not dynamics_ready else "your right hand"

        if self.stage == "waiting":
            self.status_text = "SHOW RIGHT HAND"
            self.status_detail = f"Show {missing_text} to begin calibration"
            return
        if self.stage == "hold":
            self.status_text = "HOLD STILL"
            self.status_detail = f"Keep {missing_text} visible while holding a neutral pose"
            return
        self.status_text = "MOVE NATURALLY"
        self.status_detail = f"Keep {missing_text} visible while moving through your demo range"

    def _clear_pending_samples(self) -> None:
        self._hold_samples["tempo"].clear()
        self._hold_samples["dynamics"].clear()
        self._motion_samples["tempo"].clear()
        self._motion_samples["dynamics"].clear()
        self._pending_baseline_wrist_px["tempo"] = None
        self._pending_baseline_wrist_px["dynamics"] = None
        self._pending_baseline_hand_scale["tempo"] = None
        self._pending_baseline_hand_scale["dynamics"] = None

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
