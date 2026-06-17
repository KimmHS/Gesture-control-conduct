# Goal Report 26: MotionBERT Head With Target-80 Combo Augmentation

## Purpose

Report 25 showed that target-80 tempo + amplitude augmentation recovered stable eval 80 BPM coverage for the handcrafted feature baseline, but it was not clean enough to become the selected live fallback.

This report moves that same augmentation into the MotionBERT-Lite frozen-head path:

```text
original 60f pose windows
-> target80 combo pose augmentation
-> MotionBERT-Lite frozen encoder
-> mean_std_delta right-arm features
-> cached conducting head training
```

The acceptance gate is stricter than CV:

```text
80_recall > 0.5
bpm_mae_window <= selected feature fallback
smoothed false_switches_per_min <= 4.5
smoothed reaches 120 -> 80 in full replay
```

Because a new dataset is expected, this report is the pre-new-data baseline and rerun recipe.

## Implementation

New/updated files:

```text
tools/cache_motionbert_combo_aug_features.py
tools/evaluate_motionbert_head_detailed.py
tools/train_motionbert_conducting_head.py
tests/test_train_motionbert_head_cli.py
```

Train-only leakage control:

```text
extra augmented rows have source_sample_id
fold training includes only augmented rows whose source_sample_id is in that fold's train split
validation and eval use original windows only
```

Subsample control:

```text
--extra-sample-stride 1   # all target80 combo rows
--extra-sample-stride 3   # about one third
--extra-sample-stride 10  # about one tenth
```

## Cache Command

```bash
python tools/cache_motionbert_combo_aug_features.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --device cuda:0 \
  --batch-size 128 \
  --feature-mode mean_std_delta \
  --speed-scales 0.80,0.667 \
  --amplitude-scales 1.15,1.30 \
  --augmented-target-classes 1 \
  --output-dir outputs/right_conducting/motionbert_cache_v0_60f_stats_target80_combo
```

Cache artifact:

```text
outputs/right_conducting/motionbert_cache_v0_60f_stats_target80_combo/
```

Cache summary:

| metric | value |
|---|---:|
| feature rows | 9270 |
| feature dim | 2048 |
| skipped windows | 0 |
| filtered non-target windows | 22754 |

## Training Commands

Full target80 combo:

```bash
python tools/train_motionbert_conducting_head.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --cache-dir outputs/right_conducting/motionbert_cache_v0_60f_stats \
  --extra-cache-dir outputs/right_conducting/motionbert_cache_v0_60f_stats_target80_combo \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --device cuda:0 \
  --epochs 80 \
  --batch-size 256 \
  --lr 1e-3 \
  --hidden-dim 512 \
  --feature-mode mean_std_delta \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --output-dir outputs/right_conducting/motionbert_head_v0_60f_stats_target80_combo_e80_h512_eval60stable
```

Stride 3:

```bash
python tools/train_motionbert_conducting_head.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --cache-dir outputs/right_conducting/motionbert_cache_v0_60f_stats \
  --extra-cache-dir outputs/right_conducting/motionbert_cache_v0_60f_stats_target80_combo \
  --extra-sample-stride 3 \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --device cuda:0 \
  --epochs 80 \
  --batch-size 256 \
  --lr 1e-3 \
  --hidden-dim 512 \
  --feature-mode mean_std_delta \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --output-dir outputs/right_conducting/motionbert_head_v0_60f_stats_target80_combo_stride3_e80_h512_eval60stable
```

Stride 10:

```bash
python tools/train_motionbert_conducting_head.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --cache-dir outputs/right_conducting/motionbert_cache_v0_60f_stats \
  --extra-cache-dir outputs/right_conducting/motionbert_cache_v0_60f_stats_target80_combo \
  --extra-sample-stride 10 \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --device cuda:0 \
  --epochs 80 \
  --batch-size 256 \
  --lr 1e-3 \
  --hidden-dim 512 \
  --feature-mode mean_std_delta \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --output-dir outputs/right_conducting/motionbert_head_v0_60f_stats_target80_combo_stride10_e80_h512_eval60stable
```

## Detailed Eval Artifacts

```text
outputs/right_conducting/motionbert_stats_head_eval60stable_detailed.json
outputs/right_conducting/motionbert_stats_target80_combo_eval60stable_detailed.json
outputs/right_conducting/motionbert_stats_target80_combo_stride3_eval60stable_detailed.json
outputs/right_conducting/motionbert_stats_target80_combo_stride10_eval60stable_detailed.json
```

## CV Result

| model | extra rows all-train | cv tempo_acc | cv bpm_mae |
|---|---:|---:|---:|
| original stats head | 0 | 0.7178 | 7.5933 |
| target80 combo full | 9270 | 0.7509 | 6.6628 |
| target80 combo stride3 | 3090 | 0.7497 | 6.6357 |
| target80 combo stride10 | 927 | 0.7553 | 6.6790 |

CV improves, but CV is within-subject/take-level and is not the acceptance gate.

## Stable Transition Eval

Eval set:

```text
session_20260616_222455_eval
60f regenerated stable windows
sample_count: 243
```

| model | tempo_acc | macro_f1 | bpm_mae | 80_recall | 100_recall | 120_recall | gain_acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| original stats head | 0.3128 | 0.1767 | 20.5761 | 0.3636 | 0.7912 | 0.0000 | 0.7901 |
| target80 combo full | 0.3128 | 0.1910 | 18.2716 | 0.8182 | 0.6923 | 0.0284 | 0.8066 |
| target80 combo stride3 | 0.3539 | 0.2085 | 16.2140 | 0.8182 | 0.8242 | 0.0142 | 0.7984 |
| target80 combo stride10 | 0.3169 | 0.1930 | 19.3416 | 0.8182 | 0.7253 | 0.0142 | 0.8683 |

Reference selected feature fallback:

| model | tempo_acc | bpm_mae | 80_recall | 120_recall |
|---|---:|---:|---:|---:|
| selected feature fallback | 0.5514 | 10.6173 | 0.0000 | 0.6028 |
| target80 combo feature diagnostic | 0.5638 | 11.1934 | 0.8182 | 0.6738 |

## Prediction Counts

Original stats head:

```json
{
  "80": {"60": 7, "80": 4},
  "100": {"60": 5, "80": 14, "100": 72},
  "120": {"60": 4, "80": 70, "100": 67}
}
```

Target80 combo stride3:

```json
{
  "80": {"60": 2, "80": 9},
  "100": {"80": 15, "100": 75, "120": 1},
  "120": {"80": 40, "100": 99, "120": 2}
}
```

Interpretation:

```text
MotionBERT target80 combo successfully creates 80 BPM recall,
but it collapses most true 120 BPM windows into 80/100.
This fails the stability requirement for live tempo control.
```

## Decision

GO:

```text
MotionBERT target80 combo cache/training pipeline is implemented and reproducible.
The augmentation reliably recovers 80 BPM recall on this scoreable eval session.
```

NO-GO:

```text
Do not export this MotionBERT target80 combo head as the live model.
It does not beat the selected feature fallback on transition_eval_222455_60f_stable.
It fails bpm_mae and 120_recall gates.
```

Selected live fallback remains:

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
```

## New Dataset Gate

The user noted that more dataset is expected.
When it arrives, do not tune further on `222455_eval` first.

Run this sequence:

```text
1. Register new dataset/takes in docs/reference/CURRENT_DATA.md.
2. Decide split before training: train vs heldout.
3. Regenerate 60f dataset windows.
4. Regenerate MotionBERT original cache.
5. Regenerate target80 combo cache if 80 tail remains under-covered.
6. Rerun original head, target80 combo stride3, and selected feature fallback.
```

Pass line for the next data update:

```text
tempo_acc >= selected feature fallback
bpm_mae_window <= selected feature fallback
80_recall >= 0.5
120_recall >= 0.5
smoothed false_switches_per_min <= 4.5
smoothed reaches 120 -> 80
```
