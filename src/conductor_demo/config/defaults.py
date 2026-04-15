from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class VisionConfig:
    camera_index: int = 0
    frame_width: int = 1280
    frame_height: int = 720
    mirror: bool = True
    max_num_hands: int = 2
    model_complexity: int = 0
    detection_confidence: float = 0.6
    tracking_confidence: float = 0.6
    hand_confidence_threshold: float = 0.45


@dataclass(slots=True)
class MotionConfig:
    buffer_size: int = 120
    smoothing_alpha: float = 0.2
    lost_tracking_hold_seconds: float = 0.75
    trail_length: int = 48


@dataclass(slots=True)
class MusicConfig:
    base_bpm: float = 120.0
    default_volume: float = 0.5
    min_rate: float = 0.85
    max_rate: float = 1.15


@dataclass(slots=True)
class UIConfig:
    window_name: str = "Conductor Demo"
    show_help_overlay: bool = True
    show_landmarks: bool = True


@dataclass(slots=True)
class ControlsConfig:
    play_pause: str = "space"
    reset: str = "r"
    calibrate: str = "c"
    quit: str = "esc"

    def keymap(self) -> dict[str, str]:
        return {
            self.play_pause: "play_pause",
            self.reset: "reset",
            self.calibrate: "calibrate",
            self.quit: "quit",
        }


@dataclass(slots=True)
class AppConfig:
    app_name: str = "Conductor Demo"
    vision: VisionConfig = field(default_factory=VisionConfig)
    motion: MotionConfig = field(default_factory=MotionConfig)
    music: MusicConfig = field(default_factory=MusicConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    controls: ControlsConfig = field(default_factory=ControlsConfig)
