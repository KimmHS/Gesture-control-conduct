# Available Strict Heldout Stress

## Purpose

The selected ext bundle already passes the fixed-camera deployment-fit devset,
but final reporting still needs strict heldout evidence. This step checks whether
the existing evaluation roots are independent of the staged training source and
replays the available scoreable heldout session.

## Independence

Train manifest:

```text
outputs/right_conducting/recordings_staged_static80_transitions_manifest.json
```

Heldout roots:

| root | status | heldout sessions | path overlaps | name overlaps | note |
|---|---|---:|---:|---:|---|
| dataset/evaluation | GO | 1 | 0 | 0 | scoreable, relabeled 222455 session |
| dataset/evaluation_transitions | GO | 1 | 0 | 0 | 215630 label is still not trusted for transition scoring |

Artifacts:

```text
outputs/right_conducting/strict_static_eval_independence_ext.json
outputs/right_conducting/strict_static_eval_independence_ext.md
outputs/right_conducting/strict_transition_eval_independence_ext.json
outputs/right_conducting/strict_transition_eval_independence_ext.md
```

## Replayed Session

```text
session: dataset/evaluation/session_20260616_222455_bpm120_beat4_large
window_frames: 45
stride_frames: 3
stable_only: true
row_count: 258
```

Important scope note:

```text
222455 is independent and scoreable, but it is a 4-beat / mixed-timeline stress session.
The current fixed-camera training/dev target was built from 2-beat and 3-beat data.
Use this as strict stress evidence, not as proof that the current 2/3-beat target has no heldout gap.
```

## Strict Replay Gate

| metric | value | threshold | status |
|---|---:|---:|---|
| smoothed tempo_acc | 0.2946 | >= 0.85 | fail |
| smoothed gain_acc | 0.8760 | >= 0.90 | fail |
| false_switches_per_min | 10.5151 | <= 0.50 | fail |
| missed_switch_count | 1 | <= 0 | fail |
| switch_delay_p90_s | 0.0000 | <= 1.00 | pass |
| heldout independence | GO | GO | pass |

Gate artifact:

```text
outputs/right_conducting/strict_heldout_222455_ext_live_gate.json
outputs/right_conducting/strict_heldout_222455_ext_live_gate.md
```

## Confusion Summary

Smoothed tempo confusion:

| true BPM | support | predicted 60 | predicted 80 | predicted 100 | predicted 120 |
|---:|---:|---:|---:|---:|---:|
| 80 | 16 | 2 | 14 | 0 | 0 |
| 100 | 96 | 9 | 25 | 62 | 0 |
| 120 | 146 | 0 | 79 | 67 | 0 |

Raw tempo confusion:

| true BPM | support | predicted 60 | predicted 80 | predicted 100 | predicted 120 |
|---:|---:|---:|---:|---:|---:|
| 80 | 16 | 4 | 12 | 0 | 0 |
| 100 | 96 | 10 | 26 | 59 | 1 |
| 120 | 146 | 3 | 79 | 63 | 1 |

Interpretation:

```text
The failure is not just transition delay.
The 120 BPM heldout segment collapses mostly into 80/100 predictions.
This points to heldout condition mismatch: 4-beat/mixed conducting pattern and older evaluation capture are not covered by the current 2/3-beat fixed-camera training source.
```

## Label-Untrusted Session

`dataset/evaluation_transitions/session_20260616_215630_bpm100_beat4_large` was
also independent, but its current window labels are all tempo class `2` and do
not reflect the intended transition. It remains excluded from score claims until
relabeling is done.

For traceability only, a label-untrusted replay was written:

```text
outputs/right_conducting/strict_heldout_215630_ext_replay_label_untrusted.json
outputs/right_conducting/strict_heldout_215630_ext_replay_label_untrusted.md
```

## Live Output Artifact

```text
outputs/right_conducting/strict_heldout_222455_ext_live_outputs.jsonl
outputs/right_conducting/strict_heldout_222455_ext_live_outputs_summary.json
```

## Status

```text
live_pilot_status: GO
strict_heldout_status: NO_GO
reason: independent heldout stress replay fails strict live thresholds
```

## Verification

```text
py_compile goal_status/summarizer: OK
test_goal_status.py: 3 OK
test_motionbert_pose_stream.py: 10 OK
strict JSON artifacts: 8 OK
goal_status_selected_motionbert_live45f_ext: IN_PROGRESS / live GO / strict NO_GO
```

## Next Action

For the current 2/3-beat fixed-camera target, record a new independent heldout
set that is not included in `recordings_staged_static80_transitions_manifest`.
Minimum useful set:

```text
2 takes: 120 -> 80 -> 120, beat2, large/small
2 takes: 120 -> 80 -> 120, beat3, large/small
2 takes: 100 -> 80 -> 100, beat3, large/small
2 takes: 80 static, beat2/beat3, large/small
```

If 4-beat conducting must be supported, it has to be added intentionally as a
training/dev condition instead of being treated as an accidental heldout pass
requirement.
