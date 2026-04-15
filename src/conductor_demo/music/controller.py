from __future__ import annotations

from pathlib import Path

from conductor_demo.music.wave_backend import WavePlaybackBackend


class MusicController:
    """Demo-safe music controller for one WAV track."""

    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    ENDED = "ended"
    ERROR = "error"

    def __init__(
        self,
        base_bpm: float,
        default_volume: float,
        min_volume: float,
        max_volume: float,
        min_rate: float,
        max_rate: float,
        demo_track_path: str,
    ) -> None:
        if max_volume <= min_volume:
            raise ValueError("max_volume must be greater than min_volume")
        if max_rate <= min_rate:
            raise ValueError("max_rate must be greater than min_rate")

        self.base_bpm = base_bpm
        self.min_volume = min_volume
        self.max_volume = max_volume
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.default_volume = max(min(default_volume, max_volume), min_volume)
        self.playback_rate = 1.0
        self.track_path = self._resolve_track_path(demo_track_path)
        self.volume = self.default_volume
        self.backend: WavePlaybackBackend | None = None
        self._state = self.STOPPED
        self._last_error: str | None = None
        self._rebuild_backend()

    @property
    def is_playing(self) -> bool:
        return self.state == self.PLAYING

    @property
    def state(self) -> str:
        if self._state == self.ERROR or self.backend is None:
            return self.ERROR if self._last_error else self.STOPPED
        if self.backend.is_playing:
            return self.PLAYING
        if self.backend.at_end and self.position_seconds > 0.0:
            return self.ENDED
        return self._state

    @property
    def track_name(self) -> str:
        return self.track_path.name

    @property
    def duration_seconds(self) -> float:
        return self.backend.track.duration_seconds if self.backend is not None else 0.0

    @property
    def position_seconds(self) -> float:
        return self.backend.position_seconds if self.backend is not None else 0.0

    @property
    def current_bpm(self) -> float:
        return self.base_bpm * self.playback_rate

    @property
    def status_text(self) -> str:
        labels = {
            self.STOPPED: "STOPPED",
            self.PLAYING: "PLAYING",
            self.PAUSED: "PAUSED",
            self.ENDED: "ENDED",
            self.ERROR: "AUDIO ERROR",
        }
        return labels[self.state]

    @property
    def status_detail(self) -> str:
        state = self.state
        if state == self.PLAYING:
            return "Manual fallback: P pause, Space toggle, R reset"
        if state == self.PAUSED:
            return "Paused. Press G or Space to resume, S to restart"
        if state == self.ENDED:
            return "Song ended. Press S or Space to replay"
        if state == self.ERROR:
            return f"Audio issue. Press R to recover. {self._last_error or ''}".strip()
        return "Ready. Press S or Space to start playback"

    def play(self) -> None:
        if not self._ensure_backend():
            return
        self._safe_call("start playback", self._play_from_beginning, success_state=self.PLAYING)

    def pause(self) -> None:
        if self.state != self.PLAYING or self.backend is None:
            return
        self._safe_call("pause playback", self.backend.pause, success_state=self.PAUSED)

    def resume(self) -> None:
        state = self.state
        if state in {self.STOPPED, self.ENDED}:
            self.play()
            return
        if state == self.ERROR:
            if self._ensure_backend():
                self.play()
            return
        if state == self.PAUSED and self.backend is not None:
            self._safe_call("resume playback", self.backend.resume, success_state=self.PLAYING)

    def toggle_play_pause(self) -> None:
        self.toggle_pause_resume()

    def toggle_pause_resume(self) -> None:
        if self.state == self.PLAYING:
            self.pause()
            return
        self.resume()

    def set_rate(self, rate: float) -> None:
        self.playback_rate = max(self.min_rate, min(self.max_rate, float(rate)))
        if self.backend is not None:
            self._safe_call(
                "set playback rate",
                lambda: self.backend.set_rate(self.playback_rate),
            )

    def adjust_rate(self, delta: float) -> None:
        self.set_rate(self.playback_rate + delta)

    def set_volume(self, volume: float) -> None:
        self.volume = max(self.min_volume, min(self.max_volume, volume))
        if self.backend is not None:
            self._safe_call("set playback volume", self._apply_backend_volume)

    def reset(self) -> None:
        self.playback_rate = 1.0
        self.volume = self.default_volume
        if not self._ensure_backend(force_rebuild=self.state == self.ERROR):
            return
        if self.backend is None:
            return
        self._safe_call("reset playback", self.backend.reset, success_state=self.STOPPED)
        self.playback_rate = 1.0
        self._safe_call("restore playback rate", lambda: self.backend.set_rate(self.playback_rate))
        self._safe_call("restore playback volume", self._apply_backend_volume)

    def close(self) -> None:
        if self.backend is None:
            return
        try:
            self.backend.close()
        finally:
            self.backend = None

    def describe(self) -> str:
        return (
            f"state={self.state} "
            f"track={self.track_name} "
            f"playing={self.is_playing} "
            f"rate={self.playback_rate:.2f} "
            f"volume={self.volume:.2f} "
            f"pos={self.position_seconds:.1f}/{self.duration_seconds:.1f}s"
        )

    def _ensure_backend(self, force_rebuild: bool = False) -> bool:
        if self.backend is not None and not force_rebuild and self.state != self.ERROR:
            return True
        return self._rebuild_backend()

    def _rebuild_backend(self) -> bool:
        if self.backend is not None:
            try:
                self.backend.close()
            except Exception:
                pass

        try:
            self.backend = WavePlaybackBackend(self.track_path)
            self.backend.set_rate(self.playback_rate)
            self._apply_backend_volume()
            self._state = self.STOPPED
            self._last_error = None
            return True
        except Exception as exc:
            self.backend = None
            self._set_error(exc)
            return False

    def _play_from_beginning(self) -> None:
        if self.backend is None:
            raise RuntimeError("audio backend is unavailable")
        self.backend.reset()
        self.backend.set_rate(self.playback_rate)
        self._apply_backend_volume()
        self.backend.play()

    def _apply_backend_volume(self) -> None:
        if self.backend is None:
            return
        normalized = (self.volume - self.min_volume) / (self.max_volume - self.min_volume)
        self.backend.set_volume(normalized)

    def _safe_call(self, label: str, operation, success_state: str | None = None) -> bool:
        try:
            operation()
        except Exception as exc:
            self._set_error(RuntimeError(f"{label} failed: {exc}"))
            return False

        self._last_error = None
        if success_state is not None:
            self._state = success_state
        return True

    def _set_error(self, exc: Exception) -> None:
        self._state = self.ERROR
        self._last_error = str(exc)

    def _resolve_track_path(self, demo_track_path: str) -> Path:
        candidate = Path(demo_track_path)
        if candidate.is_absolute():
            return candidate
        project_root = Path(__file__).resolve().parents[3]
        return (project_root / candidate).resolve()
