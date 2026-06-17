# Goal Report 30 - After-Supply Cache/Train Runner

## Purpose

Report 29에서 새 데이터용 `intake -> stage -> prepare` runner를 만들었다. 이번 report는 그 다음 단계인 MotionBERT feature cache와 conducting head training을 같은 goal runner에 연결한다.

실제 GPU cache/train은 새 데이터가 공급된 뒤 실행한다. 현재는 dry-run으로 경로와 명령 조합을 검증했다.

## Implemented Changes

Updated:

```text
tools/cache_motionbert_conducting_features.py
tools/run_right_conducting_goal.py
tests/test_cache_motionbert_features_cli.py
tests/test_goal_command_cli.py
```

Cache fix:

```text
Before:
  cache_motionbert_conducting_features.py always read windows_60f_v0.jsonl

After:
  reads dataset manifest.json -> windows_file
  falls back to window_frames -> windows_{N}f_v0.jsonl
  final fallback remains windows_60f_v0.jsonl
```

New runner steps:

```text
cache
train
```

New runner options:

```text
--cache-dir
--head-output-dir
--device
--cache-feature-mode
--cache-batch-size
--train-epochs
--train-batch-size
--train-hidden-dim
--train-lr
```

## After-Supply Cache/Train Dry Run

Command:

```bash
python tools/run_right_conducting_goal.py \
  --dry-run \
  --steps cache,train \
  --train-source outputs/right_conducting/recordings_staged_after_supply.zip \
  --dataset-dir outputs/right_conducting/dataset_v0_60f_after_supply \
  --cache-dir outputs/right_conducting/motionbert_cache_after_supply \
  --head-output-dir outputs/right_conducting/motionbert_head_after_supply \
  --window-frames 60 \
  --stride-frames 3 \
  --device cuda:0 \
  --cache-feature-mode mean_std_delta \
  --train-epochs 60 \
  --train-hidden-dim 512 \
  --output-json outputs/right_conducting/right_conducting_goal_run_after_supply_cache_train_dryrun.json \
  --output-md outputs/right_conducting/right_conducting_goal_run_after_supply_cache_train_dryrun.md
```

Generated commands:

```bash
python tools/cache_motionbert_conducting_features.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f_after_supply \
  --zip outputs/right_conducting/recordings_staged_after_supply.zip \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --device cuda:0 \
  --batch-size 64 \
  --feature-mode mean_std_delta \
  --output-dir outputs/right_conducting/motionbert_cache_after_supply_60f

python tools/train_motionbert_conducting_head.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f_after_supply \
  --cache-dir outputs/right_conducting/motionbert_cache_after_supply_60f \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --device cuda:0 \
  --epochs 60 \
  --batch-size 256 \
  --hidden-dim 512 \
  --lr 0.001 \
  --feature-mode auto \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --output-dir outputs/right_conducting/motionbert_head_after_supply_60f
```

Dry-run artifact:

```text
outputs/right_conducting/right_conducting_goal_run_after_supply_cache_train_dryrun.json
outputs/right_conducting/right_conducting_goal_run_after_supply_cache_train_dryrun.md
```

## Gate Line

Run cache/train only after:

```text
right_conducting_goal_run_after_supply_prepare.json:
  intake_dataset == ok
  stage_recordings_zip == ok
  prepare_60f == ok

outputs/right_conducting/dataset_v0_60f_after_supply/manifest.json:
  take_count > 24 or dataset scope intentionally unchanged
  window_count > 8006 or dataset scope intentionally unchanged
  validation_augmentation_policy == "validation samples are original only"
```

Pass cache/train if:

```text
motionbert_cache_after_supply_60f/manifest.json exists
motionbert_cache_after_supply_60f/pooled_right_arm.npy rows == labels.jsonl rows
motionbert_head_after_supply_60f/scores.json exists
scores.json has cv_mean and transition_eval rows
```

## Current Decision

```text
after-supply prepare runner: GO
after-supply cache/train runner: GO as dry-run command path
actual GPU cache/train: wait for supplied dataset
selected live fallback: unchanged
```

## Verification

```bash
python -m unittest discover -s tests -p 'test_cache_motionbert_features_cli.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
python tools/run_right_conducting_goal.py --dry-run --steps cache,train ...
```

Result:

```text
cache CLI tests OK
goal command tests OK
after-supply cache/train dry-run OK
```
