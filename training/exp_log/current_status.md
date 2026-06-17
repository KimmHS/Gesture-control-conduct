# Current Status

Last updated from Report 111.

## Verdict

```text
overall goal: IN_PROGRESS
selected live model: TCN handmark live bundle
live runtime: GO
release validation: GO
strict independent heldout: NO_GO
remaining blocker: missing strict heldout roots
```

## Selected Bundle

```text
bundle: outputs/right_conducting/selected_tcn_handmark_live45f
model manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
checkpoint: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_head.pt
structure: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_structure.md
release manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json
model card: docs/exp/right_hand_conducting_model_card.md
```

Model snapshot:

```text
model_type: causal_tcn_right_arm_pose
input: [B, 45, 17, 3]
runtime tensor: [B, 9, 45]
fps: 15
stride_frames: 3
bpm_bins: [60, 80, 100, 120]
gain_classes: small, large
```

## Current Score

Deployment-fit fixed-camera supplied-set evidence, latest rerun:

```text
tempo_acc: 1.0000
gain_acc: 1.0000
80/100/120 recall: 1.0000 / 1.0000 / 1.0000
false_switches_per_min: 0.0000
missed_switch_count: 0
benchmark_p90_ms: 1.9984
stream output contract errors: 0
stdin output contract errors: 0
```

Primary artifacts:

```text
outputs/right_conducting/tcn_alltest_latest/stream_set_score.json
outputs/right_conducting/tcn_alltest_latest/stream_set_gate.json
outputs/right_conducting/tcn_alltest_latest/stream_readiness.json
outputs/right_conducting/tcn_alltest_latest/stream_benchmark.json
outputs/right_conducting/tcn_alltest_latest/tcn_goal_status.json
outputs/right_conducting/tcn_alltest_latest/current_status_snapshot.json
outputs/right_conducting/tcn_alltest_latest/current_status_snapshot.md
outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.json
outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.md
```

Regenerate this dashboard snapshot:

```bash
python tools/export_tcn_current_status.py
```

Or via the goal runner:

```bash
python tools/run_right_conducting_goal.py --steps tcn-current-status
```

## Not Yet Complete

Strict heldout roots are still absent:

```text
dataset/strict_heldout_static_v1
dataset/strict_heldout_transitions_v1
```

Required P0 strict heldout coverage:

```text
static 80 BPM: 2 beat large/small, 3 beat large/small
transition 120 -> 80 -> 120: 2 beat large/small, 3 beat large/small
```

Current strict preflight:

```text
status: NO_GO
independence_status: NO_GO
scope_status: NO_GO
P0 required / present / missing: 8 / 0 / 8
```

## Run After Strict Data Arrives

First dry-run:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh --dry-run
```

Then execute:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh
```

If needed, force a representative transition CSV:

```bash
STRICT_STREAM_CSV=dataset/strict_heldout_transitions_v1/<real_transition_file>.csv \
  scripts/run_tcn_strict_post_arrival_goal.sh
```

## Latest Verification

```text
release validation: GO, error_count 0
goal status: IN_PROGRESS, live GO, strict heldout NO_GO
full unittest suite: 264 OK, 54.287s
latest supplied-set rerun: GO, 11 CSV, 4-beat excluded
current status exporter: 268 OK, 57.367s
tcn-current-status runner step: 43 OK, 2.912s
latest full regression after runner step: 270 OK, 45.090s
strict post-arrival current-status wrapper: 270 OK, 47.045s
selected TCN model card refresh: 270 OK, 58.982s
current goal evidence audit: live GO, release GO, strict heldout NO_GO
strict post-arrival dry-run recheck: 13 steps, release validation first, data contract before preflight, current status last
strict data contract gate: added, focused tests OK, full regression 274 OK
current strict data contract snapshot: NO_GO, P0 0/8, full regression 275 OK
current status data-contract wiring: snapshots include strict_data_contract, full regression 275 OK
latest full test/release/status rerun: unittest 275 OK, supplied-set gate GO, release validation GO, strict data contract NO_GO
score doc/runner order refresh: Report 117 artifacts visible in score doc, runner CLI test 44 OK
handoff/model-card refresh: latest fulltest artifacts visible, 15 raw CSV / 11 scoreable sessions documented
submission/presentation refresh: selected TCN pipeline and latest fulltest score paths documented
release docs consistency gate: GO, 63 checks, 0 failed
release docs goal runner step: tcn-release-docs GO, full regression 281 OK
```

Latest reports:

```text
Report 100: docs/exp/goal_reports/2026-06-17_100_goal_completion_audit_matrix.md
Report 101: docs/exp/goal_reports/2026-06-17_101_strict_post_arrival_script.md
Report 102: docs/exp/goal_reports/2026-06-17_102_strict_script_test_guard.md
Report 103: docs/exp/goal_reports/2026-06-17_103_strict_script_csv_autodiscovery.md
Report 104: docs/exp/goal_reports/2026-06-17_104_current_release_status_snapshot.md
Report 105: docs/exp/goal_reports/2026-06-17_105_current_status_dashboard.md
Report 106: docs/exp/goal_reports/2026-06-17_106_full_test_and_tcn_alltest_rerun.md
Report 107: docs/exp/goal_reports/2026-06-17_107_current_status_exporter.md
Report 108: docs/exp/goal_reports/2026-06-17_108_tcn_current_status_goal_runner_step.md
Report 109: docs/exp/goal_reports/2026-06-17_109_strict_post_arrival_current_status_snapshot.md
Report 110: docs/exp/goal_reports/2026-06-17_110_selected_tcn_model_card_refresh.md
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
```
