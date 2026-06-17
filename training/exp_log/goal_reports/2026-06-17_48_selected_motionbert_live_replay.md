# Selected MotionBERT Live Replay

## Scope

```text
date: 2026-06-17
bundle: outputs/right_conducting/selected_motionbert_static80_transitions_live45f
manifest: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json
window_frames: 45
stride_frames: 3
fps: about 15
window_seconds: about 3.0
mode: full MotionBERT backbone + exported head + LiveSmoother
```

## Tooling Change

`tools/replay_motionbert_live_bundle.py` now supports:

```text
--eval-root <root>
```

This replays every scoreable session below the root and resets the live smoother per session, avoiding fake switches across take boundaries.

## Commands

Transition replay:

```bash
python tools/replay_motionbert_live_bundle.py \
  --manifest outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json \
  --eval-root dataset/transitions \
  --device cuda:0 \
  --stable-only \
  --output-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_transitions_stable.json \
  --output-md outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_transitions_stable.md \
  --output-rows outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_transitions_stable_rows.jsonl
```

Static 80 replay:

```bash
python tools/replay_motionbert_live_bundle.py \
  --manifest outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json \
  --eval-root dataset/static_variants_80 \
  --device cuda:0 \
  --stable-only \
  --output-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_static80_stable.json \
  --output-md outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_static80_stable.md \
  --output-rows outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_static80_stable_rows.jsonl
```

## Results

| eval_root | sessions | rows | mode | tempo_acc | gain_acc | true_switch | pred_switch | false_switch | missed | false/min | delay_mean_s | delay_p90_s |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dataset/static_variants_80 | 4 | 942 | raw | 1.0000 | 1.0000 | 0 | 0 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 |
| dataset/static_variants_80 | 4 | 942 | smoothed | 1.0000 | 1.0000 | 0 | 0 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 |
| dataset/transitions | 7 | 1305 | raw | 0.9854 | 1.0000 | 14 | 36 | 11 | 0 | 2.1921 | 0.0000 | 0.0000 |
| dataset/transitions | 7 | 1305 | smoothed | 0.9893 | 1.0000 | 14 | 14 | 0 | 0 | 0.0000 | 0.1998 | 0.5938 |

## Interpretation

The exported bundle is loadable and scoreable in the full runtime path, not only cached-head evaluation.

Static 80 is stable: no false switch in 4 fixed-camera static takes.

Transition replay is usable after the policy sweep: the remaining false switches are removed without reducing aggregate tempo accuracy. The remaining weak edge is delayed adaptation in:

```text
session_20260617_022517_bpm120to120_beat3_small
```

That is the current weak edge case for live use: 120 -> 80 -> 120, 3-beat, small dynamics. It has no false switch after smoothing, but it has the largest remaining p90 delay.

## Updated Bundle Evidence

The selected manifest and structure file now include replay evidence:

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_structure.md
```

## Caveat

These are deployment-fit scores because `dataset/transitions` was part of the training source for the selected candidate. For an independent claim, record a new fixed-camera transition heldout set and keep it out of training.
