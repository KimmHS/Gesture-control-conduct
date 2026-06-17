# Goal Report 06 - MotionBERT Representation Diagnosis

## Status

Current stage:

```text
mean-pooled MotionBERT head bottleneck diagnosed
mean_std_delta cache mode implemented
stats feature cache generated
stats feature head trained/evaluated
score table updated
```

Current decision:

```text
stats MotionBERT head: CV GO
stats MotionBERT head: transition/live NO-GO
fallback for transition tempo: handcrafted_feature_ml
```

## Why This Step

Report 05 showed that the frozen MotionBERT checkpoint and shapes were valid, but the mean-pooled cached head failed:

```text
mean-pooled head cv_mean tempo_acc: 0.3920
feature_baseline cv_mean tempo_acc: 0.5152
```

The likely bottleneck was too much pooling:

```text
[B, T, right_arm_joints, 512] -> mean -> [B, 512]
```

Tempo needs periodic motion information, so this step added richer summary statistics before trying a heavier temporal model.

## Code Change

Added feature extraction mode:

```text
mean:
  right-arm representation mean
  output dim: 512

mean_std_delta:
  right-arm representation mean
  right-arm representation std
  absolute temporal delta mean
  absolute temporal delta std
  output dim: 2048
```

Updated files:

```text
lib/right_conducting/motionbert_training.py
tools/cache_motionbert_conducting_features.py
tools/train_motionbert_conducting_head.py
tests/test_motionbert_training_utils.py
tests/test_cache_motionbert_features_cli.py
tests/test_train_motionbert_head_cli.py
```

The train script now reads `feature_mode` from the cache manifest during transition eval, so train and eval use the same representation.

## Commands

Cache stats features:

```bash
python tools/cache_motionbert_conducting_features.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --device cuda:0 \
  --batch-size 64 \
  --feature-mode mean_std_delta \
  --output-dir outputs/right_conducting/motionbert_cache_v0_60f_stats
```

Train/evaluate stats head:

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
  --output-dir outputs/right_conducting/motionbert_head_v0_60f_stats_e80_h512
```

## Artifacts

```text
outputs/right_conducting/motionbert_cache_v0_60f_stats/manifest.json
outputs/right_conducting/motionbert_cache_v0_60f_stats/pooled_right_arm.npy
outputs/right_conducting/motionbert_head_v0_60f_stats_e80_h512/scores.json
outputs/right_conducting/motionbert_head_v0_60f_stats_e80_h512/scores.md
outputs/right_conducting/motionbert_head_v0_60f_stats_e80_h512/all_train_head.pt
docs/exp/right_hand_conducting_scores.md
```

Cache result:

```text
feature_mode: mean_std_delta
feature_shape: [8006, 2048]
missing_keys: []
unexpected_keys: []
```

## Scores

| eval_set | fold_or_subject | tempo_acc | bpm_mae_window | gain_acc | dynamics_mae_window |
|---|---|---:|---:|---:|---:|
| cv_val | fold_0 | 0.5249 | 12.5223 | 0.9918 | 0.0585 |
| cv_val | fold_1 | 0.8446 | 3.1898 | 0.9955 | 0.0401 |
| cv_val | fold_2 | 0.7839 | 6.6641 | 1.0000 | 0.0177 |
| cv_val | cv_mean | 0.7178 | 7.4588 | 0.9958 | 0.0388 |
| transition_eval_222455 | session_20260616_222455_eval | 0.2443 | 22.2901 | 0.8397 | 0.1300 |

## Gate Check

CV gate:

```text
feature_baseline cv_mean tempo_acc: 0.5152
stats head cv_mean tempo_acc: 0.7178
result: PASS
```

Transition/live gate:

```text
feature_baseline transition_eval_222455 tempo_acc: 0.5344
stats head transition_eval_222455 tempo_acc: 0.2443
result: FAIL
```

Conclusion:

```text
The stats feature fixes within-subject CV tempo, but does not yet produce a stable live/heldout model.
```

## Interpretation

The improvement from `0.3920` to `0.7178` CV tempo accuracy confirms that mean pooling was suppressing tempo information.

The transition collapse suggests at least one of these remains true:

```text
take-level CV is still too close to train distribution
transition_eval_222455 uses 120-frame labels while train uses 60-frame labels
camera normalization is brittle across heldout recording conditions
all-train head overfits current single-subject take style
transition labels contain ambiguous windows around 33.0s
```

This is not ready for final live export. The current best live fallback remains the hand-crafted feature baseline until MotionBERT improves on transition heldout.

## Next Step

Next report should focus on heldout stability rather than CV score:

```text
1. evaluate 60-frame windows on transition_eval_222455 if labels can be regenerated
2. compare camera vs right_shoulder normalization on one fold and transition eval
3. train a small temporal head over [T, 3, 512], not only summary stats
4. apply train-only temporal/amplitude augmentation before caching
5. relabel session_20260616_215630_eval and add it to transition score
```

Next report target:

```text
Goal Report 07 - Heldout Stability and Live Fallback Policy
```
