from __future__ import annotations

import ctypes
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_TEMPO_US_PER_QUARTER = 500000
TICKS_PER_SECOND_FALLBACK = 480.0


@dataclass(slots=True)
class MidiTrackInfo:
    index: int
    name: str
    channel: int | None = None


@dataclass(slots=True)
class MidiEvent:
    tick: int
    time_seconds: float
    kind: str
    track_index: int
    channel: int | None = None
    data1: int = 0
    data2: int = 0
    meta_type: int | None = None
    payload: bytes = b""


@dataclass(slots=True)
class MidiSequence:
    path: Path
    format_type: int
    division: int
    tracks: list[MidiTrackInfo]
    events: list[MidiEvent]
    duration_seconds: float

    @property
    def track_name(self) -> str:
        return self.path.name


@dataclass(slots=True)
class ChannelState:
    program: int = 0
    bank_msb: int = 0
    bank_lsb: int = 0
    expression: int = 127
    pitch_bend: int = 8192
    other_controllers: dict[int, int] = field(default_factory=dict)


def _parse_midi_file(path: Path) -> MidiSequence:
    data = path.read_bytes()
    if data[:4] != b"MThd":
        raise RuntimeError(f"Not a valid MIDI file: `{path}`")

    header_length = int.from_bytes(data[4:8], "big")
    format_type = int.from_bytes(data[8:10], "big")
    track_count = int.from_bytes(data[10:12], "big")
    division = int.from_bytes(data[12:14], "big")
    pos = 8 + header_length

    raw_track_events: list[tuple[int, int, int, int | None, int, int, int | None, bytes]] = []
    track_infos: list[MidiTrackInfo] = []
    tempo_events: list[tuple[int, int]] = [(0, DEFAULT_TEMPO_US_PER_QUARTER)]

    for track_index in range(track_count):
        if data[pos : pos + 4] != b"MTrk":
            raise RuntimeError(f"Invalid MIDI track header at track {track_index + 1}")
        track_length = int.from_bytes(data[pos + 4 : pos + 8], "big")
        track_data = data[pos + 8 : pos + 8 + track_length]
        pos += 8 + track_length

        i = 0
        abs_tick = 0
        running_status: int | None = None
        track_name = ""
        first_channel: int | None = None

        while i < len(track_data):
            delta, i = _read_vlq(track_data, i)
            abs_tick += delta

            status = track_data[i]
            if status < 0x80:
                if running_status is None:
                    raise RuntimeError(f"Invalid running status in track {track_index + 1}")
                status = running_status
            else:
                i += 1
                if status < 0xF0:
                    running_status = status

            if status == 0xFF:
                meta_type = track_data[i]
                i += 1
                length, i = _read_vlq(track_data, i)
                payload = track_data[i : i + length]
                i += length
                if meta_type == 0x03 and payload:
                    track_name = payload.decode("latin1", errors="replace").strip()
                if meta_type == 0x51 and len(payload) == 3:
                    tempo_events.append((abs_tick, int.from_bytes(payload, "big")))
                raw_track_events.append((abs_tick, track_index, status, None, 0, 0, meta_type, payload))
                continue

            if status in (0xF0, 0xF7):
                length, i = _read_vlq(track_data, i)
                payload = track_data[i : i + length]
                i += length
                raw_track_events.append((abs_tick, track_index, status, None, 0, 0, None, payload))
                running_status = None
                continue

            event_type = status & 0xF0
            channel = status & 0x0F
            if first_channel is None:
                first_channel = channel

            if event_type in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
                data1 = track_data[i]
                data2 = track_data[i + 1]
                i += 2
            elif event_type in (0xC0, 0xD0):
                data1 = track_data[i]
                data2 = 0
                i += 1
            else:
                raise RuntimeError(f"Unsupported MIDI event status: 0x{status:02X}")

            raw_track_events.append((abs_tick, track_index, status, channel, data1, data2, None, b""))

        track_infos.append(MidiTrackInfo(index=track_index, name=track_name or f"Track {track_index + 1}", channel=first_channel))

    tempo_map = _build_tempo_map(tempo_events=tempo_events, division=division)
    events: list[MidiEvent] = []
    for tick, track_index, status, channel, data1, data2, meta_type, payload in raw_track_events:
        time_seconds = _tick_to_seconds(tick=tick, tempo_map=tempo_map, division=division)
        if status == 0xFF:
            events.append(
                MidiEvent(
                    tick=tick,
                    time_seconds=time_seconds,
                    kind="meta",
                    track_index=track_index,
                    meta_type=meta_type,
                    payload=payload,
                )
            )
            continue
        if status in (0xF0, 0xF7):
            events.append(
                MidiEvent(
                    tick=tick,
                    time_seconds=time_seconds,
                    kind="sysex",
                    track_index=track_index,
                    payload=payload,
                )
            )
            continue

        event_type = status & 0xF0
        kind = {
            0x80: "note_off",
            0x90: "note_on",
            0xA0: "poly_aftertouch",
            0xB0: "control_change",
            0xC0: "program_change",
            0xD0: "channel_aftertouch",
            0xE0: "pitch_bend",
        }.get(event_type)
        if kind is None:
            continue
        events.append(
            MidiEvent(
                tick=tick,
                time_seconds=time_seconds,
                kind=kind,
                track_index=track_index,
                channel=channel,
                data1=data1,
                data2=data2,
            )
        )

    events.sort(key=lambda item: (item.time_seconds, item.track_index))
    duration_seconds = max((event.time_seconds for event in events), default=0.0)
    return MidiSequence(
        path=path.resolve(),
        format_type=format_type,
        division=division,
        tracks=track_infos,
        events=events,
        duration_seconds=duration_seconds,
    )


def _build_tempo_map(tempo_events: list[tuple[int, int]], division: int) -> list[tuple[int, float, int]]:
    merged: dict[int, int] = {}
    for tick, tempo in tempo_events:
        merged[tick] = tempo
    ordered = sorted(merged.items())
    timeline: list[tuple[int, float, int]] = []
    current_seconds = 0.0
    previous_tick = 0
    previous_tempo = ordered[0][1] if ordered else DEFAULT_TEMPO_US_PER_QUARTER

    for tick, tempo in ordered:
        delta_ticks = tick - previous_tick
        current_seconds += (delta_ticks / max(division, 1)) * (previous_tempo / 1_000_000.0)
        timeline.append((tick, current_seconds, tempo))
        previous_tick = tick
        previous_tempo = tempo
    if not timeline:
        timeline.append((0, 0.0, DEFAULT_TEMPO_US_PER_QUARTER))
    return timeline


def _tick_to_seconds(tick: int, tempo_map: list[tuple[int, float, int]], division: int) -> float:
    current_tick, current_seconds, current_tempo = tempo_map[0]
    for next_tick, next_seconds, next_tempo in tempo_map[1:]:
        if tick < next_tick:
            break
        current_tick, current_seconds, current_tempo = next_tick, next_seconds, next_tempo
    delta_ticks = tick - current_tick
    return current_seconds + (delta_ticks / max(division, 1)) * (current_tempo / 1_000_000.0)


def _read_vlq(data: bytes, index: int) -> tuple[int, int]:
    value = 0
    while True:
        byte = data[index]
        index += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, index


class MidiPlaybackBackend:
    """Windows MIDI-out playback backend with per-group mute control."""

    GROUP_TRACK_NAMES = (
        ("Hi Winds", {"flutes", "oboes"}),
        ("Lo Winds", {"clarinets", "bassoons"}),
        ("Horns+Tpt", {"horns", "trumpets"}),
        ("Brass+Perc", {"trombones", "trombone bass", "tuba", "cymbal with stick"}),
        ("Strings", {"first violins", "second violins", "violas", "cellos", "contra basses"}),
    )

    def __init__(self, track_path: str | Path) -> None:
        self.sequence = _parse_midi_file(Path(track_path))
        self._winmm = ctypes.WinDLL("winmm")
        self._handle = ctypes.c_void_p()
        self._lock = threading.RLock()
        self._thread: threading.Thread | None = None
        self._running = True
        self._playing = False
        self._paused = False
        self._playhead_seconds = 0.0
        self._event_index = 0
        self._rate = 1.0
        self._master_volume = 1.0
        self._last_clock = time.monotonic()
        self._open_device()

        self.group_labels = tuple(label for label, _ in self.GROUP_TRACK_NAMES)
        self.track_to_group = self._build_track_to_group()
        self.active_group_indices = set(range(len(self.group_labels)))
        self._base_channel_state = {channel: ChannelState() for channel in range(16)}
        self._active_notes: dict[tuple[int, int], int] = {}
        self._thread = threading.Thread(target=self._playback_loop, name="MidiPlaybackBackend", daemon=True)
        self._thread.start()

    @property
    def is_playing(self) -> bool:
        with self._lock:
            return self._playing

    @property
    def at_end(self) -> bool:
        with self._lock:
            return self._playhead_seconds >= self.duration_seconds

    @property
    def position_seconds(self) -> float:
        with self._lock:
            return self._playhead_seconds

    @property
    def duration_seconds(self) -> float:
        return self.sequence.duration_seconds

    @property
    def track_name(self) -> str:
        return self.sequence.track_name

    def set_rate(self, rate: float) -> None:
        with self._lock:
            self._rate = max(0.25, min(2.0, float(rate)))

    def set_volume(self, volume: float) -> None:
        with self._lock:
            self._master_volume = max(0.0, min(1.0, float(volume)))
            self._apply_channel_mix_locked()

    def play(self) -> None:
        with self._lock:
            self._reset_playback_locked()
            self._playing = True
            self._paused = False
            self._last_clock = time.monotonic()

    def pause(self) -> None:
        with self._lock:
            self._playing = False
            self._paused = True
            self._silence_active_notes_locked()

    def resume(self) -> None:
        with self._lock:
            if self.at_end:
                self._reset_playback_locked()
            self._restore_state_at_playhead_locked()
            self._playing = True
            self._paused = False
            self._last_clock = time.monotonic()

    def reset(self) -> None:
        with self._lock:
            self._reset_playback_locked()

    def close(self) -> None:
        with self._lock:
            self._running = False
            self._playing = False
            self._silence_active_notes_locked()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        if self._handle:
            self._winmm.midiOutReset(self._handle)
            self._winmm.midiOutClose(self._handle)
        self._handle = ctypes.c_void_p()

    def toggle_group(self, group_index: int) -> bool:
        with self._lock:
            if group_index < 0 or group_index >= len(self.group_labels):
                return False
            if group_index in self.active_group_indices:
                self.active_group_indices.remove(group_index)
            else:
                self.active_group_indices.add(group_index)
            self._apply_channel_mix_locked()
            return group_index in self.active_group_indices

    def activate_all_groups(self) -> None:
        with self._lock:
            self.active_group_indices = set(range(len(self.group_labels)))
            self._apply_channel_mix_locked()

    def _open_device(self) -> None:
        result = self._winmm.midiOutOpen(ctypes.byref(self._handle), 0, 0, 0, 0)
        if result != 0:
            raise RuntimeError(f"Could not open Windows MIDI out device. winmm error={result}")

    def _playback_loop(self) -> None:
        while True:
            with self._lock:
                if not self._running:
                    return
                if not self._playing:
                    self._last_clock = time.monotonic()
                    sleep_seconds = 0.01
                else:
                    now = time.monotonic()
                    elapsed = now - self._last_clock
                    self._last_clock = now
                    self._playhead_seconds = min(self._playhead_seconds + elapsed * self._rate, self.duration_seconds)
                    self._dispatch_due_events_locked()
                    if self._playhead_seconds >= self.duration_seconds:
                        self._playing = False
                    sleep_seconds = 0.005
            time.sleep(sleep_seconds)

    def _dispatch_due_events_locked(self) -> None:
        events = self.sequence.events
        while self._event_index < len(events) and events[self._event_index].time_seconds <= self._playhead_seconds:
            event = events[self._event_index]
            self._event_index += 1
            self._apply_event_locked(event)

    def _apply_event_locked(self, event: MidiEvent) -> None:
        if event.channel is None:
            return

        channel_state = self._base_channel_state[event.channel]
        if event.kind == "program_change":
            channel_state.program = event.data1
            self._send_short_message(0xC0 | event.channel, event.data1, 0)
            return
        if event.kind == "pitch_bend":
            value = event.data1 | (event.data2 << 7)
            channel_state.pitch_bend = value
            self._send_short_message(0xE0 | event.channel, event.data1, event.data2)
            return
        if event.kind == "control_change":
            controller = event.data1
            value = event.data2
            if controller == 0:
                channel_state.bank_msb = value
            elif controller == 32:
                channel_state.bank_lsb = value
            elif controller == 11:
                channel_state.expression = value
                self._apply_channel_mix_locked(channel=event.channel)
                return
            elif controller in {7, 121, 123}:
                channel_state.other_controllers[controller] = value
                if controller == 123:
                    self._active_notes = {
                        key: velocity for key, velocity in self._active_notes.items() if key[0] != event.channel
                    }
                self._send_short_message(0xB0 | event.channel, controller, value)
                if controller == 121:
                    self._apply_channel_mix_locked(channel=event.channel)
                return
            else:
                channel_state.other_controllers[controller] = value
            self._send_short_message(0xB0 | event.channel, controller, value)
            return

        if event.kind == "note_on":
            note = event.data1
            velocity = event.data2
            if velocity == 0:
                self._active_notes.pop((event.channel, note), None)
            else:
                self._active_notes[(event.channel, note)] = velocity
            if self._is_group_active_for_track(event.track_index):
                self._send_short_message(0x90 | event.channel, note, velocity)
            return

        if event.kind == "note_off":
            note = event.data1
            self._active_notes.pop((event.channel, note), None)
            self._send_short_message(0x80 | event.channel, note, event.data2)
            return

        if event.kind == "channel_aftertouch":
            self._send_short_message(0xD0 | event.channel, event.data1, 0)
            return
        if event.kind == "poly_aftertouch":
            self._send_short_message(0xA0 | event.channel, event.data1, event.data2)

    def _reset_playback_locked(self) -> None:
        self._playing = False
        self._paused = False
        self._playhead_seconds = 0.0
        self._event_index = 0
        self._base_channel_state = {channel: ChannelState() for channel in range(16)}
        self._active_notes.clear()
        self._winmm.midiOutReset(self._handle)
        self._apply_channel_mix_locked()

    def _restore_state_at_playhead_locked(self) -> None:
        self._winmm.midiOutReset(self._handle)
        state = {channel: ChannelState() for channel in range(16)}
        active_notes: dict[tuple[int, int], int] = {}
        event_index = 0
        for event_index, event in enumerate(self.sequence.events):
            if event.time_seconds > self._playhead_seconds:
                break
            if event.channel is None:
                continue
            channel_state = state[event.channel]
            if event.kind == "program_change":
                channel_state.program = event.data1
            elif event.kind == "pitch_bend":
                channel_state.pitch_bend = event.data1 | (event.data2 << 7)
            elif event.kind == "control_change":
                if event.data1 == 0:
                    channel_state.bank_msb = event.data2
                elif event.data1 == 32:
                    channel_state.bank_lsb = event.data2
                elif event.data1 == 11:
                    channel_state.expression = event.data2
                else:
                    channel_state.other_controllers[event.data1] = event.data2
            elif event.kind == "note_on":
                if event.data2 == 0:
                    active_notes.pop((event.channel, event.data1), None)
                else:
                    active_notes[(event.channel, event.data1)] = event.data2
            elif event.kind == "note_off":
                active_notes.pop((event.channel, event.data1), None)
        else:
            event_index = len(self.sequence.events)

        self._base_channel_state = state
        self._active_notes = active_notes
        self._event_index = event_index if event_index < len(self.sequence.events) else len(self.sequence.events)

        for channel, channel_state in self._base_channel_state.items():
            self._send_short_message(0xB0 | channel, 0, channel_state.bank_msb)
            self._send_short_message(0xB0 | channel, 32, channel_state.bank_lsb)
            self._send_short_message(0xC0 | channel, channel_state.program, 0)
            self._send_short_message(0xE0 | channel, channel_state.pitch_bend & 0x7F, (channel_state.pitch_bend >> 7) & 0x7F)
            for controller, value in sorted(channel_state.other_controllers.items()):
                if controller in {7, 11}:
                    continue
                self._send_short_message(0xB0 | channel, controller, value)
        self._apply_channel_mix_locked()
        for (channel, note), velocity in self._active_notes.items():
            if self._is_group_active_for_channel(channel):
                self._send_short_message(0x90 | channel, note, velocity)

    def _silence_active_notes_locked(self) -> None:
        for channel in range(16):
            self._send_short_message(0xB0 | channel, 123, 0)
        self._winmm.midiOutReset(self._handle)

    def _apply_channel_mix_locked(self, channel: int | None = None) -> None:
        channels = [channel] if channel is not None else list(range(16))
        for item in channels:
            state = self._base_channel_state[item]
            effective = int(max(0.0, min(127.0, state.expression * self._master_volume * self._group_gain_for_channel(item))))
            self._send_short_message(0xB0 | item, 11, effective)

    def _group_gain_for_channel(self, channel: int) -> float:
        if self._is_group_active_for_channel(channel):
            return 1.0
        return 0.0

    def _is_group_active_for_channel(self, channel: int) -> bool:
        for track_index, group_index in self.track_to_group.items():
            track_channel = self.sequence.tracks[track_index].channel
            if track_channel == channel:
                return group_index in self.active_group_indices
        return True

    def _is_group_active_for_track(self, track_index: int) -> bool:
        group_index = self.track_to_group.get(track_index)
        return group_index is None or group_index in self.active_group_indices

    def _build_track_to_group(self) -> dict[int, int]:
        mapping: dict[int, int] = {}
        normalized_groups = [(label, {item.lower() for item in names}) for label, names in self.GROUP_TRACK_NAMES]
        for track in self.sequence.tracks:
            lowered = track.name.strip().lower()
            for index, (_label, names) in enumerate(normalized_groups):
                if lowered in names:
                    mapping[track.index] = index
                    break
        return mapping

    def _send_short_message(self, status: int, data1: int, data2: int) -> None:
        message = status | (data1 << 8) | (data2 << 16)
        self._winmm.midiOutShortMsg(self._handle, message)
