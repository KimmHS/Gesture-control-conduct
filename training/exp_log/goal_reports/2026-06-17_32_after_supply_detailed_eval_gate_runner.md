# Goal Report 32 - After-Supply Detailed Eval/Gate Runner

## Purpose

Report 31에서 score gate를 만들었지만, gate가 요구하는 per-class recall detailed JSON은 runner가 자동 생성하지 않았다.

이번 report는 `detailed -> gate`를 goal runner에 연결한다. 새 데이터로 MotionBERT head를 학습한 뒤, detailed eval과 score gate를 한 명령 흐름으로 실행할 수 있다.

## Implemented Changes

Updated:

```text
tools/run_right_conducting_goal.py
tests/test_goal_command_cli.py
```

New runner step:

```text
detailed
```

New runner option:

```text
--detailed-output-prefix
```

Behavior:

```text
detailed:
  evaluates {head_output_dir}_{window}f/all_train_head.pt
  writes {detailed_output_prefix}_{window}f.json/md

detailed,gate together:
  gate automatically uses {detailed_output_prefix}_{window}f.json
  unless --gate-detailed-json is explicitly provided
```

## After-Supply Detailed/Gate Dry Run

Command:

```bash
python tools/run_right_conducting_goal.py \
  --dry-run \
  --steps detailed,gate \
  --head-output-dir outputs/right_conducting/motionbert_head_after_supply \
  --detailed-output-prefix outputs/right_conducting/motionbert_after_supply_eval60stable_detailed \
  --gate-output-prefix outputs/right_conducting/model_gate_after_supply \
  --window-frames 60 \
  --stride-frames 3 \
  --device cuda:0 \
  --gate-require-detailed \
  --output-json outputs/right_conducting/right_conducting_goal_run_after_supply_detailed_gate_dryrun.json \
  --output-md outputs/right_conducting/right_conducting_goal_run_after_supply_detailed_gate_dryrun.md
```

Generated commands:

```bash
python tools/evaluate_motionbert_head_detailed.py \
  --head-checkpoint outputs/right_conducting/motionbert_head_after_supply_60f/all_train_head.pt \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --device cuda:0 \
  --feature-mode mean_std_delta \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --output-json outputs/right_conducting/motionbert_after_supply_eval60stable_detailed_60f.json \
  --output-md outputs/right_conducting/motionbert_after_supply_eval60stable_detailed_60f.md

python tools/check_right_conducting_score_gate.py \
  --score-json outputs/right_conducting/motionbert_head_after_supply_60f/scores.json \
  --output-json outputs/right_conducting/model_gate_after_supply_60f.json \
  --output-md outputs/right_conducting/model_gate_after_supply_60f.md \
  --detailed-json outputs/right_conducting/motionbert_after_supply_eval60stable_detailed_60f.json \
  --require-detailed
```

Dry-run artifacts:

```text
outputs/right_conducting/right_conducting_goal_run_after_supply_detailed_gate_dryrun.json
outputs/right_conducting/right_conducting_goal_run_after_supply_detailed_gate_dryrun.md
```

## Full After-Supply Sequence

After supplied data arrives:

```text
1. intake,stage,prepare
2. cache,train
3. detailed,gate
4. replay/analyze only if gate status is GO or for diagnostic comparison
```

The exact final model selection gate remains:

```text
outputs/right_conducting/model_gate_after_supply_60f.json
```

## Gate Line

Proceed to live replay/export only if:

```text
model_gate_after_supply_60f.json status == GO
tempo_80_recall and tempo_120_recall checks pass
transition_tempo_acc and bpm_mae_window checks pass
```

## Current Decision

```text
after-supply detailed eval runner: GO as dry-run command path
score gate link: GO as dry-run command path
actual detailed eval/gate: wait for supplied dataset and trained head
selected live fallback: unchanged
```

## Verification

```bash
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
python tools/run_right_conducting_goal.py --dry-run --steps detailed,gate ...
```

Result:

```text
goal command detailed/gate tests OK
after-supply detailed/gate dry-run OK
```
