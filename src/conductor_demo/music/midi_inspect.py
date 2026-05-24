from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys


def _load_mido():
    try:
        import mido
    except ImportError as exc:
        raise RuntimeError(
            "MIDI inspection requires mido. Install with `pip install 'mido[ports-rtmidi]'`."
        ) from exc
    return mido


def inspect_midi_file(path: str) -> list[str]:
    mido = _load_mido()
    midi_path = Path(path)
    midi = mido.MidiFile(midi_path)
    lines = [
        f"path: {midi_path}",
        f"type: {midi.type}",
        f"ticks_per_beat: {midi.ticks_per_beat}",
        f"tracks: {len(midi.tracks)}",
    ]

    for track_index, track in enumerate(midi.tracks):
        name = f"Track {track_index}"
        channels: set[int] = set()
        programs: list[str] = []
        note_counts: Counter[int] = Counter()

        for message in track:
            if message.type == "track_name":
                name = message.name
            if hasattr(message, "channel"):
                channels.add(message.channel)
            if message.type == "program_change":
                programs.append(f"ch={message.channel} program={message.program}")
            if message.type == "note_on" and message.velocity > 0:
                note_counts[message.channel] += 1

        lines.append(f"[{track_index}] {name}")
        lines.append(f"  channels: {sorted(channels)}")
        lines.append(f"  programs: {programs}")
        lines.append(f"  note_on_counts: {dict(sorted(note_counts.items()))}")

    return lines


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python -m conductor_demo.music.midi_inspect <path.mid>")
        return 2

    try:
        lines = inspect_midi_file(sys.argv[1])
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
