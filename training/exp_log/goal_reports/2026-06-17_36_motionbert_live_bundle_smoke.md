# Report 36 - MotionBERT Live Bundle Smoke

## Purpose

`SELECTED` MotionBERT bundle이 만들어진 뒤, live 환경에 넣기 전에 runtime loader가 실제로 동작하는지 확인한다.

검증 대상:

```text
motionbert_conducting_live_manifest.json
motionbert_conducting_head.pt
MotionBERT-Lite backbone reference
CachedConductingHead
LiveSmoother
```

## Added Runtime Loader

```text
lib/right_conducting/motionbert_live.py
tools/smoke_motionbert_live_bundle.py
```

Core API:

```python
predictor = MotionBERTLivePredictor.from_manifest(
    "outputs/right_conducting/selected_motionbert_after_supply/motionbert_conducting_live_manifest.json",
    device="cuda:0",
)

raw = predictor.predict_window(pose_window)  # [T,17,3]
smoothed = predictor.update(raw)
```

Outputs:

```text
raw:
  tempo_class
  bpm
  tempo_confidence
  bpm_distribution
  gain_class
  dynamics
  gain_confidence

smoothed:
  tempo_class
  gain_class
  bpm
  dynamics
  status
```

## Smoke CLI

Full backbone smoke:

```bash
python tools/smoke_motionbert_live_bundle.py \
  --manifest outputs/right_conducting/selected_motionbert_after_supply/motionbert_conducting_live_manifest.json \
  --device cuda:0 \
  --output-json outputs/right_conducting/motionbert_selected_live_smoke_after_supply.json
```

Fast head-only smoke:

```bash
python tools/smoke_motionbert_live_bundle.py \
  --manifest outputs/right_conducting/selected_motionbert_after_supply/motionbert_conducting_live_manifest.json \
  --device cuda:0 \
  --head-only \
  --output-json outputs/right_conducting/motionbert_selected_live_smoke_after_supply.json
```

The goal runner uses head-only by default because it verifies the exported head/manifest/smoother path quickly. Use `--smoke-full-backbone` when you want to also verify the MotionBERT checkpoint load and pose-window forward pass.

## Goal Runner Integration

`tools/run_right_conducting_goal.py` now accepts:

```text
--steps ... smoke-selected
--smoke-manifest
--smoke-output-json
--smoke-head-only
--smoke-full-backbone
```

If `--smoke-manifest` is omitted, the runner uses:

```text
{motionbert_export_dir}/motionbert_conducting_live_manifest.json
```

## After-Supply Dry Run

Generated artifact:

```text
outputs/right_conducting/right_conducting_goal_run_after_supply_5gpu_export_smoke_dryrun.json
outputs/right_conducting/right_conducting_goal_run_after_supply_5gpu_export_smoke_dryrun.md
```

Command:

```bash
python tools/run_right_conducting_goal.py \
  --dry-run \
  --steps cache,train,detailed,gate,select,export-selected,smoke-selected \
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
  --window-frames 30,60,90,120,150 \
  --stride-frames 3 \
  --devices cuda:0,cuda:1,cuda:2,cuda:3,cuda:4 \
  --parallel-gpu \
  --gate-require-detailed
```

Final dry-run command:

```text
tools/smoke_motionbert_live_bundle.py
  --manifest outputs/right_conducting/selected_motionbert_after_supply/motionbert_conducting_live_manifest.json
  --device cuda:0
  --output-json outputs/right_conducting/motionbert_selected_live_smoke_after_supply.json
  --head-only
```

## Verification

```bash
python -m unittest discover -s tests -p 'test_motionbert_live.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
python -m unittest discover -s tests -p 'test_*.py' -v
python -m compileall -q lib/right_conducting/motionbert_live.py tools/smoke_motionbert_live_bundle.py tests/test_motionbert_live.py
python -m compileall -q tools/run_right_conducting_goal.py tests/test_goal_command_cli.py
python -m compileall -q lib/right_conducting tools tests
```

Result:

```text
motionbert live tests: 3 OK
goal runner tests: 11 OK
full tests: 108 OK
compile OK
```

## Current Status

새 데이터셋은 아직 공급 전이다. 현재는 MotionBERT bundle smoke path만 준비되어 있다.

The current live runtime remains:

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
```

MotionBERT live smoke should run only after after-supply selection/export succeeds. Full replay is handled in Report 37.
