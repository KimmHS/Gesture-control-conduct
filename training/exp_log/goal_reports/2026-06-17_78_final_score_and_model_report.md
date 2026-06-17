# Report 78 - Final Current Score And Model Report

## Final Decision

Current final model is not TCN.

```text
selected primary model:
  MotionBERT-Lite frozen encoder
  + cached/pooled MotionBERT representation
  + lightweight MLP conducting head

selected handmark-only probe:
  MotionBERT-Lite frozen encoder
  + right_arm_only input mask
  + lightweight MLP conducting head

TCN:
  not selected
  not used as the final model artifact
```

Use two bundles depending on live input availability:

| use case | bundle | status |
|---|---|---|
| full pose / reference-complete handmark stream | `outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext` | primary deployment-fit GO |
| raw handmark stream with only right shoulder / elbow / wrist | `outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe` | handmark-only deployment-fit probe GO |

Important scope statement:

```text
The current result is fixed-camera deployment-fit GO.
Strict heldout generalization is still NO_GO because in-scope strict heldout coverage is missing.
```

## Primary Model Artifact

```text
manifest:
  outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_manifest.json

head checkpoint:
  outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_head.pt

structure:
  outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_structure.md

window:
  45 frames ~= 3.0s at 15fps

stride:
  3 frames

bpm bins:
  60 / 80 / 100 / 120
```

## Handmark-Only Probe Artifact

```text
manifest:
  outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/motionbert_conducting_live_manifest.json

head checkpoint:
  outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/motionbert_conducting_head.pt

input mode:
  right_arm_only

input joints:
  right shoulder / right elbow / right wrist
```

This probe is the relevant artifact when the final stream environment provides raw handmark CSV/right-arm landmarks only.

## 5-GPU Hparam Sweep Summary

Artifact:

```text
outputs/right_conducting/hparam_sweep_static80_transitions_extended_20260617.json
```

| field | value |
|---|---:|
| initial candidates | 20 |
| extended candidates | 34 |
| total candidates | 54 |
| live candidates <= 60f | 46 |
| artifacts complete | true |

Best conservative candidate:

| tag | window | transition samples | tempo acc | gain acc | r80 | r100 | r120 | false/min | p90 delay |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ext_e240_h512_lr3e3_s0_60f` | 60 | 779 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 |

Selected live-fast candidate:

| tag | window | transition samples | tempo acc | gain acc | r80 | r100 | r120 | false/min | p90 delay |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `ext_e240_h512_lr3e3_s0_45f` | 45 | 884 | 0.9989 | 1.0000 | 0.9953 | 1.0000 | 1.0000 | 0.0000 | 0.0000 |

Selection artifact:

```text
outputs/right_conducting/model_candidate_selection_ext_live45f.json
```

Selection status:

```text
status: SELECTED
candidate_count: 54
go_candidate_count: 54
selected window: 45f
```

## Primary Bundle Replay Score

Artifacts:

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_static80_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_transitions_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_replay_gate_transitions_deployment.json
```

Full-backbone streaming replay:

| eval root | sessions | rows | metric mode | tempo acc | gain acc | false/min | missed | p90 delay |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| `dataset/static_variants_80` | 4 | 942 | smoothed | 1.0000 | 1.0000 | 0.0000 | 0 | 0.0000 |
| `dataset/transitions` | 7 | 1305 | smoothed | 1.0000 | 1.0000 | 0.0000 | 0 | 0.0000 |

Deployment live gate:

```text
status: GO
tempo_acc: 1.0000
gain_acc: 1.0000
false_switches_per_min: 0.0000
missed_switch_count: 0
switch_delay_p90_s: 0.0000
```

## Runtime Score

Artifacts:

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/benchmark_transitions_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.md
```

| metric | value |
|---|---:|
| realtime budget pass | true |
| p90 end-to-end inference | 11.6339 ms |
| p95 end-to-end inference | 12.2116 ms |
| max end-to-end inference | 19.5126 ms |
| 200ms stream budget headroom | 17.1911x |
| live runtime readiness | GO |

Runtime readiness currently verifies:

```text
contract: GO
deployment replay gate: GO
benchmark: GO
live output replay: GO
online pose stream: GO
JSONL pose stream: GO
reference-complete handmark CSV stream: GO
pose quality hold gate: GO
```

## Raw Handmark CSV Full-Set Score

Artifacts:

```text
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.md
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.md
outputs/right_conducting/right_conducting_goal_handmark_csv_set_gate_dryrun.md
```

Scope:

```text
csv roots: dataset/static_variants_80,dataset/transitions
csv_count: 15
scoreable processed sessions: 11
excluded: 4 beat-4 CSV-only sessions without processed labels/pose/right_rule_features
window: 45f
stable_only: true
input_format: raw_handmark_csv_right_arm_stream
```

Margin sweep:

| transition margin | samples | mixed excluded | margin excluded | smoothed tempo acc | smoothed gain acc | false/min | p90 delay | missed | r80 | r100 | r120 | BPM MAE |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0s | 2241 | 204 | 6 | 0.9955 | 1.0000 | 0.3689 | 0.1400 | 0 | 0.9926 | 1.0000 | 1.0000 | 0.0982 |
| 3.0s | 1824 | 204 | 423 | 0.9989 | 1.0000 | 0.1230 | 0.0000 | 0 | 0.9983 | 1.0000 | 1.0000 | 0.0219 |

Gate result at 3s margin:

```text
status: GO
eval_session_count: 11
sample_count: 1824
tempo_acc: 0.9989
gain_acc: 1.0000
tempo_80_recall: 0.9983
tempo_100_recall: 1.0000
tempo_120_recall: 1.0000
false_switches_per_min: 0.1230
missed_switch_count: 0
```

Weakest remaining case:

```text
session_20260617_024003_bpm100to100_beat3_small
margin0 tempo_acc: 0.9731
main error: a few 80 BPM windows predicted as 100 BPM
```

## Strict Heldout Status

Artifacts:

```text
outputs/right_conducting/goal_status_selected_motionbert_live45f_ext.json
outputs/right_conducting/goal_status_selected_motionbert_live45f_ext.md
outputs/right_conducting/current_eval_roots_strict_preflight.json
outputs/right_conducting/current_eval_roots_strict_preflight.md
outputs/right_conducting/current_eval_roots_strict_missing_checklist.md
```

Current status:

| item | status | reason |
|---|---|---|
| live pilot | GO | deployment-fit replay/runtime/stream evidence passes |
| strict heldout | NO_GO | in-scope strict heldout coverage missing |
| final goal dashboard | IN_PROGRESS | strict scope and strict replay gate are not complete |

Strict preflight:

```text
status: NO_GO
next_action: record P0 strict heldout cases under dataset/strict_heldout_static_v1 and dataset/strict_heldout_transitions_v1
failed checks:
  strict_scope_go
  strict_scope_p0_complete
  strict_missing_p0_capture_count
```

This means:

```text
Do not claim broad generalization yet.
Current claim is fixed-camera deployment-fit live control.
For strict final reporting, record independent in-scope static/transition heldout sessions and rerun the strict chain.
```

## Final Commands

Re-run raw handmark full-set score/gate:

```bash
python tools/run_right_conducting_goal.py \
  --steps handmark-csv-stream-set-score,handmark-csv-stream-set-gate \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe \
  --handmark-csv-set-root dataset/static_variants_80,dataset/transitions \
  --handmark-csv-set-stable-only \
  --handmark-csv-set-score-json outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.json \
  --handmark-csv-set-score-md outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.md \
  --handmark-csv-set-rows-jsonl outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_rows.jsonl \
  --handmark-csv-set-gate-json outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.json \
  --handmark-csv-set-gate-md outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.md
```

Re-run primary runtime readiness:

```bash
python tools/run_right_conducting_goal.py \
  --steps live-runtime-readiness \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext \
  --live-runtime-readiness-output-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.json \
  --live-runtime-readiness-output-md outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.md
```

Strict heldout chain after new heldout recording:

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence,strict-heldout-scope,strict-heldout-missing-checklist,strict-heldout-preflight,replay-selected,diagnose-replay,live-output,live-replay-gate,goal-status \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/strict_heldout_static_v1,dataset/strict_heldout_transitions_v1 \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext \
  --motionbert-replay-stable-only \
  --live-replay-gate-require-independence
```

## Final Summary

```text
Model used:
  MotionBERT-Lite + MLP conducting head

Model not used:
  TCN

Primary deployment-fit status:
  GO

Raw handmark-only deployment-fit status:
  GO

Realtime readiness:
  GO

Strict heldout/generalization:
  NO_GO

Main remaining risk:
  independent in-scope heldout data is missing
```
