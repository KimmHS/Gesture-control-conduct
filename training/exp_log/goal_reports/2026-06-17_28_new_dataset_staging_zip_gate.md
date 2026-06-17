# Goal Report 28 - New Dataset Staging Zip Gate

## Purpose

새 dataset이 root folder 형태로 공급될 예정이므로, 기존 학습 코드가 기대하는 `recordings.zip` 포맷으로 안전하게 staging하는 gate를 추가했다.

현재 cache/train/eval 도구들은 `source_pose_path`를 zip 내부 경로로 읽는다. 그래서 모든 소비자 코드를 root path 기반으로 바꾸기보다, 새 train root들을 canonical recordings zip으로 합치는 쪽이 더 작고 재현 가능하다.

## Implemented Files

```text
lib/right_conducting/dataset_staging.py
tools/build_right_conducting_recordings_zip.py
tests/test_dataset_staging.py
```

## Staging Policy

Staged zip에 넣는 파일:

```text
meta.json
pose_right_h36m_masked.npy
labels_frame.jsonl
labels_window.jsonl
right_rule_features.npy
pose_17_h36m.npy
pose_33_mediapipe.npy
right_arm_3joints.npy
```

Staged zip에 넣지 않는 파일:

```text
raw_video.mp4
recommended_augmented_v0/
labels_tempo_augmented_15f.jsonl
tempo_augmented_15f.npy
```

Failure conditions:

```text
missing train root -> fail
non-train_ready session -> fail by default
duplicate take id across roots -> fail
no train_ready session -> fail
```

## Current Workspace Smoke

Build current staged zip:

```bash
python tools/build_right_conducting_recordings_zip.py \
  --train-roots dataset/recordings \
  --output-zip outputs/right_conducting/recordings_staged_current.zip \
  --output-json outputs/right_conducting/recordings_staged_current_manifest.json
```

Result:

| metric | value |
|---|---:|
| take_count | 24 |
| 60 BPM takes | 6 |
| 80 BPM takes | 6 |
| 100 BPM takes | 6 |
| 120 BPM takes | 6 |

Prepare from staged zip:

```bash
python tools/prepare_right_conducting_dataset.py \
  --zip outputs/right_conducting/recordings_staged_current.zip \
  --output-dir outputs/right_conducting/dataset_v0_60f_staged_current \
  --window-frames 60 \
  --stride-frames 3 \
  --folds 3 \
  --augment-copies 0
```

Prepare result:

| metric | value |
|---|---:|
| take_count | 24 |
| window_count | 8006 |
| fold_count | 3 |
| fold_0 train_original | 5318 |
| fold_0 val_original | 2688 |
| fold_1 train_original | 5335 |
| fold_1 val_original | 2671 |
| fold_2 train_original | 5359 |
| fold_2 val_original | 2647 |

Artifacts:

```text
outputs/right_conducting/recordings_staged_current.zip
outputs/right_conducting/recordings_staged_current_manifest.json
outputs/right_conducting/dataset_v0_60f_staged_current/manifest.json
```

## New Dataset Command Sequence

When supplied data arrives:

```bash
python tools/audit_right_conducting_dataset_intake.py \
  --train-roots dataset/recordings,NEW_TRAIN_ROOT \
  --eval-roots dataset/evaluation_transitions,NEW_EVAL_ROOT \
  --output-json outputs/right_conducting/dataset_intake_audit_after_supply.json \
  --output-md outputs/right_conducting/dataset_intake_audit_after_supply.md
```

Then stage train roots:

```bash
python tools/build_right_conducting_recordings_zip.py \
  --train-roots dataset/recordings,NEW_TRAIN_ROOT \
  --output-zip outputs/right_conducting/recordings_staged_after_supply.zip \
  --output-json outputs/right_conducting/recordings_staged_after_supply_manifest.json
```

Then prepare windows/folds:

```bash
python tools/prepare_right_conducting_dataset.py \
  --zip outputs/right_conducting/recordings_staged_after_supply.zip \
  --output-dir outputs/right_conducting/dataset_v0_60f_after_supply \
  --window-frames 60 \
  --stride-frames 3 \
  --folds 3 \
  --augment-copies 5
```

Training/evaluation commands should then point to:

```text
--zip outputs/right_conducting/recordings_staged_after_supply.zip
--dataset-dir outputs/right_conducting/dataset_v0_60f_after_supply
```

## Current Decision

```text
New-data intake gate: GO
New-data staging zip gate: GO
Current selected live fallback remains unchanged.
Do not tune further on the single current transition eval before registering supplied data.
```

## Verification

```bash
python -m unittest discover -s tests -p 'test_dataset_staging.py' -v
python tools/build_right_conducting_recordings_zip.py --train-roots dataset/recordings ...
python tools/prepare_right_conducting_dataset.py --zip outputs/right_conducting/recordings_staged_current.zip ...
```

Result:

```text
3 staging tests OK
current staged zip build OK
prepare from staged zip OK
```
