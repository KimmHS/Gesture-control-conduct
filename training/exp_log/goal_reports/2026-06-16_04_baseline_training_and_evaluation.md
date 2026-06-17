# Goal Report 04: Baseline Training and Evaluation

Date: 2026-06-16  
Scope: MotionBERT-Lite head 학습 전, current v0 dataset에서 rule baseline과 hand-crafted feature baseline을 먼저 측정했다.

## 1. Implemented Files

| File | Role |
|---|---|
| `lib/right_conducting/baselines.py` | metrics, pose window features, nearest-centroid classifier, rule predictor, eval artifact filter |
| `tools/evaluate_right_conducting_baselines.py` | fold validation + `222455_eval` baseline score CLI |
| `tests/test_right_conducting_baselines.py` | metric/classifier/eval artifact filter tests |
| `tests/test_evaluate_right_conducting_baselines_cli.py` | CLI import/help smoke test |
| `docs/exp/right_hand_conducting_scores.md` | measured baseline score table |

## 2. Command

```bash
python tools/evaluate_right_conducting_baselines.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --output-json outputs/right_conducting/baseline_scores_v0_60f.json \
  --output-md outputs/right_conducting/baseline_scores_v0_60f.md
```

Artifacts:

```text
outputs/right_conducting/baseline_scores_v0_60f.json
outputs/right_conducting/baseline_scores_v0_60f.md
docs/exp/right_hand_conducting_scores.md
```

## 3. Models

### rule_based_fft_amp_v0_60f

No training. It estimates tempo from dominant FFT frequency of right-wrist relative y motion, then maps to nearest BPM bin. Gain uses right-wrist vertical amplitude threshold.

This is intentionally simple and acts as a sanity baseline, not the final control policy.

### feature_baseline_v0_60f

Nearest-centroid classifier on hand-crafted pose-window features:

```text
wrist speed mean/std/max
wrist acceleration mean/std
shoulder-wrist radius mean/std/range
relative wrist x/y mean/std
relative elbow mean
right-arm valid ratio
dominant BPM feature
```

Separate classifiers are trained for tempo class and gain class. It uses original train windows only. The 5x virtual augmentation manifest is prepared for the deep model loader but is not yet consumed by this baseline.

## 4. Results Summary

| Model | Eval | Tempo Acc | BPM MAE | Gain Acc | Dynamics MAE |
|---|---|---:|---:|---:|---:|
| feature_baseline | 3-fold cv mean | 0.5152 | 14.3469 | 0.9933 | 0.0040 |
| rule_based | 3-fold cv mean | 0.2100 | 34.3614 | 0.8330 | 0.1002 |
| feature_baseline | transition_eval_222455 | 0.5344 | 9.3130 | 0.8168 | 0.1099 |
| rule_based | transition_eval_222455 | 0.0000 | 51.2977 | 0.5649 | 0.2611 |

Full table:

```text
docs/exp/right_hand_conducting_scores.md
outputs/right_conducting/baseline_scores_v0_60f.md
```

## 5. Interpretation

Feature baseline is the first useful non-deep baseline. It gives a concrete line for MotionBERT-Lite to beat:

```text
tempo_acc target to beat on cv_mean: > 0.5152
bpm_mae_window target to beat on cv_mean: < 14.3469
gain_acc target to beat on transition_eval_222455: > 0.8168
```

Rule-based tempo failed. The wrist-y FFT assumption does not match the current recording enough to classify tempo reliably.

```text
rule_based cv_mean tempo_acc: 0.2100
rule_based transition_eval_222455 tempo_acc: 0.0000
```

Gain is much easier than tempo in take-level CV, but transition eval gain macro-F1 is weak because `222455_eval` is imbalanced and has a very short `small` dynamics segment.

## 6. Eval Contamination Check

The eval script explicitly filters out:

```text
recommended_augmented_v0/
labels_tempo_augmented_15f.jsonl
tempo_augmented_15f.npy
label_backup_*/
```

Only root eval files are used:

```text
labels_window.jsonl
pose_right_h36m_masked.npy
right_rule_features.npy
```

The first eval run failed because `label_backup_*/labels_window.jsonl` was accidentally allowed by the file filter. A regression test was added and the filter now excludes `label_backup_*`.

## 7. Go / No-Go

| Item | Status | Reason |
|---|---|---|
| Baseline score table | GO | `rule_based` and `handcrafted_feature_ml` rows measured |
| MotionBERT-Lite head training | GO | baseline line exists; dataset manifest exists |
| Rule baseline as final fallback | NO-GO for tempo | tempo accuracy too low |
| Transition latency metrics | NO-GO | heldout label quality/quantity still weak |
| 215630 eval scoring | NO-GO | relabel still pending |

## 8. Next Step

Goal Report 05 should cover MotionBERT-Lite smoke test and head training.

Minimum next deliverables:

```text
load checkpoint/MB_lite.yaml and checkpoint/mb_lite_v0.pt
smoke test T=60 and T=120
right-arm pooling head
soft-label KL tempo loss
gain classification head
train on fold_0 first, then all folds
append motionbert_lite_head rows to right_hand_conducting_scores.md
```

Pass line for the next stage:

```text
MotionBERT head cv_mean tempo_acc > 0.5152
or, if not achieved, report failure and fall back to feature_baseline while diagnosing encoder/input mismatch
```
