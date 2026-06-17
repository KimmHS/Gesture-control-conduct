# Goal Report 22: Eval Relabel and Down-Transition Data Decision

## Purpose

Reports 17-21 show that the current selected fallback cannot reliably handle the `120 -> 80` down-transition in the only scoreable transition session.

This report audits the evaluation sessions and decides whether to:

```text
1. add session_20260616_215630_eval to the score now,
2. relabel it first,
3. or collect additional down-transition heldout data.
```

## Implementation

New files:

```text
lib/right_conducting/eval_session_audit.py
tools/audit_right_conducting_eval_sessions.py
tests/test_eval_session_audit.py
```

The audit checks:

```text
required original files exist:
  labels_frame.jsonl
  labels_window.jsonl
  pose_right_h36m_masked.npy
  right_rule_features.npy

manual_timeline.json exists
frame labels contain at least two BPM targets
window labels contain at least two BPM targets
eval-local augmentation artifacts are present but excluded from scoring
```

## Command

```bash
python tools/audit_right_conducting_eval_sessions.py \
  --eval-root dataset/evaluation_transitions \
  --output-json outputs/right_conducting/eval_session_readiness_audit.json \
  --output-md outputs/right_conducting/eval_session_readiness_audit.md
```

Artifacts:

```text
outputs/right_conducting/eval_session_readiness_audit.json
outputs/right_conducting/eval_session_readiness_audit.md
```

## Audit Result

| session | scoreable transition eval | frame BPM targets | window BPM targets | frame transitions | mixed windows | blocking reasons |
|---|---|---|---|---:|---:|---|
| session_20260616_215630_eval | false | `[100.0]` | `[100.0]` | 0 | 0 | missing manual timeline; frame/window labels contain fewer than two BPM targets |
| session_20260616_222455_eval | true | `[100.0, 120.0, 80.0]` | `[100.0, 120.0, 80.0]` | 2 | 34 | none |

Both sessions contain eval-local augmentation artifacts:

```text
recommended_augmented_v0/
labels_tempo_augmented_15f.jsonl
tempo_augmented_15f.npy
```

These remain excluded from scoring.

## 215630 Current State

Current files exist:

```text
labels_frame.jsonl
labels_window.jsonl
pose_right_h36m_masked.npy
right_rule_features.npy
raw_video.mp4
```

But current labels are constant:

```text
labels_frame.jsonl:
  frame_count: 900
  bpm_target: 100.0 for all frames

labels_window.jsonl:
  window_count: 131
  bpm_target: 100.0 for all windows
  tempo_class: 2 for all windows
```

Missing:

```text
manual_timeline.json
```

Decision:

```text
session_20260616_215630_eval must remain excluded from score.
```

Reason:

```text
The user previously noted that tempo likely changes in the middle,
but the repository currently has no trusted transition timestamp.
Scoring it as constant 100 BPM would be dishonest.
Inferring the transition from model outputs or motion features would contaminate evaluation labels.
```

## Required Relabel Input

Minimum information needed to score `215630_eval`:

```json
{
  "session_name": "session_20260616_215630_bpm100_beat4_large",
  "time_unit": "seconds_from_recording_start",
  "raw_user_events": [
    {
      "time": 0.0,
      "bpm": 100.0,
      "meter_beats": 4,
      "dynamics_condition": "large"
    },
    {
      "time": "<CHANGE_TIME_SECONDS>",
      "bpm": "<NEW_BPM>"
    }
  ],
  "applied_segments": [
    {
      "start": 0.0,
      "end": "<CHANGE_TIME_SECONDS>",
      "bpm": 100.0,
      "meter_beats": 4,
      "dynamics_condition": "large"
    },
    {
      "start": "<CHANGE_TIME_SECONDS>",
      "end": null,
      "bpm": "<NEW_BPM>",
      "meter_beats": 4,
      "dynamics_condition": "large"
    }
  ]
}
```

If meter or dynamics also changed, those timestamps must be added as separate raw events and applied segments.

## After Relabel

Once `manual_timeline.json`, `labels_frame.jsonl`, and `labels_window.jsonl` are updated for `215630_eval`, rerun:

```bash
python tools/audit_right_conducting_eval_sessions.py \
  --eval-root dataset/evaluation_transitions \
  --output-json outputs/right_conducting/eval_session_readiness_audit.json \
  --output-md outputs/right_conducting/eval_session_readiness_audit.md
```

Then rerun the same score diagnostics used for `222455_eval`:

```bash
python tools/evaluate_right_conducting_transition_margins.py \
  --artifact outputs/right_conducting/selected/feature_baseline_live_v0.json \
  --eval-session dataset/evaluation_transitions/session_20260616_215630_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --input-norm camera \
  --margins 0,0.5,1,2,3 \
  --output-json outputs/right_conducting/transition_margin_scores_215630_60f.json \
  --output-md outputs/right_conducting/transition_margin_scores_215630_60f.md
```

## Data Decision

Current scoreable transition set:

```text
1 session only:
  session_20260616_222455_eval
```

This is not enough to claim robust live down-transition control.

Minimum additional heldout set:

| ID | scenario | purpose |
|---|---|---|
| T1 | `120 -> 80`, large | direct failure reproduction |
| T2 | `100 -> 80`, large | down-transition without 120 source |
| T3 | stable `80`, large | false-switch and stable-tail coverage |

Preferred heldout set from `dataset_shortage_action_plan.md`:

```text
60 -> 100 large
100 -> 60 large
100 small -> 100 large
100 large -> 100 small
80 small -> 120 large
plus 120 -> 80 large because it is the current failure case
```

## Decision

```text
Do not continue model-only tuning as the primary path.
```

Current selected live fallback remains:

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
```

Current live claim:

```text
GO:
  temporary live fallback for demo with known limitations
  tempo/gain output pipeline and scoring infrastructure

NO-GO:
  robust live 120 -> 80 down-transition control
  final model claim based on one scoreable transition session
```

## Next Gate

Recommended next step:

```text
Report 23: implement relabel helper for manual_timeline -> labels_frame/window
```

This should only be run after the true `215630_eval` transition timestamps are supplied.

If timestamps are not available:

```text
record the minimum additional heldout set above and keep 215630 excluded.
```
