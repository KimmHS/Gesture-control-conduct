# Ext Bundle Label-Free Online Pose Stream

## Purpose

The selected ext bundle must work in the final stream path, where labels are not
available and pose frames arrive one at a time. This report replays the new
`selected_motionbert_static80_transitions_live45f_ext` bundle through:

```text
label-free window scan
online frame buffer
right-arm pose quality hold gate
```

## Bundle

```text
export_dir: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext
manifest: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_manifest.json
window_frames: 45
stride_frames: 3
fps: 15
cold_start: about 3.0s
update_interval: about 0.2s
```

## Inputs

```text
static80:
  dataset/static_variants_80/fixed-camera-high-arm/session_20260617_035040_bpm080_beat2_small/pose_right_h36m_masked.npy

transition:
  dataset/transitions/session_20260617_022517_bpm120to120_beat3_small/pose_right_h36m_masked.npy

degraded static80:
  outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/degraded_static80_035040_pose.npy

degraded transition:
  outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/degraded_transition_022517_pose.npy
```

The degraded pose files zero right shoulder/elbow/wrist confidence for frames
`90..150`.

## Results

Label-free window scan:

| case | rows | tempo classes | raw tempo switches | smoothed tempo switches | gain switches |
|---|---:|---|---:|---:|---:|
| static80 035040 | 236 | `[1]` | 0 | 0 | 0 |
| transition 022517 | 216 | `[1, 3]` | 9 | 2 | 0 |

Online frame buffer:

| case | rows | tempo classes | raw tempo switches | smoothed tempo switches | gain switches |
|---|---:|---|---:|---:|---:|
| static80 035040 | 236 | `[1]` | 0 | 0 | 0 |
| transition 022517 | 216 | `[1, 3]` | 9 | 2 | 0 |

Window scan vs online buffer comparison:

```text
status: PASS
ignore_fields: source.source_id
static80 rows: 236 == 236
transition rows: 216 == 216
first_mismatch_indices: []
```

Pose quality gate simulation:

| case | rows | invalid | held invalid | tempo classes | raw switches | smoothed switches | gain switches |
|---|---:|---:|---:|---|---:|---:|---:|
| degraded static80 | 236 | 28 | 28 | `[1]` | 0 | 0 | 0 |
| degraded transition | 216 | 28 | 28 | `[1, 3]` | 9 | 2 | 0 |

## Artifact Paths

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/pose_stream_static80_035040_live_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/pose_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/pose_stream_transition_022517_live_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/pose_stream_transition_022517_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/online_pose_stream_static80_035040_live_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/online_pose_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/online_pose_stream_transition_022517_live_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/online_pose_stream_transition_022517_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/online_pose_stream_comparison.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/online_pose_stream_comparison.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/degraded_online_pose_stream_static80_035040_live_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/degraded_online_pose_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/degraded_online_pose_stream_transition_022517_live_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/degraded_online_pose_stream_transition_022517_summary.json
outputs/right_conducting/goal_status_selected_motionbert_live45f_ext.json
```

The ext manifest and structure file now include `pose_stream_evidence`,
`online_pose_stream_evidence`, and `pose_quality_gate_evidence`.

## Verification

```bash
python -m py_compile lib/right_conducting/motionbert_pose_stream.py tools/run_motionbert_pose_stream.py tools/run_right_conducting_goal.py
python -m unittest discover -s tests -p 'test_motionbert_pose_stream.py' -v
python -m unittest discover -s tests -p 'test_goal_status.py' -v
python -m unittest discover -s tests -p 'test_train_motionbert_head_cli.py' -v
```

Result:

```text
py_compile: OK
test_motionbert_pose_stream.py: 10 OK
test_goal_status.py: 2 OK
test_train_motionbert_head_cli.py: 6 OK
stream JSON artifacts: 9 OK
```

## Status

```text
live_pilot_status: GO
strict_heldout_status: NO_GO
```

This strengthens the final stream wiring evidence for the selected ext bundle.
It does not replace the still-needed independent heldout transition replay.
