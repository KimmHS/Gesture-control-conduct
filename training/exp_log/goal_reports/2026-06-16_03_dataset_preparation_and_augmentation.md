# Goal Report 03: Dataset Preparation and Augmentation

Date: 2026-06-16  
Scope: Report 02에서 발견한 `120f ~= 8s`, 6-bin label artifact 문제를 피하기 위해 current v0용 `60f / stride3` dataset manifest를 새로 생성하고, train-only augmentation을 5배 이상으로 확장했다.

## 1. Implemented Files

| File | Role |
|---|---|
| `lib/right_conducting/dataset_prep.py` | 4-bin BPM soft label, 60f window label, take-level folds, train-only augmentation sample manifest 생성 |
| `tools/prepare_right_conducting_dataset.py` | `dataset/recordings.zip`을 읽어 output manifest를 생성하는 CLI |
| `tests/test_right_conducting_dataset_prep.py` | label/window/fold/augmentation invariants |
| `tests/test_prepare_right_conducting_dataset_cli.py` | CLI import/help smoke test |

TDD sequence:

```text
1. dataset_prep tests 작성
2. RED 확인: lib.right_conducting module missing
3. dataset_prep 구현
4. GREEN 확인
5. CLI smoke test 작성
6. RED 확인: tools/ script import path failure
7. CLI import path 수정
8. GREEN 확인
```

## 2. Generated Dataset Artifact

Command:

```bash
python tools/prepare_right_conducting_dataset.py \
  --zip dataset/recordings.zip \
  --output-dir outputs/right_conducting/dataset_v0_60f \
  --window-frames 60 \
  --stride-frames 3 \
  --folds 3 \
  --augment-copies 5 \
  --seed 42
```

Output root:

```text
outputs/right_conducting/dataset_v0_60f/
```

Files:

```text
manifest.json
takes.jsonl
windows_60f_v0.jsonl
folds.json
fold_0/train_samples.jsonl
fold_0/val_samples.jsonl
fold_1/train_samples.jsonl
fold_1/val_samples.jsonl
fold_2/train_samples.jsonl
fold_2/val_samples.jsonl
```

This stage uses virtual augmentation. It does not duplicate pose arrays on disk. Each augmented row records `source_sample_id`, `aug_type`, seed, and label updates. The training loader must apply the recipe when loading the source window.

## 3. Manifest Result

From `outputs/right_conducting/dataset_v0_60f/manifest.json`:

| Field | Value |
|---|---:|
| take_count | 24 |
| window_frames | 60 |
| stride_frames | 3 |
| bpm_bins | `[60, 80, 100, 120]` |
| original window_count | 8,006 |
| fold_count | 3 |
| augment copies per train window | 5 |

Fold summary:

| Fold | Train original | Train augmented | Train total | Val original | Val augmented | Aug ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 5,318 | 26,590 | 31,908 | 2,688 | 0 | 5.0 |
| 1 | 5,335 | 26,675 | 32,010 | 2,671 | 0 | 5.0 |
| 2 | 5,359 | 26,795 | 32,154 | 2,647 | 0 | 5.0 |

Pass line:

```text
train augmented samples >= 5x train original: PASS
validation augmented samples == 0: PASS
tempo distribution length == 4: PASS
```

## 4. Label Distribution

Original 60f windows:

| Label | Count |
|---|---:|
| tempo_class 0 / 60 BPM | 1,685 |
| tempo_class 1 / 80 BPM | 1,686 |
| tempo_class 2 / 100 BPM | 1,686 |
| tempo_class 3 / 120 BPM | 2,949 |

Gain labels:

| Gain | Count |
|---|---:|
| large | 4,635 |
| small | 3,371 |

Notes:

```text
Tempo take counts are balanced, but window counts are not.
The 120 BPM class is larger because early 120 BPM recordings are longer.
Score reports must include per-take aggregation, not only window mean.
```

## 5. Augmentation Recipes

Each train original window receives one copy of each recipe:

| aug_type | Label effect |
|---|---|
| `coordinate_jitter` | label-preserving |
| `confidence_dropout` | label-preserving |
| `small_affine` | label-preserving |
| `temporal_stretch` | updates `bpm_target`, `tempo_class`, `bpm_distribution` |
| `amplitude_scaling` | updates `dynamics_value`, `gain_class`, `gain_label` |

Temporal stretch definition is now fixed:

```text
time_scale > 1.0 means faster apparent motion
bpm_aug = bpm_original * time_scale
```

Safe boundary policy:

```text
60 BPM windows use time_scale 1.05
120 BPM windows use time_scale 0.95
middle BPM windows may use 0.95 or 1.05
nearest class is computed over [60, 80, 100, 120]
```

## 6. Verification Commands

Unit tests:

```bash
python tests/test_right_conducting_dataset_prep.py -v
python tests/test_prepare_right_conducting_dataset_cli.py -v
```

Dataset generation:

```bash
python tools/prepare_right_conducting_dataset.py \
  --zip dataset/recordings.zip \
  --output-dir outputs/right_conducting/dataset_v0_60f \
  --window-frames 60 \
  --stride-frames 3 \
  --folds 3 \
  --augment-copies 5 \
  --seed 42
```

Manifest invariant check:

```text
for each fold:
  train_augmented >= 5 * train_original
  val_augmented == 0
```

Fold aug type check:

```text
fold_0: each aug_type count = 5318
fold_1: each aug_type count = 5335
fold_2: each aug_type count = 5359
```

## 7. Current Limitations

This stage prepares labels and virtual augmentation recipes only. It does not yet:

```text
materialize augmented pose arrays
train rule/feature/MotionBERT models
write score rows
export final model checkpoint
run streaming replay
```

This is intentional. The next stage should consume this manifest and produce baseline scores before MotionBERT training.

## 8. Next Step

Goal Report 04 should cover baseline training/evaluation.

Minimum next deliverables:

```text
rule_based baseline over fold val and 222455_eval
feature_baseline using right_rule_features or simple window pose features
right_hand_conducting_scores.md updated with real rows
no use of 215630_eval until relabel
```
