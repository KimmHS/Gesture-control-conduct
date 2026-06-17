# Report 37 - MotionBERT Live Bundle Replay

## Purpose

`SELECTED` MotionBERT bundle을 live predictor로 smoke한 뒤, scoreable eval session에서 streaming replay metric까지 뽑는다.

이 단계는 final stream 환경의 핵심 지표를 다시 만든다.

```text
raw tempo/gain accuracy
smoothed tempo/gain accuracy
false_switches_per_min
switch_delay_mean_s
switch_delay_p90_s
rows jsonl for failure inspection
```

## Added Tool

```text
lib/right_conducting/motionbert_replay.py
tools/replay_motionbert_live_bundle.py
```

Input:

```text
--manifest outputs/right_conducting/selected_motionbert_after_supply/motionbert_conducting_live_manifest.json
--eval-session dataset/evaluation_transitions/session_20260616_222455_eval
```

Output:

```text
outputs/right_conducting/motionbert_selected_live_replay_after_supply.json
outputs/right_conducting/motionbert_selected_live_replay_after_supply.md
outputs/right_conducting/motionbert_selected_live_replay_after_supply_rows.jsonl
```

## Replay Behavior

For each eval window:

```text
pose_right_h36m_masked[start:end]
-> MotionBERTLivePredictor.predict_window()
-> raw tempo/gain/dynamics prediction
-> MotionBERTLivePredictor.update()
-> smoothed tempo/gain/dynamics prediction
-> row append
```

Metrics use the existing replay metric implementation:

```text
lib/right_conducting/stream_replay.py::compute_replay_metrics
```

This keeps feature fallback replay and MotionBERT replay comparable.

## Goal Runner Integration

`tools/run_right_conducting_goal.py` now accepts:

```text
--steps ... replay-selected
--motionbert-replay-output-json
--motionbert-replay-output-md
--motionbert-replay-output-rows
--motionbert-replay-stable-only
--motionbert-replay-max-windows
```

`--motionbert-replay-stable-only` is recommended for the first after-supply model comparison because the detailed eval/gate path also uses stable windows.

## After-Supply Dry Run

Generated artifact:

```text
outputs/right_conducting/right_conducting_goal_run_after_supply_5gpu_full_live_dryrun.json
outputs/right_conducting/right_conducting_goal_run_after_supply_5gpu_full_live_dryrun.md
```

Command:

```bash
python tools/run_right_conducting_goal.py \
  --dry-run \
  --steps cache,train,detailed,gate,select,export-selected,smoke-selected,replay-selected \
  --train-source outputs/right_conducting/recordings_staged_after_supply.zip \
  --dataset-dir outputs/right_conducting/dataset_v0_after_supply \
  --cache-dir outputs/right_conducting/motionbert_cache_after_supply \
  --head-output-dir outputs/right_conducting/motionbert_head_after_supply \
  --detailed-output-prefix outputs/right_conducting/motionbert_after_supply_evalstable_detailed \
  --gate-output-prefix outputs/right_conducting/model_gate_after_supply \
  --selection-output-json outputs/right_conducting/model_candidate_selection_after_supply.json \
  --selection-output-md outputs/right_conducting/model_candidate_selection_after_supply.md \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_after_supply \
  --smoke-output-json outputs/right_conducting/motionbert_selected_live_smoke_after_supply.json \
  --motionbert-replay-output-json outputs/right_conducting/motionbert_selected_live_replay_after_supply.json \
  --motionbert-replay-output-md outputs/right_conducting/motionbert_selected_live_replay_after_supply.md \
  --motionbert-replay-output-rows outputs/right_conducting/motionbert_selected_live_replay_after_supply_rows.jsonl \
  --motionbert-replay-stable-only \
  --window-frames 30,60,90,120,150 \
  --stride-frames 3 \
  --devices cuda:0,cuda:1,cuda:2,cuda:3,cuda:4 \
  --parallel-gpu \
  --gate-require-detailed
```

Final dry-run command:

```text
tools/replay_motionbert_live_bundle.py
  --manifest outputs/right_conducting/selected_motionbert_after_supply/motionbert_conducting_live_manifest.json
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval
  --device cuda:0
  --output-json outputs/right_conducting/motionbert_selected_live_replay_after_supply.json
  --output-md outputs/right_conducting/motionbert_selected_live_replay_after_supply.md
  --output-rows outputs/right_conducting/motionbert_selected_live_replay_after_supply_rows.jsonl
  --stable-only
```

## Verification

```bash
python -m unittest discover -s tests -p 'test_motionbert_replay.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
python -m compileall -q lib/right_conducting/motionbert_replay.py tools/replay_motionbert_live_bundle.py tests/test_motionbert_replay.py
python -m compileall -q tools/run_right_conducting_goal.py tests/test_goal_command_cli.py
```

Result:

```text
motionbert replay tests: 3 OK
goal runner tests: 12 OK
compile OK
```

## Current Status

새 데이터셋은 아직 공급 전이다. Current selected live runtime remains:

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
```

MotionBERT replay should run only after after-supply selection/export/smoke succeeds.
