# Report 33 - After-Supply 5-GPU Frame Sweep Runner

## Purpose

새 데이터셋이 공급되면 단일 `60f` 모델만 학습하지 않고, 현재 약 15 FPS 데이터 기준의 window 길이 후보를 병렬로 비교한다.

```text
30f  ~= 2s
60f  ~= 4s  # current default
90f  ~= 6s
120f ~= 8s
150f ~= 10s
```

목표는 live 환경에서 tempo/gain classification의 latency/stability tradeoff를 빠르게 확인하는 것이다.

## Runner Change

`tools/run_right_conducting_goal.py`에 다음 옵션을 추가했다.

```text
--devices cuda:0,cuda:1,cuda:2,cuda:3,cuda:4
--parallel-gpu
```

적용 범위:

```text
cache    -> frame index 기준 round-robin device 배정
train    -> 같은 frame window가 같은 GPU를 사용
detailed -> 같은 frame window가 같은 GPU를 사용
gate     -> score JSON/detailed JSON 검증 단계라 GPU 배정 없음
```

`--parallel-gpu`를 실제 실행에 주면 같은 phase 안의 frame-sweep 명령을 동시에 실행한다. 순서는 phase barrier를 유지한다.

```text
cache 30/60/90/120/150 in parallel
-> train 30/60/90/120/150 in parallel
-> detailed eval 30/60/90/120/150 in parallel
-> score gate 30/60/90/120/150
```

## Required Prepare

5-GPU sweep 전에 모든 window-frame dataset을 먼저 만들어야 한다.

```bash
python tools/run_right_conducting_goal.py \
  --steps intake,stage,prepare \
  --train-roots dataset/recordings,NEW_TRAIN_ROOT \
  --eval-roots dataset/evaluation_transitions,NEW_EVAL_ROOT \
  --stage-output-zip outputs/right_conducting/recordings_staged_after_supply.zip \
  --stage-output-json outputs/right_conducting/recordings_staged_after_supply_manifest.json \
  --dataset-dir outputs/right_conducting/dataset_v0_after_supply \
  --window-frames 30,60,90,120,150 \
  --stride-frames 3
```

## 5-GPU Dry Run

Generated artifact:

```text
outputs/right_conducting/right_conducting_goal_run_after_supply_5gpu_dryrun.json
outputs/right_conducting/right_conducting_goal_run_after_supply_5gpu_dryrun.md
outputs/right_conducting/right_conducting_goal_run_after_supply_5gpu_select_dryrun.json
outputs/right_conducting/right_conducting_goal_run_after_supply_5gpu_select_dryrun.md
outputs/right_conducting/right_conducting_goal_run_after_supply_5gpu_select_export_dryrun.json
outputs/right_conducting/right_conducting_goal_run_after_supply_5gpu_select_export_dryrun.md
```

Command:

```bash
python tools/run_right_conducting_goal.py \
  --dry-run \
  --steps cache,train,detailed,gate,select,export-selected \
  --train-source outputs/right_conducting/recordings_staged_after_supply.zip \
  --dataset-dir outputs/right_conducting/dataset_v0_after_supply \
  --cache-dir outputs/right_conducting/motionbert_cache_after_supply \
  --head-output-dir outputs/right_conducting/motionbert_head_after_supply \
  --detailed-output-prefix outputs/right_conducting/motionbert_after_supply_evalstable_detailed \
  --gate-output-prefix outputs/right_conducting/model_gate_after_supply \
  --selection-output-json outputs/right_conducting/model_candidate_selection_after_supply.json \
  --selection-output-md outputs/right_conducting/model_candidate_selection_after_supply.md \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_after_supply \
  --window-frames 30,60,90,120,150 \
  --stride-frames 3 \
  --devices cuda:0,cuda:1,cuda:2,cuda:3,cuda:4 \
  --parallel-gpu \
  --gate-require-detailed
```

## Device Assignment

| window | device | cache output | head output | gate output |
|---:|---|---|---|---|
| 30f | `cuda:0` | `motionbert_cache_after_supply_30f` | `motionbert_head_after_supply_30f` | `model_gate_after_supply_30f.json` |
| 60f | `cuda:1` | `motionbert_cache_after_supply_60f` | `motionbert_head_after_supply_60f` | `model_gate_after_supply_60f.json` |
| 90f | `cuda:2` | `motionbert_cache_after_supply_90f` | `motionbert_head_after_supply_90f` | `model_gate_after_supply_90f.json` |
| 120f | `cuda:3` | `motionbert_cache_after_supply_120f` | `motionbert_head_after_supply_120f` | `model_gate_after_supply_120f.json` |
| 150f | `cuda:4` | `motionbert_cache_after_supply_150f` | `motionbert_head_after_supply_150f` | `model_gate_after_supply_150f.json` |

## Decision Rule

`60f` remains the default candidate unless another frame window passes the same score gate and gives a better live tradeoff.

Minimum gate for selected model candidate:

```text
cv_tempo_acc >= 0.70
cv_gain_acc >= 0.95
transition_tempo_acc >= 0.60
transition_bpm_mae_window <= 10.0
transition_gain_acc >= 0.80
tempo_80_recall >= 0.50
tempo_120_recall >= 0.50
```

If multiple windows pass:

```text
prefer lower switch delay and lower false_switches_per_min
tie-breaker: lower bpm_mae_window
tie-breaker: shorter window for live responsiveness
```

## Verification

```bash
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
python -m unittest discover -s tests -p 'test_*.py' -v
python -m compileall -q tools/run_right_conducting_goal.py tests/test_goal_command_cli.py
python -m compileall -q lib/right_conducting tools tests
```

Result:

```text
8 tests OK
96 tests OK
compile OK
```

## Current Status

새 데이터셋은 아직 공급 전이다. 이 report는 실제 score가 아니라, 공급 직후 5-GPU frame sweep을 재현 가능하게 실행하기 위한 runner/report 준비 단계다.
