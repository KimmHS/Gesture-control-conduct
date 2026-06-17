# Goal Report 07 - Heldout Stability and Live Fallback Policy

## Status

Current stage:

```text
labels_frame -> 60-frame eval window generation: implemented
mixed BPM stable-window filtering: implemented
baseline 60f stable heldout score: measured
MotionBERT stats 60f stable heldout score: measured
score table / model card: updated
```

Current decision:

```text
MotionBERT stats head is not ready for live export.
Best current transition tempo fallback is handcrafted_feature_ml.
```

## Why This Step

Report 06 showed that stats MotionBERT improved CV but failed on `transition_eval_222455`:

```text
stats head cv_mean tempo_acc: 0.7178
stats head transition_eval_222455 120f tempo_acc: 0.2443
```

One possible issue was evaluation mismatch:

```text
train windows: 60 frames ~= 4s
existing transition labels: 120 frames ~= 8s
```

This step regenerated heldout evaluation windows from `labels_frame.jsonl` using the same 60-frame length as training.

## Code Change

Added eval window generation:

```text
lib/right_conducting/eval_windows.py
```

Behavior:

```text
input: labels_frame.jsonl + pose_right_h36m_masked.npy
output: v0-compatible window rows
window: configurable, current check uses 60 frames
stride: configurable, current check uses 3 frames
mixed_bpm_label: true if window spans more than one BPM label
stable_eval_windows: removes mixed BPM windows
```

Updated evaluators:

```text
tools/evaluate_right_conducting_baselines.py
tools/train_motionbert_conducting_head.py
```

New flags:

```text
--eval-window-frames
--eval-stride-frames
--eval-stable-only
```

## Commands

Baseline 60f stable heldout:

```bash
python tools/evaluate_right_conducting_baselines.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --output-json outputs/right_conducting/baseline_scores_v0_60f_eval60stable.json \
  --output-md outputs/right_conducting/baseline_scores_v0_60f_eval60stable.md
```

MotionBERT stats 60f stable heldout:

```bash
python tools/train_motionbert_conducting_head.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --cache-dir outputs/right_conducting/motionbert_cache_v0_60f_stats \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --device cuda:0 \
  --epochs 80 \
  --hidden-dim 512 \
  --lr 0.001 \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --output-dir outputs/right_conducting/motionbert_head_v0_60f_stats_e80_h512_eval60stable
```

## Window Summary

```text
all 60f windows: 281
stable 60f windows: 243
mixed BPM windows excluded: 38
stable BPM counts:
  100 BPM: 91
  120 BPM: 141
  80 BPM: 11
stable gain counts:
  large: 224
  small: 19
```

This heldout set is still imbalanced and still single-session, but it is now aligned with the 60-frame train window length.

## Scores

| model | eval_set | tempo_acc | bpm_mae_window | gain_acc | dynamics_mae_window |
|---|---|---:|---:|---:|---:|
| handcrafted_feature_ml | transition_eval_222455_60f_stable | 0.5514 | 10.6173 | 0.7654 | 0.1407 |
| rule_based | transition_eval_222455_60f_stable | 0.0000 | 50.3704 | 0.5103 | 0.2938 |
| MotionBERT stats head | transition_eval_222455_60f_stable | 0.3128 | 20.5761 | 0.7901 | 0.1275 |

CV context:

```text
handcrafted_feature_ml cv_mean tempo_acc: 0.5152
MotionBERT stats cv_mean tempo_acc: 0.6826 on this rerun
```

## Gate Check

Live candidate gate:

```text
must beat handcrafted_feature_ml on transition_eval_222455_60f_stable tempo_acc
```

Current result:

```text
handcrafted_feature_ml: 0.5514
MotionBERT stats head: 0.3128
```

Decision:

```text
MotionBERT stats head: FAIL for live tempo
handcrafted_feature_ml: fallback for live tempo
```

## Interpretation

The 60-frame stable check rules out simple train/eval window mismatch as the only cause. MotionBERT stats features still overfit within-subject take structure and do not transfer to the transition recording.

The current live policy should be conservative:

```text
tempo:
  use handcrafted_feature_ml as fallback
  do not export MotionBERT stats head as selected tempo model yet

gain:
  MotionBERT stats and feature baseline are both usable but heldout gain set is imbalanced
```

## Next Step

The next useful step is not another pooled summary head. Move to a temporal model or improve heldout data:

```text
1. temporal head over MotionBERT right-arm token sequence
2. train-only augmentation recache, especially temporal stretch
3. camera vs right_shoulder normalization comparison
4. relabel session_20260616_215630_eval and add second transition score
5. implement live smoothing/fallback policy using handcrafted_feature_ml until deep model passes heldout gate
```

Next report target:

```text
Goal Report 08 - Live Fallback Export
```
