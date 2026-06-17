# Goal Report 19: Class-Balanced Ridge Feature Classifier

## Purpose

The selected 60-frame feature fallback still misses the stable 80 BPM tail after the `120 -> 80` transition.

This step checks whether a small-data fix can help before changing the model family:

```text
16 handcrafted right-arm pose features
-> Standardized ridge classifier
-> optional class_weight=balanced
-> temporal artifact export path
```

`context_size=1` is used here, so this is a non-temporal linear boundary over the same window features, not a temporal model.

## Code Change

Files:

```text
lib/right_conducting/temporal_classifier.py
tools/evaluate_right_conducting_temporal.py
tests/test_temporal_classifier.py
tests/test_evaluate_temporal_cli.py
```

Changes:

```text
StandardizedRidgeClassifier(class_weight="balanced")
  -> sample weights n_samples / (n_classes * class_count)
  -> weighted ridge solve through sqrt(sample_weight)

evaluate_right_conducting_temporal.py
  -> --class-weight none|balanced
  -> CV, transition eval, and exported artifact use the same setting
```

Test intent:

```text
imbalanced toy data:
  unweighted ridge ignores the minority class
  balanced ridge recovers the minority query
```

## Commands

Balanced alpha sweep:

```bash
python tools/evaluate_right_conducting_temporal.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --context-size 1 \
  --ridge-alpha 1.0 \
  --class-weight balanced \
  --output-json outputs/right_conducting/linear_balanced_scores_v0_60f_c1_a1.json \
  --output-md outputs/right_conducting/linear_balanced_scores_v0_60f_c1_a1.md \
  --output-artifact outputs/right_conducting/linear_balanced_60f_c1_a1/temporal_feature_live_v0_60f_c1_a1_balanced.json
```

Replay:

```bash
python tools/replay_right_conducting_temporal.py \
  --artifact outputs/right_conducting/linear_balanced_60f_c1_a10/temporal_feature_live_v0_60f_c1_a10_balanced.json \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --context-size 1 \
  --switch-threshold 0.15 \
  --fast-switch-threshold 0.40 \
  --confirm-updates 2 \
  --output-json outputs/right_conducting/linear_balanced_replay_222455_60f_c1_a10_tuned.json \
  --output-md outputs/right_conducting/linear_balanced_replay_222455_60f_c1_a10_tuned.md \
  --output-rows outputs/right_conducting/linear_balanced_replay_222455_60f_c1_a10_tuned_rows.jsonl
```

## Artifacts

Scores:

```text
outputs/right_conducting/linear_unweighted_scores_v0_60f_c1_a1.json
outputs/right_conducting/linear_balanced_scores_v0_60f_c1_a0.1.json
outputs/right_conducting/linear_balanced_scores_v0_60f_c1_a1.json
outputs/right_conducting/linear_balanced_scores_v0_60f_c1_a10.json
```

Exported candidate artifacts:

```text
outputs/right_conducting/linear_unweighted_60f_c1_a1/temporal_feature_live_v0_60f_c1_a1.json
outputs/right_conducting/linear_balanced_60f_c1_a0.1/temporal_feature_live_v0_60f_c1_a0.1_balanced.json
outputs/right_conducting/linear_balanced_60f_c1_a1/temporal_feature_live_v0_60f_c1_a1_balanced.json
outputs/right_conducting/linear_balanced_60f_c1_a10/temporal_feature_live_v0_60f_c1_a10_balanced.json
```

Replay artifacts:

```text
outputs/right_conducting/linear_unweighted_replay_222455_60f_c1_a1_tuned.json
outputs/right_conducting/linear_unweighted_replay_222455_60f_c1_a1_tuned_analysis.json
outputs/right_conducting/linear_balanced_replay_222455_60f_c1_a10_tuned.json
outputs/right_conducting/linear_balanced_replay_222455_60f_c1_a10_tuned_analysis.json
```

## Offline Stable Eval

Compared against the selected fallback:

| candidate | class_weight | alpha | cv tempo_acc | cv macro_f1 | stable tempo_acc | stable macro_f1 | stable bpm_mae | stable gain_acc |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| selected feature_baseline all | none | - | 0.5152 | - | 0.5514 | 0.2885 | 10.6173 | 0.7654 |
| linear ridge c1 | none | 1.0 | 0.5916 | 0.5280 | 0.2099 | 0.0907 | 17.2840 | 0.7531 |
| linear ridge c1 | balanced | 0.1 | 0.6033 | 0.5559 | 0.2840 | 0.1150 | 15.7202 | 0.7490 |
| linear ridge c1 | balanced | 1.0 | 0.6023 | 0.5549 | 0.2840 | 0.1150 | 15.7202 | 0.7490 |
| linear ridge c1 | balanced | 10.0 | 0.5976 | 0.5493 | 0.2840 | 0.1146 | 15.5556 | 0.7449 |

Observation:

```text
Balanced weighting slightly improves the linear ridge candidate over unweighted ridge,
but it is still far below the selected nearest-centroid feature fallback on transition stable eval.
```

## Stable Confusion Check

Class mapping:

```text
0: 60 BPM
1: 80 BPM
2: 100 BPM
3: 120 BPM
```

Stable true/predicted tempo counts:

| candidate | true 80 predictions | all stable pred_counts |
|---|---|---|
| linear ridge c1 unweighted a1 | `{100: 4, 60: 7}` | `{60: 19, 100: 190, 120: 34}` |
| linear ridge c1 balanced a10 | `{100: 5, 60: 6}` | `{60: 16, 80: 1, 100: 210, 120: 16}` |

Key point:

```text
The balanced model does not recover the true 80 BPM tail.
Its only 80 BPM prediction in the stable set is actually a true 100 BPM window.
```

## Streaming Replay

Full replay uses the same tuned policy values as the selected fallback check:

```text
switch_threshold: 0.15
fast_switch_threshold: 0.40
confirm_updates: 2
```

| candidate | raw tempo_acc | raw false/min | raw reached | raw missed | smoothed tempo_acc | smoothed false/min | smoothed reached | smoothed missed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| linear ridge c1 unweighted a1 | 0.2171 | 17.1243 | 0 | 2 | 0.2100 | 9.6324 | 0 | 2 |
| linear ridge c1 balanced a10 | 0.2811 | 20.3351 | 0 | 2 | 0.2989 | 8.5621 | 0 | 2 |

Both real tempo switches are missed by raw and smoothed output:

```text
100 -> 120 BPM: missed
120 -> 80 BPM: missed
```

## Decision

```text
class-balanced ridge feature classifier: NO-GO as selected live model.
selected live fallback remains outputs/right_conducting/selected/feature_baseline_live_v0.json.
```

Reason:

```text
Class weighting fixes a synthetic imbalance test, but not the real heldout session.
It does not classify the stable 80 BPM tail correctly and it also damages 120 BPM stability.
```

Next step:

```text
Do not spend more time on linear class weighting alone.
Move to data/label-side fixes or a model that uses stronger temporal shape:
  1. relabel/add second eval transition set
  2. inspect 80 BPM train vs eval feature distribution
  3. test train-only tempo-stretch augmentation with heldout-safe grouping
```
