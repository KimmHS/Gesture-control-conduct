# Report 42 - Planned Experiments

## Current State

Authoritative required-data manifest:

```text
docs/exp/right_conducting_required_data_manifest.json
```

Current audit artifact:

```text
outputs/right_conducting/devset_edge_case_audit.json
outputs/right_conducting/devset_edge_case_audit.md
```

Current audit snapshot:

```text
static_session_count: 0
transition_session_count: 11
p0_complete: false
P0 required/present/missing: 10 / 4 / 6
P1 required/present/missing: 4 / 4 / 0
P2 required/present/missing: 2 / 0 / 2
```

The immediate missing data is still fixed-camera 80 BPM static coverage:

```text
dataset/static_variants_80
```

The existing transition stress set is:

```text
dataset/transitions
```

## Experiment Order

| order | experiment | purpose | run condition | pass line | output |
|---:|---|---|---|---|---|
| 0 | Devset coverage audit | Confirm required static/transition edge cases exist | after data copy | `p0_complete=true` | `devset_edge_case_audit.*` |
| 1 | Current-head static 80 score | Check whether stable 80 BPM is recognizable without transition ambiguity | after `dataset/static_variants_80` is present | static 80 recall `>=0.60`, gain acc `>=0.80` | `motionbert_devset_static_score_60f.*` |
| 2 | Current-head transition stress score | Check whether 120->80 held tail is recovered after margin filtering | after static score | transition 80 recall `>=0.50` at margin 3s, gain acc `>=0.80` | `motionbert_devset_transition_score_60f.*` |
| 3 | Devset gate | Combine coverage, static score, transition score | after experiments 0-2 | gate status `GO` | `motionbert_devset_gate_60f.*` |
| 4 | 5-GPU MotionBERT sweep | Train/evaluate frame-window candidates only after devset is meaningful | after gate inputs exist | regular score gate `GO` and devset gate `GO` | `model_gate_after_supply_*f.*`, selection json/md |
| 5 | Selected bundle export | Replace fallback only with a gated MotionBERT model | after selection `SELECTED` | live smoke + replay pass | exported bundle under `outputs/right_conducting` |
| 6 | Failure branch | If gate fails, identify whether failure is stable 80, transition 80, or gain | whenever 1-3 fail | no export; choose next model/data action | next report |

## Planned Commands

### 0. Coverage audit

```bash
python tools/run_right_conducting_goal.py \
  --steps devset-audit \
  --devset-static-root dataset/static_variants_80 \
  --devset-transition-root dataset/transitions \
  --devset-requirements docs/exp/right_conducting_required_data_manifest.json \
  --devset-output-json outputs/right_conducting/devset_edge_case_audit.json \
  --devset-output-md outputs/right_conducting/devset_edge_case_audit.md \
  --output-json outputs/right_conducting/right_conducting_goal_devset_audit.json \
  --output-md outputs/right_conducting/right_conducting_goal_devset_audit.md
```

### 1-3. Static score, transition score, and devset gate

```bash
python tools/run_right_conducting_goal.py \
  --steps devset-audit,motionbert-devset-score,devset-gate \
  --head-output-dir outputs/right_conducting/motionbert_head_after_supply \
  --devset-static-root dataset/static_variants_80 \
  --devset-transition-root dataset/transitions \
  --devset-requirements docs/exp/right_conducting_required_data_manifest.json \
  --devset-output-json outputs/right_conducting/devset_edge_case_audit.json \
  --devset-output-md outputs/right_conducting/devset_edge_case_audit.md \
  --devset-static-score-prefix outputs/right_conducting/motionbert_devset_static_score \
  --devset-transition-score-prefix outputs/right_conducting/motionbert_devset_transition_score \
  --devset-gate-output-prefix outputs/right_conducting/motionbert_devset_gate \
  --window-frames 60 \
  --stride-frames 3 \
  --device cuda:0 \
  --output-json outputs/right_conducting/right_conducting_goal_devset_pipeline.json \
  --output-md outputs/right_conducting/right_conducting_goal_devset_pipeline.md
```

### 4. 5-GPU sweep after devset is scoreable

```bash
python tools/run_right_conducting_goal.py \
  --steps cache,train,detailed,gate,select \
  --dataset-dir outputs/right_conducting/dataset_v0_60f_after_supply \
  --cache-dir outputs/right_conducting/motionbert_cache_after_supply \
  --head-output-dir outputs/right_conducting/motionbert_head_after_supply \
  --detailed-output-prefix outputs/right_conducting/motionbert_detailed_after_supply \
  --gate-output-prefix outputs/right_conducting/model_gate_after_supply \
  --selection-output-json outputs/right_conducting/model_candidate_selection_after_supply.json \
  --selection-output-md outputs/right_conducting/model_candidate_selection_after_supply.md \
  --window-frames 30,60,90,120,150 \
  --stride-frames 3 \
  --devices cuda:0,cuda:1,cuda:2,cuda:3,cuda:4 \
  --parallel-gpu \
  --gate-require-detailed
```

### 5. Selection/export with devset gate required

```bash
python tools/run_right_conducting_goal.py \
  --steps devset-gate,gate,select,export-selected,smoke-selected,replay-selected \
  --head-output-dir outputs/right_conducting/motionbert_head_after_supply \
  --gate-output-prefix outputs/right_conducting/model_gate_after_supply \
  --devset-static-score-prefix outputs/right_conducting/motionbert_devset_static_score \
  --devset-transition-score-prefix outputs/right_conducting/motionbert_devset_transition_score \
  --devset-gate-output-prefix outputs/right_conducting/motionbert_devset_gate \
  --selection-output-json outputs/right_conducting/model_candidate_selection_after_supply_devset_required.json \
  --selection-output-md outputs/right_conducting/model_candidate_selection_after_supply_devset_required.md \
  --motionbert-export-dir outputs/right_conducting/motionbert_selected_live_bundle \
  --window-frames 60 \
  --stride-frames 3 \
  --device cuda:0
```

`devset-gate,gate,select`를 같이 실행하면 selection은 matching devset gate JSON을 자동으로 요구한다.

## Interpretation Rules

Static score:

```text
Primary question: stable 80 BPM을 transition ambiguity 없이 맞추는가?
Primary metric: tempo_per_class_recall["80"]
Do not interpret as switch latency.
```

Transition score:

```text
Primary question: transition_margin_seconds=3 이후에도 held 80 BPM tail을 맞추는가?
Primary metric: tempo_per_class_recall["80"] at margin 3s
Replay switch delay is reference only after margin filtering.
```

Sweep score:

```text
The model must pass both the regular score gate and the fixed-camera devset gate.
If either gate is NO_GO, keep the current fallback and do not export MotionBERT as selected.
```

## If A Step Fails

| failing step | likely meaning | next action |
|---|---|---|
| coverage audit | required devset is incomplete | collect missing static 80 cases first |
| static 80 recall low | model cannot recognize stable 80 under fixed setup | inspect input normalization/features before another hparam sweep |
| transition 80 recall low but static 80 OK | transition adaptation/smoothing issue | evaluate shorter windows and streaming policy |
| gain acc low | amplitude/gain label mismatch | inspect dynamics labels and measured amplitude distribution |
| CV good but devset gate NO_GO | overfit/domain cue collapse | keep fallback; do not export selected MotionBERT |

## Current Decision

```text
Do not start another broad 5-GPU hparam sweep until fixed-camera 80 BPM static devset is present.
After that, run experiments 0-3 first.
Only run export after model selection is SELECTED with devset gate GO.
```

