# Goal Report 23: Manual Timeline Relabel Helper

## Purpose

Report 22 decided that `session_20260616_215630_eval` must stay excluded until trusted transition timestamps are supplied.

This report implements the relabel helper needed for that next step, but does not relabel `215630_eval` yet.

Principle:

```text
Do not infer evaluation labels from model output or motion features.
Only apply explicit manual_timeline.json timestamps.
```

## Implementation

New files:

```text
lib/right_conducting/manual_timeline_relabel.py
tools/relabel_right_conducting_eval_from_timeline.py
tests/test_manual_timeline_relabel.py
```

The helper:

```text
labels_frame.jsonl + manual_timeline.json
-> relabeled labels_frame.jsonl
-> regenerated 60f labels_window JSONL
-> summary.json / summary.md
```

It is dry-run by default. It writes to `outputs/` and does not modify the source dataset session.

## Command

Dry-run on the already scoreable `222455_eval` session:

```bash
python tools/relabel_right_conducting_eval_from_timeline.py \
  --session dataset/evaluation_transitions/session_20260616_222455_eval \
  --window-frames 60 \
  --stride-frames 3 \
  --output-dir outputs/right_conducting/relabel_dryrun_222455_60f
```

Artifacts:

```text
outputs/right_conducting/relabel_dryrun_222455_60f/labels_frame.jsonl
outputs/right_conducting/relabel_dryrun_222455_60f/labels_window_60f.jsonl
outputs/right_conducting/relabel_dryrun_222455_60f/manual_timeline.json
outputs/right_conducting/relabel_dryrun_222455_60f/summary.json
outputs/right_conducting/relabel_dryrun_222455_60f/summary.md
```

## Dry-Run Result

Timeline BPM transition times:

```text
manual_timeline.json: 22.0s, 54.0s
relabeled frame labels: 22.042992s, 54.058506s
```

Frame label counts match the existing scoreable session:

| BPM | frame count |
|---:|---:|
| 100 | 330 |
| 120 | 480 |
| 80 | 90 |

Regenerated 60-frame windows:

| metric | value |
|---|---:|
| total windows | 281 |
| mixed BPM windows | 38 |
| stable windows | 243 |
| 100 BPM windows | 101 |
| 120 BPM windows | 159 |
| 80 BPM windows | 21 |

This matches the existing transition-margin evaluation base:

```text
281 total 60f windows
38 mixed BPM excluded
243 stable windows
```

## Why Original labels_window Counts Differ

The source `labels_window.jsonl` in `222455_eval` is a 120-frame historical label file:

```text
original labels_window rows: 131
```

Current v0 scoring regenerates 60-frame windows from `labels_frame.jsonl`, matching train window length:

```text
regenerated 60f rows: 281
```

Therefore the helper writes:

```text
labels_window_60f.jsonl
```

It does not overwrite the historical `labels_window.jsonl`.

## 215630 Status

Current `215630_eval` remains blocked:

```text
manual_timeline.json: missing
labels_frame.jsonl: constant 100 BPM
labels_window.jsonl: constant 100 BPM
```

The helper is ready, but actual relabel still requires user-provided timeline data:

```text
time 0.0s:
  bpm: 100
  meter_beats: 4
  dynamics_condition: large

time <CHANGE_TIME_SECONDS>:
  bpm: <NEW_BPM>
```

If there are meter/dynamics changes, they must be included as timestamped events too.

## Decision

```text
manual_timeline relabel helper: GO
215630_eval score inclusion: still NO-GO until timestamps are supplied
```

Current selected live fallback remains:

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
```

## Next Gate

If `215630_eval` timestamps are supplied:

```text
1. create manual_timeline.json for 215630_eval
2. run relabel dry-run
3. inspect audit output
4. only then update dataset labels or score from relabeled output
```

If timestamps are not available:

```text
record additional heldout down-transition sessions instead.
minimum:
  120 -> 80 large
  100 -> 80 large
  stable 80 large
```
