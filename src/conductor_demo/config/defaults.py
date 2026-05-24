from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class VisionConfig:
    camera_index: int = 0
    frame_width: int = 1280
    frame_height: int = 720
    mirror: bool = True
    camera_open_retries: int = 3
    camera_reopen_retries: int = 2
    camera_retry_delay_seconds: float = 0.4
    max_num_hands: int = 2
    model_complexity: int = 1
    detection_confidence: float = 0.65
    tracking_confidence: float = 0.6
    hand_confidence_threshold: float = 0.55
    min_hand_scale_px: float = 36.0


@dataclass(slots=True)
class MotionConfig:
    buffer_size: int = 120
    smoothing_alpha: float = 0.2
    lost_tracking_hold_seconds: float = 0.75
    trail_length: int = 48


@dataclass(slots=True)
class DynamicsConfig:
    window_seconds: float = 0.6
    min_samples: int = 8
    smoothing_alpha: float = 0.18
    idle_smoothing_alpha: float = 0.08
    confidence_floor: float = 0.55
    reference_span_hand_scales: float = 6.0
    output_deadband: float = 0.025


@dataclass(slots=True)
class CalibrationConfig:
    enabled: bool = True
    hold_seconds: float = 1.0
    motion_seconds: float = 2.0
    min_hold_samples: int = 12
    min_motion_samples: int = 20
    min_motion_span_px: float = 90.0
    min_motion_span_hand_scales: float = 4.2
    dynamics_span_multiplier: float = 1.05
    tempo_motion_floor_ratio: float = 0.18
    tempo_motion_ceiling_ratio: float = 0.68


@dataclass(slots=True)
class MusicConfig:
    demo_track_path: str = "assets/audio/demo_song.wav"
    base_bpm: float = 120.0
    default_volume: float = 0.5
    min_volume: float = 0.2
    max_volume: float = 1.0
    min_rate: float = 0.85
    max_rate: float = 1.15
    rate_step: float = 0.04


@dataclass(slots=True)
class MidiConfig:
    enabled: bool = False
    port_name: str | None = None
    midi_file_path: str = "assets/audio/Symphony7_2.mid"
    expression_cc: int = 11


@dataclass(slots=True)
class UIConfig:
    window_name: str = "Conductor Demo"
    show_help_overlay: bool = True
    show_landmarks: bool = True


@dataclass(slots=True)
class ControlsConfig:
    play_from_start: str = "s"
    pause: str = "p"
    resume: str = "g"
    pause_resume_toggle: str = "space"
    reset: str = "r"
    calibrate: str = "c"
    tempo_down: str = "["
    tempo_up: str = "]"
    quit: str = "esc"

    def keymap(self) -> dict[str, str]:
        return {
            self.play_from_start: "play_from_start",
            self.pause: "pause",
            self.resume: "resume",
            self.pause_resume_toggle: "pause_resume_toggle",
            self.reset: "reset",
            self.calibrate: "calibrate",
            self.tempo_down: "tempo_down",
            self.tempo_up: "tempo_up",
            self.quit: "quit",
        }


@dataclass(slots=True)
class AppConfig:
    app_name: str = "Conductor Demo"
    vision: VisionConfig = field(default_factory=VisionConfig)
    motion: MotionConfig = field(default_factory=MotionConfig)
    dynamics: DynamicsConfig = field(default_factory=DynamicsConfig)
    calibration: CalibrationConfig = field(default_factory=CalibrationConfig)
    music: MusicConfig = field(default_factory=MusicConfig)
    midi: MidiConfig = field(default_factory=MidiConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    controls: ControlsConfig = field(default_factory=ControlsConfig)
