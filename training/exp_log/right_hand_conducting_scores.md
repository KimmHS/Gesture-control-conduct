# Right-Hand Conducting Scores

이 파일은 current v0 실험 score table이다. 현재 live-facing selected model은 TCN handmark classifier다. MotionBERT 계열 결과는 비교 및 이전 후보로 유지한다.

## Current v0 Scope

```text
fps: about 15
tempo bins: 60 / 80 / 100 / 120
default window: 60 frames ~= 4s
120-frame windows: ~= 8s ablation on current data
```

## TCN Quick Probe

Report:

```text
docs/exp/goal_reports/2026-06-17_79_tcn_quick_probe.md
```

Artifacts:

```text
outputs/right_conducting/tcn_quick_probe_20260617/30f/scores.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/scores.json
outputs/right_conducting/tcn_quick_probe_20260617/60f/scores.json
outputs/right_conducting/tcn_quick_probe_20260617/90f/scores.json
outputs/right_conducting/tcn_quick_probe_20260617/120f/scores.json
```

Scope:

```text
model: causal residual Conv1d TCN
input: right shoulder / right elbow / right wrist pose sequence
roots: dataset/static_variants_80, dataset/transitions
status: deployment-fit quick probe
strict heldout: not proven
```

Margin 3s score:

| window | samples | mixed excl | margin excl | raw tempo | smooth tempo | smooth gain | false/min | p90 delay | r80 | r100 | r120 | bpm mae |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 30 | 1952 | 134 | 420 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 45 | 1827 | 204 | 420 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 60 | 1702 | 274 | 420 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 90 | 1452 | 414 | 420 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 120 | 1202 | 554 | 420 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

Interpretation:

```text
TCN fits the current fixed-camera static80 + transition deployment set easily.
80 BPM stable middle segments are correct after margin removal.
Do not use this as strict generalization evidence because the same processed roots are used for training and scoring.
The current selected live bundle is outputs/right_conducting/selected_tcn_handmark_live45f.
```

## Latest TCN Supplied-Set Full Rerun

Report:

```text
docs/exp/goal_reports/2026-06-17_106_full_test_and_tcn_alltest_rerun.md
docs/exp/goal_reports/2026-06-17_117_full_test_release_and_status_rerun.md
```

Artifacts:

```text
outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.json
outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.md
outputs/right_conducting/tcn_alltest_latest/stream_set_gate_fulltest_latest.json
outputs/right_conducting/tcn_alltest_latest/stream_set_gate_fulltest_latest.md
outputs/right_conducting/tcn_alltest_latest/stream_readiness.json
outputs/right_conducting/tcn_alltest_latest/stream_benchmark.json
outputs/right_conducting/tcn_alltest_latest/tcn_goal_status_fulltest_latest.json
outputs/right_conducting/tcn_alltest_latest/tcn_goal_status_fulltest_latest.md
outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.json
outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.md
outputs/right_conducting/tcn_alltest_latest/current_strict_data_contract_fulltest_latest.json
outputs/right_conducting/tcn_alltest_latest/current_strict_data_contract_fulltest_latest.md
```

Scope:

```text
model: selected TCN handmark live bundle
csv roots: dataset/static_variants_80, dataset/transitions
beat4: excluded
csv_count: 15 discovered raw CSV files
scoreable processed sessions: 11
stable_only: true
strict heldout: not proven
```

Margin sweep:

| margin | samples | mixed | margin_excl | raw tempo | smooth tempo | smooth gain | false/min | p90 | missed | r80 | r100 | r120 | bpm mae |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 2241 | 204 | 6 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 0.5 | 2172 | 204 | 75 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 1.0 | 2103 | 204 | 144 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 2.0 | 1964 | 204 | 283 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 3.0 | 1824 | 204 | 423 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

Runtime:

| status | p90 ms | update budget ms | headroom | stream rows | stdin rows | output contract errors |
|---|---:|---:|---:|---:|---:|---:|
| GO | 1.9984 | 200.0000 | 100.0821 | 216 | 3 | 0 |

Goal status:

| overall | live | strict heldout | reason |
|---|---|---|---|
| IN_PROGRESS | GO | NO_GO | strict roots dataset/strict_heldout_static_v1 and dataset/strict_heldout_transitions_v1 are missing |

TCN 45f handmark CSV live stream score:

```text
report: docs/exp/goal_reports/2026-06-17_80_tcn_handmark_live_stream.md
readiness_report: docs/exp/goal_reports/2026-06-17_81_tcn_handmark_stream_readiness_gate.md
set_score: outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_score.json
set_gate: outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_gate.json
single_stream_summary: outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_summary.json
latency_benchmark: outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_benchmark.json
readiness: outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_handmark_stream_readiness.json
live_manifest: outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_live_manifest.json
```

| margin | samples | mixed | margin_excl | raw tempo | smooth tempo | smooth gain | false/min | p90 | r80 | r100 | r120 | bpm mae |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 2241 | 204 | 6 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 3.0 | 1824 | 204 | 423 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

TCN 45f handmark stream readiness:

| score gate | update p90 ms | update budget ms | headroom | stream rows | invalid | status |
|---|---:|---:|---:|---:|---:|---|
| GO | 1.6180 | 200.0000 | 123.6107 | 216 | 0 | GO |

TCN handmark stream caveat:

```text
This is a real handmark CSV/stdin live path, but the score is still deployment-fit because the same fixed-camera sessions were used to train the TCN checkpoint.
```

## Latest Extended 5-GPU Sweep

Report:

```text
docs/exp/goal_reports/2026-06-17_59_extended_5gpu_hparam_sweep.md
```

Artifacts:

```text
outputs/right_conducting/hparam_sweep_static80_transitions_extended_20260617.json
outputs/right_conducting/hparam_sweep_static80_transitions_extended_20260617.md
outputs/right_conducting/model_candidate_selection_ext_live45f.json
outputs/right_conducting/model_candidate_selection_ext_live45f.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_manifest.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_structure.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_head.pt
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_static80_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_transitions_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_static80_stable_failure_diagnosis.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_transitions_stable_failure_diagnosis.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/benchmark_transitions_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_replay_gate_transitions_deployment.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/jsonl_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/jsonl_stream_transition_022415_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/handmark_csv_stream_transition_022415_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/handmark_csv_ref_stream_transition_022415_summary.json
outputs/right_conducting/goal_status_selected_motionbert_live45f_ext.json
outputs/right_conducting/goal_status_selected_motionbert_live45f_ext.md
```

Current decision:

```text
primary live MotionBERT candidate: GO
primary: ext_e240_h512_lr3e3_s0_45f
conservative 60f: ext_e240_h512_lr3e3_s0_60f
reason: 45f keeps about 3s context at 15fps and improves the old 45f row while preserving zero smoothed false switches.
```

Extended sweep scope:

```text
initial_candidates: 20
extended_candidates: 34
total_candidates: 54
gpu_workers: 5
eval_roots: dataset/static_variants_80, dataset/transitions
transition_margin_seconds: 3
```

Primary live row on `dataset/transitions`, 3s transition margin:

| candidate | window | samples | tempo_acc | bpm_mae | gain_acc | r80 | r100 | r120 | smoothed false/min | p90 delay |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ext_e240_h512_lr3e3_s0_45f | 45 | 884 | 0.9989 | 0.0226 | 1.0000 | 0.9953 | 1.0000 | 1.0000 | 0.0000 | 0.0000 |
| ext_e240_h512_lr3e3_s0_60f conservative | 60 | 779 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 |

Full-backbone live replay of the exported 45f ext bundle:

| eval_root | sessions | rows | mode | tempo_acc | gain_acc | false/min | missed | p90 delay |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| dataset/static_variants_80 | 4 | 942 | smoothed | 1.0000 | 1.0000 | 0.0000 | 0 | 0.0000 |
| dataset/transitions | 7 | 1305 | smoothed | 1.0000 | 1.0000 | 0.0000 | 0 | 0.0000 |

Deployment-fit diagnosis vs current eval diagnosis:

| scope | rows | sessions | smoothed tempo_acc | smoothed gain_acc | smoothed true tempo | smoothed pred tempo | error runs | interpretation |
|---|---:|---:|---:|---:|---|---|---:|---|
| deployment static80 | 942 | 4 | 1.0000 | 1.0000 | 80:942 | 80:942 | 0 | expected constant 80 static behavior |
| deployment transitions | 1305 | 7 | 1.0000 | 1.0000 | 80:422, 100:252, 120:631 | 80:422, 100:252, 120:631 | 0 | fixed-camera transition live pilot passes |
| current eval roots | 544 | 2 | 0.1691 | 0.9412 | 80:16, 100:382, 120:146 | 60:11, 80:388, 100:145 | 9 | independent stress/scope replay fails |

Report:

```text
docs/exp/goal_reports/2026-06-17_68_deployment_vs_current_eval_diagnosis.md
```

Full-backbone live benchmark of the exported 45f ext bundle:

| device | windows | update_budget_ms | end_to_end_p90_ms | max_ms | headroom | status |
|---|---:|---:|---:|---:|---:|---|
| cuda:3 | 1305 | 200.0000 | 11.6339 | 19.5126 | 17.1911 | PASS |

Live runtime readiness gate:

| status | contract | deployment gate | benchmark | live output replay | online stream | JSONL stream | handmark CSV stream | pose quality |
|---|---|---|---|---|---|---|---|---|
| GO | GO | GO | GO | GO | GO | GO | GO | GO |

Artifact:

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.md
```

Label-free and online stream evidence of the exported 45f ext bundle:

| case | mode | rows | tempo classes | raw switches | smoothed switches | invalid | held invalid |
|---|---|---:|---|---:|---:|---:|---:|
| static80 035040 | window scan | 236 | `[1]` | 0 | 0 | 0 | 0 |
| transition 022517 | window scan | 216 | `[1, 3]` | 9 | 2 | 0 | 0 |
| static80 035040 | online buffer | 236 | `[1]` | 0 | 0 | 0 | 0 |
| transition 022517 | online buffer | 216 | `[1, 3]` | 9 | 2 | 0 | 0 |
| static80 035040 | JSONL frame stream | 236 | `[1]` | 0 | 0 | 0 | 0 |
| transition 022415 | JSONL frame stream | 216 | `[1, 3]` | 2 | 2 | 0 | 0 |
| static80 035040 | handmark CSV + reference | 236 | `[1]` | 0 | 0 | 0 | 0 |
| transition 022415 | handmark CSV right-arm only | 216 | `[0, 2, 3]` | 10 | 4 | 0 | 0 |
| transition 022415 | handmark CSV + reference | 216 | `[1, 3]` | 2 | 2 | 0 | 0 |
| degraded static80 035040 | online buffer + quality hold | 236 | `[1]` | 0 | 0 | 28 | 28 |
| degraded transition 022517 | online buffer + quality hold | 216 | `[1, 3]` | 9 | 2 | 28 | 28 |

Online comparison:

```text
status: PASS
window scan and online buffer are identical after ignoring source.source_id.
```

Current consolidated status:

| status | live pilot | strict heldout | reason |
|---|---|---|---|
| IN_PROGRESS | GO | NO_GO | ext bundle passes deployment replay, benchmark, label-free stream, online buffer, JSONL/stdin stream, reference-supplemented handmark CSV stream, and pose-quality evidence; strict heldout scope gate is NO_GO because in-scope 2/3-beat heldout coverage is 0/8; available independent 222455 stress also fails |

Current eval strict chain execution:

| eval roots | independence | scope | rows | tempo_acc | gain_acc | false/min | missed | goal status |
|---|---|---|---:|---:|---:|---:|---:|---|
| dataset/evaluation,dataset/evaluation_transitions | GO | NO_GO | 544 | 0.1691 | 0.9412 | 5.7848 | 1 | IN_PROGRESS |

Artifact:

```text
docs/exp/goal_reports/2026-06-17_66_current_eval_strict_chain_execution.md
docs/exp/goal_reports/2026-06-17_67_replay_failure_diagnosis.md
outputs/right_conducting/goal_status_current_eval_roots_ext_chain.json
outputs/right_conducting/current_eval_roots_live_gate_ext_chain.json
outputs/right_conducting/current_eval_roots_replay_failure_diagnosis_ext_chain.json
outputs/right_conducting/current_eval_roots_strict_missing_checklist.md
outputs/right_conducting/current_eval_roots_strict_preflight.md
```

Current eval failure diagnosis:

| session | rows | true tempo | smoothed tempo | tempo acc | dominant issue |
|---|---:|---|---|---:|---|
| 222455 | 258 | 80:16, 100:96, 120:146 | 60:11, 80:118, 100:129 | 0.2946 | 120 is never predicted; 120 -> 80/100 |
| 215630 | 286 | 100:286 | 80:270, 100:16 | 0.0559 | constant true label and near-collapse to 80 |

Available independent heldout stress:

| eval session | independence | rows | tempo_acc | gain_acc | false/min | missed | status | note |
|---|---|---:|---:|---:|---:|---:|---|---|
| dataset/evaluation/session_20260616_222455_bpm120_beat4_large | GO | 258 | 0.2946 | 0.8760 | 10.5151 | 1 | NO_GO | 4-beat/mixed timeline stress, outside current 2/3-beat dev target |

Strict heldout scope audit:

| roots | independence | scope status | P0 required | P0 present | P0 missing | note |
|---|---|---|---:|---:|---:|---|
| dataset/evaluation,dataset/evaluation_transitions | GO | NO_GO | 8 | 0 | 8 | current evaluation roots are independent but do not cover 2/3-beat fixed-camera heldout scope |

Strict heldout recording checklist:

```text
outputs/right_conducting/current_eval_roots_strict_missing_checklist.md
```

Strict heldout preflight gate:

| status | independence | scope | P0 present | P0 missing | P0 capture count | next action |
|---|---|---|---:|---:|---:|---|
| NO_GO | GO | NO_GO | 0 | 8 | 8 | record P0 strict heldout cases under `dataset/strict_heldout_static_v1` and `dataset/strict_heldout_transitions_v1` |

Artifact:

```text
outputs/right_conducting/current_eval_roots_strict_preflight.md
```

Goal status strict checks:

| check | value | passed | detail |
|---|---|---:|---|
| heldout_independence_go | GO | true | status gate |
| strict_heldout_scope_go | NO_GO | false | status=NO_GO, p0_complete=False |
| strict_live_gate_go | NO_GO | false | status gate |

Smoothed tempo confusion on 222455:

| true BPM | support | pred 60 | pred 80 | pred 100 | pred 120 |
|---:|---:|---:|---:|---:|---:|
| 80 | 16 | 2 | 14 | 0 | 0 |
| 100 | 96 | 9 | 25 | 62 | 0 |
| 120 | 146 | 0 | 79 | 67 | 0 |

Strict interpretation:

```text
222455 proves that the current selected bundle should not be claimed as generally robust to 4-beat or mixed-timeline heldout conducting.
For the current 2/3-beat fixed-camera target, a separate independent heldout set is still needed.
```

Important caveat:

```text
dataset/transitions is included in the deployment-fit training source for this sweep.
dataset/static_variants_80 is also included in that training source.
Use these numbers as fixed-camera deployment-fit scores, not independent subject/session generalization.
For strict heldout reporting, record a new fixed-camera transition set and keep it out of training.
```

## Right-Arm-Only Handmark Probe

Report:

```text
docs/exp/goal_reports/2026-06-17_74_right_arm_only_input_mask_probe.md
```

Artifacts:

```text
outputs/right_conducting/model_candidate_selection_right_arm_only_live45f_probe.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/motionbert_conducting_live_manifest.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/motionbert_conducting_live_structure.md
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/motionbert_conducting_head.pt
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/replay_static80_transitions_stable.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/live_replay_gate_deployment_fit.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/benchmark_transitions_stable.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_transition_022415_summary.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.md
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.md
```

Right-arm-only sweep:

| window | CV tempo | old 222455 tempo | old 222455 r120 | devset margin3 tempo | devset r80 | devset r120 | devset gate |
|---:|---:|---:|---:|---:|---:|---:|---|
| 30 | 0.7478 | 0.2637 | 0.0000 | 0.9494 | 0.9675 | 0.9887 | GO |
| 45 | 0.7796 | 0.3605 | 0.0068 | 0.9955 | 0.9858 | 1.0000 | GO |
| 60 | 0.7724 | 0.3128 | 0.0000 | 0.9974 | 0.9943 | 1.0000 | GO |
| 90 | 0.7548 | 0.3380 | 0.0000 | 0.9947 | 0.9906 | 1.0000 | GO |
| 120 | 0.7297 | 0.1563 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | GO |

Exported 45f probe replay:

| scope | rows | smoothed tempo_acc | smoothed gain_acc | false/min | missed | p90 delay | status |
|---|---:|---:|---:|---:|---:|---:|---|
| static80 + transitions deployment-fit | 2247 | 0.9951 | 1.0000 | 0.3681 | 0 | 0.2734 | GO |

Raw handmark CSV without reference joints:

| case | rows | tempo classes | raw switches | smoothed switches | invalid |
|---|---:|---|---:|---:|---:|
| static80 035040 | 236 | `[1]` | 0 | 0 | 0 |
| transition 022415 | 216 | `[1, 3]` | 4 | 2 | 0 |

Raw handmark CSV full set score:

Report:

```text
docs/exp/goal_reports/2026-06-17_75_raw_handmark_csv_stream_set_score.md
```

| margin_s | samples | mixed_excluded | margin_excluded | raw_tempo | smooth_tempo | smooth_gain | false/min | p90_s | missed | r80 | r100 | r120 | BPM MAE |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 2241 | 204 | 6 | 0.9946 | 0.9955 | 1.0000 | 0.3689 | 0.1400 | 0 | 0.9926 | 1.0000 | 1.0000 | 0.0982 |
| 1.0 | 2103 | 204 | 144 | 0.9971 | 0.9976 | 1.0000 | 0.2459 | 0.0000 | 0 | 0.9961 | 1.0000 | 1.0000 | 0.0476 |
| 3.0 | 1824 | 204 | 423 | 0.9978 | 0.9989 | 1.0000 | 0.1230 | 0.0000 | 0 | 0.9983 | 1.0000 | 1.0000 | 0.0219 |

Raw handmark CSV stream set gate:

```text
report: docs/exp/goal_reports/2026-06-17_76_handmark_csv_stream_set_gate.md
runner_report: docs/exp/goal_reports/2026-06-17_77_goal_runner_handmark_csv_set_gate.md
status: GO
margin: 3s
thresholds: tempo_acc >= 0.98, gain_acc >= 0.95, r80/r100/r120 >= 0.90, false/min <= 0.5, missed == 0
artifact: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.json
goal_dryrun: outputs/right_conducting/right_conducting_goal_handmark_csv_set_gate_dryrun.md
```

Weakest margin-3 session:

```text
session_20260617_024003_bpm100to100_beat3_small
tempo_acc: 0.9841
r80: 0.9333
r100: 1.0000
error: two 80 BPM windows predicted as 100 BPM
```

Important caveat:

```text
The right-arm-only probe is fixed-camera deployment-fit only.
The primary final bundle remains selected_motionbert_static80_transitions_live45f_ext.
Use the right-arm-only probe only when live input has right shoulder/elbow/wrist but no reference joints.
Strict heldout generalization remains NO_GO until new in-scope heldout data is recorded outside the staged training manifest.
```

## Latest Static80 + Transition 5-GPU Sweep

Report:

```text
docs/exp/goal_reports/2026-06-17_47_static80_transition_5gpu_hparam_sweep.md
```

Artifacts:

```text
outputs/right_conducting/hparam_sweep_static80_transitions_20260617.json
outputs/right_conducting/hparam_sweep_static80_transitions_20260617.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_structure.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_head.pt
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_static80_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_transitions_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/policy_sweep_transitions_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/benchmark_transitions_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/heldout_independence_static80_transitions.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_replay_gate_transitions_deployment.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_replay_gate_transitions_strict.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_output_contract.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_output_sample.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_outputs_static80_stable.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_outputs_transitions_stable.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/pose_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/pose_stream_transition_022517_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_transition_022517_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_comparison.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/degraded_online_pose_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/degraded_online_pose_stream_transition_022517_summary.json
outputs/right_conducting/goal_status_selected_motionbert_live45f.json
```

Current decision:

```text
primary live MotionBERT candidate: GO
primary: static80_transitions_e120_h512_lr3e3_45f
fallback: static80_transitions_e160_h512_lr1e3_60f
reason: 45f gives about 3s context at 15fps, best <=60f transition score, and zero smoothed false switches after policy sweep.
```

Primary live row on `dataset/transitions`, 3s transition margin:

| candidate | window | samples | tempo_acc | bpm_mae | gain_acc | r80 | r100 | r120 | smoothed false/min | p90 delay |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| e120_h512_lr3e3 | 45 | 884 | 0.9943 | 0.1131 | 1.0000 | 0.9810 | 0.9948 | 1.0000 | 0.1993 | 0.0000 |
| e160_h512_lr1e3 fallback | 60 | 779 | 0.9936 | 0.1284 | 1.0000 | 0.9886 | 0.9884 | 0.9977 | 0.0000 | 0.0000 |

Live policy sweep on the exported 45f bundle:

| policy | switch_threshold | fast_switch_threshold | confirm | tempo_acc | gain_acc | pred_switch | false_switch | false/min | missed | p90 delay |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 0.58 | 0.78 | 2 | 0.9893 | 1.0000 | 22 | 4 | 0.7971 | 0 | 0.0000 |
| selected | 0.72 | 0.90 | 2 | 0.9893 | 1.0000 | 14 | 0 | 0.0000 | 0 | 0.5938 |

Full-backbone live replay of the exported 45f bundle:

| eval_root | sessions | rows | mode | tempo_acc | gain_acc | false/min | missed | p90 delay |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| dataset/static_variants_80 | 4 | 942 | smoothed | 1.0000 | 1.0000 | 0.0000 | 0 | 0.0000 |
| dataset/transitions | 7 | 1305 | smoothed | 0.9893 | 1.0000 | 0.0000 | 0 | 0.5938 |

Live replay gate:

| gate | require independence | status | tempo_acc | gain_acc | false/min | missed | p90 delay | reason |
|---|---|---|---:|---:|---:|---:|---:|---|
| deployment-fit | false | GO | 0.9893 | 1.0000 | 0.0000 | 0 | 0.5938 | replay thresholds pass |
| strict heldout | true | NO_GO | 0.9893 | 1.0000 | 0.0000 | 0 | 0.5938 | heldout independence is NO_GO |

Full-backbone live benchmark of the exported 45f bundle:

| device | windows | update_budget_ms | end_to_end_p90_ms | max_ms | headroom | status |
|---|---:|---:|---:|---:|---:|---|
| cuda:2 | 1305 | 200.0000 | 12.1389 | 16.0964 | 16.4759 | PASS |

Current weak edge:

```text
session_20260617_022517_bpm120to120_beat3_small
120 -> 80 -> 120, 3-beat, small dynamics; no false switch remains, but this has the largest smoothed delay p90.
```

Important caveat:

```text
dataset/transitions is included in the deployment-fit training source for this sweep.
dataset/static_variants_80 is also included in that training source.
strict heldout independence status: NO_GO
root conflicts: 2
session path overlaps: 11
Use these numbers as fixed-camera deployment-fit scores, not independent subject/session generalization.
For strict heldout reporting, record a new fixed-camera transition set and keep it out of training.
```

Current consolidated status:

| status | live pilot | strict heldout | reason |
|---|---|---|---|
| IN_PROGRESS | GO | NO_GO | strict heldout independence and strict live replay gate are not GO |

Live/MIDI output contract:

```text
schema_version: right_conducting_live_output_v1
tempo_bpm source: smoothed bpm
velocity_scale: smoothed dynamics -> 0.35..1.00
cc11_expression: smoothed dynamics -> 32..127
sample: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_output_sample.json
```

Live output replay rows:

| source | rows | tempo classes | gain classes | artifact |
|---|---:|---|---|---|
| static80 stable | 942 | `[1]` | `[0, 1]` | `live_outputs_static80_stable.jsonl` |
| transitions stable | 1305 | `[1, 2, 3]` | `[0, 1]` | `live_outputs_transitions_stable.jsonl` |

Label-free pose stream rows:

| source | rows | tempo classes | raw switches | smoothed switches | labels used |
|---|---:|---|---:|---:|---|
| static80 high-arm small | 236 | `[1]` | 0 | 0 | no |
| transition 022517 beat3 small | 216 | `[1, 3]` | 6 | 2 | no |

Online frame-buffer rows:

| source | rows | tempo classes | raw switches | smoothed switches | comparison |
|---|---:|---|---:|---:|---|
| static80 high-arm small | 236 | `[1]` | 0 | 0 | window-scan match |
| transition 022517 beat3 small | 216 | `[1, 3]` | 6 | 2 | window-scan match |

`online_pose_stream_comparison.json` status is `PASS`, ignoring only `source.source_id`.

Pose quality gate rows:

| source | rows | invalid | held invalid | tempo classes | smoothed switches |
|---|---:|---:|---:|---|---:|
| degraded static80 high-arm small | 236 | 28 | 28 | `[1]` | 0 |
| degraded transition 022517 beat3 small | 216 | 28 | 28 | `[1, 3]` | 2 |

## Previous 5-GPU MotionBERT Sweep

Report:

```text
docs/exp/goal_reports/2026-06-17_38_5gpu_hparam_sweep_transition_stress.md
```

Artifacts:

```text
outputs/right_conducting/hparam_sweep_summary_20260617.json
outputs/right_conducting/hparam_sweep_summary_20260617.md
outputs/right_conducting/dataset_intake_after_transitions_schedule.json
outputs/right_conducting/dataset_intake_after_transitions_schedule.md
```

Current decision:

```text
MotionBERT selected replacement: NO_GO
selected live fallback replacement: NO
reason: every hparam candidate fails heldout transition tempo gate
```

Best row on the current scoreable `222455` stable transition eval:

| candidate | window | status | cv_acc | 222455_acc | bpm_mae | gain_acc | r80 | r120 |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| h512_lr3e4_e120 | 90 | NO_GO | 0.7424 | 0.3756 | 14.5540 | 0.7746 | 0.0000 | 0.0000 |

Representative `dataset/transitions` stress rows after `3s` transition margin:

| candidate | window | samples | tempo_acc | bpm_mae | gain_acc | r80 | r100 | r120 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| h1024_lr3e4_e120_120f | 120 | 570 | 0.5035 | 10.2105 | 0.8351 | 0.0000 | 0.3978 | 0.6554 |
| h512_lr1e3_e80_30f | 30 | 1560 | 0.4128 | 14.1026 | 0.9679 | 0.0000 | 0.3873 | 0.6430 |
| h512_lr3e4_e120_90f | 90 | 900 | 0.4556 | 11.7778 | 0.9689 | 0.0000 | 0.3684 | 0.6710 |

Interpretation:

```text
The failure is not explained by transition-edge ambiguity alone.
On 222455, candidates collapse away from 120 BPM.
On dataset/transitions, candidates recover 120 moderately but collapse away from 80 BPM.
More MotionBERT head hparam tuning alone is not the next bottleneck.
```

Next devset needed:

```text
80 BPM fixed-camera static variants under meter/dynamics changes
120 -> 80 -> 120 heldout transitions after transition-margin exclusion
```

## Required Rows

```text
rule_based                 # measured
handcrafted_feature_ml     # measured
motionbert_lite_head       # measured, current pooled-head candidate is no-go for tempo
```

## Score Extraction Checklist

Offline window classification score:

```text
run_name
model_type
feature_subset
normalization
eval_set
fold_or_subject
window_frames
eval_stride_frames
stable_only
sample_count
mixed_bpm_excluded_count
tempo_acc
tempo_macro_precision
tempo_macro_recall
tempo_macro_f1
tempo_weighted_precision
tempo_weighted_recall
tempo_weighted_f1
tempo_per_class_precision
tempo_per_class_recall
tempo_per_class_f1
tempo_per_class_support
bpm_mae_window
bpm_mae_take
bpm_distribution_kl
gain_acc
gain_macro_precision
gain_macro_recall
gain_macro_f1
gain_weighted_precision
gain_weighted_recall
gain_weighted_f1
gain_per_class_precision
gain_per_class_recall
gain_per_class_f1
gain_per_class_support
dynamics_mae_window
dynamics_mae_take
dynamics_corr
avg_inference_ms
notes
```

Streaming replay score:

```text
artifact
eval_session
window_frames
stride_frames
row_count
stable_only
switch_threshold
fast_switch_threshold
confirm_updates
mode                         # raw / smoothed
tempo_acc
gain_acc
tempo_macro_precision
tempo_macro_recall
tempo_macro_f1
gain_macro_precision
gain_macro_recall
gain_macro_f1
true_switch_count
pred_switch_count
false_switch_count
false_switches_per_min
switch_delay_mean_s
switch_delay_p90_s
missed_switch_count
notes
```

Label/eval coverage metadata:

```text
eval_session
frame_count
window_count
stable_window_count
mixed_bpm_window_count
tempo_class_counts
bpm_target_counts
gain_class_counts
has_manual_timeline
excluded_reason
```

## Standard Result Output Contract

앞으로 실험 결과는 아래 묶음으로 뽑는다. 핵심 원칙은 stable train/CV, old transition eval, new transition stress를 섞지 않고 같은 column schema로 비교하는 것이다.

Recommended artifacts:

```text
outputs/right_conducting/<run_name>_score_summary.json
outputs/right_conducting/<run_name>_score_summary.md
outputs/right_conducting/<run_name>_score_tables.csv
outputs/right_conducting/<run_name>_graphs/
```

### 1. Overall Model Comparison

Main score table. One row per model / dataset / window size.

| column | note |
|---|---|
| run_name | unique run id |
| model_type | feature_baseline / motionbert_lite_head / rule_based |
| data_source | stable_cv / old_transition_eval / new_transition_stress |
| eval_set | exact eval set name |
| window_frames | 30 / 45 / 60 / 90 / 120 |
| stride_frames | eval stride |
| sample_count | scored windows |
| tempo_acc | overall tempo accuracy |
| tempo_macro_precision | macro precision |
| tempo_macro_recall | macro recall |
| tempo_macro_f1 | macro F1 |
| bpm_mae_window | window-level BPM MAE |
| gain_acc | gain class accuracy |
| gain_macro_precision | gain macro precision |
| gain_macro_recall | gain macro recall |
| gain_macro_f1 | gain macro F1 |
| dynamics_mae_window | continuous dynamics MAE |
| avg_inference_ms | realtime cost |
| status | GO / NO_GO / selected |
| notes | label caveat / augmentation caveat |

### 2. Window Size Sweep

This table checks whether context length helps or hurts.

| window_frames | tempo_acc | tempo_macro_f1 | bpm_mae_window | 80_recall | 100_recall | 120_recall | gain_acc | gain_macro_f1 | status |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 30 |  |  |  |  |  |  |  |  |  |
| 45 |  |  |  |  |  |  |  |  |  |
| 60 |  |  |  |  |  |  |  |  |  |
| 90 |  |  |  |  |  |  |  |  |  |
| 120 |  |  |  |  |  |  |  |  |  |

### 3. Transition Margin Sweep

This table checks whether errors are caused by ambiguous transition boundaries.

| margin_s | sample_count | mixed_excluded | margin_excluded | tempo_acc | tempo_macro_f1 | bpm_mae_window | 80_recall | 100_recall | 120_recall | gain_acc | dynamics_mae_window |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0 |  |  |  |  |  |  |  |  |  |  |  |
| 0.5 |  |  |  |  |  |  |  |  |  |  |  |
| 1.0 |  |  |  |  |  |  |  |  |  |  |  |
| 2.0 |  |  |  |  |  |  |  |  |  |  |  |
| 3.0 |  |  |  |  |  |  |  |  |  |  |  |

### 4. Per-Class Tempo Metrics

Use this table for every important eval set.

| bpm_class | precision | recall | f1 | support | common_wrong_predictions |
|---:|---:|---:|---:|---:|---|
| 60 |  |  |  |  |  |
| 80 |  |  |  |  |  |
| 100 |  |  |  |  |  |
| 120 |  |  |  |  |  |

### 5. Per-Class Gain Metrics

Accuracy alone is not enough because the current heldout gain labels can be imbalanced.

| gain_class | precision | recall | f1 | support |
|---|---:|---:|---:|---:|
| small |  |  |  |  |
| large |  |  |  |  |

### 6. Streaming Replay Metrics

This table decides whether offline accuracy survives live-style smoothing.

| mode | tempo_acc | gain_acc | false_switches_per_min | true_switch_count | pred_switch_count | missed_switch_count | switch_delay_mean_s | switch_delay_p90_s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| raw |  |  |  |  |  |  |  |  |
| smoothed |  |  |  |  |  |  |  |  |

### 7. Dataset Coverage

Use this before reporting scores so the reader can see what data was actually scored.

| split | session | bpm_sequence | meter | dynamics_label | frames | duration_s | scoreable | excluded_reason |
|---|---|---|---:|---|---:|---:|---|---|
| train |  |  |  |  |  |  |  |  |
| eval |  |  |  |  |  |  |  |  |
| stress |  |  |  |  |  |  |  |  |

### 8. Required Graphs

| graph | x-axis | y-axis | purpose |
|---|---|---|---|
| window_size_vs_score | window_frames | tempo_acc / macro_f1 / bpm_mae | context length tradeoff |
| margin_vs_score | margin_s | tempo_acc / 80_recall / bpm_mae | transition-boundary ambiguity check |
| tempo_confusion_matrix | predicted BPM | true BPM | wrong class diagnosis |
| per_class_recall_f1 | BPM class | recall / F1 | weak tempo class diagnosis |
| gain_per_class_f1 | gain class | F1 / support | small-vs-large imbalance check |
| true_pred_timeline | time_s | true BPM and predicted BPM | switch timing and delay diagnosis |
| bpm_error_histogram | predicted BPM - true BPM | count | error distribution |
| gain_true_pred_line | time_s | true/pred dynamics | gain stability |
| per_session_heatmap | session | metric | session-specific failure |

### 9. Decision Gate

Report the gate result next to every candidate.

| check | threshold |
|---|---:|
| cv_tempo_acc | >= 0.70 |
| cv_gain_acc | >= 0.95 |
| transition_tempo_acc | >= 0.60 |
| transition_bpm_mae_window | <= 10.0 |
| transition_gain_acc | >= 0.80 |
| tempo_80_recall | >= 0.50 |
| tempo_120_recall | >= 0.50 |
| false_switches_per_min | as low as selected fallback |
| switch_delay_p90_s | <= selected fallback |

Decision labels:

```text
selected    exported or current live fallback
GO          passes all gates but not necessarily exported
NO_GO       fails one or more required gates
DIAG_ONLY   useful diagnostic, not a live candidate
```

## Required Score Columns

Canonical report columns for the main score table:

```text
run_name
model_type
normalization
window_frames
eval_set
fold_or_subject
tempo_acc
tempo_macro_precision
tempo_macro_recall
tempo_macro_f1
bpm_mae_window
bpm_mae_take
bpm_distribution_kl
gain_acc
gain_macro_precision
gain_macro_recall
gain_macro_f1
dynamics_mae_window
dynamics_mae_take
dynamics_corr
tempo_false_switches_per_min
dynamics_false_switches_per_min
tempo_switch_latency_p90_s
dynamics_switch_latency_p90_s
avg_inference_ms
notes
```

## Current Evaluation Status

Scoreable now:

```text
dataset/evaluation/session_20260616_222455_bpm120_beat4_large
dataset/transitions
```

Scoring must read only original eval artifacts:

```text
labels_frame.jsonl
labels_window.jsonl
pose_right_h36m_masked.npy
right_rule_features.npy
```

Exclude eval-local augmentation artifacts from score computation:

```text
recommended_augmented_v0/
labels_tempo_augmented_15f.jsonl
tempo_augmented_15f.npy
```

`manual_timeline.json` has an ambiguous event at `33.0s`; transition reports must state the mixed/ambiguous-window handling rule.

Pending relabel:

```text
dataset/evaluation_transitions/session_20260616_215630_bpm100_beat4_large
```

Do not report `session_20260616_215630_bpm100_beat4_large` scores until its tempo transition labels are regenerated.

Historical sections below may still use the old short names `session_20260616_222455_eval` and
`session_20260616_215630_eval`; the authoritative current filesystem paths are the paths in this
section.

## Current Baseline Results

Generated by:

```bash
python tools/evaluate_right_conducting_baselines.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --output-json outputs/right_conducting/baseline_scores_v0_60f.json \
  --output-md outputs/right_conducting/baseline_scores_v0_60f.md
```

Artifacts:

```text
outputs/right_conducting/baseline_scores_v0_60f.json
outputs/right_conducting/baseline_scores_v0_60f.md
```

Notes:

- `cv_val` uses take-level 3-fold validation from `outputs/right_conducting/dataset_v0_60f`.
- `feature_baseline_v0_60f` trains nearest-centroid classifiers on original train windows only.
- `rule_based_fft_amp_v0_60f` uses wrist-y FFT for tempo and wrist amplitude threshold for gain.
- `transition_eval_222455` uses original eval artifacts only. It does not read `recommended_augmented_v0`, `labels_tempo_augmented_15f.jsonl`, `tempo_augmented_15f.npy`, or `label_backup_*`.
- Switch latency and false switch metrics are not reported yet because current heldout transition labeling is still too weak.

| run_name | model_type | eval_set | fold_or_subject | window_frames | tempo_acc | tempo_macro_f1 | bpm_mae_window | bpm_mae_take | gain_acc | gain_macro_f1 | dynamics_mae_window | dynamics_corr | avg_inference_ms | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| feature_baseline_v0_60f | handcrafted_feature_ml | cv_val | fold_0 | 60 | 0.4766 | 0.4657 | 11.7560 | 12.7236 | 0.9851 | 0.9848 | 0.0089 | 0.9700 | 0.0005 | nearest-centroid on pose window features; train uses original windows only |
| rule_based_fft_amp_v0_60f | rule_based | cv_val | fold_0 | 60 | 0.2087 | 0.0863 | 34.9330 | 30.0000 | 0.9624 | 0.9618 | 0.0225 | 0.9264 | 0.2396 | FFT wrist-y tempo and wrist amplitude gain threshold |
| feature_baseline_v0_60f | handcrafted_feature_ml | cv_val | fold_1 | 60 | 0.5054 | 0.5098 | 16.2261 | 18.2038 | 0.9948 | 0.9946 | 0.0031 | 0.9893 | 0.0004 | nearest-centroid on pose window features; train uses original windows only |
| rule_based_fft_amp_v0_60f | rule_based | cv_val | fold_1 | 60 | 0.2104 | 0.0885 | 34.3167 | 29.7943 | 0.8948 | 0.8945 | 0.0631 | 0.8091 | 0.2821 | FFT wrist-y tempo and wrist amplitude gain threshold |
| feature_baseline_v0_60f | handcrafted_feature_ml | cv_val | fold_2 | 60 | 0.5637 | 0.4976 | 15.0586 | 17.7313 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.0006 | nearest-centroid on pose window features; train uses original windows only |
| rule_based_fft_amp_v0_60f | rule_based | cv_val | fold_2 | 60 | 0.2108 | 0.0904 | 33.8345 | 29.6550 | 0.6419 | 0.6258 | 0.2149 | 0.4526 | 0.3246 | FFT wrist-y tempo and wrist amplitude gain threshold |
| feature_baseline_v0_60f | handcrafted_feature_ml | cv_val | cv_mean | 60 | 0.5152 | 0.4911 | 14.3469 | 16.2196 | 0.9933 | 0.9931 | 0.0040 | 0.9864 | 0.0005 | mean over 3 take-level folds |
| rule_based_fft_amp_v0_60f | rule_based | cv_val | cv_mean | 60 | 0.2100 | 0.0884 | 34.3614 | 29.8164 | 0.8330 | 0.8274 | 0.1002 | 0.7294 | 0.2821 | mean over 3 take-level folds |
| feature_baseline_v0_60f | handcrafted_feature_ml | transition_eval_222455 | session_20260616_222455_eval | 120 | 0.5344 | 0.2721 | 9.3130 | 9.3130 | 0.8168 | 0.4876 | 0.1099 | -0.0194 | 0.0008 | trained on all v0 original 60f windows; eval uses original labels_window only |
| rule_based_fft_amp_v0_60f | rule_based | transition_eval_222455 | session_20260616_222455_eval | 120 | 0.0000 | 0.0000 | 51.2977 | 51.2977 | 0.5649 | 0.4758 | 0.2611 | 0.2810 | 0.3163 | early heldout only; ambiguous 33s timeline remains caveat |

## Current MotionBERT-Lite Head Results

Generated by:

```bash
python tools/smoke_motionbert_conducting.py \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --device cuda:0 \
  --output outputs/right_conducting/motionbert_smoke_v0.json

python tools/cache_motionbert_conducting_features.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --device cuda:0 \
  --output-dir outputs/right_conducting/motionbert_cache_v0_60f

python tools/train_motionbert_conducting_head.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --cache-dir outputs/right_conducting/motionbert_cache_v0_60f \
  --zip dataset/recordings.zip \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --device cuda:0 \
  --epochs 60 \
  --hidden-dim 256 \
  --lr 0.001 \
  --output-dir outputs/right_conducting/motionbert_head_v0_60f
```

Artifacts:

```text
outputs/right_conducting/motionbert_smoke_v0.json
outputs/right_conducting/motionbert_cache_v0_60f/pooled_right_arm.npy
outputs/right_conducting/motionbert_head_v0_60f/scores.json
outputs/right_conducting/motionbert_head_v0_60f/fold_0_head.pt
outputs/right_conducting/motionbert_head_v0_60f/fold_1_head.pt
outputs/right_conducting/motionbert_head_v0_60f/fold_2_head.pt
outputs/right_conducting/motionbert_head_v0_60f/all_train_head.pt
```

Smoke result:

```text
checkpoint: checkpoint/mb_lite_v0.pt
device: cuda:0
missing_keys: []
unexpected_keys: []
T=60 representation: [2, 60, 17, 512]
T=120 representation: [2, 120, 17, 512]
cached pooled feature shape: [8006, 512]
```

| run_name | model_type | eval_set | fold_or_subject | window_frames | tempo_acc | tempo_macro_f1 | bpm_mae_window | bpm_mae_take | gain_acc | gain_macro_f1 | dynamics_mae_window | dynamics_corr | avg_inference_ms | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| motionbert_lite_head_v0_60f | motionbert_lite_head | cv_val | fold_0 | 60 | 0.4144 | 0.3328 | 16.0640 | 19.1766 | 0.8869 | 0.8861 | 0.1384 | 0.8215 | 0.0022 | frozen MotionBERT-Lite pooled right-arm reps; head trained on original train windows |
| motionbert_lite_head_v0_60f | motionbert_lite_head | cv_val | fold_1 | 60 | 0.3340 | 0.3049 | 16.9974 | 18.3408 | 0.9813 | 0.9807 | 0.0781 | 0.9381 | 0.0002 | frozen MotionBERT-Lite pooled right-arm reps; head trained on original train windows |
| motionbert_lite_head_v0_60f | motionbert_lite_head | cv_val | fold_2 | 60 | 0.4277 | 0.3167 | 18.0582 | 21.0180 | 0.9588 | 0.9583 | 0.1035 | 0.9019 | 0.0001 | frozen MotionBERT-Lite pooled right-arm reps; head trained on original train windows |
| motionbert_lite_head_v0_60f | motionbert_lite_head | cv_val | cv_mean | 60 | 0.3920 | 0.3181 | 17.0398 | 19.5118 | 0.9423 | 0.9417 | 0.1067 | 0.8872 | 0.0008 | mean over 3 take-level folds |
| motionbert_lite_head_v0_60f | motionbert_lite_head | transition_eval_222455 | session_20260616_222455_eval | 120 | 0.2824 | 0.1905 | 23.2061 | 23.2061 | 0.8550 | 0.4609 | 0.1196 | 0.1913 | 7.4972 | all-train head; eval uses original labels_window only; ambiguous 33s caveat |

Hyperparameter check:

```text
e200_h512 run:
  cv_mean tempo_acc: 0.3859
  transition_eval_222455 tempo_acc: 0.2366
  cv_mean gain_acc: 0.9507
  transition_eval_222455 gain_acc: 0.9237
```

Longer training and larger hidden dimension did not improve tempo over the e60/h256 run.

## MotionBERT-Lite Stats Feature Check

This run tests the diagnosis that mean pooling removes tempo information. It caches right-arm representation statistics instead of only a mean vector.

Generated by:

```bash
python tools/cache_motionbert_conducting_features.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --device cuda:0 \
  --batch-size 64 \
  --feature-mode mean_std_delta \
  --output-dir outputs/right_conducting/motionbert_cache_v0_60f_stats

python tools/train_motionbert_conducting_head.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --cache-dir outputs/right_conducting/motionbert_cache_v0_60f_stats \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --device cuda:0 \
  --epochs 80 \
  --hidden-dim 512 \
  --lr 0.001 \
  --output-dir outputs/right_conducting/motionbert_head_v0_60f_stats_e80_h512
```

Artifacts:

```text
outputs/right_conducting/motionbert_cache_v0_60f_stats/manifest.json
outputs/right_conducting/motionbert_cache_v0_60f_stats/pooled_right_arm.npy
outputs/right_conducting/motionbert_head_v0_60f_stats_e80_h512/scores.json
outputs/right_conducting/motionbert_head_v0_60f_stats_e80_h512/all_train_head.pt
```

Feature mode:

```text
mean_std_delta
feature_shape: [8006, 2048]
```

| run_name | model_type | eval_set | fold_or_subject | window_frames | tempo_acc | tempo_macro_f1 | bpm_mae_window | bpm_mae_take | gain_acc | gain_macro_f1 | dynamics_mae_window | dynamics_corr | avg_inference_ms | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| motionbert_lite_head_stats_v0_60f | motionbert_lite_head | cv_val | fold_0 | 60 | 0.5249 | 0.4561 | 12.5223 | 14.9674 | 0.9918 | 0.9916 | 0.0585 | 0.9617 | 0.0003 | frozen MotionBERT-Lite mean_std_delta right-arm reps; head trained on original train windows |
| motionbert_lite_head_stats_v0_60f | motionbert_lite_head | cv_val | fold_1 | 60 | 0.8446 | 0.8461 | 3.1898 | 2.4845 | 0.9955 | 0.9954 | 0.0401 | 0.9784 | 0.0002 | frozen MotionBERT-Lite mean_std_delta right-arm reps; head trained on original train windows |
| motionbert_lite_head_stats_v0_60f | motionbert_lite_head | cv_val | fold_2 | 60 | 0.7839 | 0.7711 | 6.6641 | 7.8470 | 1.0000 | 1.0000 | 0.0177 | 0.9973 | 0.0002 | frozen MotionBERT-Lite mean_std_delta right-arm reps; head trained on original train windows |
| motionbert_lite_head_stats_v0_60f | motionbert_lite_head | cv_val | cv_mean | 60 | 0.7178 | 0.6911 | 7.4588 | 8.4329 | 0.9958 | 0.9957 | 0.0388 | 0.9791 | 0.0003 | mean over 3 take-level folds |
| motionbert_lite_head_stats_v0_60f | motionbert_lite_head | transition_eval_222455 | session_20260616_222455_eval | 120 | 0.2443 | 0.1635 | 22.2901 | 22.2901 | 0.8397 | 0.5929 | 0.1300 | 0.2578 | 7.5088 | all-train head with mean_std_delta reps; eval uses original labels_window only; ambiguous 33s caveat |

## 60f Stable Heldout Check

This check regenerates evaluation windows from `labels_frame.jsonl` so heldout evaluation uses the same 60-frame length as training. Mixed-BPM windows are excluded from this classification score.

Generated by:

```bash
python tools/evaluate_right_conducting_baselines.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --output-json outputs/right_conducting/baseline_scores_v0_60f_eval60stable.json \
  --output-md outputs/right_conducting/baseline_scores_v0_60f_eval60stable.md

python tools/train_motionbert_conducting_head.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --cache-dir outputs/right_conducting/motionbert_cache_v0_60f_stats \
  --config checkpoint/MB_lite.yaml \
  --checkpoint checkpoint/mb_lite_v0.pt \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --device cuda:0 \
  --epochs 80 \
  --hidden-dim 512 \
  --lr 0.001 \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --output-dir outputs/right_conducting/motionbert_head_v0_60f_stats_e80_h512_eval60stable
```

Window summary:

```text
all 60f windows: 281
stable 60f windows: 243
mixed BPM windows excluded: 38
stable BPM counts: 100 BPM = 91, 120 BPM = 141, 80 BPM = 11
stable gain counts: large = 224, small = 19
```

| run_name | model_type | eval_set | fold_or_subject | window_frames | tempo_acc | tempo_macro_f1 | bpm_mae_window | gain_acc | dynamics_mae_window | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| feature_baseline_v0_60f | handcrafted_feature_ml | transition_eval_222455_60f_stable | session_20260616_222455_eval | 60 | 0.5514 | 0.2885 | 10.6173 | 0.7654 | 0.1407 | best current transition tempo fallback |
| rule_based_fft_amp_v0_60f | rule_based | transition_eval_222455_60f_stable | session_20260616_222455_eval | 60 | 0.0000 | 0.0000 | 50.3704 | 0.5103 | 0.2938 | not reliable for tempo |
| motionbert_lite_head_stats_v0_60f | motionbert_lite_head | transition_eval_222455_60f_stable | session_20260616_222455_eval | 60 | 0.3128 | 0.1767 | 20.5761 | 0.7901 | 0.1275 | CV strong but heldout tempo weak |

## Selected Live Fallback Artifact

Current selected streamable artifact:

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
outputs/right_conducting/selected/feature_baseline_live_v0_structure.md
outputs/right_conducting/selected/selected_model_manifest.json
```

Export command:

```bash
python tools/export_right_conducting_fallback.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --score-json outputs/right_conducting/baseline_scores_v0_60f_eval60stable.json \
  --output-dir outputs/right_conducting/selected \
  --artifact-name feature_baseline_live_v0.json
```

The artifact uses the `feature_baseline_v0_60f` row from `transition_eval_222455_60f_stable`:

```text
tempo_acc: 0.5514
bpm_mae_window: 10.6173
gain_acc: 0.7654
dynamics_mae_window: 0.1407
```

## Streaming Replay Metrics

Tuned selected artifact:

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
switch_threshold: 0.15
fast_switch_threshold: 0.40
confirm_updates: 2
```

Replay artifacts:

```text
outputs/right_conducting/stream_replay_222455_60f_tuned.json
outputs/right_conducting/stream_replay_222455_60f_tuned.md
outputs/right_conducting/stream_replay_222455_60f_tuned_rows.jsonl
outputs/right_conducting/stream_replay_222455_60f_tuned_analysis.json
outputs/right_conducting/stream_replay_222455_60f_tuned_analysis.md
```

| mode | tempo_acc | gain_acc | pred_switch_count | false_switch_count | false_switches_per_min | switch_delay_mean_s | switch_delay_p90_s |
|---|---:|---:|---:|---:|---:|---:|---:|
| raw | 0.4982 | 0.7936 | 30 | 16 | 17.1243 | 6.6031 | 6.6031 |
| smoothed | 0.4698 | 0.8434 | 8 | 4 | 4.2811 | 7.6037 | 7.6037 |

Delay diagnosis:

```text
true switches: 2
raw reached target switches: 1
raw missed target switches: 1
first switch 100 -> 120 BPM:
  raw delay: 6.6031s
  smoothed delay: 7.6037s
  smoothing extra delay: 1.0006s
second switch 120 -> 80 BPM:
  raw never reaches 80 BPM
```

Conclusion:

```text
The main latency bottleneck is classifier-side delay/miss, not only stream smoothing.
```

## Stream Policy Sweep

Policy sweep artifact:

```text
outputs/right_conducting/stream_policy_sweep_222455.json
outputs/right_conducting/stream_policy_sweep_222455.md
```

Constraint:

```text
max_false_switches_per_min: 5.0
```

Selected policy:

```text
switch_threshold: 0.15
fast_switch_threshold: 0.40
confirm_updates: 2
tempo_acc: 0.4698
false_switches_per_min: 4.2811
switch_delay_mean_s: 7.6037
```

`session_20260616_215630_eval` remains excluded because its current labels are constant 100 BPM and `manual_timeline.json` is missing.

## 30f Classifier Latency Probe

30f artifacts:

```text
outputs/right_conducting/dataset_v0_30f/
outputs/right_conducting/baseline_scores_v0_30f_eval30stable.json
outputs/right_conducting/selected_30f/feature_baseline_live_v0_30f.json
outputs/right_conducting/selected_30f_sweep/feature_baseline_live_v0_30f_sweep.json
outputs/right_conducting/stream_replay_222455_30f_tuned.json
outputs/right_conducting/stream_replay_222455_30f_tuned_analysis.json
outputs/right_conducting/stream_policy_sweep_222455_30f.json
outputs/right_conducting/stream_replay_222455_30f_selected.json
outputs/right_conducting/stream_replay_222455_30f_selected_analysis.json
```

Stable heldout comparison:

| candidate | eval_set | tempo_acc | bpm_mae_window | gain_acc | dynamics_mae_window |
|---|---|---:|---:|---:|---:|
| feature_baseline_v0_60f | transition_eval_222455_60f_stable | 0.5514 | 10.6173 | 0.7654 | 0.1407 |
| feature_baseline_v0_30f | transition_eval_222455_30f_stable | 0.4249 | 15.2381 | 0.7875 | 0.1275 |

Replay comparison:

| candidate | mode | tempo_acc | false_switches_per_min | switch_delay_mean_s | raw_missed_switches |
|---|---|---:|---:|---:|---:|
| 60f tuned | raw | 0.4982 | 17.1243 | 6.6031 | 1 |
| 60f tuned | smoothed | 0.4698 | 4.2811 | 7.6037 | 1 |
| 30f tuned | raw | 0.4192 | 18.6009 | 1.4010 | 1 |
| 30f tuned | smoothed | 0.3574 | 11.3672 | 7.4039 | 1 |

30f sweep-selected row:

```text
switch_threshold: 0.35
fast_switch_threshold: 0.50
confirm_updates: 3
tempo_acc: 0.4914
gain_acc: 0.9966
false_switches_per_min: 3.1002
reported switch_delay_mean_s: 0.0000
```

Caveat:

```text
The 0.0000s delay is caused by a pre-switch on 100 -> 120 BPM.
30f still misses the 120 -> 80 BPM raw switch.
Do not treat the 30f sweep row as final live success.
```

## Temporal Feature Ridge Probe

Temporal ridge artifacts:

```text
outputs/right_conducting/temporal_scores_v0_30f_c2.json
outputs/right_conducting/temporal_scores_v0_30f_c3.json
outputs/right_conducting/temporal_scores_v0_30f_c5.json
outputs/right_conducting/temporal_30f_c5/temporal_feature_live_v0_30f_c5.json
outputs/right_conducting/temporal_replay_222455_30f_c5_tuned.json
outputs/right_conducting/temporal_replay_222455_30f_c5_tuned_analysis.json
outputs/right_conducting/temporal_policy_sweep_222455_30f_c5.json
```

Heldout score:

| model | context | cv tempo_acc | heldout tempo_acc | bpm_mae_window | heldout gain_acc |
|---|---:|---:|---:|---:|---:|
| feature_baseline_v0_30f | 1 | 0.4757 | 0.4249 | 15.2381 | 0.7875 |
| temporal_feature_ridge_v0_30f_c2 | 2 | 0.5356 | 0.2601 | 15.8242 | 0.7582 |
| temporal_feature_ridge_v0_30f_c3 | 3 | 0.5354 | 0.2527 | 16.5568 | 0.7582 |
| temporal_feature_ridge_v0_30f_c5 | 5 | 0.5391 | 0.2491 | 16.3370 | 0.7546 |

c5 replay:

| mode | tempo_acc | false_switches_per_min | switch_delay_mean_s | switch_delay_p90_s |
|---|---:|---:|---:|---:|
| raw | 0.2509 | 20.6677 | 17.4088 | 27.6538 |
| smoothed | 0.2474 | 10.3338 | 30.4154 | 30.4154 |

Decision:

```text
temporal_feature_ridge_v0_30f_c5 is no-go.
It improves within-subject CV but fails heldout transition and live latency.
```

## Normalization Comparison

Artifacts:

```text
outputs/right_conducting/normalization_scores_v0_60f_right_shoulder.json
outputs/right_conducting/normalization_scores_v0_60f_right_arm_length.json
outputs/right_conducting/normalization_scores_v0_30f_right_shoulder.json
outputs/right_conducting/normalization_scores_v0_30f_right_arm_length.json
outputs/right_conducting/stream_replay_222455_60f_right_shoulder_tuned.json
outputs/right_conducting/stream_replay_222455_30f_right_shoulder_tuned.json
```

Stable heldout:

| candidate | input_norm | tempo_acc | bpm_mae_window | gain_acc | dynamics_mae_window |
|---|---|---:|---:|---:|---:|
| 60f camera | camera | 0.5514 | 10.6173 | 0.7654 | 0.1407 |
| 60f right_shoulder | right_shoulder | 0.5473 | 10.7819 | 0.8066 | 0.1160 |
| 60f right_arm_length | right_arm_length | 0.4609 | 15.3086 | 0.5556 | 0.2667 |
| 30f camera | camera | 0.4249 | 15.2381 | 0.7875 | 0.1275 |
| 30f right_shoulder | right_shoulder | 0.4542 | 14.5055 | 0.8059 | 0.1165 |
| 30f right_arm_length | right_arm_length | 0.3663 | 18.0952 | 0.5275 | 0.2835 |

Tuned replay:

| candidate | mode | tempo_acc | gain_acc | false_switches_per_min | switch_delay_mean_s | missed_switches |
|---|---|---:|---:|---:|---:|---:|
| 60f camera | smoothed | 0.4698 | 0.8434 | 4.2811 | 7.6037 | 1 |
| 60f right_shoulder | smoothed | 0.4840 | 0.8470 | 4.2811 | 7.6037 | 1 |
| 30f camera | smoothed | 0.3574 | 0.8179 | 11.3672 | 7.4039 | 1 |
| 30f right_shoulder | smoothed | 0.3780 | 0.8316 | 11.3672 | 7.6040 | 1 |

Decision:

```text
right_shoulder: keep as ablation option; not selected as live replacement.
right_arm_length: no-go.
selected fallback remains 60f camera.
Reason: all candidates still miss 120 -> 80; 60f camera keeps best stable heldout tempo.
```

## Missed 120 -> 80 Diagnosis

Artifacts:

```text
outputs/right_conducting/missed_transition_222455_60f_camera_diagnosis.json
outputs/right_conducting/missed_transition_222455_60f_camera_diagnosis.md
outputs/right_conducting/missed_transition_222455_30f_camera_diagnosis.json
outputs/right_conducting/missed_transition_222455_30f_camera_diagnosis.md
```

Tail diagnosis:

| candidate | stable 80 rows | raw pred counts | mean dist to 80 | mean dist to 100 | mean dist to 120 |
|---|---:|---|---:|---:|---:|
| 60f camera | 11 | `{2: 8, 3: 3}` | 12.2564 | 6.9435 | 7.7270 |
| 30f camera | 21 | `{2: 13, 3: 8}` | 17.6613 | 13.1599 | 13.7887 |

Conclusion:

```text
The raw classifier never emits class 1 in stable 80 BPM tail windows.
The failure is not primarily the smoother.
The fallback relies too much on static pose mean features; dominant_bpm collapses near 60 BPM for all classes.
```

Next candidate:

```text
pose-invariant feature subset:
  remove/downweight rel_wrist_x_mean, rel_wrist_y_mean, rel_elbow_x_mean, rel_elbow_y_mean
  keep motion/radius/amplitude/validity features
```

## Pose-Invariant Feature Subset Candidate

Report:

```text
docs/exp/goal_reports/2026-06-17_16_pose_invariant_feature_subset.md
```

Artifacts:

```text
outputs/right_conducting/pose_invariant_scores_v0_60f.json
outputs/right_conducting/pose_invariant_scores_v0_30f.json
outputs/right_conducting/stream_replay_222455_60f_pose_invariant_tuned.json
outputs/right_conducting/stream_replay_222455_30f_pose_invariant_tuned.json
outputs/right_conducting/stream_policy_sweep_222455_60f_pose_invariant.json
outputs/right_conducting/stream_policy_sweep_222455_30f_pose_invariant.json
outputs/right_conducting/pose_invariant_report16_summary.json
```

Feature subset:

```text
source features: 16
selected features: 12
removed static mean features:
  rel_wrist_x_mean
  rel_wrist_y_mean
  rel_elbow_x_mean
  rel_elbow_y_mean
```

Stable heldout comparison:

| candidate | feature_subset | window | cv_mean tempo_acc | stable tempo_acc | stable bpm_mae | stable gain_acc |
|---|---|---:|---:|---:|---:|---:|
| 60f selected fallback | all | 60 | 0.5152 | 0.5514 | 10.6173 | 0.7654 |
| 60f pose-invariant | pose_invariant | 60 | 0.4795 | 0.4938 | 13.0864 | 0.8189 |
| 30f latency probe | all | 30 | 0.4757 | 0.4249 | 15.2381 | 0.7875 |
| 30f pose-invariant | pose_invariant | 30 | 0.4522 | 0.4579 | 14.7985 | 0.8095 |

Streaming replay comparison:

| candidate | mode | tempo_acc | gain_acc | false_switches_per_min | reached true switches | missed true switches | switch_delay_mean_s |
|---|---|---:|---:|---:|---:|---:|---:|
| 60f all | raw | 0.4982 | 0.7936 | 17.1243 | 1/2 | 1/2 | 6.6031 |
| 60f all | smoothed | 0.4698 | 0.8434 | 4.2811 | 1/2 | 1/2 | 7.6037 |
| 60f pose-invariant | raw | 0.4484 | 0.8399 | 14.9837 | 2/2 | 0/2 | 3.0016 |
| 60f pose-invariant | smoothed | 0.3203 | 0.8505 | 5.3513 | 1/2 | 1/2 | 7.6037 |
| 30f all | raw | 0.4192 | 0.8041 | 18.6009 | 1/2 | 1/2 | 1.4010 |
| 30f all | smoothed | 0.3574 | 0.8351 | 11.3672 | 1/2 | 1/2 | 7.4039 |
| 30f pose-invariant | raw | 0.4502 | 0.8179 | 29.9682 | 2/2 | 0/2 | 2.1012 |
| 30f pose-invariant | smoothed | 0.3677 | 0.8041 | 11.3672 | 1/2 | 1/2 | 5.6032 |

Decision:

```text
pose_invariant feature subset: NO-GO as selected live model.
```

Reason:

```text
It lets the raw classifier reach both true switches, including 120 -> 80.
But 60f stable tempo_acc drops from 0.5514 to 0.4938, and policy sweep trades false-switch control for 17-18s delay.
```

## Transition Margin Evaluation

Report:

```text
docs/exp/goal_reports/2026-06-17_17_transition_margin_evaluation.md
```

Artifacts:

```text
outputs/right_conducting/transition_margin_scores_222455_60f.json
outputs/right_conducting/transition_margin_scores_222455_60f.md
```

Setup:

```text
artifact: outputs/right_conducting/selected/feature_baseline_live_v0.json
eval_session: dataset/evaluation_transitions/session_20260616_222455_eval
window_frames: 60
stride_frames: 3
transition_times: 22.0s, 54.0s from manual_timeline.json
session_20260616_215630_eval: excluded
```

Original eval files used:

```text
labels_frame.jsonl
labels_window.jsonl
pose_right_h36m_masked.npy
right_rule_features.npy
```

Eval-local augmentation artifacts excluded:

```text
recommended_augmented_v0/
labels_tempo_augmented_15f.jsonl
tempo_augmented_15f.npy
```

Offline classification by transition margin:

| margin_s | sample_count | mixed_excluded | margin_excluded | tempo_acc | tempo_macro_f1 | 80_recall | 80_support | bpm_mae | gain_acc | dynamics_mae |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 243 | 38 | 0 | 0.5514 | 0.2885 | 0.0000 | 11 | 10.6173 | 0.7654 | 0.1407 |
| 0.5 | 231 | 38 | 12 | 0.5671 | 0.2943 | 0.0000 | 8 | 10.3896 | 0.7532 | 0.1481 |
| 1.0 | 223 | 38 | 20 | 0.5830 | 0.3013 | 0.0000 | 6 | 10.0448 | 0.7444 | 0.1534 |
| 2.0 | 203 | 38 | 40 | 0.6158 | 0.3174 | 0.0000 | 1 | 9.3596 | 0.7192 | 0.1685 |
| 3.0 | 187 | 38 | 56 | 0.6310 | 0.3255 | 0.0000 | 0 | 9.1979 | 0.6952 | 0.1829 |

Streaming replay reference:

| margin_s | row_count | raw_tempo_acc | raw_false_switches_per_min | raw_missed | smoothed_tempo_acc | smoothed_false_switches_per_min | smoothed_missed |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 243 | 0.5514 | 17.1243 | 1 | 0.6214 | 4.2811 | 1 |
| 0.5 | 231 | 0.5671 | 17.1243 | 1 | 0.6364 | 4.2811 | 1 |
| 1.0 | 223 | 0.5830 | 16.0540 | 1 | 0.6413 | 4.2811 | 1 |
| 2.0 | 203 | 0.6158 | 13.9135 | 1 | 0.6552 | 3.2108 | 1 |
| 3.0 | 187 | 0.6310 | 14.0258 | 0 | 0.6578 | 3.8252 | 0 |

Interpretation:

```text
Overall tempo_acc improves as the margin grows, but this is mostly because the 80 BPM tail is removed from the score.
80 BPM recall stays 0.0000 for every margin where any 80 BPM window remains.
At margin 1.0, true 80 windows are still predicted as {100: 4, 120: 2}.
At margin 2.0, the only remaining true 80 window is predicted as 100.
Therefore the 120 -> 80 failure is not only transition-boundary ambiguity.
```

## Hybrid Static-Weighted Feature Classifier

Report:

```text
docs/exp/goal_reports/2026-06-17_18_hybrid_static_weight_classifier.md
```

Summary:

```text
outputs/right_conducting/hybrid_static_report18_summary.json
```

Candidate artifacts:

```text
outputs/right_conducting/selected_60f_hybrid_static025/feature_baseline_live_v0_60f_hybrid_static025.json
outputs/right_conducting/selected_60f_hybrid_static050/feature_baseline_live_v0_60f_hybrid_static050.json
outputs/right_conducting/selected_60f_hybrid_static075/feature_baseline_live_v0_60f_hybrid_static075.json
```

Stable heldout comparison:

| candidate | cv tempo_acc | stable tempo_acc | stable bpm_mae | stable gain_acc | 80 recall | true 80 prediction counts |
|---|---:|---:|---:|---:|---:|---|
| all | 0.5152 | 0.5514 | 10.6173 | 0.7654 | 0.0000 | `{100: 8, 120: 3}` |
| pose_invariant | 0.4795 | 0.4938 | 13.0864 | 0.8189 | 0.1818 | `{80: 2, 100: 9}` |
| hybrid_static025 | 0.5059 | 0.5144 | 12.3457 | 0.8148 | 0.0000 | `{100: 11}` |
| hybrid_static050 | 0.5124 | 0.5226 | 11.9342 | 0.8025 | 0.0000 | `{100: 10, 120: 1}` |
| hybrid_static075 | 0.5137 | 0.5226 | 11.5226 | 0.7860 | 0.0000 | `{100: 9, 120: 2}` |

Full replay comparison:

| candidate | raw tempo_acc | raw false/min | raw reached | raw missed | smoothed tempo_acc | smoothed false/min | smoothed reached | smoothed missed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 0.4982 | 17.1243 | 1 | 1 | 0.4698 | 4.2811 | 1 | 1 |
| pose_invariant | 0.4484 | 14.9837 | 2 | 0 | 0.3203 | 5.3513 | 1 | 1 |
| hybrid_static025 | 0.4698 | 18.1945 | 1 | 1 | 0.3523 | 4.2811 | 1 | 1 |
| hybrid_static050 | 0.4733 | 18.1945 | 1 | 1 | 0.3630 | 6.4216 | 1 | 1 |
| hybrid_static075 | 0.4769 | 12.8432 | 1 | 1 | 0.3915 | 6.4216 | 1 | 1 |

Decision:

```text
hybrid_static feature weighting: NO-GO as selected live model.
```

Reason:

```text
hybrid_static050/075 recover some tempo_acc compared with pose_invariant,
but 80 BPM recall remains 0 and full replay still misses 120 -> 80.
Selected live fallback remains feature_subset=all.
```

## Class-Balanced Ridge Feature Classifier

Report:

```text
docs/exp/goal_reports/2026-06-17_19_class_balanced_ridge_feature_classifier.md
```

Code path:

```text
lib/right_conducting/temporal_classifier.py
tools/evaluate_right_conducting_temporal.py --class-weight none|balanced
```

Artifacts:

```text
outputs/right_conducting/linear_unweighted_scores_v0_60f_c1_a1.json
outputs/right_conducting/linear_balanced_scores_v0_60f_c1_a0.1.json
outputs/right_conducting/linear_balanced_scores_v0_60f_c1_a1.json
outputs/right_conducting/linear_balanced_scores_v0_60f_c1_a10.json
outputs/right_conducting/linear_balanced_replay_222455_60f_c1_a10_tuned.json
outputs/right_conducting/linear_balanced_replay_222455_60f_c1_a10_tuned_analysis.json
```

Stable heldout comparison:

| candidate | class_weight | alpha | cv tempo_acc | stable tempo_acc | stable macro_f1 | stable bpm_mae | stable gain_acc |
|---|---|---:|---:|---:|---:|---:|---:|
| selected feature_baseline all | none | - | 0.5152 | 0.5514 | 0.2885 | 10.6173 | 0.7654 |
| linear ridge c1 | none | 1.0 | 0.5916 | 0.2099 | 0.0907 | 17.2840 | 0.7531 |
| linear ridge c1 | balanced | 0.1 | 0.6033 | 0.2840 | 0.1150 | 15.7202 | 0.7490 |
| linear ridge c1 | balanced | 1.0 | 0.6023 | 0.2840 | 0.1150 | 15.7202 | 0.7490 |
| linear ridge c1 | balanced | 10.0 | 0.5976 | 0.2840 | 0.1146 | 15.5556 | 0.7449 |

Stable confusion check:

| candidate | true 80 predictions | all stable pred_counts |
|---|---|---|
| linear ridge c1 unweighted a1 | `{100: 4, 60: 7}` | `{60: 19, 100: 190, 120: 34}` |
| linear ridge c1 balanced a10 | `{100: 5, 60: 6}` | `{60: 16, 80: 1, 100: 210, 120: 16}` |

Replay check:

| candidate | raw tempo_acc | raw false/min | raw reached | raw missed | smoothed tempo_acc | smoothed false/min | smoothed reached | smoothed missed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| linear ridge c1 unweighted a1 | 0.2171 | 17.1243 | 0 | 2 | 0.2100 | 9.6324 | 0 | 2 |
| linear ridge c1 balanced a10 | 0.2811 | 20.3351 | 0 | 2 | 0.2989 | 8.5621 | 0 | 2 |

Decision:

```text
class-balanced ridge feature classifier: NO-GO as selected live model.
```

Reason:

```text
Balanced weighting improves the linear ridge candidate over unweighted ridge,
but it still does not recover true 80 BPM windows.
The only stable 80 BPM prediction from balanced_a10 is a true 100 BPM window.
Selected live fallback remains outputs/right_conducting/selected/feature_baseline_live_v0.json.
```

## 80 BPM Feature Distribution Diagnosis

Report:

```text
docs/exp/goal_reports/2026-06-17_20_80_bpm_feature_distribution_diagnosis.md
```

Artifacts:

```text
outputs/right_conducting/feature_distribution_80_tail_60f.json
outputs/right_conducting/feature_distribution_80_tail_60f.md
```

Setup:

```text
train: outputs/right_conducting/dataset_v0_60f/windows_60f_v0.jsonl, aug_type=original
eval: session_20260616_222455_eval, regenerated 60f stable windows
input_norm: camera
focus_class: 1 / 80 BPM
competitor_class: 2 / 100 BPM
```

Class counts:

| split | 60 | 80 | 100 | 120 |
|---|---:|---:|---:|---:|
| train original 60f | 1685 | 1686 | 1686 | 2949 |
| eval 222455 stable 60f | 0 | 11 | 91 | 141 |

Stable eval 80 nearest train class:

| nearest train class | count |
|---|---:|
| 100 BPM | 8 |
| 120 BPM | 3 |

Mean standardized distance for stable eval 80:

| train class | distance |
|---|---:|
| 60 BPM | 13.9402 |
| 80 BPM | 12.2489 |
| 100 BPM | 6.9425 |
| 120 BPM | 7.7321 |

Top feature shifts from train 80 to eval 80:

| feature | train 80 mean | eval 80 mean | pooled z shift |
|---|---:|---:|---:|
| rel_elbow_y_mean | 0.1423 | 0.2297 | 2.1133 |
| rel_wrist_y_mean | -0.1315 | -0.0391 | 1.6488 |
| rel_wrist_x_mean | 0.0858 | 0.0485 | -1.2408 |
| rel_elbow_x_mean | 0.1310 | 0.1476 | 0.8289 |
| rel_wrist_y_std | 0.1606 | 0.2101 | 0.7875 |

Decision:

```text
The 80 BPM tail failure is a feature-space coverage/domain mismatch,
not just a train class-count imbalance.
```

Implication:

```text
More classifier-only changes on the same feature space are low ROI.
Next step should return to train-only tempo-stretch augmentation or additional down-transition data.
```

## Tempo-Stretch Coverage Sanity Check

Report:

```text
docs/exp/goal_reports/2026-06-17_21_tempo_stretch_coverage_sanity_check.md
```

Artifacts:

```text
outputs/right_conducting/tempo_stretch_mild_80_tail_60f.json
outputs/right_conducting/tempo_stretch_mild_80_tail_60f.md
outputs/right_conducting/tempo_stretch_bridge_80_tail_60f.json
outputs/right_conducting/tempo_stretch_bridge_80_tail_60f.md
```

Mild A2-style stretch:

```text
speed_scales: 0.92, 1.10
augmented windows: 15964
source_to_aug_class_counts:
  0->0: 3358
  1->1: 3360
  2->2: 1686
  2->3: 1674
  3->3: 5886
```

Aggressive bridge probe:

```text
speed_scales: 0.80, 0.667
augmented windows: 16012
source_to_aug_class_counts:
  2->1: 1686
  3->1: 2949
```

Stable eval 80 nearest train class:

| train set | nearest class counts | dist to 80 | dist to 100 | dist to 120 |
|---|---|---:|---:|---:|
| original | `{100: 8, 120: 3}` | 12.2489 | 6.9425 | 7.7321 |
| original + mild stretch | `{100: 7, 120: 4}` | 12.5453 | 7.1237 | 7.3328 |
| original + bridge stretch | `{100: 11}` | 9.1352 | 7.1368 | 8.3212 |

Decision:

```text
tempo-stretch-only augmentation: NO-GO as the next selected training change.
```

Reason:

```text
Mild stretch does not create missing 80 BPM coverage.
Aggressive bridge stretch moves train 80 closer to eval 80,
but all 11 stable eval 80 windows remain nearest to train 100.
```

## Eval Session Readiness Audit

Report:

```text
docs/exp/goal_reports/2026-06-17_22_eval_relabel_and_down_transition_data_decision.md
```

Artifacts:

```text
outputs/right_conducting/eval_session_readiness_audit.json
outputs/right_conducting/eval_session_readiness_audit.md
```

Audit result:

| session | scoreable transition eval | frame BPM targets | window BPM targets | frame transitions | mixed windows | blocking reasons |
|---|---|---|---|---:|---:|---|
| session_20260616_215630_eval | false | `[100.0]` | `[100.0]` | 0 | 0 | missing manual timeline; frame/window labels contain fewer than two BPM targets |
| session_20260616_222455_eval | true | `[100.0, 120.0, 80.0]` | `[100.0, 120.0, 80.0]` | 2 | 34 | none |

Decision:

```text
session_20260616_215630_eval remains excluded from score until relabeled.
```

Reason:

```text
Current labels are constant 100 BPM.
manual_timeline.json is missing.
Scoring it now would treat a likely transition session as stable 100 BPM, which would invalidate the report.
```

## Manual Timeline Relabel Helper

Report:

```text
docs/exp/goal_reports/2026-06-17_23_manual_timeline_relabel_helper.md
```

Dry-run artifacts:

```text
outputs/right_conducting/relabel_dryrun_222455_60f/labels_frame.jsonl
outputs/right_conducting/relabel_dryrun_222455_60f/labels_window_60f.jsonl
outputs/right_conducting/relabel_dryrun_222455_60f/summary.json
outputs/right_conducting/relabel_dryrun_222455_60f/summary.md
```

Dry-run check on `222455_eval`:

| item | value |
|---|---|
| manual timeline BPM transitions | `22.0s, 54.0s` |
| relabeled frame transition times | `22.042992s, 54.058506s` |
| regenerated 60f windows | `281` |
| mixed BPM windows | `38` |
| stable windows | `243` |

Decision:

```text
manual_timeline relabel helper: GO
215630_eval score inclusion: still NO-GO until timestamps are supplied
```

## Reproducible Goal Command

Report:

```text
docs/exp/goal_reports/2026-06-17_24_reproducible_goal_command.md
```

Command:

```bash
bash scripts/run_right_conducting_goal.sh \
  --steps audit,eval,replay,analyze \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --window-frames 60 \
  --stride-frames 3 \
  --normalizations camera \
  --artifact outputs/right_conducting/selected/feature_baseline_live_v0.json \
  --switch-threshold 0.15 \
  --fast-switch-threshold 0.40 \
  --confirm-updates 2 \
  --output-json outputs/right_conducting/right_conducting_goal_run_222455_60f.json \
  --output-md outputs/right_conducting/right_conducting_goal_run_222455_60f.md
```

Artifacts:

```text
outputs/right_conducting/right_conducting_goal_run_222455_60f.json
outputs/right_conducting/right_conducting_goal_run_222455_60f.md
outputs/right_conducting/stream_replay_222455_60f_goal_analysis.json
outputs/right_conducting/stream_replay_222455_60f_goal_analysis.md
```

Run status:

| step | status |
|---|---|
| audit_eval_sessions | ok |
| eval_transition_margins_222455_60f | ok |
| replay_222455_60f | ok |
| analyze_replay_222455_60f | ok |

Replayed switch result:

| metric | value |
|---|---:|
| switch_count | 2 |
| raw_reached_count | 1 |
| raw_missed_count | 1 |
| smoothed_reached_count | 1 |
| smoothed_missed_count | 1 |
| raw_delay_p90_s | 6.6031 |
| smoothed_delay_p90_s | 7.6037 |

Decision:

```text
goal command: GO for current reproducible audit/eval/replay/analyze subset.
120 -> 80 robust live control: still NO-GO.
```

## Target-80 Combo Augmentation Candidate

Report:

```text
docs/exp/goal_reports/2026-06-17_25_target80_combo_augmentation_candidate.md
```

Artifacts:

```text
outputs/right_conducting/combo_aug_bridge_target80_tail_60f.json
outputs/right_conducting/combo_aug_baseline_target80_60f.json
outputs/right_conducting/selected_60f_target80_combo_aug/feature_baseline_target80_combo_aug_60f.json
outputs/right_conducting/stream_replay_222455_60f_target80_combo_aug_analysis.json
outputs/right_conducting/transition_margin_scores_222455_60f_target80_combo_aug.json
```

Coverage diagnosis on stable eval 80 tail:

| train set | added windows | nearest train class counts | dist to 80 | dist to 100 |
|---|---:|---|---:|---:|
| original | 0 | `{100: 8, 120: 3}` | 12.2489 | 6.9425 |
| combo all generated classes | 32024 | `{100: 11}` | 4.0370 | 3.0525 |
| combo target 80 only | 9270 | `{80: 9, 120: 2}` | 4.1749 | 4.8357 |

Offline stable score:

| model | tempo_acc | macro_f1 | bpm_mae | 80_recall | true 80 predictions |
|---|---:|---:|---:|---:|---|
| original feature baseline | 0.5514 | 0.2885 | 10.6173 | 0.0000 | `{100: 8, 120: 3}` |
| target80 combo feature baseline | 0.5638 | 0.3837 | 11.1934 | 0.8182 | `{80: 9, 120: 2}` |

Margin sweep:

| margin_s | sample_count | tempo_acc | bpm_mae | 80_support | 80_recall |
|---:|---:|---:|---:|---:|---:|
| 0.0 | 243 | 0.5638 | 11.1934 | 11 | 0.8182 |
| 0.5 | 231 | 0.5628 | 11.3420 | 8 | 0.7500 |
| 1.0 | 223 | 0.5695 | 11.2108 | 6 | 0.8333 |
| 2.0 | 203 | 0.5665 | 11.4286 | 1 | 1.0000 |
| 3.0 | 187 | 0.5455 | 12.0856 | 0 | 0.0000 |

Full replay with `switch_threshold=0.15`, `fast_switch_threshold=0.40`, `confirm_updates=2`:

| metric | value |
|---|---:|
| raw_reached_count | 2 |
| raw_missed_count | 0 |
| raw_delay_p90_s | 2.0210 |
| smoothed_reached_count | 2 |
| smoothed_missed_count | 0 |
| smoothed_delay_p90_s | 6.3632 |
| smoothed false_switches_per_min | 6.4216 |

Policy sweep caveat:

```text
The swept low-false-switch policy misses the smoothed 120 -> 80 transition.
The candidate is useful evidence for target80 augmentation, but it is not selected live fallback.
```

Decision:

```text
target80 combo augmentation direction: GO for next stronger-model training probe.
target80 combo feature-baseline artifact as selected live model: NO-GO.
selected live fallback remains outputs/right_conducting/selected/feature_baseline_live_v0.json.
```

## MotionBERT Target-80 Combo Training

Report:

```text
docs/exp/goal_reports/2026-06-17_26_motionbert_target80_combo_training.md
```

Artifacts:

```text
outputs/right_conducting/motionbert_cache_v0_60f_stats_target80_combo/
outputs/right_conducting/motionbert_head_v0_60f_stats_target80_combo_e80_h512_eval60stable/
outputs/right_conducting/motionbert_head_v0_60f_stats_target80_combo_stride3_e80_h512_eval60stable/
outputs/right_conducting/motionbert_head_v0_60f_stats_target80_combo_stride10_e80_h512_eval60stable/
outputs/right_conducting/motionbert_stats_target80_combo_stride3_eval60stable_detailed.json
```

MotionBERT target80 combo cache:

| metric | value |
|---|---:|
| augmented rows | 9270 |
| feature_dim | 2048 |
| filtered non-target windows | 22754 |

Stable transition eval:

| model | tempo_acc | macro_f1 | bpm_mae | 80_recall | 100_recall | 120_recall | gain_acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| original stats head | 0.3128 | 0.1767 | 20.5761 | 0.3636 | 0.7912 | 0.0000 | 0.7901 |
| target80 combo full | 0.3128 | 0.1910 | 18.2716 | 0.8182 | 0.6923 | 0.0284 | 0.8066 |
| target80 combo stride3 | 0.3539 | 0.2085 | 16.2140 | 0.8182 | 0.8242 | 0.0142 | 0.7984 |
| target80 combo stride10 | 0.3169 | 0.1930 | 19.3416 | 0.8182 | 0.7253 | 0.0142 | 0.8683 |

Interpretation:

```text
Target80 combo augmentation transfers into MotionBERT head training and recovers 80 BPM recall,
but the head collapses true 120 BPM windows into 80/100.
This fails the live tempo stability gate.
```

Decision:

```text
MotionBERT target80 combo pipeline: GO as reproducible pre-new-data experiment.
MotionBERT target80 combo head as selected live model: NO-GO.
Next: integrate supplied new dataset, then rerun the same gates instead of tuning further on one eval session.
```

## New Dataset Intake Gate

Report:

```text
docs/exp/goal_reports/2026-06-17_38_5gpu_hparam_sweep_transition_stress.md
```

Command:

```bash
python tools/audit_right_conducting_dataset_intake.py \
  --train-roots dataset/recordings \
  --eval-roots dataset/evaluation_transitions,dataset/transitions \
  --output-json outputs/right_conducting/dataset_intake_after_transitions_schedule.json \
  --output-md outputs/right_conducting/dataset_intake_after_transitions_schedule.md
```

Current audit summary:

| metric | value |
|---|---:|
| session_count | 36 |
| train_session_count | 24 |
| eval_session_count | 12 |
| missing_train_root_count | 0 |
| missing_eval_root_count | 0 |
| train_ready_count | 24 |
| eval_scoreable_count | 11 |
| eval_pending_relabel_count | 1 |

Scoring implication:

```text
Use dataset/evaluation/session_20260616_222455_bpm120_beat4_large for the current single-session score.
Use dataset/transitions as transition stress/dev evaluation only, with eval-local augmentation excluded.
Keep dataset/evaluation_transitions/session_20260616_215630_bpm100_beat4_large excluded until relabeled.
```

## New Dataset Staging Zip Gate

Report:

```text
docs/exp/goal_reports/2026-06-17_28_new_dataset_staging_zip_gate.md
```

Current staging smoke:

```bash
python tools/build_right_conducting_recordings_zip.py \
  --train-roots dataset/recordings \
  --output-zip outputs/right_conducting/recordings_staged_current.zip \
  --output-json outputs/right_conducting/recordings_staged_current_manifest.json
```

Prepare smoke:

```bash
python tools/prepare_right_conducting_dataset.py \
  --zip outputs/right_conducting/recordings_staged_current.zip \
  --output-dir outputs/right_conducting/dataset_v0_60f_staged_current \
  --window-frames 60 \
  --stride-frames 3 \
  --folds 3 \
  --augment-copies 0
```

Result:

| metric | value |
|---|---:|
| staged take_count | 24 |
| prepared window_count | 8006 |
| fold_count | 3 |

After supplied data arrives:

```text
Use outputs/right_conducting/recordings_staged_after_supply.zip as --zip.
Use outputs/right_conducting/dataset_v0_60f_after_supply as --dataset-dir.
Do not train from raw supplied roots directly unless all consumers are updated to root-path loading.
```

The reproducible runner path is documented in:

```text
docs/exp/goal_reports/2026-06-17_29_after_supply_goal_runner.md
docs/exp/goal_reports/2026-06-17_30_after_supply_cache_train_runner.md
docs/exp/goal_reports/2026-06-17_33_after_supply_5gpu_frame_sweep_runner.md
docs/exp/goal_reports/2026-06-17_34_after_supply_model_selection_runner.md
docs/exp/goal_reports/2026-06-17_35_motionbert_selected_export_bundle.md
docs/exp/goal_reports/2026-06-17_36_motionbert_live_bundle_smoke.md
docs/exp/goal_reports/2026-06-17_37_motionbert_live_bundle_replay.md
```

## Model Score Gate

Report:

```text
docs/exp/goal_reports/2026-06-17_31_model_score_gate.md
docs/exp/goal_reports/2026-06-17_32_after_supply_detailed_eval_gate_runner.md
docs/exp/goal_reports/2026-06-17_33_after_supply_5gpu_frame_sweep_runner.md
docs/exp/goal_reports/2026-06-17_34_after_supply_model_selection_runner.md
docs/exp/goal_reports/2026-06-17_35_motionbert_selected_export_bundle.md
docs/exp/goal_reports/2026-06-17_36_motionbert_live_bundle_smoke.md
docs/exp/goal_reports/2026-06-17_37_motionbert_live_bundle_replay.md
```

Current model candidate selection artifact:

```text
outputs/right_conducting/model_candidate_selection_current_motionbert_target80_combo.json
status: NO_GO
reason: current MotionBERT target80 combo gate has no GO candidate
```

Current MotionBERT export guard:

```text
command: tools/export_motionbert_selected_bundle.py --selection-json outputs/right_conducting/model_candidate_selection_current_motionbert_target80_combo.json
result: selection status must be SELECTED, got NO_GO
decision: no MotionBERT live bundle is exported for the current failed model
```

Current gate artifact:

```text
outputs/right_conducting/model_gate_current_motionbert_target80_combo_stride3.json
outputs/right_conducting/model_gate_current_motionbert_target80_combo_stride3.md
```

Pass line:

| check | threshold |
|---|---:|
| cv_tempo_acc | >= 0.70 |
| cv_gain_acc | >= 0.95 |
| transition_tempo_acc | >= 0.60 |
| transition_bpm_mae_window | <= 10.0 |
| transition_gain_acc | >= 0.80 |
| tempo_80_recall | >= 0.50 |
| tempo_120_recall | >= 0.50 |

Current MotionBERT target80 combo stride3:

```text
status: NO_GO
failed:
  transition_tempo_acc = 0.3539
  transition_bpm_mae_window = 16.2140
  transition_gain_acc = 0.7984
  tempo_120_recall = 0.0142
```

## Interpretation

Stats MotionBERT-Lite head is the best current within-subject CV model, but it is not the best transition heldout model.

```text
feature_baseline cv_mean:
  tempo_acc: 0.5152
  bpm_mae_window: 14.3469
  gain_acc: 0.9933

feature_baseline transition_eval_222455:
  tempo_acc: 0.5344
  bpm_mae_window: 9.3130
  gain_acc: 0.8168
```

Current pooled MotionBERT-Lite head underperforms the hand-crafted feature baseline on tempo.

```text
motionbert_lite_head cv_mean:
  tempo_acc: 0.3920
  bpm_mae_window: 17.0398
  gain_acc: 0.9423

motionbert_lite_head transition_eval_222455:
  tempo_acc: 0.2824
  bpm_mae_window: 23.2061
  gain_acc: 0.8550
```

Rule-based tempo is not reliable in this dataset.

```text
rule_based cv_mean tempo_acc: 0.2100
rule_based transition_eval_222455 tempo_acc: 0.0000
```

Current decision:

```text
MotionBERT-Lite checkpoint / shape / T=60,T=120 smoke: GO
Mean-pooled right-arm head: NO-GO
Stats right-arm head: CV GO, 120f transition NO-GO, 60f stable transition NO-GO
Best current fallback for transition tempo: handcrafted_feature_ml
```

The stats feature confirms that `[B,T,3,512] -> mean -> [B,512]` was losing tempo information inside CV. However, the same stats head fails on both `120f` transition labels and regenerated `60f stable` transition windows, so it is not stable enough for live export. Next model step must target heldout stability: temporal head, train-only augmentation recache, normalization comparison, and stricter transition labels. Gain is already easy under within-subject CV, but transition eval gain macro-F1 is low because `222455_eval` is imbalanced and has only a short small-dynamics segment.

## TCN Handmark Stream Score

Report:

```text
docs/exp/goal_reports/2026-06-17_82_tcn_goal_runner_full_test.md
docs/exp/goal_reports/2026-06-17_83_selected_tcn_live_bundle.md
docs/exp/goal_reports/2026-06-17_85_tcn_manifest_runtime_path.md
docs/exp/goal_reports/2026-06-17_86_tcn_2beat3beat_all_test_and_strict_preflight.md
docs/exp/goal_reports/2026-06-17_87_tcn_stdin_live_output_contract.md
docs/exp/goal_reports/2026-06-17_88_tcn_readiness_gate_includes_stdin.md
docs/exp/goal_reports/2026-06-17_89_tcn_strict_heldout_post_arrival_chain.md
docs/exp/goal_reports/2026-06-17_90_live_output_jsonl_contract_gate.md
```

Artifacts:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_structure.md
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_head.pt
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_score.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_gate.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_benchmark.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_handmark_stream_readiness.json
outputs/right_conducting/selected_tcn_handmark_live45f/manifest_stream_set_score.json
outputs/right_conducting/selected_tcn_handmark_live45f/manifest_stream_set_gate.json
outputs/right_conducting/selected_tcn_handmark_live45f/manifest_stream_benchmark.json
outputs/right_conducting/selected_tcn_handmark_live45f/manifest_stream_readiness.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_set_score.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_set_gate.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_benchmark.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_strict_heldout_preflight.json
outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_summary.json
outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_outputs.jsonl
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness_with_stdin.json
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_post_arrival_goal_dryrun.md
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_outputs_contract.json
outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_outputs_contract.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness_with_output_contract.json
```

Margin 3.0s, stable-only, latest 2/3-beat-only all-test:

| metric | value |
|---|---:|
| csv_count | 11 |
| eval_session_count | 11 |
| sample_count | 1824 |
| mixed_bpm_excluded_count | 204 |
| transition_margin_excluded_count | 423 |
| smoothed tempo_acc | 1.0000 |
| smoothed gain_acc | 1.0000 |
| 80 BPM recall | 1.0000 |
| 100 BPM recall | 1.0000 |
| 120 BPM recall | 1.0000 |
| false_switches_per_min | 0.0000 |
| missed_switch_count | 0.0000 |

Readiness:

```text
score gate: GO
stream readiness: GO
selected checkpoint benchmark p90: 2.2745 ms
selected checkpoint benchmark headroom: 87.9320
manifest runtime benchmark p90: 1.7361 ms
manifest runtime benchmark headroom: 115.2018
2/3-beat-only all-test benchmark p90: 1.6854 ms
2/3-beat-only all-test benchmark headroom: 118.6673
stdin live smoke: GO, 3 JSONL outputs, invalid 0
JSONL output contract: GO, alltest errors 0, stdin errors 0
readiness with output contract gate: GO
selected stream invalid outputs: 0
strict heldout preflight: NO_GO, P0 0/8 because strict heldout roots are not present
strict heldout post-arrival chain: dry-run ready
```

Interpretation: TCN is the current best fixed-camera live candidate. The latest all-test explicitly excludes leftover `beat4` CSV files and uses only 2/3-beat supplied data. This score still uses supplied fixed-camera data and should not be presented as strict independent heldout generalization.

## TCN Completion Audit After Report 92

Artifact:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_status_current.json
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_status_current.md
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_status_runner_chain.json
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_status_runner_chain.md
```

| status | live_status | strict_heldout_status | tempo_acc | gain_acc | p90 ms | stream rows | stdin rows |
|---|---|---|---:|---:|---:|---:|---:|
| IN_PROGRESS | GO | NO_GO | 1.0000 | 1.0000 | 1.6854 | 216 | 3 |

Strict completion remains blocked by missing roots:

```text
dataset/strict_heldout_static_v1
dataset/strict_heldout_transitions_v1
```

## Strict Final Chain After Report 93

Dry-run artifacts:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_post_arrival_goal_dryrun.json
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_post_arrival_goal_dryrun.md
```

The final strict chain now ends with:

```text
tcn-handmark-stream-readiness with stream/stdin JSONL output contract
tcn-goal-status --fail-on-in-progress
```

Final status artifacts after strict data arrives:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_goal_status.json
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_goal_status.md
```

## Live Release Handoff After Report 94

Artifacts:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json
docs/exp/tcn_live_handoff_runbook.md
```

Status:

```text
LIVE_READY_STRICT_HELDOUT_PENDING
live_status: GO
strict_heldout_status: NO_GO
```

## Live Release Validation After Report 95

Artifacts:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation.json
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation.md
```

Result:

```text
status: GO
error_count: 0
```

Goal runner chain:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_release_validation_goal_chain.json
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_release_validation_goal_chain.md
```

## Strict Release-Precheck Chain After Report 97

Preferred strict post-arrival dry-run:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_post_arrival_goal_dryrun.json
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_post_arrival_goal_dryrun.md
```

Order after Report 109:

```text
tcn_release_validate -> heldout_independence -> strict_heldout_scope -> strict_heldout_preflight -> strict scoring/readiness -> tcn_goal_status -> tcn_current_status
```

## Strict Heldout Current Preflight After Report 99

Artifacts:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/report99_strict_heldout_independence.json
outputs/right_conducting/selected_tcn_handmark_live45f/report99_strict_heldout_scope.json
outputs/right_conducting/selected_tcn_handmark_live45f/report99_strict_heldout_missing_checklist.json
outputs/right_conducting/selected_tcn_handmark_live45f/report99_strict_heldout_preflight.json
```

Result:

| gate | status | key evidence |
|---|---|---|
| heldout independence | NO_GO | heldout session count 0, missing strict roots 2 |
| strict scope | NO_GO | P0 required/present/missing = 8/0/8 |
| strict preflight | NO_GO | P0 capture count 8 |

This does not change the live score. It confirms that the selected TCN live path is runnable, while strict independent heldout generalization is still unproven until `dataset/strict_heldout_static_v1` and `dataset/strict_heldout_transitions_v1` exist and pass the Report 97 release-precheck chain.

## Goal Completion Audit After Report 100

Report:

```text
docs/exp/goal_reports/2026-06-17_100_goal_completion_audit_matrix.md
```

Verdict:

```text
live runtime deliverables: DONE
deployment-fit supplied-set score: DONE
release handoff: DONE
strict independent heldout: NOT DONE
overall goal: IN_PROGRESS
```

## Strict Post-Arrival Script After Report 101

Preferred command after strict data arrival:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh
```

Dry-run first:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh --dry-run
```

Verified dry-run artifact:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_post_arrival_goal_run.json
```

The script keeps `tcn_release_validate` first and `tcn_goal_status` last.

## Strict Post-Arrival Script Test Guard After Report 102

The strict post-arrival script is now covered by `tests/test_goal_command_cli.py`.

Verification:

```text
test_goal_command_cli.py: 41 OK
full unittest suite: 262 OK, 56.763s
```

The guarded invariant is:

```text
dry-run command count: 11
first step: tcn_release_validate
last step: tcn_goal_status
env override for STRICT_STREAM_CSV is propagated
```

## Strict Post-Arrival CSV Autodiscovery After Report 103

The strict post-arrival script now selects its representative transition CSV in this order:

```text
STRICT_STREAM_CSV env
default P0 transition filename if present
first sorted *.csv under strict transition root
placeholder path for dry-run visibility
```

Verification:

```text
test_goal_command_cli.py: 42 OK
full unittest suite: 263 OK, 58.555s
```

## Current Release Status Snapshot After Report 104

Artifacts:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_report104.json
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_status_report104.json
```

Result:

```text
release validation: GO, error_count 0
goal status: IN_PROGRESS
live status: GO
strict heldout status: NO_GO
```

Selected live metrics remain:

```text
tempo_acc: 1.0000
gain_acc: 1.0000
false_switches_per_min: 0.0000
missed_switch_count: 0
benchmark_p90_ms: 1.6854
stream/stdin contract errors: 0 / 0
```

## Current Status Dashboard After Report 105

Short handoff entry point:

```text
docs/exp/current_status.md
```

It summarizes the selected TCN live bundle, current supplied-set score, strict heldout blocker, and strict post-arrival command.
