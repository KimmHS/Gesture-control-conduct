from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PlaybackState:
    is_playing: bool = False
    rate: float = 1.0
    volume: float = 0.5


@dataclass(slots=True)
class CalibrationState:
    enabled: bool = True
    calibrated: bool = False
    baseline_hand_scale: float | None = None


@dataclass(slots=True)
class AppState:
    tracking_ok: bool = False
    active_hand: str | None = None
    playback: PlaybackState = field(default_factory=PlaybackState)
    calibration: CalibrationState = field(default_factory=CalibrationState)
    fallback_hint: str = "Space play/pause | R reset | C calibrate | Esc quit"
