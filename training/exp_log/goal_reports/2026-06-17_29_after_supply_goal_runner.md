# Goal Report 29 - After-Supply Goal Runner

## Purpose

Report 27/28에서 개별로 만든 `intake -> stage -> prepare` gate를 goal runner에 연결했다.

새 데이터가 공급되면 사용자는 개별 명령을 기억하지 않고, 같은 runner에서 train/eval root만 바꿔 `after_supply` dataset을 만들 수 있다.

## Implemented Changes

Updated:

```text
tools/run_right_conducting_goal.py
tests/test_goal_command_cli.py
```

New supported steps:

```text
intake
stage
prepare
```

Existing score steps remain:

```text
audit
eval
replay
analyze
```

New runner options:

```text
--train-roots
--eval-roots
--stage-output-zip
--stage-output-json
--intake-output-json
--intake-output-md
```

When `stage` and `prepare` are both requested, `prepare` automatically uses `--stage-output-zip` as its `--zip` input.

## Current Workspace Execution

Command:

```bash
python tools/run_right_conducting_goal.py \
  --steps intake,stage,prepare \
  --train-roots dataset/recordings \
  --eval-roots dataset/evaluation_transitions \
  --stage-output-zip outputs/right_conducting/recordings_staged_goal_current.zip \
  --stage-output-json outputs/right_conducting/recordings_staged_goal_current_manifest.json \
  --dataset-dir outputs/right_conducting/dataset_v0_60f_goal_current \
  --window-frames 60 \
  --stride-frames 3 \
  --output-json outputs/right_conducting/right_conducting_goal_run_intake_stage_prepare_current.json \
  --output-md outputs/right_conducting/right_conducting_goal_run_intake_stage_prepare_current.md
```

Result:

| step | status |
|---|---|
| intake_dataset | ok |
| stage_recordings_zip | ok |
| prepare_60f | ok |

Prepared manifest:

| metric | value |
|---|---:|
| take_count | 24 |
| window_count | 8006 |
| fold_count | 3 |
| fold_0 augmentation ratio | 5.0 |
| fold_1 augmentation ratio | 5.0 |
| fold_2 augmentation ratio | 5.0 |

Artifacts:

```text
outputs/right_conducting/right_conducting_goal_run_intake_stage_prepare_current.json
outputs/right_conducting/right_conducting_goal_run_intake_stage_prepare_current.md
outputs/right_conducting/dataset_intake_goal.json
outputs/right_conducting/dataset_intake_goal.md
outputs/right_conducting/recordings_staged_goal_current.zip
outputs/right_conducting/recordings_staged_goal_current_manifest.json
outputs/right_conducting/dataset_v0_60f_goal_current/manifest.json
```

## After-Supply Command

When the supplied dataset arrives:

```bash
python tools/run_right_conducting_goal.py \
  --steps intake,stage,prepare \
  --train-roots dataset/recordings,NEW_TRAIN_ROOT \
  --eval-roots dataset/evaluation_transitions,NEW_EVAL_ROOT \
  --stage-output-zip outputs/right_conducting/recordings_staged_after_supply.zip \
  --stage-output-json outputs/right_conducting/recordings_staged_after_supply_manifest.json \
  --intake-output-json outputs/right_conducting/dataset_intake_audit_after_supply.json \
  --intake-output-md outputs/right_conducting/dataset_intake_audit_after_supply.md \
  --dataset-dir outputs/right_conducting/dataset_v0_60f_after_supply \
  --window-frames 60 \
  --stride-frames 3 \
  --output-json outputs/right_conducting/right_conducting_goal_run_after_supply_prepare.json \
  --output-md outputs/right_conducting/right_conducting_goal_run_after_supply_prepare.md
```

Then train/eval commands should use:

```text
--zip outputs/right_conducting/recordings_staged_after_supply.zip
--dataset-dir outputs/right_conducting/dataset_v0_60f_after_supply
```

## Gate Line

Proceed to cache/train only if:

```text
intake_dataset: ok
stage_recordings_zip: ok
prepare_60f: ok
train_ready_count increased or dataset scope is intentionally unchanged
eval_scoreable_count >= 1
validation_augmentation_policy == "validation samples are original only"
```

## Verification

```bash
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
python tools/run_right_conducting_goal.py --steps intake,stage,prepare ...
```

Result:

```text
4 goal-command tests OK
current intake/stage/prepare goal run OK
```
