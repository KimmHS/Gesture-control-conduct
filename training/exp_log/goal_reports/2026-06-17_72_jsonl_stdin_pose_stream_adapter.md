# JSONL/stdin Pose Stream Adapter

## Purpose

Selected MotionBERT live bundle already supported replay rows and `.npy` pose sequence streaming. This report adds the missing realtime-style input edge: one H36M17 pose frame per JSONL line, including stdin support.

## Added Runtime Path

```text
tools/convert_pose_npy_to_jsonl.py
tools/run_motionbert_pose_jsonl_stream.py
lib/right_conducting/motionbert_pose_jsonl_stream.py
```

Input schema per JSONL line:

```text
{"frame_index": 0, "timestamp_s": 0.0, "pose": [[x, y, confidence], ... 17 joints total]}
```

Accepted pose keys:

```text
pose
joints
landmarks
pose_right_h36m_masked
pose_flat / joints_flat / landmarks_flat
```

The stream adapter pushes each parsed `[17,3]` frame into the existing `OnlinePoseFrameStreamer`, so output schema and smoothing policy stay identical to the selected live runtime.

## Goal Runner Step

```bash
python tools/run_right_conducting_goal.py \
  --steps pose-jsonl-stream-selected \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext \
  --pose-stream-npy dataset/transitions/session_20260617_022415_bpm120to120_beat2_small/pose_right_h36m_masked.npy \
  --pose-stream-source-id transition_022415_jsonl
```

For actual stdin:

```bash
python tools/run_motionbert_pose_jsonl_stream.py \
  --manifest outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_manifest.json \
  --pose-jsonl - \
  --output-jsonl - \
  --flush-each-output
```

## Smoke Results

| case | device | frames | rows | mode | tempo classes | tempo switches | gain switches | invalid |
|---|---|---:|---:|---|---|---:|---:|---:|
| static80 035040 beat2 small | cuda:0 | 750 | 236 | jsonl_online | `[1]` | 0 | 0 | 0 |
| transition 022415 120->80->120 beat2 small | cuda:1 | 690 | 216 | jsonl_online | `[1, 3]` | 2 | 0 | 0 |

Artifacts:

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/jsonl_stream_static80_035040_input.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/jsonl_stream_static80_035040_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/jsonl_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/jsonl_stream_transition_022415_input.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/jsonl_stream_transition_022415_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/jsonl_stream_transition_022415_summary.json
```

## Readiness Update

`jsonl_pose_stream_evidence` is now registered in the selected live manifest. `tools/check_motionbert_live_runtime_readiness.py` checks the JSONL frame-stream input, output JSONL, summary mode, frame count, row count, input format, and invalid count.

Current selected bundle readiness:

```text
status: GO
jsonl_pose_stream: GO
artifact: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.md
```

## Verification

```text
python -m py_compile lib/right_conducting/motionbert_pose_jsonl_stream.py tools/run_motionbert_pose_jsonl_stream.py tools/convert_pose_npy_to_jsonl.py tools/run_right_conducting_goal.py
PYTHONPATH=. python tests/test_motionbert_pose_jsonl_stream.py
PYTHONPATH=. python tests/test_goal_command_cli.py
PYTHONPATH=. python tests/test_motionbert_pose_stream.py
PYTHONPATH=. python tests/test_live_runtime_readiness.py
python tools/check_motionbert_live_runtime_readiness.py --manifest outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_manifest.json
```

All commands passed.

## Status

Live pilot stream path is stronger: `.npy` pose replay, online frame buffer, and JSONL/stdin frame stream now all produce the same live output contract. Strict heldout generalization remains `NO_GO` until the in-scope independent 2/3-beat fixed-camera heldout set is recorded.
