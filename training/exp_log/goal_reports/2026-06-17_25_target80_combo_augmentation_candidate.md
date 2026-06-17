# Goal Report 25: Target-80 Tempo + Amplitude Augmentation Candidate

## Purpose

Report 21 showed that tempo-stretch alone moves the eval 80 BPM tail closer to train 80, but not enough.
The stable eval 80 windows were still nearest to train 100.

This report tests a narrower train-only augmentation:

```text
temporal speed_scale: 0.80, 0.667
amplitude_scale: 1.15, 1.30
keep only augmented windows whose new tempo_class is 1 / 80 BPM
```

The goal is not to claim a final model from one eval session.
The goal is to check whether targeted label-changing augmentation can recover the missed `120 -> 80` down-transition without using eval-local augmented files.

## Implementation

New code:

```text
lib/right_conducting/pose_augmentation.py
  amplitude_scale_pose_window
  amplitude_scale_label

tools/diagnose_right_conducting_combo_augmentation.py
tools/evaluate_right_conducting_combo_aug_baseline.py
tests/test_tempo_stretch_diagnostic.py
```

The evaluation continues to use only original eval artifacts:

```text
labels_frame.jsonl
labels_window.jsonl
pose_right_h36m_masked.npy
right_rule_features.npy
```

Eval-local augmentation remains excluded:

```text
recommended_augmented_v0/
labels_tempo_augmented_15f.jsonl
tempo_augmented_15f.npy
```

## Commands

Coverage diagnosis, all generated classes:

```bash
python tools/diagnose_right_conducting_combo_augmentation.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --input-norm camera \
  --speed-scales 0.80,0.667 \
  --amplitude-scales 1.15,1.30 \
  --output-json outputs/right_conducting/combo_aug_bridge_80_tail_60f.json \
  --output-md outputs/right_conducting/combo_aug_bridge_80_tail_60f.md
```

Coverage diagnosis, target 80 only:

```bash
python tools/diagnose_right_conducting_combo_augmentation.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --input-norm camera \
  --speed-scales 0.80,0.667 \
  --amplitude-scales 1.15,1.30 \
  --augmented-target-classes 1 \
  --output-json outputs/right_conducting/combo_aug_bridge_target80_tail_60f.json \
  --output-md outputs/right_conducting/combo_aug_bridge_target80_tail_60f.md
```

Offline feature-baseline candidate:

```bash
python tools/evaluate_right_conducting_combo_aug_baseline.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --input-norm camera \
  --speed-scales 0.80,0.667 \
  --amplitude-scales 1.15,1.30 \
  --augmented-target-classes 1 \
  --output-artifact outputs/right_conducting/selected_60f_target80_combo_aug/feature_baseline_target80_combo_aug_60f.json \
  --output-json outputs/right_conducting/combo_aug_baseline_target80_60f.json \
  --output-md outputs/right_conducting/combo_aug_baseline_target80_60f.md
```

Full replay:

```bash
python tools/replay_right_conducting_stream.py \
  --artifact outputs/right_conducting/selected_60f_target80_combo_aug/feature_baseline_target80_combo_aug_60f.json \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --input-norm camera \
  --switch-threshold 0.15 \
  --fast-switch-threshold 0.40 \
  --confirm-updates 2 \
  --output-json outputs/right_conducting/stream_replay_222455_60f_target80_combo_aug.json \
  --output-md outputs/right_conducting/stream_replay_222455_60f_target80_combo_aug.md \
  --output-rows outputs/right_conducting/stream_replay_222455_60f_target80_combo_aug_rows.jsonl
```

## Artifacts

```text
outputs/right_conducting/combo_aug_bridge_80_tail_60f.json
outputs/right_conducting/combo_aug_bridge_80_tail_60f.md
outputs/right_conducting/combo_aug_bridge_target80_tail_60f.json
outputs/right_conducting/combo_aug_bridge_target80_tail_60f.md
outputs/right_conducting/combo_aug_baseline_target80_60f.json
outputs/right_conducting/combo_aug_baseline_target80_60f.md
outputs/right_conducting/selected_60f_target80_combo_aug/feature_baseline_target80_combo_aug_60f.json
outputs/right_conducting/stream_replay_222455_60f_target80_combo_aug_analysis.json
outputs/right_conducting/stream_replay_222455_60f_target80_combo_aug_swept_analysis.json
outputs/right_conducting/transition_margin_scores_222455_60f_target80_combo_aug.json
outputs/right_conducting/transition_margin_scores_222455_60f_target80_combo_aug.md
```

## Coverage Result

Stable eval 80 tail has 11 windows.

| train set | added windows | nearest train class counts | dist to 80 | dist to 100 |
|---|---:|---|---:|---:|
| original | 0 | `{100: 8, 120: 3}` | 12.2489 | 6.9425 |
| combo all generated classes | 32024 | `{100: 11}` | 4.0370 | 3.0525 |
| combo target 80 only | 9270 | `{80: 9, 120: 2}` | 4.1749 | 4.8357 |

Interpretation:

```text
Targeted tempo + amplitude augmentation is the first augmentation probe that moves most eval 80 tail windows nearest to train 80.
Adding all generated classes moves class 100 too, so it does not recover nearest-class behavior.
```

## Offline Score

Eval set:

```text
session_20260616_222455_eval
60f regenerated stable windows
sample_count: 243
```

| model | tempo_acc | macro_f1 | bpm_mae | 80_recall | true 80 predictions |
|---|---:|---:|---:|---:|---|
| original feature baseline | 0.5514 | 0.2885 | 10.6173 | 0.0000 | `{100: 8, 120: 3}` |
| target80 combo feature baseline | 0.5638 | 0.3837 | 11.1934 | 0.8182 | `{80: 9, 120: 2}` |

Tradeoff:

```text
80 recall recovers strongly.
Overall tempo_acc improves slightly.
BPM MAE gets worse because true 100 BPM windows are over-predicted as 80 BPM.
```

True 100 predictions for target80 combo:

```text
{60: 8, 80: 25, 100: 33, 120: 25}
```

## Margin Sweep

| margin_s | sample_count | tempo_acc | bpm_mae | 80_support | 80_recall |
|---:|---:|---:|---:|---:|---:|
| 0.0 | 243 | 0.5638 | 11.1934 | 11 | 0.8182 |
| 0.5 | 231 | 0.5628 | 11.3420 | 8 | 0.7500 |
| 1.0 | 223 | 0.5695 | 11.2108 | 6 | 0.8333 |
| 2.0 | 203 | 0.5665 | 11.4286 | 1 | 1.0000 |
| 3.0 | 187 | 0.5455 | 12.0856 | 0 | 0.0000 |

Unlike the original fallback, margin filtering is not what creates 80 recall.
The target80 combo candidate still predicts 80 in stable tail windows.

## Replay Result

Policy:

```text
switch_threshold: 0.15
fast_switch_threshold: 0.40
confirm_updates: 2
```

| metric | value |
|---|---:|
| raw_reached_count | 2 |
| raw_missed_count | 0 |
| raw_delay_p90_s | 2.0210 |
| smoothed_reached_count | 2 |
| smoothed_missed_count | 0 |
| smoothed_delay_p90_s | 6.3632 |
| smoothed false_switches_per_min | 6.4216 |

Switch breakdown:

| switch | raw_delay_s | smoothed_delay_s |
|---|---:|---:|
| 100 -> 120 | 2.2010 | 6.8033 |
| 120 -> 80 | 0.4006 | 2.4020 |

Policy sweep selected:

```text
switch_threshold: 0.25
fast_switch_threshold: 0.40
confirm_updates: 4
false_switches_per_min: 2.1405
```

But detailed replay analysis shows this is not a clean live fix:

```text
100 -> 120 was already at target before the switch.
120 -> 80 was missed after smoothing.
```

## Decision

GO:

```text
targeted tempo + amplitude augmentation is a useful direction for recovering 80 BPM coverage.
raw classifier reaches both transitions on the current scoreable eval session.
```

NO-GO:

```text
Do not replace selected live fallback yet.
The candidate increases 100 -> 80 false predictions and worsens BPM MAE.
The policy that reduces false switches misses the 120 -> 80 smoothed transition.
```

Selected live fallback remains:

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
```

Diagnostic candidate artifact:

```text
outputs/right_conducting/selected_60f_target80_combo_aug/feature_baseline_target80_combo_aug_60f.json
```

## Next Gate

Recommended next step:

```text
Turn target80 combo augmentation into a train-only option for a stronger model candidate,
but add a regularization/selection gate that prevents true 100 BPM from collapsing into 80 BPM.
```

Concrete candidates:

```text
1. Train MotionBERT/TCN head with target80 combo augmentation and soft BPM distribution.
2. Add class-conditional augmentation weights instead of adding all generated target80 samples equally.
3. Require simultaneous gates:
   80_recall > 0.5
   bpm_mae_window <= original fallback
   smoothed false_switches_per_min <= 4.5
   smoothed reaches 120 -> 80 in full replay
```
