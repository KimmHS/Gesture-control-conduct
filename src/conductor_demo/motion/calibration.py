from __future__ import annotations


class CalibrationManager:
    """Placeholder calibration state and hooks."""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self.calibrated = False
        self.baseline_hand_scale: float | None = None

    def start(self) -> None:
        self.calibrated = False

    def complete(self, baseline_hand_scale: float = 1.0) -> None:
        self.baseline_hand_scale = baseline_hand_scale
        self.calibrated = True

    def reset(self) -> None:
        self.calibrated = False
        self.baseline_hand_scale = None
