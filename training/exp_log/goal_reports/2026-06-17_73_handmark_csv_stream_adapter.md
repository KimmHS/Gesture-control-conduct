# Handmark CSV Stream Adapter

## Purpose

The selected MotionBERT live bundle now accepts:

```text
replay rows
pose_right_h36m_masked.npy
H36M17 JSONL/stdin frame stream
raw handmark recording CSV/stdin
```

This report adds the CSV/stdin path for the raw recording schema described in `docs/reference/DATASET.md`.

## Added Runtime Path

```text
lib/right_conducting/handmark_csv_stream.py
tools/run_motionbert_handmark_csv_stream.py
tools/run_right_conducting_goal.py --steps handmark-csv-stream-selected
```

CSV input columns used:

```text
right_shoulder_x/right_shoulder_y/right_shoulder_conf
right_elbow_x/right_elbow_y/right_elbow_conf
right_wrist_x/right_wrist_y/right_wrist_conf
optional reference joints: shoulder_center, neck, left_shoulder
```

Runtime mapping:

```text
right_shoulder -> H36M17 index 14
right_elbow    -> H36M17 index 15
right_wrist    -> H36M17 index 16
reference supplement -> H36M17 indices 8, 9, 11
all other joints -> confidence 0
```

## Command

Reference-supplemented dataset smoke:

```bash
python tools/run_right_conducting_goal.py \
  --steps handmark-csv-stream-selected \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext \
  --handmark-csv-stream-csv dataset/transitions/session_20260617_022415_bpm120to120_beat2_small.csv \
  --handmark-csv-stream-reference-pose-npy dataset/transitions/session_20260617_022415_bpm120to120_beat2_small/pose_right_h36m_masked.npy \
  --pose-stream-source-id transition_022415_handmark_csv_ref
```

Actual stdin mode:

```bash
python tools/run_motionbert_handmark_csv_stream.py \
  --manifest outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_manifest.json \
  --handmark-csv - \
  --output-jsonl - \
  --flush-each-output
```

For true live use, the upstream tracker should emit the right-arm columns plus reference joints, or emit H36M17 JSONL directly.

## Diagnosis

CSV right-arm coordinates match `pose_right_h36m_masked.npy` almost exactly:

| case | joint | mean absolute coordinate error |
|---|---|---:|
| static80 035040 | right shoulder/elbow/wrist | about `2.5e-6` |
| transition 022415 | right shoulder/elbow/wrist | about `2.5e-6` |

The bottleneck was not the right-arm CSV values. The issue was that the trained MotionBERT input also keeps reference joints:

```text
masked_keep_indices: [8, 9, 11, 14, 15, 16]
reference joints: shoulder_center, neck, left_shoulder
```

Raw CSV has the right arm but not those reference joints. With right-arm-only CSV, the static case remains stable, but the transition case no longer behaves like the pose stream.

## Smoke Results

| case | mode | reference | frames | rows | tempo classes | raw switches | smoothed switches | invalid |
|---|---|---|---:|---:|---|---:|---:|---:|
| static80 035040 | CSV right-arm only | none | 750 | 236 | `[1]` | 0 | 0 | 0 |
| transition 022415 | CSV right-arm only | none | 690 | 216 | `[0, 2, 3]` | 10 | 4 | 0 |
| static80 035040 | CSV + reference supplement | pose_right_h36m_masked.npy | 750 | 236 | `[1]` | 0 | 0 | 0 |
| transition 022415 | CSV + reference supplement | pose_right_h36m_masked.npy | 690 | 216 | `[1, 3]` | 2 | 2 | 0 |

Artifacts:

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/handmark_csv_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/handmark_csv_stream_transition_022415_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/handmark_csv_ref_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/handmark_csv_ref_stream_transition_022415_summary.json
```

## Readiness Update

`handmark_csv_stream_evidence` is registered in:

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_manifest.json
```

Current readiness:

```text
status: GO
handmark_csv_stream: GO
artifact: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.md
```

Important condition:

```text
GO applies to handmark CSV with reference joints.
Right-arm-only CSV is executable but not deployment-equivalent for transition control.
```

## Verification

```text
python -m py_compile lib/right_conducting/handmark_csv_stream.py tools/run_motionbert_handmark_csv_stream.py tools/run_right_conducting_goal.py
PYTHONPATH=. python tests/test_handmark_csv_stream.py
PYTHONPATH=. python tests/test_goal_command_cli.py
PYTHONPATH=. python tests/test_live_runtime_readiness.py
python tools/check_motionbert_live_runtime_readiness.py --manifest outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_manifest.json
```

All commands passed.

## Status

Live input coverage is stronger, but strict heldout generalization is still `NO_GO`. The next data requirement remains unchanged: record independent fixed-camera 2/3-beat heldout static80 and 120->80->120 takes outside the staged training manifest.
