from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PlaybackState:
    mode: str = "stopped"
    is_playing: bool = False
    bpm: float = 120.0
    rate: float = 1.0
    volume: float = 0.5
    track_name: str = "-"
    position_seconds: float = 0.0
    duration_seconds: float = 0.0
    status_text: str = "STOPPED"
    status_detail: str = "Press S or Space to start"


@dataclass(slots=True)
class DynamicsState:
    intensity: float = 0.0
    raw_intensity: float = 0.0
    span_px: float = 0.0
    reference_span_px: float = 1.0


@dataclass(slots=True)
class CalibrationState:
    enabled: bool = True
    active: bool = False
    calibrated: bool = False
    stage: str = "idle"
    progress: float = 0.0
    status_text: str = "READY"
    status_detail: str = "Press C to run a quick calibration"
    baseline_wrist_px: tuple[float, float] | None = None
    baseline_hand_scale: float | None = None
    comfortable_motion_span_px: float | None = None
    dynamics_reference_span_px: float | None = None
    tempo_motion_floor_px: float | None = None
    tempo_motion_ceiling_px: float | None = None


@dataclass(slots=True)
class AppState:
    tracking_ok: bool = False
    active_hand: str | None = None
    playback: PlaybackState = field(default_factory=PlaybackState)
    dynamics: DynamicsState = field(default_factory=DynamicsState)
    calibration: CalibrationState = field(default_factory=CalibrationState)
    fallback_hint: str = "S play | P pause | G resume | Space toggle | R reset | Esc quit"
