# Goal Report 18: Hybrid Static-Weighted Feature Classifier

## Purpose

Reports 15-17 showed two competing failures:

```text
all features:
  best stable tempo_acc
  but 80 BPM recall is 0

pose_invariant:
  can emit 80 BPM and raw reaches 120 -> 80
  but stable tempo_acc and smoothed stability collapse
```

This report tests a middle path: keep all 16 handcrafted features, but downweight the four static pose mean features in the nearest-centroid distance.

## Implementation

Added feature subsets:

```text
hybrid_static025
hybrid_static050
hybrid_static075
```

They all use the same 16 feature inputs as `all`, but apply lower distance weights to:

```text
rel_wrist_x_mean
rel_wrist_y_mean
rel_elbow_x_mean
rel_elbow_y_mean
```

Weights:

```text
hybrid_static025: static mean weight 0.25
hybrid_static050: static mean weight 0.50
hybrid_static075: static mean weight 0.75
other features: 1.00
```

Changed files:

```text
lib/right_conducting/baselines.py
lib/right_conducting/live_fallback.py
tools/evaluate_right_conducting_baselines.py
```

The exported live artifact now stores `feature_weights` in both tempo and gain model dictionaries. Legacy artifacts without this field still load with all-one weights.

## Commands

Stable heldout score:

```bash
python tools/evaluate_right_conducting_baselines.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --input-norm camera \
  --feature-subset hybrid_static050 \
  --output-json outputs/right_conducting/hybrid_static050_scores_v0_60f.json \
  --output-md outputs/right_conducting/hybrid_static050_scores_v0_60f.md
```

Export:

```bash
python tools/export_right_conducting_fallback.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --score-json outputs/right_conducting/hybrid_static050_scores_v0_60f.json \
  --output-dir outputs/right_conducting/selected_60f_hybrid_static050 \
  --artifact-name feature_baseline_live_v0_60f_hybrid_static050.json \
  --input-norm camera \
  --feature-subset hybrid_static050 \
  --switch-threshold 0.15 \
  --fast-switch-threshold 0.40 \
  --confirm-updates 2
```

Margin evaluation:

```bash
python tools/evaluate_right_conducting_transition_margins.py \
  --artifact outputs/right_conducting/selected_60f_hybrid_static050/feature_baseline_live_v0_60f_hybrid_static050.json \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --input-norm camera \
  --margins 0,0.5,1,2,3 \
  --output-json outputs/right_conducting/transition_margin_scores_222455_60f_hybrid_static050.json \
  --output-md outputs/right_conducting/transition_margin_scores_222455_60f_hybrid_static050.md
```

Summary:

```text
outputs/right_conducting/hybrid_static_report18_summary.json
```

## Stable Heldout Comparison

Evaluation:

```text
dataset/evaluation_transitions/session_20260616_222455_eval
60f regenerated windows from labels_frame.jsonl
mixed_bpm_label=True excluded
eval-local augmentation excluded
```

| candidate | cv tempo_acc | stable tempo_acc | stable bpm_mae | stable gain_acc | 80 recall | true 80 prediction counts |
|---|---:|---:|---:|---:|---:|---|
| all | 0.5152 | 0.5514 | 10.6173 | 0.7654 | 0.0000 | `{100: 8, 120: 3}` |
| pose_invariant | 0.4795 | 0.4938 | 13.0864 | 0.8189 | 0.1818 | `{80: 2, 100: 9}` |
| hybrid_static025 | 0.5059 | 0.5144 | 12.3457 | 0.8148 | 0.0000 | `{100: 11}` |
| hybrid_static050 | 0.5124 | 0.5226 | 11.9342 | 0.8025 | 0.0000 | `{100: 10, 120: 1}` |
| hybrid_static075 | 0.5137 | 0.5226 | 11.5226 | 0.7860 | 0.0000 | `{100: 9, 120: 2}` |

Interpretation:

```text
hybrid_static050/075 recover some stable tempo score compared with pose_invariant.
But neither recovers 80 BPM recall.
The 120 -> 80 failure remains.
```

## Streaming Replay

Full replay on regenerated 60f windows:

| candidate | raw tempo_acc | raw false/min | raw reached | raw missed | smoothed tempo_acc | smoothed false/min | smoothed reached | smoothed missed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 0.4982 | 17.1243 | 1 | 1 | 0.4698 | 4.2811 | 1 | 1 |
| pose_invariant | 0.4484 | 14.9837 | 2 | 0 | 0.3203 | 5.3513 | 1 | 1 |
| hybrid_static025 | 0.4698 | 18.1945 | 1 | 1 | 0.3523 | 4.2811 | 1 | 1 |
| hybrid_static050 | 0.4733 | 18.1945 | 1 | 1 | 0.3630 | 6.4216 | 1 | 1 |
| hybrid_static075 | 0.4769 | 12.8432 | 1 | 1 | 0.3915 | 6.4216 | 1 | 1 |

Interpretation:

```text
hybrid_static075 reduces raw false switches, but it still misses the 120 -> 80 switch.
smoothed false switches exceed 5/min for hybrid_static050/075.
No hybrid candidate satisfies the live gate.
```

## Decision

```text
hybrid_static feature weighting: NO-GO as selected live model.
```

Reason:

```text
The weighted hybrid variants improve over pose_invariant on stable tempo_acc,
but they do not recover 80 BPM recall and still miss the 120 -> 80 transition in full replay.
```

Keep selected live fallback:

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
feature_subset: all
```

Keep hybrid artifacts as ablation outputs:

```text
outputs/right_conducting/selected_60f_hybrid_static025/feature_baseline_live_v0_60f_hybrid_static025.json
outputs/right_conducting/selected_60f_hybrid_static050/feature_baseline_live_v0_60f_hybrid_static050.json
outputs/right_conducting/selected_60f_hybrid_static075/feature_baseline_live_v0_60f_hybrid_static075.json
```

## Next Step

Smoothing-only and static-weight-only changes are exhausted for this failure.

Next model step should use a classifier that can learn class-specific boundaries instead of nearest centroid:

```text
candidate:
  standardized logistic/ridge classifier on 16 pose features
  class-balanced tempo loss or class weights
  train-only temporal/amplitude augmentation retained
  evaluate with transition-margin table and full replay

gate:
  stable 80 recall > 0
  raw reached true switches 2/2
  smoothed false_switches_per_min <= 5
  stable tempo_acc >= 0.52
```
