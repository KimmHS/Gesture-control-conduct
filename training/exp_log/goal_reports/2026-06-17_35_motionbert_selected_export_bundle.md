# Report 35 - MotionBERT Selected Export Bundle

## Purpose

새 데이터 학습 후 `model_candidate_selection_after_supply.json`이 `SELECTED`가 되면, live 환경에 넣을 수 있는 MotionBERT-Lite conducting bundle을 생성한다.

이 단계는 selected 후보를 실제 runtime artifact로 묶는 단계다. 현재 failed MotionBERT head는 export하지 않는다.

## Added Tool

```text
tools/export_motionbert_selected_bundle.py
lib/right_conducting/motionbert_export.py
```

Input:

```text
--selection-json outputs/right_conducting/model_candidate_selection_after_supply.json
--output-dir outputs/right_conducting/selected_motionbert_after_supply
```

Output:

```text
outputs/right_conducting/selected_motionbert_after_supply/
  motionbert_conducting_head.pt
  motionbert_conducting_live_manifest.json
  motionbert_conducting_live_structure.md
```

The backbone remains referenced, not copied:

```text
checkpoint/MB_lite.yaml
checkpoint/mb_lite_v0.pt
```

## Export Guard

The exporter requires:

```text
selection.status == SELECTED
selection.selected is present
head checkpoint exists
```

Current failed model check:

```bash
python tools/export_motionbert_selected_bundle.py \
  --selection-json outputs/right_conducting/model_candidate_selection_current_motionbert_target80_combo.json \
  --output-dir outputs/right_conducting/selected_motionbert_current_no_go_probe
```

Result:

```text
selection status must be SELECTED, got NO_GO
```

This is expected. It prevents accidental replacement of the current fallback with a failed MotionBERT head.

## Bundle Structure

The manifest records:

```text
model_type: motionbert_lite_frozen_backbone_cached_head
input_shape: [B, window_frames, 17, 3]
right_arm_indices: [14, 15, 16]
feature_mode: mean or mean_std_delta
bpm_bins: [60, 80, 100, 120]
gain_mapping: small=0.25, large=0.85
head_architecture:
  class: CachedConductingHead
  feature_dim: inferred from trunk.1.weight
  hidden_dim: inferred from trunk.1.weight
  outputs:
    tempo_logits
    bpm_distribution_logits
    gain_logits
    dynamics
```

Runtime pipeline:

```text
MediaPipe Pose 33
-> H36M17 right-arm masked pose
-> MotionBERT-Lite frozen backbone get_representation
-> right_arm_representation_features(mode=...)
-> CachedConductingHead
-> LiveSmoother
-> MIDI tempo / velocity / CC11 control
```

## Goal Runner Integration

`tools/run_right_conducting_goal.py` now accepts:

```text
--steps ... export-selected
--export-selection-json
--motionbert-export-dir
```

If `--export-selection-json` is omitted, it uses `--selection-output-json`.

## After-Supply Dry Run

Generated artifact:

```text
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

The final dry-run command is:

```text
tools/export_motionbert_selected_bundle.py
  --selection-json outputs/right_conducting/model_candidate_selection_after_supply.json
  --output-dir outputs/right_conducting/selected_motionbert_after_supply
```

## Verification

```bash
python -m unittest discover -s tests -p 'test_motionbert_export.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
python -m unittest discover -s tests -p 'test_*.py' -v
python -m compileall -q lib/right_conducting/motionbert_export.py tools/export_motionbert_selected_bundle.py tests/test_motionbert_export.py
python -m compileall -q tools/run_right_conducting_goal.py tests/test_goal_command_cli.py
python -m compileall -q lib/right_conducting tools tests
```

Result:

```text
motionbert export tests: 3 OK
goal runner tests: 10 OK
full tests: 104 OK
compile OK
```

## Current Status

새 데이터셋은 아직 공급 전이다. 현재 selected live artifact는 계속 feature baseline fallback이다.

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
```

MotionBERT bundle export는 after-supply selection이 `SELECTED`일 때만 실행한다. Export 후 runtime smoke는 Report 36에서 다룬다.
