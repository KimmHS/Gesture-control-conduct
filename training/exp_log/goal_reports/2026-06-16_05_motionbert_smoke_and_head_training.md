# Goal Report 05 - MotionBERT-Lite Smoke Test and Head Training

## Status

Current stage:

```text
MotionBERT-Lite checkpoint load: done
T=60 / T=120 forward smoke: done
right-arm pooled feature cache: done
cached conducting head training/eval: done
score table update: done
```

Current decision:

```text
MotionBERT-Lite backbone integration: GO
current mean-pooled cached head as final tempo model: NO-GO
best current fallback for tempo: handcrafted_feature_ml
```

## Why This Step

Report 04 showed that the hand-crafted feature baseline is the model to beat:

```text
feature_baseline cv_mean tempo_acc: 0.5152
feature_baseline transition_eval_222455 tempo_acc: 0.5344
```

This step tested whether a frozen MotionBERT-Lite encoder plus a lightweight conducting head can beat that baseline on current v0 data.

## Inputs

```text
dataset: outputs/right_conducting/dataset_v0_60f
train source: dataset/recordings.zip
MotionBERT config: checkpoint/MB_lite.yaml
MotionBERT checkpoint: checkpoint/mb_lite_v0.pt
scoreable eval: dataset/evaluation_transitions/session_20260616_222455_eval
excluded eval: dataset/evaluation_transitions/session_20260616_215630_eval
```

Current v0 assumptions remain:

```text
fps: about 15fps
tempo bins: 60 / 80 / 100 / 120
train/CV window: 60 frames ~= 4s
transition_eval_222455 labels_window: 120 frames ~= 8s
```

## Commands

Smoke test:

```bash
python tools/smoke_motionbert_conducting.py \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --device cuda:0 \
  --output outputs/right_conducting/motionbert_smoke_v0.json
```

Cache pooled right-arm features:

```bash
python tools/cache_motionbert_conducting_features.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --device cuda:0 \
  --output-dir outputs/right_conducting/motionbert_cache_v0_60f
```

Train/evaluate cached head:

```bash
python tools/train_motionbert_conducting_head.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --cache-dir outputs/right_conducting/motionbert_cache_v0_60f \
  --zip dataset/recordings.zip \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --device cuda:0 \
  --epochs 60 \
  --hidden-dim 256 \
  --lr 0.001 \
  --output-dir outputs/right_conducting/motionbert_head_v0_60f
```

Hyperparameter check:

```bash
python tools/train_motionbert_conducting_head.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --cache-dir outputs/right_conducting/motionbert_cache_v0_60f \
  --zip dataset/recordings.zip \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --device cuda:0 \
  --epochs 200 \
  --hidden-dim 512 \
  --lr 0.0005 \
  --output-dir outputs/right_conducting/motionbert_head_v0_60f_e200_h512
```

## Artifacts

```text
outputs/right_conducting/motionbert_smoke_v0.json
outputs/right_conducting/motionbert_cache_v0_60f/manifest.json
outputs/right_conducting/motionbert_cache_v0_60f/pooled_right_arm.npy
outputs/right_conducting/motionbert_head_v0_60f/scores.json
outputs/right_conducting/motionbert_head_v0_60f/scores.md
outputs/right_conducting/motionbert_head_v0_60f/all_train_head.pt
outputs/right_conducting/motionbert_head_v0_60f_e200_h512/scores.json
```

Score table:

```text
docs/exp/right_hand_conducting_scores.md
```

## Smoke Result

```text
checkpoint: checkpoint/mb_lite_v0.pt
device: cuda:0
missing_keys: []
unexpected_keys: []
T=60 input: [2, 60, 17, 3]
T=60 representation: [2, 60, 17, 512]
T=120 input: [2, 120, 17, 3]
T=120 representation: [2, 120, 17, 512]
tempo logits: [2, 4]
bpm distribution logits: [2, 4]
gain logits: [2, 2]
dynamics: [2]
```

The checkpoint loads cleanly and both current v0 length `60` and eval length `120` pass forward shape checks.

## Cache Result

```text
feature_shape: [8006, 512]
missing_keys: []
unexpected_keys: []
```

The cached feature is currently mean-pooled over right-arm MotionBERT tokens:

```text
[B, T, right_shoulder/right_elbow/right_wrist, 512]
  -> mean over T and joints
  -> [B, 512]
```

## Scores

### Main Run

```text
run: outputs/right_conducting/motionbert_head_v0_60f
epochs: 60
hidden_dim: 256
lr: 0.001
```

| eval_set | fold_or_subject | tempo_acc | bpm_mae_window | gain_acc | dynamics_mae_window |
|---|---|---:|---:|---:|---:|
| cv_val | fold_0 | 0.4144 | 16.0640 | 0.8869 | 0.1384 |
| cv_val | fold_1 | 0.3340 | 16.9974 | 0.9813 | 0.0781 |
| cv_val | fold_2 | 0.4277 | 18.0582 | 0.9588 | 0.1035 |
| cv_val | cv_mean | 0.3920 | 17.0398 | 0.9423 | 0.1067 |
| transition_eval_222455 | session_20260616_222455_eval | 0.2824 | 23.2061 | 0.8550 | 0.1196 |

### Longer Run Check

```text
run: outputs/right_conducting/motionbert_head_v0_60f_e200_h512
epochs: 200
hidden_dim: 512
lr: 0.0005
```

| eval_set | fold_or_subject | tempo_acc | bpm_mae_window | gain_acc | dynamics_mae_window |
|---|---|---:|---:|---:|---:|
| cv_val | cv_mean | 0.3859 | 17.8156 | 0.9507 | 0.0949 |
| transition_eval_222455 | session_20260616_222455_eval | 0.2366 | 24.1221 | 0.9237 | 0.1173 |

Longer training and a larger head improved gain slightly but made tempo worse.

## Comparison To Gate

Gate for moving forward as selected model:

```text
tempo_acc must beat feature_baseline cv_mean 0.5152
transition_eval_222455 tempo_acc should not regress below feature_baseline 0.5344
```

Current result:

```text
motionbert_lite_head cv_mean tempo_acc: 0.3920
motionbert_lite_head transition_eval_222455 tempo_acc: 0.2824
```

Result:

```text
NO-GO for current mean-pooled cached head
```

## Diagnosis

The failure is not checkpoint loading or input shape:

```text
checkpoint loads without missing/unexpected keys
T=60 and T=120 forward smoke pass
cached feature count matches 8006 windows
```

Likely bottleneck:

```text
mean pooling [T x right-arm joints] into [512] discards periodic tempo information
training uses original windows only, not the 5x virtual augmentation recipes
current v0 is small and likely single-subject
camera normalization remains the only measured mode
```

This means the next useful step is not simply more epochs. The model needs a representation/head change or augmentation-aware recaching.

## Next Step

Step down one level and try a richer MotionBERT feature/head before export:

```text
1. cache mean + std + temporal delta stats over right-arm tokens
2. train a small temporal head over [T, 3, 512] instead of pooled [512]
3. consume train-only virtual augmentation recipes before MotionBERT caching
4. compare camera vs right_shoulder normalization on at least one fold
5. keep handcrafted_feature_ml as fallback until MotionBERT beats it
```

Next report target:

```text
Goal Report 06 - MotionBERT Representation Diagnosis
```
