# Goal Report 21: Tempo-Stretch Coverage Sanity Check

## Purpose

Report 20 showed that stable eval 80 BPM windows are closer to train 100/120 than to train 80 in the current feature space.

This report checks whether train-only tempo-stretch augmentation can fix that coverage problem before using it in model training.

Main question:

```text
If we materialize tempo-stretched train windows in memory,
do stable eval 80 BPM windows become nearest to train 80 BPM?
```

## Implementation

New files:

```text
lib/right_conducting/pose_augmentation.py
tools/diagnose_right_conducting_tempo_stretch.py
tests/test_tempo_stretch_diagnostic.py
```

The tool does not write augmented pose arrays into the dataset and does not touch validation/eval files.

It only:

```text
train original pose window
-> temporal_stretch_pose_window(...)
-> update bpm_target / tempo_class / bpm_distribution
-> compute the same 16 handcrafted features
-> compare original train vs original+stretched train against eval 80 tail
```

Eval-local augmentation remains excluded:

```text
recommended_augmented_v0/
labels_tempo_augmented_15f.jsonl
tempo_augmented_15f.npy
```

## Commands

Mild A2-style tempo-stretch:

```bash
python tools/diagnose_right_conducting_tempo_stretch.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --input-norm camera \
  --speed-scales 0.92,1.10 \
  --focus-class 1 \
  --competitor-class 2 \
  --top-k 8 \
  --output-json outputs/right_conducting/tempo_stretch_mild_80_tail_60f.json \
  --output-md outputs/right_conducting/tempo_stretch_mild_80_tail_60f.md
```

Aggressive bridge probe:

```bash
python tools/diagnose_right_conducting_tempo_stretch.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --input-norm camera \
  --speed-scales 0.80,0.667 \
  --focus-class 1 \
  --competitor-class 2 \
  --top-k 8 \
  --output-json outputs/right_conducting/tempo_stretch_bridge_80_tail_60f.json \
  --output-md outputs/right_conducting/tempo_stretch_bridge_80_tail_60f.md
```

Artifacts:

```text
outputs/right_conducting/tempo_stretch_mild_80_tail_60f.json
outputs/right_conducting/tempo_stretch_mild_80_tail_60f.md
outputs/right_conducting/tempo_stretch_bridge_80_tail_60f.json
outputs/right_conducting/tempo_stretch_bridge_80_tail_60f.md
```

## Mild Tempo-Stretch Result

Speed scales:

```text
0.92, 1.10
```

Augmentation summary:

| metric | value |
|---|---:|
| train original windows | 8006 |
| augmented windows | 15964 |
| skipped augmented windows | 48 |

Source to augmented hard-class counts:

```text
0->0: 3358
1->1: 3360
2->2: 1686
2->3: 1674
3->3: 5886
```

Important:

```text
Mild stretch creates no new 80 BPM windows from 100/120 BPM.
It mostly preserves hard class labels, except some 100 -> 120 near the upper boundary.
```

Stable eval 80 nearest train class:

| train set | nearest class counts | dist to 80 | dist to 100 | dist to 120 |
|---|---|---:|---:|---:|
| original | `{100: 8, 120: 3}` | 12.2489 | 6.9425 | 7.7321 |
| original + mild stretch | `{100: 7, 120: 4}` | 12.5453 | 7.1237 | 7.3328 |

Decision:

```text
mild tempo-stretch: NO-GO for fixing the 80 BPM tail coverage.
```

## Aggressive Bridge Probe

Speed scales:

```text
0.80, 0.667
```

This is not a recommended final augmentation policy. It is a stress test to see whether creating 80-labeled samples from faster source classes can cover the eval 80 tail.

Source to augmented hard-class counts:

```text
0->0: 3370
1->0: 3372
2->0: 1686
2->1: 1686
3->1: 2949
3->2: 2949
```

Stable eval 80 nearest train class:

| train set | nearest class counts | dist to 80 | dist to 100 | dist to 120 |
|---|---|---:|---:|---:|
| original | `{100: 8, 120: 3}` | 12.2489 | 6.9425 | 7.7321 |
| original + bridge stretch | `{100: 11}` | 9.1352 | 7.1368 | 8.3212 |

Bridge stretch moves train 80 closer to eval 80:

```text
distance to train 80: 12.2489 -> 9.1352
```

But it still fails the gate:

```text
all 11 eval 80 windows are still nearest to train 100.
```

Top remaining pulls toward 100 after bridge stretch:

| feature | class80 distance - class100 distance |
|---|---:|
| rel_elbow_y_mean | 0.6357 |
| wrist_speed_std | 0.4541 |
| wrist_speed_max | 0.4488 |
| wrist_accel_std | 0.4129 |
| rel_wrist_y_mean | 0.3892 |

Interpretation:

```text
Aggressive tempo-stretch reduces the static-pose mismatch,
but the eval 80 tail still has motion magnitude / acceleration closer to train 100.
```

## Decision

```text
tempo-stretch-only augmentation: NO-GO as the next selected training change.
```

Reason:

```text
The planned mild range does not create the missing 80 BPM coverage.
The aggressive bridge range partially helps but still leaves every stable eval 80 window nearest to train 100.
```

This means the next useful step should not be "train the same classifier with tempo-stretch and hope".

## Next Gate

Recommended next step:

```text
Report 22: focused down-transition data/label decision
```

Concrete options:

```text
1. Relabel session_20260616_215630_eval and re-run transition margin + feature distribution.
2. Add a small stable/down-transition heldout set:
   120 -> 80
   100 -> 80
   stable 80 large
3. If no new data is possible, test amplitude+tempo combined augmentation as a diagnostic only,
   but do not claim robust live 120 -> 80 control from current evidence.
```

Current selected live fallback remains:

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
```
