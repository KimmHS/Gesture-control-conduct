# Right-Arm-Only Input Mask Probe

## Purpose

Raw handmark CSV can provide right shoulder / elbow / wrist, but not always the reference joints used by the primary exported model. This probe checks whether a MotionBERT head trained with `input_mask_mode=right_arm_only` can serve as a fixed-camera handmark-only fallback.

This is not a strict heldout claim. The new `dataset/static_variants_80` and `dataset/transitions` sessions are included in `outputs/right_conducting/recordings_staged_static80_transitions.zip`, so their scores are deployment-fit / training-fit checks.

## Dataset Intake

| root | processed sessions | duration | fps | decision |
|---|---:|---:|---:|---|
| `dataset/static_variants_80` | 4 | 50.02-50.06s | 14.93-14.98 | keep |
| `dataset/transitions` | 7 | 46.02-46.06s | 14.94-14.99 | keep |

4-beat transition CSV files are present, but they are CSV-only and do not have processed `labels/pose/right_rule_features` directories. They stay excluded from the current 2/3-beat model scope.

## Commands

```bash
python tools/run_right_conducting_goal.py \
  --steps cache,train,detailed,gate \
  --train-source outputs/right_conducting/recordings_staged_static80_transitions.zip \
  --dataset-dir outputs/right_conducting/dataset_v0_static80_transitions \
  --cache-dir outputs/right_conducting/motionbert_cache_static80_transitions_right_arm_only \
  --head-output-dir outputs/right_conducting/motionbert_head_static80_transitions_right_arm_only_e120_h512_lr3e3 \
  --detailed-output-prefix outputs/right_conducting/motionbert_right_arm_only_detailed \
  --gate-output-prefix outputs/right_conducting/model_gate_right_arm_only \
  --window-frames 30,45,60,90,120 \
  --stride-frames 3 \
  --devices cuda:0,cuda:1,cuda:2,cuda:3,cuda:4 \
  --parallel-gpu \
  --cache-feature-mode mean_std_delta \
  --input-mask-mode right_arm_only \
  --train-epochs 120 \
  --train-hidden-dim 512 \
  --train-lr 0.003 \
  --train-batch-size 256 \
  --cache-batch-size 128 \
  --gate-require-detailed
```

```bash
python tools/run_right_conducting_goal.py \
  --steps motionbert-devset-score,devset-gate \
  --devset-static-root dataset/static_variants_80 \
  --devset-transition-root dataset/transitions \
  --head-output-dir outputs/right_conducting/motionbert_head_static80_transitions_right_arm_only_e120_h512_lr3e3 \
  --window-frames 30,45,60,90,120 \
  --stride-frames 3 \
  --devices cuda:0,cuda:1,cuda:2,cuda:3,cuda:4 \
  --cache-feature-mode mean_std_delta \
  --input-mask-mode right_arm_only
```

## Result Summary

| window | CV tempo | old 222455 tempo | old 222455 r120 | devset margin3 tempo | devset r80 | devset r120 | devset gate |
|---:|---:|---:|---:|---:|---:|---:|---|
| 30 | 0.7478 | 0.2637 | 0.0000 | 0.9494 | 0.9675 | 0.9887 | GO |
| 45 | 0.7796 | 0.3605 | 0.0068 | 0.9955 | 0.9858 | 1.0000 | GO |
| 60 | 0.7724 | 0.3128 | 0.0000 | 0.9974 | 0.9943 | 1.0000 | GO |
| 90 | 0.7548 | 0.3380 | 0.0000 | 0.9947 | 0.9906 | 1.0000 | GO |
| 120 | 0.7297 | 0.1563 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | GO |

Interpretation:

- The right-arm-only model fits the current fixed-camera 2/3-beat staged data.
- It still fails the older independent `222455` 4-beat stress case, especially 120 BPM recall.
- Therefore this model can be exported as a handmark-only fixed-camera probe, but it does not replace the primary reference-complete MotionBERT bundle.

## Exported Probe Bundle

```text
manifest: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/motionbert_conducting_live_manifest.json
structure: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/motionbert_conducting_live_structure.md
head: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/motionbert_conducting_head.pt
input_mask_mode: right_arm_only
window_frames: 45
stride_frames: 3
```

The 45-frame probe is preferred over 60-frame for live use because it keeps about 3 seconds of context at 15fps and still passes the fixed-camera devset gate.

## Runtime Checks

| check | value | status |
|---|---:|---|
| full-backbone smoke | loads manifest/head/backbone | PASS |
| replay rows | 2247 | PASS |
| replay smoothed tempo_acc | 0.9951 | GO |
| replay smoothed gain_acc | 1.0000 | GO |
| replay smoothed false switches/min | 0.3681 | GO under 0.5 threshold |
| replay smoothed p90 delay | 0.2734s | GO |
| benchmark p90 | 12.2568ms | PASS |
| benchmark headroom | 16.3175x | PASS |

Raw handmark CSV stream without reference joints:

| case | rows | tempo classes | raw switches | smoothed switches | invalid |
|---|---:|---|---:|---:|---:|
| static80 035040 | 236 | `[1]` | 0 | 0 | 0 |
| transition 022415 | 216 | `[1, 3]` | 4 | 2 | 0 |

## Decision

Primary live model remains:

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext
```

Use it when the runtime can provide H36M17 or reference-complete handmark CSV including joints 8/9/11.

The new right-arm-only bundle is a fixed-camera handmark-only probe:

```text
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe
```

It is useful when only right shoulder / elbow / wrist are available, but the report must say that strict heldout generalization is still not proven.
