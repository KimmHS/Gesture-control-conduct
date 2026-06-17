# Report 34 - After-Supply Model Selection Runner

## Purpose

5-GPU frame sweep이 끝난 뒤 `model_gate_after_supply_30f.json`부터 `150f.json`까지 사람이 하나씩 열어보는 병목을 없앤다.

새 도구는 gate 결과를 모아 다음을 자동으로 만든다.

```text
outputs/right_conducting/model_candidate_selection_after_supply.json
outputs/right_conducting/model_candidate_selection_after_supply.md
```

이 파일은 export가 아니라 selected 후보 판정 리포트다.

## Added Tool

```text
tools/select_right_conducting_model_candidate.py
lib/right_conducting/model_selection.py
```

Input:

```text
--gate-jsons   score gate JSON list or glob
--replay-jsons optional stream replay JSON list or glob
```

Selection rule:

```text
1. Gate status must be GO.
2. If replay JSONs are provided:
   prefer replay present,
   lower smoothed false_switches_per_min,
   lower smoothed switch_delay_p90_s,
   lower BPM MAE,
   higher transition tempo/gain accuracy,
   shorter window.
3. If replay JSONs are not provided:
   prefer lower BPM MAE,
   higher transition tempo/gain accuracy,
   higher CV tempo accuracy,
   shorter window.
```

If no candidate has `GO`, output status is `NO_GO` and no model is selected.

## Current Artifact Check

Current MotionBERT target80 combo gate:

```bash
python tools/select_right_conducting_model_candidate.py \
  --gate-jsons outputs/right_conducting/model_gate_current_motionbert_target80_combo_stride3.json \
  --output-json outputs/right_conducting/model_candidate_selection_current_motionbert_target80_combo.json \
  --output-md outputs/right_conducting/model_candidate_selection_current_motionbert_target80_combo.md
```

Result:

```text
status: NO_GO
candidate_count: 1
go_candidate_count: 0
failed_checks:
  transition_tempo_acc
  transition_bpm_mae_window
  transition_gain_acc
  tempo_120_recall
```

This confirms the selector does not accidentally promote the current failed MotionBERT head.

## Goal Runner Integration

`tools/run_right_conducting_goal.py` now accepts:

```text
--steps ... select
--selection-gate-jsons
--selection-replay-jsons
--selection-require-replay
--selection-output-json
--selection-output-md
```

If `--selection-gate-jsons` is omitted, the runner derives the frame sweep gate paths from `--gate-output-prefix` and `--window-frames`.

## After-Supply 5-GPU Command

Dry-run artifact:

```text
outputs/right_conducting/right_conducting_goal_run_after_supply_5gpu_select_dryrun.json
outputs/right_conducting/right_conducting_goal_run_after_supply_5gpu_select_dryrun.md
```

Command:

```bash
python tools/run_right_conducting_goal.py \
  --dry-run \
  --steps cache,train,detailed,gate,select \
  --train-source outputs/right_conducting/recordings_staged_after_supply.zip \
  --dataset-dir outputs/right_conducting/dataset_v0_after_supply \
  --cache-dir outputs/right_conducting/motionbert_cache_after_supply \
  --head-output-dir outputs/right_conducting/motionbert_head_after_supply \
  --detailed-output-prefix outputs/right_conducting/motionbert_after_supply_evalstable_detailed \
  --gate-output-prefix outputs/right_conducting/model_gate_after_supply \
  --selection-output-json outputs/right_conducting/model_candidate_selection_after_supply.json \
  --selection-output-md outputs/right_conducting/model_candidate_selection_after_supply.md \
  --window-frames 30,60,90,120,150 \
  --stride-frames 3 \
  --devices cuda:0,cuda:1,cuda:2,cuda:3,cuda:4 \
  --parallel-gpu \
  --gate-require-detailed
```

The final dry-run command is:

```text
tools/select_right_conducting_model_candidate.py
  --gate-jsons model_gate_after_supply_30f.json,...,model_gate_after_supply_150f.json
  --output-json model_candidate_selection_after_supply.json
```

## Decision Boundary

`model_candidate_selection_after_supply.json` can only promote a model candidate if the underlying gate is `GO`.

It does not overwrite:

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
```

Export/selected replacement is handled by Report 35 and still requires selection status `SELECTED`.

## Verification

```bash
python -m unittest discover -s tests -p 'test_model_selection.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
python -m unittest discover -s tests -p 'test_*.py' -v
python -m compileall -q lib/right_conducting/model_selection.py tools/select_right_conducting_model_candidate.py tests/test_model_selection.py
python -m compileall -q tools/run_right_conducting_goal.py tests/test_goal_command_cli.py
python -m compileall -q lib/right_conducting tools tests
```

Result:

```text
model selection tests: 3 OK
goal runner tests: 9 OK
full tests: 100 OK
compile OK
```

## Current Status

새 데이터셋은 아직 공급 전이다. 이번 report는 새 데이터 학습 후 score gate 결과를 자동 집계하고 후보 선택 리포트를 만들기 위한 준비 단계다.
