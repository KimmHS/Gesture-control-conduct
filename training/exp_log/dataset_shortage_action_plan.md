# Dataset Shortage Action Plan

24 takes / 단일 인물 추정 / heldout transition 1개 상황에서 v0 실험을 어떻게 보완할지와, 사용자에게 추가로 요청할 녹화 리스트를 정리한다. 우선순위는 (효과) × (구현/녹화 비용의 역수) 기준이다.

## Quick Navigation

| 보고 싶은 내용 | 위치 |
|---|---|
| 현재 데이터 상태와 risk | [Current State](#current-state) |
| 추가 녹화 없이 시도할 개선 | [Section A](#section-a-추가-녹화-없이-시도할-개선) |
| 사용자에게 요청할 추가 녹화 리스트 | [Section B](#section-b-사용자에게-요청할-추가-녹화-리스트) |
| 시간별 의사결정 | [Decision Tree](#decision-tree) |
| 데이터 추가 시 지킬 원칙 | [Reporting Rule](#reporting-rule) |
| 새 데이터 공급 후 첫 명령 | [Supplied Data Intake](#supplied-data-intake) |

---

## Current State

`docs/reference/CURRENT_DATA.md` + `docs/exp/right_hand_conducting_experiment_overview.md` 기준 (2026-06-16).

Latest status after Report 111:

```text
selected fixed-camera live pilot bundle: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext
deployment-fit replay: GO
live runtime readiness: GO
label-free / online stream evidence: GO
JSONL/stdin pose stream evidence: GO
handmark CSV stream evidence: GO only when reference joints 8/9/11 are present or supplied
pose quality hold gate: GO
available strict heldout independence: GO for dataset/evaluation,dataset/evaluation_transitions
available strict heldout stress: NO_GO on 222455
strict heldout scope audit: NO_GO
reason: available eval roots are independent but cover 0/8 current P0 2/3-beat fixed-camera heldout cases.
diagnosis: deployment-fit static80/transitions replay has no smoothed tempo error runs, but current eval roots collapse on out-of-scope stress.
next hard gate: record new in-scope fixed-camera heldout roots that are not included in recordings_staged_static80_transitions_manifest.json.
strict pass now requires three gates:
  1. heldout independence GO
  2. strict heldout scope audit GO
  3. live replay gate GO
right-arm-only probe after Report 74:
  manifest: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/motionbert_conducting_live_manifest.json
  status: fixed-camera handmark-only probe GO on deployment-fit replay, not strict heldout replacement
  use case: live input has only right shoulder/elbow/wrist and no reference joints 8/9/11
raw handmark CSV set score after Report 75:
  score: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.json
  gate: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.json
  gate_status: GO
  margin3 smoothed tempo_acc: 0.9989
  margin3 r80/r100/r120: 0.9983 / 1.0000 / 1.0000
  margin3 false_switches_per_min: 0.1230
  status: deployment-fit pass, still not strict heldout
TCN handmark live stream after Report 80:
  folder: outputs/right_conducting/tcn_quick_probe_20260617/45f
  live_manifest: outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_live_manifest.json
  score: outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_score.json
  gate: outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_gate.json
  readiness: outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_handmark_stream_readiness.json
  margin3 smoothed tempo_acc: 1.0000
  margin3 r80/r100/r120: 1.0000 / 1.0000 / 1.0000
  margin3 false_switches_per_min: 0.0000
  latency p90: 1.6180 ms against 200 ms update budget
  status: practical fixed-camera TCN fallback GO, still not strict heldout
selected TCN bundle after Report 83:
  folder: outputs/right_conducting/selected_tcn_handmark_live45f
  manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
  structure: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_structure.md
  checkpoint: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_head.pt
  selected checkpoint live smoke rows: 216
  selected checkpoint invalid outputs: 0
  selected checkpoint latency p90: 2.2745 ms against 200 ms update budget
  status: current live-facing fixed-camera bundle, still not strict heldout
manifest runtime after Report 85:
  entrypoint: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
  command mode: tools/run_tcn_handmark_csv_stream.py --manifest
  manifest score: outputs/right_conducting/selected_tcn_handmark_live45f/manifest_stream_set_score.json
  manifest gate: outputs/right_conducting/selected_tcn_handmark_live45f/manifest_stream_set_gate.json
  manifest readiness: outputs/right_conducting/selected_tcn_handmark_live45f/manifest_stream_readiness.json
  manifest latency p90: 1.7361 ms against 200 ms update budget
  status: preferred runtime entrypoint, still not strict heldout
2/3-beat-only all-test after Report 86:
  score: outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_set_score.json
  gate: outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_set_gate.json
  readiness: outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness.json
  csv_count: 11
  margin3 smoothed tempo_acc: 1.0000
  margin3 smoothed gain_acc: 1.0000
  margin3 false_switches_per_min: 0.0000
  latency p90: 1.6854 ms against 200 ms update budget
  beat4 CSV files: explicitly excluded
  strict preflight: NO_GO, P0 0/8 because dataset/strict_heldout_static_v1 and dataset/strict_heldout_transitions_v1 are not present
stdin live contract after Report 87:
  command mode: tools/run_tcn_handmark_csv_stream.py --handmark-csv - --output-jsonl - --flush-each-output
  smoke summary: outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_summary.json
  smoke rows: 3
  smoke invalid: 0
  status: pipe-style live runtime GO, still not strict heldout
readiness gate with stdin after Report 88:
  artifact: outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness_with_stdin.json
  status: GO
  checks: score gate, benchmark, CSV stream smoke, stdin live JSONL smoke
  status caveat: still not strict heldout
strict heldout post-arrival chain after Report 89:
  dryrun: outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_post_arrival_goal_dryrun.md
  status: ready to run after dataset/strict_heldout_static_v1 and dataset/strict_heldout_transitions_v1 are recorded
  guard: strict-heldout-preflight uses --fail-on-no-go before model score reporting
live output JSONL contract after Report 90:
  alltest validation: outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_outputs_contract.json
  stdin validation: outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_outputs_contract.json
  readiness: outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness_with_output_contract.json
  status: GO, zero contract errors
final TCN live verification after Report 91:
  report: docs/exp/goal_reports/2026-06-17_91_tcn_live_final_verification_snapshot.md
  fixed-camera supplied-set status: GO
  alltest margin3 samples: 1824
  alltest tempo/gain acc: 1.0000 / 1.0000
  alltest JSONL contract: GO, 216 rows, zero errors
  stdin JSONL contract: GO, 3 rows, zero errors
  full unittest suite: 252 OK
  strict heldout status: NO_GO until dataset/strict_heldout_static_v1 and dataset/strict_heldout_transitions_v1 are recorded
latest TCN all-test rerun after Report 106:
  folder: outputs/right_conducting/tcn_alltest_latest
  score: outputs/right_conducting/tcn_alltest_latest/stream_set_score.json
  gate: outputs/right_conducting/tcn_alltest_latest/stream_set_gate.json
  readiness: outputs/right_conducting/tcn_alltest_latest/stream_readiness.json
  benchmark: outputs/right_conducting/tcn_alltest_latest/stream_benchmark.json
  csv_count: 11
  beat4 CSV files: excluded
  margin3 samples: 1824
  margin3 smoothed tempo_acc: 1.0000
  margin3 smoothed gain_acc: 1.0000
  margin3 r80/r100/r120: 1.0000 / 1.0000 / 1.0000
  margin3 false_switches_per_min: 0.0000
  latency p90: 1.9984 ms against 200 ms update budget
  full unittest suite: 264 OK
  status: live/runtime GO, strict heldout still NO_GO
current status exporter after Report 107:
  command: tools/export_tcn_current_status.py
  json: outputs/right_conducting/tcn_alltest_latest/current_status_snapshot.json
  markdown: outputs/right_conducting/tcn_alltest_latest/current_status_snapshot.md
  full unittest suite: 268 OK
  status: reproducible dashboard generation from goal/release/preflight artifacts
tcn-current-status goal runner step after Report 108:
  step: tcn-current-status
  command: tools/run_right_conducting_goal.py --steps tcn-current-status
  json: outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.json
  markdown: outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.md
  focused runner tests: 43 OK
  full regression suite: 270 OK
  status: dashboard generation is now part of the reproducible goal command surface
selected TCN model card refresh after Report 110:
  report: docs/exp/goal_reports/2026-06-17_110_selected_tcn_model_card_refresh.md
  model_card: docs/exp/right_hand_conducting_model_card.md
  current selected model: selected_tcn_handmark_live45f
  trainable_parameter_count: 147910
  status: model card now opens with TCN selected model, MotionBERT kept as historical comparison
current goal evidence audit after Report 111:
  report: docs/exp/goal_reports/2026-06-17_111_current_goal_evidence_audit.md
  selected live model: selected_tcn_handmark_live45f
  supplied fixed-camera score: tempo_acc 1.0000, gain_acc 1.0000, false_switches_per_min 0.0000
  runtime status: GO
  release validation: GO
  strict heldout: NO_GO, P0 0/8
  latest full unittest suite: 270 OK, 58.982s
  completion line: scripts/run_tcn_strict_post_arrival_goal.sh must finish with strict_heldout_status GO
strict post-arrival dry-run recheck after Report 112:
  report: docs/exp/goal_reports/2026-06-17_112_strict_post_arrival_dryrun_recheck.md
  dryrun: outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_post_arrival_goal_run.json
  step_count: 12
  first step: tcn-release-validate
  last step: tcn-current-status
  status: command wiring ready, strict data still required
strict heldout data contract after Report 113:
  contract: docs/exp/strict_heldout_data_contract.md
  report: docs/exp/goal_reports/2026-06-17_113_strict_heldout_data_contract.md
  key rule: each strict CSV must have a sibling processed session directory with the same stem
  required processed artifacts: meta.json, labels_frame.jsonl, labels_window.jsonl, pose_right_h36m_masked.npy, right_rule_features.npy
strict data contract gate after Report 114:
  report: docs/exp/goal_reports/2026-06-17_114_strict_data_contract_gate.md
  checker: tools/check_right_conducting_strict_data_contract.py
  strict post-arrival chain: 13 steps, data contract gate before strict preflight
  dryrun assertion: strict_post_arrival_13step_data_contract_dryrun_assertions_ok
  full unittest suite: 274 OK, 59.183s
current strict data contract snapshot after Report 115:
  report: docs/exp/goal_reports/2026-06-17_115_current_strict_data_contract_snapshot.md
  artifact: outputs/right_conducting/tcn_alltest_latest/current_strict_data_contract.json
  status: NO_GO
  P0 required / present / missing: 8 / 0 / 8
  next action: record strict heldout P0 roots before stream scoring
  full unittest suite: 275 OK, 57.475s
current status data-contract wiring after Report 116:
  report: docs/exp/goal_reports/2026-06-17_116_current_status_includes_data_contract.md
  artifacts: outputs/right_conducting/tcn_alltest_latest/current_status_snapshot.json, outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.json
  strict_data_contract.status: NO_GO
  strict_data_contract.p0_present: 0
  wrapper: final tcn-current-status step now receives strict_v1_tcn_release_precheck_data_contract.json
  full unittest suite: 275 OK, 58.739s
full test/release/status rerun after Report 117:
  report: docs/exp/goal_reports/2026-06-17_117_full_test_release_and_status_rerun.md
  full unittest suite: 275 OK, 56.925s
  release validation: GO
  supplied-set gate: GO, 15 CSV / 11 scoreable sessions, margin 3s tempo_acc 1.0, gain_acc 1.0
  strict data contract: NO_GO, P0 0/8
  status artifact: outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.json
score doc/runner order refresh after Report 118:
  report: docs/exp/goal_reports/2026-06-17_118_score_doc_and_runner_order_refresh.md
  score doc now points to: outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.json
  strict wrapper order assertion: strict_post_arrival_order_assertions_ok
  focused runner tests: 44 OK, 2.846s
handoff/model-card refresh after Report 119:
  report: docs/exp/goal_reports/2026-06-17_119_tcn_handoff_and_model_card_refresh.md
  handoff: docs/exp/tcn_live_handoff_runbook.md
  model card: docs/exp/right_hand_conducting_model_card.md
  latest status artifact: outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.json
  assertion: handoff_model_card_latest_assertions_ok
submission/presentation refresh after Report 120:
  report: docs/exp/goal_reports/2026-06-17_120_submission_and_presentation_refresh.md
  submission format: docs/exp/final_report_submission_format.md
  presentation summary: docs/exp/presentation_training_summary.md
  assertion: submission_presentation_latest_tcn_assertions_ok
release docs consistency gate after Report 121:
  report: docs/exp/goal_reports/2026-06-17_121_tcn_release_docs_consistency_gate.md
  checker: tools/check_tcn_release_docs.py
  artifact: outputs/right_conducting/tcn_alltest_latest/release_docs_check.json
  status: GO, 63 checks, 0 failed
  focused tests: 4 OK, 0.137s
release docs goal runner step after Report 122:
  report: docs/exp/goal_reports/2026-06-17_122_goal_runner_tcn_release_docs_step.md
  step: tcn-release-docs
  artifact: outputs/right_conducting/tcn_alltest_latest/release_docs_goal_chain.json
  status: GO, 63 checks, 0 failed
  focused runner tests: 45 OK, 2.942s
  full unittest suite: 281 OK, 58.072s
TCN completion audit after Report 92:
  report: docs/exp/goal_reports/2026-06-17_92_tcn_goal_status_completion_audit.md
  command: tools/summarize_tcn_right_conducting_goal_status.py
  goal runner step: tcn-goal-status
  artifact: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_status_current.json
  status: IN_PROGRESS
  live_status: GO
  strict_heldout_status: NO_GO
  full unittest suite: 257 OK
strict final post-arrival chain after Report 93:
  report: docs/exp/goal_reports/2026-06-17_93_strict_post_arrival_final_chain.md
  dryrun: outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_post_arrival_goal_dryrun.md
  final status artifact: outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_goal_status.json
  includes: strict preflight fail-fast, stream/stdin JSONL contract readiness, tcn-goal-status --fail-on-in-progress
TCN live release handoff after Report 94:
  report: docs/exp/goal_reports/2026-06-17_94_tcn_live_release_handoff.md
  release manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json
  runbook: docs/exp/tcn_live_handoff_runbook.md
  status: LIVE_READY_STRICT_HELDOUT_PENDING
TCN live release validation after Report 95:
  report: docs/exp/goal_reports/2026-06-17_95_tcn_live_release_manifest_validation.md
  validator: tools/check_tcn_live_release_manifest.py
  artifact: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation.json
  status: GO
  error_count: 0
  full unittest suite: 260 OK
TCN release validation runner after Report 96:
  report: docs/exp/goal_reports/2026-06-17_96_tcn_release_validation_goal_runner.md
  goal runner step: tcn-release-validate
  artifact: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_release_validation_goal_chain.json
  status: GO
  full unittest suite: 261 OK
strict release-precheck final chain after Report 97:
  report: docs/exp/goal_reports/2026-06-17_97_strict_chain_with_release_precheck.md
  dryrun: outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_post_arrival_goal_dryrun.md
  first step: tcn-release-validate --fail-on-no-go
  final step: tcn-goal-status --fail-on-in-progress
  full unittest suite: 261 OK, 56.241s
full test rerun after Report 98:
  report: docs/exp/goal_reports/2026-06-17_98_full_test_rerun.md
  release validation: GO, error_count 0
  goal status: IN_PROGRESS, live GO, strict heldout NO_GO
strict heldout current preflight after Report 99:
  report: docs/exp/goal_reports/2026-06-17_99_strict_heldout_current_preflight.md
  strict preflight: NO_GO
  heldout session count: 0
  missing roots: dataset/strict_heldout_static_v1, dataset/strict_heldout_transitions_v1
  P0 required / present / missing: 8 / 0 / 8
goal completion audit after Report 100:
  report: docs/exp/goal_reports/2026-06-17_100_goal_completion_audit_matrix.md
  verdict: live ready, strict heldout pending, goal active
strict post-arrival script after Report 101:
  report: docs/exp/goal_reports/2026-06-17_101_strict_post_arrival_script.md
  script: scripts/run_tcn_strict_post_arrival_goal.sh
  dry-run: strict_v1_tcn_release_precheck_post_arrival_goal_run.json, 11 steps, release validation first, tcn-goal-status last
strict post-arrival current-status snapshot after Report 109:
  report: docs/exp/goal_reports/2026-06-17_109_strict_post_arrival_current_status_snapshot.md
  script: scripts/run_tcn_strict_post_arrival_goal.sh
  dry-run: strict_v1_tcn_release_precheck_post_arrival_goal_run.json, 13 steps, release validation first, data contract before preflight, tcn-current-status last
  final snapshot: strict_v1_tcn_release_precheck_current_status.json/md
  focused runner tests: 43 OK
  full regression suite: 270 OK
strict post-arrival script test guard after Report 102:
  report: docs/exp/goal_reports/2026-06-17_102_strict_script_test_guard.md
  focused test: test_goal_command_cli.py 41 OK
  full unittest suite: 262 OK, 56.763s
strict post-arrival CSV autodiscovery after Report 103:
  report: docs/exp/goal_reports/2026-06-17_103_strict_script_csv_autodiscovery.md
  behavior: STRICT_STREAM_CSV env wins, else default P0 filename, else first sorted CSV under strict transition root
  focused test: test_goal_command_cli.py 42 OK
  full unittest suite: 263 OK, 58.555s
current release/status snapshot after Report 104:
  report: docs/exp/goal_reports/2026-06-17_104_current_release_status_snapshot.md
  release validation: GO, error_count 0
  goal status: IN_PROGRESS, live GO, strict heldout NO_GO
current status dashboard after Report 105:
  report: docs/exp/goal_reports/2026-06-17_105_current_status_dashboard.md
  dashboard: docs/exp/current_status.md
  verdict: live GO, strict heldout NO_GO, goal active
```

Strict heldout preflight command:

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence,strict-heldout-scope,strict-heldout-missing-checklist,strict-heldout-preflight,replay-selected,diagnose-replay,live-output,live-replay-gate,goal-status \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/strict_heldout_static_v1,dataset/strict_heldout_transitions_v1 \
  --heldout-independence-output-json outputs/right_conducting/strict_heldout_independence_v1.json \
  --heldout-independence-output-md outputs/right_conducting/strict_heldout_independence_v1.md \
  --heldout-scope-output-json outputs/right_conducting/strict_heldout_scope_v1.json \
  --heldout-scope-output-md outputs/right_conducting/strict_heldout_scope_v1.md \
  --heldout-target-static-root dataset/strict_heldout_static_v1 \
  --heldout-target-transition-root dataset/strict_heldout_transitions_v1 \
  --heldout-missing-output-json outputs/right_conducting/strict_heldout_missing_checklist_v1.json \
  --heldout-missing-output-md outputs/right_conducting/strict_heldout_missing_checklist_v1.md \
  --heldout-preflight-output-json outputs/right_conducting/strict_heldout_preflight_v1.json \
  --heldout-preflight-output-md outputs/right_conducting/strict_heldout_preflight_v1.md \
  --heldout-preflight-fail-on-no-go \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext \
  --motionbert-replay-stable-only \
  --motionbert-replay-output-json outputs/right_conducting/strict_heldout_replay_v1.json \
  --motionbert-replay-output-md outputs/right_conducting/strict_heldout_replay_v1.md \
  --motionbert-replay-output-rows outputs/right_conducting/strict_heldout_replay_v1_rows.jsonl \
  --replay-diagnosis-output-json outputs/right_conducting/strict_heldout_replay_diagnosis_v1.json \
  --replay-diagnosis-output-md outputs/right_conducting/strict_heldout_replay_diagnosis_v1.md \
  --live-output-jsonl outputs/right_conducting/strict_heldout_live_outputs_v1.jsonl \
  --live-output-summary-json outputs/right_conducting/strict_heldout_live_outputs_v1_summary.json \
  --live-replay-gate-output-json outputs/right_conducting/strict_heldout_live_gate_v1.json \
  --live-replay-gate-output-md outputs/right_conducting/strict_heldout_live_gate_v1.md \
  --live-replay-gate-require-independence \
  --goal-status-output-json outputs/right_conducting/goal_status_strict_heldout_v1.json \
  --goal-status-output-md outputs/right_conducting/goal_status_strict_heldout_v1.md
```

| 항목 | 값 |
|---|---|
| training takes | 24 |
| training subject | 1명 추정 (single-subject) |
| BPM coverage | `60 / 80 / 100 / 120` — 4 클래스, 중간값 없음 |
| dynamics coverage | `small / large` — 2 클래스, 중간 없음 |
| meter coverage | `2 / 3 / 4` |
| usable heldout (stress) | `dataset/evaluation/session_20260616_222455_bpm120_beat4_large`, but 4-beat/mixed timeline and current strict gate NO_GO |
| transition stress set | `dataset/transitions` 11 takes, `100/120 -> 80 -> 100/120` |
| processed 2/3-beat dev/static set | 11 processed sessions, all >= 40s, no 4-beat processed session mixed in |
| excluded beat4 CSV-only data | 4 transition CSV files without processed labels/pose/right_rule_features |
| pending heldout (mislabeled) | `dataset/evaluation_transitions/session_20260616_215630_bpm100_beat4_large` |
| in-scope strict heldout coverage | 0/8 P0 cases — see `outputs/right_conducting/strict_heldout_scope_audit_ext.md` |

Risk:

- single-subject overfitting을 take-level cross-validation으로 잡지 못한다.
- `tempo_false_switches_per_min`, `tempo_switch_latency_p90_s`를 1개 세션으로 측정하면 분산이 매우 크다.
- BPM이 4 discrete class라 70 / 90 / 110 같은 중간값은 학습도 평가도 불가능하다.
- `bpm_distribution` 같은 soft label이 frame annotation에 이미 있는데 hard class로 떨궈서 정보가 버려진다.
- 2026-06-17 5-GPU hparam sweep 결과, 222455에서는 `tempo_120_recall`, 새 `dataset/transitions`에서는 `tempo_80_recall`이 무너졌다. 단순 head hparam 문제가 아니라 take/domain-specific tempo cue collapse로 본다.

Latest reference:

```text
Report 38: docs/exp/goal_reports/2026-06-17_38_5gpu_hparam_sweep_transition_stress.md
Report 62: docs/exp/goal_reports/2026-06-17_62_strict_heldout_scope_audit.md
Report 65: docs/exp/goal_reports/2026-06-17_65_strict_goal_status_runner_chain.md
Report 66: docs/exp/goal_reports/2026-06-17_66_current_eval_strict_chain_execution.md
Report 67: docs/exp/goal_reports/2026-06-17_67_replay_failure_diagnosis.md
Report 68: docs/exp/goal_reports/2026-06-17_68_deployment_vs_current_eval_diagnosis.md
Report 69: docs/exp/goal_reports/2026-06-17_69_strict_heldout_missing_checklist_runner.md
Report 70: docs/exp/goal_reports/2026-06-17_70_strict_heldout_preflight_gate.md
Report 71: docs/exp/goal_reports/2026-06-17_71_live_runtime_readiness_gate.md
Report 72: docs/exp/goal_reports/2026-06-17_72_jsonl_stdin_pose_stream_adapter.md
Report 73: docs/exp/goal_reports/2026-06-17_73_handmark_csv_stream_adapter.md
Report 74: docs/exp/goal_reports/2026-06-17_74_right_arm_only_input_mask_probe.md
Report 75: docs/exp/goal_reports/2026-06-17_75_raw_handmark_csv_stream_set_score.md
Report 76: docs/exp/goal_reports/2026-06-17_76_handmark_csv_stream_set_gate.md
Report 77: docs/exp/goal_reports/2026-06-17_77_goal_runner_handmark_csv_set_gate.md
Report 79: docs/exp/goal_reports/2026-06-17_79_tcn_quick_probe.md
Report 80: docs/exp/goal_reports/2026-06-17_80_tcn_handmark_live_stream.md
Report 81: docs/exp/goal_reports/2026-06-17_81_tcn_handmark_stream_readiness_gate.md
Report 82: docs/exp/goal_reports/2026-06-17_82_tcn_goal_runner_full_test.md
Report 83: docs/exp/goal_reports/2026-06-17_83_selected_tcn_live_bundle.md
Report 84: docs/exp/goal_reports/2026-06-17_84_webcam_overlay_recovery_and_full_tests.md
Report 85: docs/exp/goal_reports/2026-06-17_85_tcn_manifest_runtime_path.md
Report 86: docs/exp/goal_reports/2026-06-17_86_tcn_2beat3beat_all_test_and_strict_preflight.md
Report 87: docs/exp/goal_reports/2026-06-17_87_tcn_stdin_live_output_contract.md
Report 88: docs/exp/goal_reports/2026-06-17_88_tcn_readiness_gate_includes_stdin.md
Report 89: docs/exp/goal_reports/2026-06-17_89_tcn_strict_heldout_post_arrival_chain.md
Report 90: docs/exp/goal_reports/2026-06-17_90_live_output_jsonl_contract_gate.md
Report 91: docs/exp/goal_reports/2026-06-17_91_tcn_live_final_verification_snapshot.md
Report 92: docs/exp/goal_reports/2026-06-17_92_tcn_goal_status_completion_audit.md
Report 93: docs/exp/goal_reports/2026-06-17_93_strict_post_arrival_final_chain.md
Report 94: docs/exp/goal_reports/2026-06-17_94_tcn_live_release_handoff.md
Report 95: docs/exp/goal_reports/2026-06-17_95_tcn_live_release_manifest_validation.md
Report 96: docs/exp/goal_reports/2026-06-17_96_tcn_release_validation_goal_runner.md
Report 97: docs/exp/goal_reports/2026-06-17_97_strict_chain_with_release_precheck.md
Report 98: docs/exp/goal_reports/2026-06-17_98_full_test_rerun.md
Report 99: docs/exp/goal_reports/2026-06-17_99_strict_heldout_current_preflight.md
Report 100: docs/exp/goal_reports/2026-06-17_100_goal_completion_audit_matrix.md
Report 101: docs/exp/goal_reports/2026-06-17_101_strict_post_arrival_script.md
Report 102: docs/exp/goal_reports/2026-06-17_102_strict_script_test_guard.md
Report 103: docs/exp/goal_reports/2026-06-17_103_strict_script_csv_autodiscovery.md
Report 104: docs/exp/goal_reports/2026-06-17_104_current_release_status_snapshot.md
Report 105: docs/exp/goal_reports/2026-06-17_105_current_status_dashboard.md
Report 111: docs/exp/goal_reports/2026-06-17_111_current_goal_evidence_audit.md
Report 112: docs/exp/goal_reports/2026-06-17_112_strict_post_arrival_dryrun_recheck.md
Report 113: docs/exp/goal_reports/2026-06-17_113_strict_heldout_data_contract.md
Report 114: docs/exp/goal_reports/2026-06-17_114_strict_data_contract_gate.md
Report 115: docs/exp/goal_reports/2026-06-17_115_current_strict_data_contract_snapshot.md
Report 116: docs/exp/goal_reports/2026-06-17_116_current_status_includes_data_contract.md
Report 117: docs/exp/goal_reports/2026-06-17_117_full_test_release_and_status_rerun.md
Report 118: docs/exp/goal_reports/2026-06-17_118_score_doc_and_runner_order_refresh.md
Report 119: docs/exp/goal_reports/2026-06-17_119_tcn_handoff_and_model_card_refresh.md
Report 120: docs/exp/goal_reports/2026-06-17_120_submission_and_presentation_refresh.md
Report 121: docs/exp/goal_reports/2026-06-17_121_tcn_release_docs_consistency_gate.md
Report 122: docs/exp/goal_reports/2026-06-17_122_goal_runner_tcn_release_docs_step.md
selected ext bundle: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext
right-arm-only probe bundle: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe
TCN handmark fallback: outputs/right_conducting/tcn_quick_probe_20260617/45f
selected TCN handmark bundle: outputs/right_conducting/selected_tcn_handmark_live45f
handmark CSV set gate goal command: outputs/right_conducting/right_conducting_goal_handmark_csv_set_gate_dryrun.md
live runtime readiness: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.md
strict scope audit: outputs/right_conducting/strict_heldout_scope_audit_ext.md
strict missing checklist: outputs/right_conducting/current_eval_roots_strict_missing_checklist.md
strict preflight gate: outputs/right_conducting/current_eval_roots_strict_preflight.md
```

## Supplied Data Intake

새 dataset이 공급되면 모델 튜닝보다 먼저 다음 세 gate를 통과시킨다.

```bash
python tools/run_right_conducting_goal.py \
  --steps intake,stage,prepare \
  --train-roots dataset/recordings,NEW_TRAIN_ROOT \
  --eval-roots dataset/evaluation,dataset/evaluation_transitions,NEW_EVAL_ROOT \
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

Gate line:

```text
intake: no missing roots, train sessions are train_ready, heldout transitions are scoreable or explicitly pending
stage: no duplicate take id, no non-ready train session, canonical zip created
prepare: 60f windows/folds generated; validation remains original only
```

그 다음 MotionBERT cache/train dry-run command를 실제 실행으로 바꾼다.

```bash
python tools/run_right_conducting_goal.py \
  --steps cache,train \
  --train-source outputs/right_conducting/recordings_staged_after_supply.zip \
  --dataset-dir outputs/right_conducting/dataset_v0_60f_after_supply \
  --cache-dir outputs/right_conducting/motionbert_cache_after_supply \
  --head-output-dir outputs/right_conducting/motionbert_head_after_supply \
  --window-frames 60 \
  --stride-frames 3 \
  --device cuda:0 \
  --cache-feature-mode mean_std_delta \
  --train-epochs 60 \
  --train-hidden-dim 512
```

5장 GPU를 모두 쓸 수 있고 새 데이터가 충분하면 window-frame sweep을 병렬로 실행한다. 이때 prepare 단계도 같은 `--window-frames`로 먼저 만들어져 있어야 한다.

```bash
python tools/run_right_conducting_goal.py \
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

이 sweep의 기본 판단은 `60f`를 기준 후보로 유지하되, 더 짧은 window가 같은 score gate를 통과하고 replay false switch를 악화시키지 않을 때 live 후보로 올리는 것이다.
`model_candidate_selection_after_supply.json`이 `SELECTED`가 아니면 selected live artifact를 교체하지 않는다.
`export-selected`는 이 경우 실패해야 정상이며, MotionBERT bundle은 생성하지 않는다.
`smoke-selected`는 export된 manifest/head/smoother path가 live predictor로 로드되는지 확인한다.
`replay-selected`는 exported MotionBERT bundle을 eval session에 다시 흘려 raw/smoothed live metric을 만든다.

학습 후 detailed eval과 score gate를 통과해야 selected model 후보로 올린다.

```bash
python tools/run_right_conducting_goal.py \
  --steps detailed,gate \
  --head-output-dir outputs/right_conducting/motionbert_head_after_supply \
  --detailed-output-prefix outputs/right_conducting/motionbert_after_supply_eval60stable_detailed \
  --window-frames 60 \
  --gate-require-detailed \
  --gate-output-prefix outputs/right_conducting/model_gate_after_supply
```

Reference:

```text
Report 27: docs/exp/goal_reports/2026-06-17_27_new_dataset_intake_gate.md
Report 28: docs/exp/goal_reports/2026-06-17_28_new_dataset_staging_zip_gate.md
Report 29: docs/exp/goal_reports/2026-06-17_29_after_supply_goal_runner.md
Report 30: docs/exp/goal_reports/2026-06-17_30_after_supply_cache_train_runner.md
Report 31: docs/exp/goal_reports/2026-06-17_31_model_score_gate.md
Report 32: docs/exp/goal_reports/2026-06-17_32_after_supply_detailed_eval_gate_runner.md
Report 33: docs/exp/goal_reports/2026-06-17_33_after_supply_5gpu_frame_sweep_runner.md
Report 34: docs/exp/goal_reports/2026-06-17_34_after_supply_model_selection_runner.md
Report 35: docs/exp/goal_reports/2026-06-17_35_motionbert_selected_export_bundle.md
Report 36: docs/exp/goal_reports/2026-06-17_36_motionbert_live_bundle_smoke.md
Report 37: docs/exp/goal_reports/2026-06-17_37_motionbert_live_bundle_replay.md
Report 38: docs/exp/goal_reports/2026-06-17_38_5gpu_hparam_sweep_transition_stress.md
```

## Current Devset Priority After Report 38

다음 데이터는 training augmentation보다 dev/eval 분리를 위해 먼저 필요하다.

Minimum request:

```text
80 static:
- 80 / 2박 / large / fixed camera / high arm
- 80 / 2박 / small / fixed camera / high arm
- 80 / 3박 / large / fixed camera / low arm
- 80 / 3박 / small / fixed camera / low arm
- 80 / 4박 / large / fixed camera / neutral arm
- 80 / 4박 / small / fixed camera / neutral arm

transition:
- 120 -> 80 -> 120 / 2박 / large
- 120 -> 80 -> 120 / 2박 / small
- 120 -> 80 -> 120 / 4박 / large
- 120 -> 80 -> 120 / 4박 / small
```

Gate:

```text
80 static recall >= 0.6 after margin-independent scoring
120 -> 80 held tail 80 recall >= 0.5 after transition_margin_seconds=3
gain_acc >= 0.8
```

이 gate를 못 넘으면 MotionBERT selected replacement는 하지 않는다.

---

## Section A: 추가 녹화 없이 시도할 개선

### A1. Soft-label 학습 (HIGH)

`labels_frame.jsonl`에 `bpm_distribution`이 `[0.0, 0.05, 0.2, 0.5, 0.2, 0.05]` 형태로 이미 있다.

변경:

```text
loss(tempo) = CrossEntropy(logits, tempo_class)
        ->  KLDivLoss(log_softmax(logits), bpm_distribution)
```

효과:

- 100 BPM 학습 시 80 / 120 클래스에도 implicit gradient가 흘러 자료 효율이 오른다.
- argmax-eval과의 mismatch는 small data에서 효과가 우세하다.

Acceptance: KLDiv 적용 fold mean `joint_acc`가 hard CE 대비 `>= +0.01`.

### A2. Label-changing augmentation 활성화 (HIGH)

현재 `DATASET_AUGMENTATION.md §5`에서 v0 제외, `§6`에 future plan으로 미뤄둔 항목을 v0로 끌어온다.

```text
temporal_stretch s in [0.92, 1.10]
  bpm_aug = bpm_original * s
  tempo_class = nearest bin
  bpm_distribution = recompute from bpm_aug

amplitude_scaling a in [0.75, 1.30]
  p_aug[t] = origin + a * (p[t] - origin)
  dynamics_aug = clip(dynamics_original * a, 0, 1)
  dynamics_class = "large" if dynamics_aug >= 0.5 else "small"
```

효과: 24 take 상황에서 BPM-aware augmentation 없이 학습하면 take-level wrist trajectory 패턴이 BPM 자체보다 강한 cue가 될 위험을 줄인다.

Acceptance: TCN 120f 기준 `transition_eval`의 `tempo_acc`가 `+0.02` 이상.

Current evidence:

```text
Report 25 tested target-80 tempo+amplitude augmentation as a feature-baseline diagnostic.
80 BPM recall improved 0.0000 -> 0.8182 on stable 222455 eval windows,
but BPM MAE worsened 10.6173 -> 11.1934 because true 100 BPM windows became over-predicted as 80.
Conclusion: use this direction for stronger model training, but gate it with BPM MAE and false-switch constraints.
```

### A3. Auxiliary head `beat_phase` (MEDIUM)

`labels_frame.jsonl`에 `beat_phase_start/end`가 있다. shared encoder 다음에 `(sin, cos)` 두 출력의 보조 head를 추가한다.

```python
loss = tempo_kld + dynamics_ce + 0.1 * (1 - cos_similarity(phase_pred, phase_target))
```

효과: small data에서 multi-task regularization 효과, BPM 추론의 grounding 강화.

### A4. Confidence-aware loss weighting (MEDIUM)

per-window `valid_ratio = min(valid_right_shoulder, valid_right_elbow, valid_right_wrist)` 를 sample weight로 사용.

```python
loss_per_sample = (tempo_loss + dynamics_loss) * valid_ratio
```

효과: 노이즈 큰 윈도우(특히 `session_20260616_212313_bpm120_beat2_small`)의 grad 영향 감소.

### A5. Self-supervised pretraining on 24 takes (MEDIUM)

DSTformer / TCN backbone을 24 takes의 random temporal mask reconstruction (mask ratio 15%)으로 먼저 pretrain → tempo / dynamics head fine-tune.

비용: 추가 학습 cycle 1개와 reconstruction head 코드.

효과: backbone이 wrist trajectory의 잠재 구조를 먼저 학습. small downstream 성능 ↑가 일반적으로 관찰된다.

### A6. Within-class window mixup (LOW)

같은 `(tempo_class, dynamics_class)` 쌍의 두 window를 `alpha=0.5`로 섞는다. Soft label과 자연스럽게 조합된다.

### A7. Rule-based / sklearn 베이스라인 보고 (LOW, narrative용)

- Rule-based: 기존 `right_rule_features.npy`로 wrist period FFT → BPM, shoulder-wrist amplitude → dynamics. 학습 없이 `transition_eval`만 측정.
- SVM / RandomForest on hand-crafted features.

효과: 발표 narrative ("딥러닝이 rule을 이긴다") 확보. score table 1~2 행 추가.

### A8. Leave-One-Session-Out 분석 (LOW)

24 model을 LOSO로 학습해서 take별 difficulty 분포를 본다. fold 2 variance 가설 검증용. 시간 여유가 있을 때만.

### A9. Confidence calibration (LOW)

학습 모델의 raw softmax를 temperature scaling으로 보정해서 `live_policy.yaml`의 `switch_threshold`, `fast_switch_threshold`가 의미 있는 값이 되게 한다.

---

## Section B: 사용자에게 요청할 추가 녹화 리스트

Format은 `docs/reference/RECORDING_PLAN.md` / `EVALUATION_RECORDING_CHECKLIST.md`를 따른다. 우선순위 순.

### B1. Multi-subject extension (HIGHEST)

목적: single-subject overfitting을 measurable하게 만든다. 이게 없으면 model card에 "single-subject 한계"를 영구 기재해야 한다.

요청:

```text
추가 인물: 2명 이상
1인당 takes: 8 (BPM 60/80/100/120 x dynamics small/large, meter 4박 고정)
duration: 각 60초
audio: 기본 OFF
저장:
  data/recordings_subject_B/
  data/recordings_subject_C/
```

분리 정책:

```text
subject A (현재): train + 3-fold CV
subject B, C   : heldout (training / hyperparameter / early stopping 미사용)
```

총량: 약 16분 (사용자 2명 시간).

### B2. Stable-hold heldout set (HIGH)

목적: `tempo_false_switches_per_min`을 신뢰성 있게 측정. 현재 heldout이 transition 1개뿐이라 hold latency vs false_switch trade-off를 측정 못 한다.

요청 (60초씩, 각 1 take):

| BPM | meter | dynamics |
|---|---|---|
| 80 | 4 | large |
| 100 | 4 | large |
| 100 | 4 | small |
| 120 | 4 | small |

저장:

```text
data/evaluation_stable/
```

총량: 4 takes (4분).

### B3. Transition heldout set 확장 (HIGH)

목적: `switch_latency_p90_s`의 분산 감소. 현재 1 transition session으로는 통계가 약하다.

요청 (각 60~90초, 중간 1회 변화):

| ID | from | to | 변화 변수 |
|---|---|---|---|
| T1 | 60 BPM / large | 100 BPM / large | tempo only |
| T2 | 100 BPM / large | 60 BPM / large | tempo only |
| T3 | 100 BPM / small | 100 BPM / large | dynamics only |
| T4 | 100 BPM / large | 100 BPM / small | dynamics only |
| T5 | 80 BPM / small | 120 BPM / large | tempo + dynamics |

녹화 규칙:

```text
transition 시점은 metronome 변경 시각을 자동 기록 (manual_timeline.json 자동 생성)
또는 사람이 +- 5 frame 이내로 기록
```

저장:

```text
data/evaluation_transitions_v1/
```

총량: 5 takes (약 7분).

### B4. session_20260616_215630_eval 처리 (HIGH, 빠름)

이미 녹화된 1 take를 살린다.

옵션 1: relabel — 실제 transition 시점을 `labels_window.jsonl` / `labels_frame.jsonl`에 반영.
옵션 2: re-record — 같은 protocol로 재촬영하고 깔끔한 timeline 동봉.

비용: relabel은 1 take 분량이라 10분 이내.

### B5. 중간 BPM 탐색 (MEDIUM, optional)

현재 classification 범위는 4 BPM뿐이다. demo에서 70 / 90 / 110이 자연스러우면 다음 추가.

| BPM | meter | dynamics | takes |
|---|---|---|---|
| 70 | 4 | large | 1 |
| 90 | 4 | large | 1 |
| 110 | 4 | large | 1 |

용도: regression head 학습 / 검증. classification head 유지면 nearest bin 매핑으로 사용. classification 유지하기로 했으면 skip.

총량: 3 takes (3분).

### B6. Dynamics calibration (MEDIUM)

목적: `right_rule_features.npy`의 `small_ref` / `large_ref` 기준값을 사용자별로 보정. multi-subject (B1)와 함께 진행하면 효율적.

요청 (사용자별):

```text
정지 자세    : 5초
small 지휘   : 10초
large 지휘   : 10초
total       : 25초
```

저장:

```text
data/calibration/<subject>/
```

### B7. 카메라 / 조명 / 의상 분산 (DEFERRED)

현재 수집 정책은 카메라 위치와 거리를 고정하는 것이다. 따라서 Report 39 이후 devset에는 카메라 거리/조명/배경 variation을 넣지 않는다.

목적 자체는 deploy 환경 robustness 측정이지만, 지금 bottleneck은 camera robustness가 아니라 fixed-camera heldout tempo stability다. 아래 항목은 최종 demo 이후 여유가 있을 때만 진행한다.

요청 (1인 기준, 4 takes, 동일 `100 BPM / large / 4박 / 60초`):

| 변수 | 변경 |
|---|---|
| 카메라 거리 | 평소의 약 2배 거리 |
| 조명 | 어둡게 (스탠드 하나만) |
| 의상 | 반팔 / 긴팔 차이 |
| 배경 | 복잡 배경 |

저장:

```text
data/evaluation_robustness/
```

---

## Recording Budget

| 우선순위 | 항목 | 시간 |
|---|---|---|
| HIGHEST | B1 multi-subject (2명) | 16분 (사용자 2명 시간) |
| HIGH | B2 stable-hold heldout | 4분 |
| HIGH | B3 transition heldout v1 | 7분 |
| HIGH | B4 215630 relabel | 0~10분 (relabel만) |
| MEDIUM | B5 중간 BPM | 3분 |
| MEDIUM | B6 calibration | 6분 |
| LOW | B7 robustness | 4분 |

```text
HIGHEST + HIGH 최소 묶음:
  본인 약 11분 (B2 + B3 + B4)
  추가 인물 시간 16분 (B1)

전체:
  약 50분
```

---

## Decision Tree

```text
사용자 추가 시간 0~30분:
  -> B4 (relabel) + B2 (stable-hold 4 takes)
  -> Section A의 A1, A2, A4 우선 시도
  -> model card에 "single-subject" 한계 기재

사용자 추가 시간 30~60분:
  -> B1 (1명 추가 8 takes) + B2 + B3 + B4
  -> Section A의 A1, A2, A3, A4, A7 모두 시도
  -> multi-subject heldout 결과를 score table 별도 컬럼으로 보고

사용자 추가 시간 불가:
  -> Section A 모두 시도
  -> A1 (soft label) -> A2 (label-changing aug) -> A4 (confidence weight) 순서가 첫 ROI
  -> rule-based / SVM 베이스라인을 같은 score table에 넣어 narrative 보강
  -> model card에 "single-subject, 1 transition session" 한계 명시

새 데이터 공급 예정:
  -> 현재 222455_eval에 추가 튜닝하지 않음
  -> 새 take를 train/heldout으로 먼저 분리
  -> CURRENT_DATA.md 갱신
  -> Report 26의 original head / target80 combo stride3 / selected fallback gate를 재실행
```

---

## Reporting Rule

추가 데이터가 들어오더라도 아래 원칙은 유지한다.

- 새 takes는 저장 전에 `train / heldout` 중 어디로 들어갈지 먼저 결정한다.
- heldout takes는 cross-validation, hyperparameter 선택, early stopping, augmentation 어디에도 사용하지 않는다.
- 모든 새 takes는 `docs/reference/CURRENT_DATA.md` 표에 1행 추가한다.
- multi-subject heldout 결과는 score table에 `subject` 컬럼을 추가해서 동일 take를 다른 subject와 합치지 않는다.
- transition heldout에는 transition frame index를 `manual_timeline.json`에 반드시 동봉한다. 없으면 `switch_latency` 계산이 신뢰할 수 없다.
