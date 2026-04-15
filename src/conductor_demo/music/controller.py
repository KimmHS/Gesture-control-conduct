from __future__ import annotations


class MusicController:
    """Minimal playback-state placeholder.

    A real backend can replace this later without changing the rest of the app.
    """

    def __init__(self, base_bpm: float, default_volume: float) -> None:
        self.base_bpm = base_bpm
        self.default_volume = default_volume
        self.is_playing = False
        self.playback_rate = 1.0
        self.volume = default_volume

    def toggle_play_pause(self) -> None:
        self.is_playing = not self.is_playing

    def set_rate(self, rate: float) -> None:
        self.playback_rate = rate

    def set_volume(self, volume: float) -> None:
        self.volume = volume

    def reset(self) -> None:
        self.is_playing = False
        self.playback_rate = 1.0
        self.volume = self.default_volume
