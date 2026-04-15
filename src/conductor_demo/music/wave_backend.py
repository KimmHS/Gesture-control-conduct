from __future__ import annotations

import logging
import threading
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


LOGGER = logging.getLogger(__name__)


def _require_sounddevice() -> Any:
    try:
        import sounddevice as sd
    except ImportError as exc:
        raise RuntimeError("sounddevice is required. Install dependencies with `pip install -r requirements.txt`.") from exc
    return sd


@dataclass(slots=True)
class WaveTrack:
    path: Path
    samples: np.ndarray
    sample_rate: int
    channels: int

    @property
    def frame_count(self) -> int:
        return int(self.samples.shape[0])

    @property
    def duration_seconds(self) -> float:
        return float(self.frame_count / self.sample_rate)


class WavePlaybackBackend:
    """Simple WAV playback backend with rate and volume control."""

    def __init__(self, track_path: str | Path) -> None:
        self.track = self._load_track(Path(track_path))
        self._sd: Any | None = None
        self._stream: Any | None = None
        self._lock = threading.RLock()
        self._playing = False
        self._playhead = 0.0
        self._volume = 1.0
        self._rate = 1.0

    @property
    def is_playing(self) -> bool:
        with self._lock:
            return self._playing

    @property
    def at_end(self) -> bool:
        with self._lock:
            return self._playhead >= max(self.track.frame_count - 1, 0)

    @property
    def position_seconds(self) -> float:
        with self._lock:
            return float(self._playhead / self.track.sample_rate)

    def set_rate(self, rate: float) -> None:
        with self._lock:
            self._rate = max(0.25, min(2.0, float(rate)))

    def set_volume(self, volume: float) -> None:
        with self._lock:
            self._volume = max(0.0, min(1.0, float(volume)))

    def play(self) -> None:
        self._ensure_stream()
        with self._lock:
            if self.at_end:
                self._playhead = 0.0
            self._playing = True

    def pause(self) -> None:
        with self._lock:
            self._playing = False

    def resume(self) -> None:
        self._ensure_stream()
        with self._lock:
            if not self.at_end:
                self._playing = True

    def reset(self) -> None:
        with self._lock:
            self._playing = False
            self._playhead = 0.0

    def close(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
        self._stream = None

    def _ensure_stream(self) -> None:
        if self._stream is not None:
            return

        sd = _require_sounddevice()
        self._sd = sd
        self._stream = sd.OutputStream(
            samplerate=self.track.sample_rate,
            channels=self.track.channels,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()

    def _callback(self, outdata: np.ndarray, frames: int, _time_info: Any, status: Any) -> None:
        if status:
            LOGGER.debug("Audio callback status: %s", status)

        outdata.fill(0.0)
        with self._lock:
            playing = self._playing
            playhead = self._playhead
            rate = self._rate
            volume = self._volume

        if not playing or self.track.frame_count < 2:
            return

        rendered, next_playhead, ended = self._render_block(playhead, frames, rate)
        if rendered.size:
            outdata[: rendered.shape[0], :] = rendered * volume

        with self._lock:
            self._playhead = next_playhead
            if ended:
                self._playing = False

    def _render_block(self, playhead: float, frames: int, rate: float) -> tuple[np.ndarray, float, bool]:
        frame_count = self.track.frame_count
        if frame_count < 2 or playhead >= frame_count - 1:
            return np.zeros((0, self.track.channels), dtype=np.float32), float(max(frame_count - 1, 0)), True

        positions = playhead + np.arange(frames, dtype=np.float64) * rate
        valid_mask = positions < (frame_count - 1)
        if not np.any(valid_mask):
            return np.zeros((0, self.track.channels), dtype=np.float32), float(frame_count - 1), True

        valid_positions = positions[valid_mask]
        lower = np.floor(valid_positions).astype(np.int64)
        upper = lower + 1
        frac = (valid_positions - lower).astype(np.float32)[:, None]

        lower_samples = self.track.samples[lower]
        upper_samples = self.track.samples[upper]
        rendered = lower_samples + (upper_samples - lower_samples) * frac

        next_playhead = playhead + len(valid_positions) * rate
        ended = len(valid_positions) < frames or next_playhead >= frame_count - 1
        if ended:
            next_playhead = float(frame_count - 1)

        return rendered.astype(np.float32, copy=False), next_playhead, ended

    def _load_track(self, track_path: Path) -> WaveTrack:
        if not track_path.exists():
            raise RuntimeError(f"Demo track not found: `{track_path}`")

        with wave.open(str(track_path), "rb") as handle:
            channels = handle.getnchannels()
            sample_rate = handle.getframerate()
            sample_width = handle.getsampwidth()
            frame_count = handle.getnframes()
            raw = handle.readframes(frame_count)

        if frame_count < 2:
            raise RuntimeError("Demo track must contain at least 2 frames.")

        if sample_width == 1:
            samples = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
        elif sample_width == 2:
            samples = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
        elif sample_width == 4:
            samples = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648.0
        else:
            raise RuntimeError("Only 8-bit, 16-bit, or 32-bit PCM WAV files are supported.")

        samples = samples.reshape(-1, channels)
        return WaveTrack(
            path=track_path.resolve(),
            samples=samples,
            sample_rate=sample_rate,
            channels=channels,
        )
