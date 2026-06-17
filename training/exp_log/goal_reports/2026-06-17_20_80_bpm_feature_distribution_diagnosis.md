# Goal Report 20: 80 BPM Feature Distribution Diagnosis

## Purpose

Reports 17-19 show the same failure from three angles:

```text
stable 80 BPM tail in session_20260616_222455_eval is not classified as 80 BPM.
```

This report checks whether the failure is due to simple class imbalance or a feature-space/domain mismatch.

Main question:

```text
Are stable eval 80 BPM windows actually closer to train 80 BPM,
or are they closer to train 100/120 BPM in the current feature space?
```

## Implementation

New files:

```text
lib/right_conducting/feature_distribution.py
tools/diagnose_right_conducting_feature_distribution.py
tests/test_feature_distribution_diagnostics.py
```

The diagnostic uses the same 16 handcrafted right-arm features as the selected fallback:

```text
pose_right_h36m_masked.npy
-> pose_window_features(...)
-> train class centroids in standardized feature space
-> eval focus-class nearest train class check
```

This is not a new model candidate. It is a failure diagnosis before returning to augmentation/data steps.

## Command

```bash
python tools/diagnose_right_conducting_feature_distribution.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --input-norm camera \
  --focus-class 1 \
  --competitor-class 2 \
  --top-k 10 \
  --output-json outputs/right_conducting/feature_distribution_80_tail_60f.json \
  --output-md outputs/right_conducting/feature_distribution_80_tail_60f.md
```

Artifacts:

```text
outputs/right_conducting/feature_distribution_80_tail_60f.json
outputs/right_conducting/feature_distribution_80_tail_60f.md
```

## Data Used

Train:

```text
outputs/right_conducting/dataset_v0_60f/windows_60f_v0.jsonl
dataset/recordings.zip
aug_type == original only
```

Eval:

```text
dataset/evaluation_transitions/session_20260616_222455_eval
labels_frame.jsonl
pose_right_h36m_masked.npy
stable windows only
```

Excluded eval-local augmentation:

```text
recommended_augmented_v0/
labels_tempo_augmented_15f.jsonl
tempo_augmented_15f.npy
```

`session_20260616_215630_eval` is still excluded.

## Class Counts

Class mapping:

```text
0: 60 BPM
1: 80 BPM
2: 100 BPM
3: 120 BPM
```

| split | class 0 | class 1 | class 2 | class 3 |
|---|---:|---:|---:|---:|
| train original 60f | 1685 | 1686 | 1686 | 2949 |
| eval 222455 stable 60f | 0 | 11 | 91 | 141 |

Interpretation:

```text
The train set is not missing 80 BPM.
The eval set has very little stable 80 BPM evidence: only 11 windows.
```

## Focus 80 BPM Nearest Train Class

For the 11 stable eval 80 BPM windows:

| metric | value |
|---|---|
| nearest train class counts | `{100 BPM: 8, 120 BPM: 3}` |
| mean distance to train 60 | 13.9402 |
| mean distance to train 80 | 12.2489 |
| mean distance to train 100 | 6.9425 |
| mean distance to train 120 | 7.7321 |

Key result:

```text
Every stable eval 80 BPM window is closer to train 100/120 than to train 80.
```

This explains why class-balanced ridge did not recover the tail. The issue is not only class count; the eval 80 motion lives in the wrong region of the current feature space.

## Top 80 BPM Feature Shifts

Largest eval-80 shift from train-80, measured in train pooled standard-deviation units:

| feature | train 80 mean | eval 80 mean | pooled z shift |
|---|---:|---:|---:|
| rel_elbow_y_mean | 0.1423 | 0.2297 | 2.1133 |
| rel_wrist_y_mean | -0.1315 | -0.0391 | 1.6488 |
| rel_wrist_x_mean | 0.0858 | 0.0485 | -1.2408 |
| rel_elbow_x_mean | 0.1310 | 0.1476 | 0.8289 |
| rel_wrist_y_std | 0.1606 | 0.2101 | 0.7875 |
| rel_wrist_x_std | 0.0520 | 0.0745 | 0.6657 |
| wrist_speed_max | 1.9400 | 2.4964 | 0.5296 |
| wrist_speed_std | 0.5181 | 0.6453 | 0.4934 |

## Features Pulling Eval 80 Toward Train 100

Positive value means the eval 80 mean is closer to the train 100 centroid than to the train 80 centroid on that feature.

| feature | class1 distance - class2 distance |
|---|---:|
| rel_elbow_y_mean | 2.8356 |
| rel_wrist_y_mean | 1.6392 |
| rel_wrist_x_mean | 0.6732 |
| wrist_speed_max | 0.2462 |
| wrist_speed_std | 0.2192 |
| shoulder_wrist_radius_std | 0.1346 |
| wrist_accel_std | 0.0625 |

Interpretation:

```text
Static arm placement still dominates the 80 BPM tail failure.
Motion magnitude features also move toward faster classes, so just dropping static mean features is not enough.
```

This matches Reports 16 and 18:

```text
pose_invariant recovered only 2 / 11 stable 80 windows and hurt overall tempo_acc.
hybrid static weighting did not recover stable 80 recall.
```

## Decision

```text
More classifier-only changes on the same current feature space are low ROI.
Return to data/augmentation/label-side work.
```

Reason:

```text
The train set has 1686 original 80 BPM windows,
but the eval 80 tail is closer to train 100/120 in the selected feature space.
This is a domain/coverage problem, not just a class imbalance problem.
```

## Next Gate

Recommended next step:

```text
Report 21: tempo-stretch augmentation sanity check
```

Acceptance line:

```text
GO only if train-only tempo-stretch creates realistic 80 BPM-like feature coverage
without leaking eval-local augmented files or mixing augmented windows into validation/test.
```

If tempo-stretch does not move eval-80 nearest-class behavior:

```text
collect/relabel more heldout down-transition data:
  120 -> 80
  100 -> 80
  120 -> 60
```
