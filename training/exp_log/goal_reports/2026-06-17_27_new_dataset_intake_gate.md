# Goal Report 27 - New Dataset Intake Gate

## Purpose

사용자가 새 dataset 공급 예정이라고 했기 때문에, 추가 튜닝을 멈추고 새 데이터가 들어왔을 때 먼저 통과해야 하는 intake gate를 구현했다.

이 gate의 목적은 다음 세 가지다.

```text
1. train recording과 heldout eval recording을 세션 단위로 분리한다.
2. eval-local augmentation 산출물이 score에 섞이지 않도록 표시한다.
3. relabel 전 transition session을 scoreable로 착각하지 않게 한다.
```

## Implemented Files

```text
lib/right_conducting/dataset_intake.py
tools/audit_right_conducting_dataset_intake.py
tests/test_dataset_intake.py
```

## Current Baseline Audit

Command:

```bash
python tools/audit_right_conducting_dataset_intake.py \
  --train-roots dataset/recordings \
  --eval-roots dataset/evaluation_transitions \
  --output-json outputs/right_conducting/dataset_intake_audit.json \
  --output-md outputs/right_conducting/dataset_intake_audit.md
```

Artifacts:

```text
outputs/right_conducting/dataset_intake_audit.json
outputs/right_conducting/dataset_intake_audit.md
```

Summary:

| metric | value |
|---|---:|
| session_count | 26 |
| train_session_count | 24 |
| eval_session_count | 2 |
| missing_train_root_count | 0 |
| missing_eval_root_count | 0 |
| train_ready_count | 24 |
| eval_scoreable_count | 1 |
| eval_pending_relabel_count | 1 |

BPM target counts:

| split | 60 | 80 | 100 | 120 |
|---|---:|---:|---:|---:|
| train | 6 | 6 | 6 | 6 |
| eval | 0 | 1 | 2 | 1 |

Current decisions:

```text
dataset/recordings/*:
  train_ready: 24

dataset/evaluation_transitions/session_20260616_222455_eval:
  heldout_transition_scoreable
  BPM targets: 80 / 100 / 120
  manual_timeline.json exists
  eval-local augmentation exists but must be excluded from score

dataset/evaluation_transitions/session_20260616_215630_eval:
  heldout_transition_pending_relabel
  current labels are constant 100 BPM
  manual_timeline.json missing
  do not score yet
```

## New Dataset Intake Rule

When the supplied dataset arrives, run the same audit before any training/cache/augmentation job.

Example:

```bash
python tools/audit_right_conducting_dataset_intake.py \
  --train-roots dataset/recordings,NEW_TRAIN_ROOT \
  --eval-roots dataset/evaluation_transitions,NEW_EVAL_ROOT \
  --output-json outputs/right_conducting/dataset_intake_audit_after_supply.json \
  --output-md outputs/right_conducting/dataset_intake_audit_after_supply.md
```

Acceptance criteria:

```text
train sessions:
  decision must be train_ready
  required original artifacts must exist
  labels_frame.jsonl should contain one stable BPM target per take

heldout transition sessions:
  decision must be heldout_transition_scoreable
  required original artifacts must exist
  labels_frame.jsonl must contain at least two BPM targets
  manual_timeline.json must exist

score policy:
  score only original labels_frame.jsonl / labels_window.jsonl / pose_right_h36m_masked.npy / right_rule_features.npy
  do not score recommended_augmented_v0 / labels_tempo_augmented_15f.jsonl / tempo_augmented_15f.npy
```

## Current Decision

```text
Selected live fallback remains:
  outputs/right_conducting/selected/feature_baseline_live_v0.json

Do not select the MotionBERT target80 combo head yet.
Next real step is to register the supplied dataset, rerun this intake gate, then rerun split/train/eval gates.
```

## Verification

```bash
python -m unittest discover -s tests -p 'test_dataset_intake.py' -v
```

Result:

```text
4 tests OK
```
