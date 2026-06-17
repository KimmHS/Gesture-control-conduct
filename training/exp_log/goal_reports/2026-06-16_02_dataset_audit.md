# Goal Report 02: Dataset Audit

Date: 2026-06-16  
Scope: `dataset/recordings.zip`와 current transition eval set을 실제 파일 기준으로 점검.

## 1. Summary

현재 training recording 자체는 v0 실험을 시작할 수 있는 형태다. 다만 기존 `labels_window.jsonl`은 `120f / stride6` 기반이라 현재 15fps 데이터에서는 약 8초 window다. Goal 구현의 기본값인 `60f / stride3` 약 4초 window는 새로 생성해야 한다.

Decision:

```text
direct training on current labels_window.jsonl: NO-GO for v0 default
dataset relabel/window regeneration: REQUIRED
augmentation generation: after regenerated train split only
eval scoring: only original labels_window/pose/rule_features, never eval-local augmentation
```

## 2. Training Zip Audit

Command evidence:

```text
source: dataset/recordings.zip
sessions with meta.json: 24
csv-only/no-meta sessions inside zip: 0
```

Take-level distribution from `meta.json`:

| Field | Counts |
|---|---|
| BPM | `60: 6`, `80: 6`, `100: 6`, `120: 6` |
| dynamics prompt | `large: 12`, `small: 12` |
| meter | `2: 8`, `3: 8`, `4: 8` |

Window counts:

| Window policy | Count | Meaning |
|---|---:|---|
| existing `labels_window.jsonl` | 3,773 | `120f / stride6`, about 8s at current 15fps |
| possible `60f / stride3` | 8,006 | target v0 default, about 4s |
| possible `120f / stride6` | 3,773 | matches existing labels |

Important imbalance:

```text
Take counts are balanced by BPM.
Window counts are not fully balanced because early 120 BPM recordings are longer.
Per-take aggregation is required in score reports.
```

## 3. Current Label Artifact Issues

Observed from zip `labels_window.jsonl`:

```text
train label windows total: 3773
tempo_class counts: 0=785, 1=786, 2=786, 3=1416
bpm_distribution length: 6 for all windows
```

Problems:

1. Current v0 is 4-class `60/80/100/120`, but existing `bpm_distribution` still has length 6.
2. Existing windows are 120 frames, not the v0 default 60 frames.
3. Some window rows do not carry `dynamics_condition`; they do have continuous `dynamics`, and `meta.json` has take-level dynamics prompt.
4. 120 BPM has more windows because three old 120 BPM takes are longer than 60 seconds.

Required regeneration:

```text
labels_window_60f_v0.jsonl
pose_right_h36m_masked_windows_60f_v0.npy
manifest_60f_v0.json
folds_take_level_v0.json
```

Recommended label policy:

```text
tempo_class: nearest in [60, 80, 100, 120]
bpm_distribution: length 4 over [60, 80, 100, 120]
dynamics_value: existing continuous dynamics if present
gain_class: small/large from meta dynamics_condition, or thresholded dynamics_value when meta is missing
valid_ratio: min shoulder/elbow/wrist valid ratios
```

## 4. Existing Augmentation Audit

Existing zip contains `recommended_augmented_v0` labels for only 21 sessions.

```text
recommended_aug_label_files: 21
recommended_aug_windows_total: 8208
original 120f windows: 3773
current augmented/original ratio: about 2.18x
```

This does not satisfy the goal requirement of dataset expansion by 5x or more.

Action:

```text
ignore existing recommended_augmented_v0 for final v0 training pipeline
generate new train-only augmentation from regenerated 60f windows
target total train samples >= 5x original train-window count
```

The old augmentation may remain as historical artifact but must not be treated as the final expanded dataset.

## 5. Evaluation Audit

### session_20260616_222455_eval

```text
fps_estimate: 14.985
frame_count: 900
duration_seconds: 59.994599
labels_window_count: 131
tempo_class_counts: {1: 6, 2: 45, 3: 80}
dynamics_counts: large=121, small=10
manual_timeline: exists
ambiguous event: 33.0s
```

Use for early heldout only. It can support rough classification checks but switch latency/false switch claims must state how ambiguous/mixed windows are handled.

Scoring include:

```text
labels_window.jsonl
pose_right_h36m_masked.npy
right_rule_features.npy
```

Scoring exclude:

```text
recommended_augmented_v0/
labels_tempo_augmented_15f.jsonl
tempo_augmented_15f.npy
label_backup_*/
```

### session_20260616_215630_eval

```text
fps_estimate: 14.983
frame_count: 900
duration_seconds: 59.999675
labels_window_count: 131
tempo_class_counts: {2: 131}
manual_timeline: missing
status: excluded until relabel
```

This session must not enter score table until transition labels are regenerated.

## 6. Go / No-Go

| Stage | Status | Reason |
|---|---|---|
| Stage 0 dataset audit | GO | zip/meta/eval facts inspected |
| Train on existing 120f labels as v0 default | NO-GO | 120f is about 8s, distribution length is 6 |
| Generate 60f v0 labels/windows | GO | all sessions have pose and meta |
| Generate 5x augmentation | GO after 60f regeneration | existing augmentation is only 2.18x and partial |
| Evaluate `222455_eval` classification | GO with caveat | early heldout only |
| Evaluate `215630_eval` | NO-GO | relabel/manual timeline missing |
| Report switch latency p90 | NO-GO until label policy is defined | only one transition with ambiguous event |

## 7. Next Implementation Step

Create dataset preparation code that:

```text
1. reads dataset/recordings.zip without relying on old labels_window.jsonl
2. extracts pose_right_h36m_masked.npy and meta.json per session
3. builds 60f/stride3 windows
4. writes v0 4-bin tempo distribution
5. writes gain_class and dynamics_value consistently
6. creates take-level folds before augmentation
7. generates train-only augmented windows >= 5x
8. writes an audit manifest proving validation/eval have no augmentation
```

Next report:

```text
Goal Report 03: Dataset Preparation and Augmentation Implementation
```
