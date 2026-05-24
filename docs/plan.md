# MIDI Landmark Conducting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a two-hand conducting demo where MediaPipe hand landmarks control section selection, dynamics, cue gestures, and MIDI expression output for `assets/audio/Symphony7_2.mid`.

**Architecture:** Keep the current webcam, hand tracking, motion buffer, WAV playback, and debug overlay intact. Add a small landmark-mapping layer that reads both hands, turns left-hand index position into section selection, turns right-wrist motion into expression/downbeat commands, then optionally sends MIDI CC messages to an external synth/DAW.

**Tech Stack:** Python, OpenCV, MediaPipe Hand Landmarker, existing `MotionBuffer`, existing `MusicController`, optional `mido[ports-rtmidi]` for MIDI output, standard-library `unittest` for focused tests.

---

## Scope

### First Working Demo

Build **Two-hand Section Mixer**:

```text
Left hand  = select orchestra section
Right hand = control selected section dynamics and cue/downbeat
MIDI       = send CC11 Expression for selected section channels
Audio      = keep existing WAV playback as fallback/demo bed
```

The first demo should show visible control even before MIDI audio is perfect:

```text
STRINGS | WOODWINDS | BRASS | PERCUSSION
                 TUTTI

Selected: STRINGS
Right: RH_DYN_LOUD
Command: CMD_SET_STRINGS_EXPRESSION_112
MIDI: CC11 ch=0 value=112
```

### Not First

Do not start with internal MIDI synthesis. A `.mid` file contains notes and events, not rendered audio. To hear section-level control, one of these is needed:

- external synth/DAW receiving MIDI CC messages,
- a software synth plus soundfont,
- pre-rendered section stems.

For this project, the stable first path is **visual mapping + MIDI CC output**. Internal MIDI playback can be added after the control layer is proven.

---

## Control Mapping

### Landmark Inputs

Use MediaPipe hand landmarks already produced by `HandTracker`.

```text
Left index tip landmark: 8
Right wrist landmark: 0
```

### Left Hand

The left hand selects the current target section by placing the index fingertip inside a screen zone.

| Left-hand state | Mapping |
| --- | --- |
| index tip inside `STRINGS` zone | `selected_section = STRINGS` |
| index tip inside `WOODWINDS` zone | `selected_section = WOODWINDS` |
| index tip inside `BRASS` zone | `selected_section = BRASS` |
| index tip inside `PERCUSSION` zone | `selected_section = PERCUSSION` |
| index tip inside `TUTTI` zone | `selected_section = TUTTI` |
| no stable left target | keep last target briefly, then fall back to `TUTTI` |

Use a short dwell time so selection does not flicker:

```text
left_dwell_seconds = 0.25
left_hold_seconds = 0.75
```

### Right Hand

The right hand controls dynamics and cue for the selected section.

```python
right_intensity = normalized_right_wrist_motion_span  # 0.0 to 1.0
expression = int(30 + right_intensity * 97)           # 30 to 127
```

| Right intensity | Label | MIDI/Internal value |
| ---: | --- | ---: |
| `0.00 - 0.35` | `SOFT` | `30 - 64` |
| `0.35 - 0.65` | `NORMAL` | `65 - 95` |
| `0.65 - 1.00` | `LOUD` | `96 - 127` |

Downbeat detection:

```text
recent right-wrist motion is mostly downward
vertical span is larger than horizontal span
downward velocity exceeds threshold
cooldown prevents duplicate beats
```

### Commands

```text
LH_POINT_SECTION + RH_MOTION_SIZE = CMD_SET_<SECTION>_EXPRESSION_<VALUE>
LH_POINT_SECTION + RH_DOWNBEAT    = CMD_CUE_<SECTION>
No left target + right control    = TUTTI/global control
```

---

## MIDI Plan

### MIDI File

Use:

```text
assets/audio/Symphony7_2.mid
```

Known local file check:

```text
Standard MIDI data, format 1, 13 tracks, timing 1/384
```

### MIDI Control Strategy

Use CC11 Expression first.

```text
CC7  = channel volume
CC11 = expression controller
```

Reason:

- CC11 is safer for live musical shaping.
- CC7 can stay as the channel's baseline volume.
- Sending CC11 does not require rewriting the MIDI file.

### Initial Section Channel Map

This map was adjusted after inspecting track names/channels from `Symphony7_2.mid`.

```python
SECTION_CHANNELS = {
    "STRINGS": [7, 8, 10, 11, 12],
    "WOODWINDS": [0, 1, 2, 3, 4, 5],
    "BRASS": [],
    "PERCUSSION": [6],
    "TUTTI": [],
}
```

`TUTTI` sends CC11 to all channels in the other groups.
`Symphony7_2.mid` does not expose a brass channel in the current file. The `BRASS` UI zone is still present for gesture/game vocabulary, but MIDI output for `BRASS` is a no-op until a brass track/channel is added or remapped.

### MIDI Runtime Modes

Support these modes in order:

1. **No MIDI:** visual mapping only, current WAV playback unchanged.
2. **MIDI output:** send CC11 to an opened output port with `mido`.
3. **MIDI playback/synth:** later work using an external synth, DAW, or soundfont-backed player.

---

## File Structure

### Modify

- `src/conductor_demo/vision/tracker.py`
  - Keep existing single active-hand output.
  - Add `TrackingResult.hands` so new code can read both hands.

- `src/conductor_demo/app/runner.py`
  - Keep current active-hand motion and WAV controls.
  - Add per-hand motion buffers.
  - Update two-hand mapper each frame.
  - Draw mapping overlay.
  - Apply MIDI output when enabled.

- `src/conductor_demo/config/defaults.py`
  - Add a small `MidiConfig`.
  - Keep MIDI disabled by default.

- `src/conductor_demo/main.py`
  - Add optional CLI flags for MIDI mode.

- `requirements.txt`
  - Add `mido[ports-rtmidi]` only when MIDI output is implemented.

### Create

- `src/conductor_demo/game/__init__.py`
- `src/conductor_demo/game/two_hand_mapping.py`
  - Landmark zones.
  - `TwoHandMapper`.
  - `MappingState`.
  - Overlay drawing for section meters and command text.

- `src/conductor_demo/music/midi_output.py`
  - `MidiSectionOutput`.
  - CC11 routing.
  - Safe no-op behavior when MIDI is disabled or the port is unavailable.

- `src/conductor_demo/music/midi_inspect.py`
  - Small helper to print tracks, channels, program changes, and note counts from `Symphony7_2.mid`.

- `tests/test_tracking_result.py`
- `tests/test_two_hand_mapping.py`
- `tests/test_midi_output.py`

---

## Task 1: Expose Both Hands From Tracker

**Files:**

- Modify: `src/conductor_demo/vision/tracker.py`
- Test: `tests/test_tracking_result.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_tracking_result.py`.

```python
import unittest

from conductor_demo.vision.tracker import HandObservation, TrackingResult


class TrackingResultTests(unittest.TestCase):
    def test_hands_default_is_empty_per_instance(self):
        first = TrackingResult()
        second = TrackingResult()

        first.hands["Left"] = HandObservation(
            label="Left",
            handedness_score=0.9,
            wrist_px=(10.0, 20.0),
            hand_scale_px=50.0,
            bbox=(0, 0, 30, 40),
            landmarks_px=[(10, 20)] * 21,
        )

        self.assertIn("Left", first.hands)
        self.assertNotIn("Left", second.hands)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify failure**

```bash
PYTHONPATH=src python -m unittest tests.test_tracking_result -v
```

Expected failure before implementation:

```text
AttributeError: 'TrackingResult' object has no attribute 'hands'
```

- [ ] **Step 3: Add `hands` to `TrackingResult`**

In `src/conductor_demo/vision/tracker.py`, change the dataclass import:

```python
from dataclasses import dataclass, field
```

Add this field to `TrackingResult`:

```python
hands: dict[str, HandObservation] = field(default_factory=dict)
```

- [ ] **Step 4: Fill `hands` inside live tracking**

After the `observations = self._extract_observations(results, width, height)` line, build:

```python
hands_by_label = {
    obs.label: obs
    for obs in observations
    if obs.handedness_score >= self.hand_confidence_threshold
    and obs.hand_scale_px >= self.min_hand_scale_px
}
```

Pass it into the live return:

```python
hands=hands_by_label,
```

Hold/lost results can keep the default empty dict because stale dual-hand control should not send new commands.

- [ ] **Step 5: Run verification**

```bash
PYTHONPATH=src python -m unittest tests.test_tracking_result -v
PYTHONPATH=src python -m compileall src
```

Expected:

```text
OK
```

---

## Task 2: Add Landmark-Based Two-Hand Mapper

**Files:**

- Create: `src/conductor_demo/game/__init__.py`
- Create: `src/conductor_demo/game/two_hand_mapping.py`
- Test: `tests/test_two_hand_mapping.py`

- [ ] **Step 1: Write mapper tests**

Create tests for:

```text
left index tip inside a zone selects that section after dwell
right wrist span maps to SOFT/NORMAL/LOUD
downward right-wrist motion produces one downbeat during cooldown
missing left hand falls back to TUTTI after hold timeout
```

Use fake hand objects with only the fields the mapper needs:

```python
from dataclasses import dataclass


@dataclass
class FakeHand:
    landmarks_px: list[tuple[int, int]]
    wrist_px: tuple[float, float]
    hand_scale_px: float = 60.0
    handedness_score: float = 0.9
```

- [ ] **Step 2: Run tests and verify failure**

```bash
PYTHONPATH=src python -m unittest tests.test_two_hand_mapping -v
```

Expected failure:

```text
ModuleNotFoundError: No module named 'conductor_demo.game'
```

- [ ] **Step 3: Create mapper module**

Implement these public names in `src/conductor_demo/game/two_hand_mapping.py`:

```python
INDEX_TIP = 8

class Section(str, Enum):
    NONE = "NONE"
    STRINGS = "STRINGS"
    WOODWINDS = "WOODWINDS"
    BRASS = "BRASS"
    PERCUSSION = "PERCUSSION"
    TUTTI = "TUTTI"

@dataclass(frozen=True, slots=True)
class Rect:
    x1: int
    y1: int
    x2: int
    y2: int

@dataclass(slots=True)
class MappingState:
    selected_section: Section = Section.TUTTI
    left_gesture: str = "LH_LOST"
    right_gesture: str = "RH_LOST"
    right_dynamic_label: str = "NORMAL"
    right_intensity: float = 0.0
    downbeat: bool = False
    command: str = "CMD_NONE"
    last_feedback: str = "READY"
    section_expression: dict[str, int] = field(
        default_factory=lambda: {
            "STRINGS": 80,
            "WOODWINDS": 80,
            "BRASS": 80,
            "PERCUSSION": 80,
            "TUTTI": 80,
        }
    )

class TwoHandMapper:
    def update(
        self,
        *,
        frame_size: tuple[int, int],
        timestamp: float,
        left_hand: object | None,
        right_hand: object | None,
        right_motion: MotionBuffer,
    ) -> MappingState:
        return self.state
```

The `return self.state` body is only the starting shape. The real implementation in this task must apply the formulas from **Control Mapping** before returning. Keep this mapper independent of OpenCV except for the optional overlay function.

- [ ] **Step 4: Add overlay function**

Add:

```python
def draw_mapping_overlay(frame: object, state: MappingState) -> object:
    return frame
```

Replace the pass-through body in the same step so it draws:

- section zones,
- selected section highlight,
- expression meter per section,
- status line with left gesture, right gesture, and command.

- [ ] **Step 5: Run verification**

```bash
PYTHONPATH=src python -m unittest tests.test_two_hand_mapping -v
PYTHONPATH=src python -m compileall src
```

Expected:

```text
OK
```

---

## Task 3: Wire Mapper Into Runner

**Files:**

- Modify: `src/conductor_demo/app/runner.py`

- [ ] **Step 1: Add imports**

```python
from conductor_demo.game.two_hand_mapping import TwoHandMapper, draw_mapping_overlay
```

- [ ] **Step 2: Add per-hand state in `AppRunner.__init__`**

```python
self.motion_by_hand = {
    "Left": MotionBuffer(maxlen=config.motion.buffer_size),
    "Right": MotionBuffer(maxlen=config.motion.buffer_size),
}
self.two_hand_mapper = TwoHandMapper()
self.mapping_state = self.two_hand_mapper.state
```

- [ ] **Step 3: Add helper to append dual-hand motion**

```python
def _append_dual_hand_motion(
    self,
    hands: dict[str, Any],
    timestamp: float,
) -> None:
    for label in ("Left", "Right"):
        hand = hands.get(label)
        if hand is None:
            continue

        wrist = hand.wrist_px
        self.motion_by_hand[label].append(
            MotionSample(
                x=wrist[0],
                y=wrist[1],
                timestamp=timestamp,
                confidence=hand.handedness_score,
                raw_x=wrist[0],
                raw_y=wrist[1],
                is_live=True,
            )
        )
```

- [ ] **Step 4: Update the camera loop**

After the existing active-hand `self.motion.append` block, add:

```python
self._append_dual_hand_motion(
    hands=tracking.hands,
    timestamp=packet.timestamp,
)

self.mapping_state = self.two_hand_mapper.update(
    frame_size=(packet.frame.shape[1], packet.frame.shape[0]),
    timestamp=packet.timestamp,
    left_hand=tracking.hands.get("Left"),
    right_hand=tracking.hands.get("Right"),
    right_motion=self.motion_by_hand["Right"],
)
```

After the `self.overlay.draw_debug` call, add:

```python
debug_frame = draw_mapping_overlay(
    frame=debug_frame,
    state=self.mapping_state,
)
```

- [ ] **Step 5: Run smoke checks**

```bash
PYTHONPATH=src python main.py --self-test --verbose
PYTHONPATH=src python main.py --max-frames 300
```

Expected:

```text
self-test completes
webcam window opens
existing debug overlay still appears
new section overlay appears
no crash when zero, one, or two hands are visible
```

---

## Task 4: Add MIDI Inspection Helper

**Files:**

- Create: `src/conductor_demo/music/midi_inspect.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Add dependency**

Add:

```text
mido[ports-rtmidi]
```

Install:

```bash
pip install -r requirements.txt
```

- [ ] **Step 2: Create MIDI inspection helper**

Implement:

```python
from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

import mido


def inspect_midi_file(path: str) -> list[str]:
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

    for line in inspect_midi_file(sys.argv[1]):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

It should print:

```text
file type
ticks per beat
track index and name
channels used by each track
program_change events
note_on counts per channel
```

- [ ] **Step 3: Run inspection**

```bash
PYTHONPATH=src python -m conductor_demo.music.midi_inspect assets/audio/Symphony7_2.mid
```

Expected:

```text
13 tracks are reported
channels and track names are visible enough to refine SECTION_CHANNELS
```

Keep the initial channel map if the file does not contain useful track names.

---

## Task 5: Add MIDI CC Output

**Files:**

- Create: `src/conductor_demo/music/midi_output.py`
- Test: `tests/test_midi_output.py`

- [ ] **Step 1: Write tests with a fake MIDI port**

Test that:

```text
STRINGS expression sends CC11 to string channels
TUTTI sends CC11 to all mapped channels
same value is not resent every frame
disabled or unopened output does nothing
```

- [ ] **Step 2: Create output module**

Implement:

```python
SECTION_CHANNELS = {
    "STRINGS": [7, 8, 10, 11, 12],
    "WOODWINDS": [0, 1, 2, 3, 4, 5],
    "BRASS": [],
    "PERCUSSION": [6],
    "TUTTI": [],
}

@dataclass(slots=True)
class MidiSectionOutput:
    enabled: bool = False
    port_name: str | None = None
    control_number: int = 11
    _port: object | None = None
    _last_values: dict[tuple[int, int], int] = field(default_factory=dict)

    def open(self) -> None:
        if not self.enabled:
            return
        self._port = mido.open_output(self.port_name)

    def close(self) -> None:
        if self._port is not None:
            self._port.close()
            self._port = None

    def apply(self, state: MappingState) -> None:
        if not self.enabled or self._port is None:
            return

        all_channels = sorted(
            {
                channel
                for section, channels in SECTION_CHANNELS.items()
                if section != "TUTTI"
                for channel in channels
            }
        )

        for section_name, expression in state.section_expression.items():
            channels = SECTION_CHANNELS.get(section_name, [])
            if section_name == "TUTTI":
                channels = all_channels

            for channel in channels:
                key = (channel, self.control_number)
                if self._last_values.get(key) == expression:
                    continue
                self._port.send(
                    mido.Message(
                        "control_change",
                        channel=channel,
                        control=self.control_number,
                        value=expression,
                    )
                )
                self._last_values[key] = expression
```

`apply()` sends:

```python
mido.Message(
    "control_change",
    channel=channel,
    control=11,
    value=expression,
)
```

- [ ] **Step 3: Run tests**

```bash
PYTHONPATH=src python -m unittest tests.test_midi_output -v
PYTHONPATH=src python -m compileall src
```

Expected:

```text
OK
```

---

## Task 6: Add MIDI Config and CLI Flags

**Files:**

- Modify: `src/conductor_demo/config/defaults.py`
- Modify: `src/conductor_demo/main.py`
- Modify: `src/conductor_demo/app/runner.py`

- [ ] **Step 1: Add config**

```python
@dataclass(slots=True)
class MidiConfig:
    enabled: bool = False
    port_name: str | None = None
    midi_file_path: str = "assets/audio/Symphony7_2.mid"
    expression_cc: int = 11
```

Add to `AppConfig`:

```python
midi: MidiConfig = field(default_factory=MidiConfig)
```

- [ ] **Step 2: Add CLI flags**

In `build_parser()`:

```python
parser.add_argument("--midi-out", help="Enable MIDI output to this port name.")
parser.add_argument(
    "--midi-file",
    default=None,
    help="MIDI file used for inspection and section-channel mapping.",
)
```

In `main()`:

```python
if args.midi_out:
    config.midi.enabled = True
    config.midi.port_name = args.midi_out
if args.midi_file:
    config.midi.midi_file_path = args.midi_file
```

- [ ] **Step 3: Open and close MIDI output in runner**

In `AppRunner.__init__`:

```python
self.midi_out = MidiSectionOutput(
    enabled=config.midi.enabled,
    port_name=config.midi.port_name,
    control_number=config.midi.expression_cc,
)
```

In `run()` before camera loop:

```python
self.midi_out.open()
```

In `finally`:

```python
self.midi_out.close()
```

After mapper update:

```python
self.midi_out.apply(self.mapping_state)
```

`MidiSectionOutput.open()` must log and disable itself if the port cannot be opened, so the visual demo still runs.

- [ ] **Step 4: Run verification**

```bash
PYTHONPATH=src python main.py --self-test --verbose
PYTHONPATH=src python main.py --max-frames 300
PYTHONPATH=src python main.py --midi-out "IAC Driver Bus 1" --max-frames 300
```

Expected:

```text
without --midi-out, behavior is unchanged
with --midi-out and a valid port, CC messages are sent
with an invalid port, the app logs a warning and keeps running
```

---

## Task 7: Add Optional Scoring Layer

**Files:**

- Create: `src/conductor_demo/game/scoring.py`
- Test: `tests/test_scoring.py`
- Modify: `src/conductor_demo/app/runner.py`
- Modify: `src/conductor_demo/game/two_hand_mapping.py`

- [ ] **Step 1: Define a short beat script**

```python
SCRIPT = [
    ("STRINGS", "NORMAL"),
    ("STRINGS", "SOFT"),
    ("WOODWINDS", "SOFT"),
    ("BRASS", "LOUD"),
    ("STRINGS", "LOUD"),
    ("PERCUSSION", "LOUD"),
    ("TUTTI", "NORMAL"),
    ("TUTTI", "SOFT"),
]
```

- [ ] **Step 2: Score only on downbeat**

```python
def score_on_downbeat(state: MappingState, beat_index: int) -> int:
    expected_section, expected_dyn = SCRIPT[beat_index % len(SCRIPT)]
    section_ok = state.selected_section.value == expected_section
    dyn_ok = state.right_dynamic_label == expected_dyn

    if section_ok and dyn_ok:
        return 100
    if section_ok:
        return 75
    if dyn_ok:
        return 55
    return 20
```

- [ ] **Step 3: Display score in overlay**

Add compact overlay text:

```text
Score: 0750 | Beat: 06 | Target: BRASS LOUD
```

- [ ] **Step 4: Run verification**

```bash
PYTHONPATH=src python -m unittest tests.test_scoring -v
PYTHONPATH=src python main.py --max-frames 300
```

Expected:

```text
score changes only when downbeat is detected
overlay text remains readable
```

---

## Manual Demo Checklist

- [ ] Run `python main.py`.
- [ ] Press `S` to start existing WAV playback.
- [ ] Show no hands: app keeps running.
- [ ] Show right hand only: `TUTTI` expression meter moves.
- [ ] Put left index in `STRINGS`: selected section changes after dwell.
- [ ] Move right hand small/medium/large: expression label changes.
- [ ] Make a clear downward stroke: `CMD_CUE_<SECTION>` appears once.
- [ ] Move left hand away briefly: selected section holds.
- [ ] Move left hand away longer than hold timeout: target returns to `TUTTI`.
- [ ] Run with MIDI port: external synth/DAW receives CC11.

---

## Suggested Implementation Order

1. Task 1: tracker exposes both hands.
2. Task 2: mapper works in unit tests.
3. Task 3: visual overlay works with webcam.
4. Task 4: inspect `Symphony7_2.mid`.
5. Task 5: MIDI output works with fake port tests.
6. Task 6: CLI/config enables real MIDI port.
7. Task 7: scoring layer if the demo needs game feedback.

Stop after Task 3 if the immediate goal is a visual proof of concept. Continue through Task 6 when the goal is real MIDI control.
