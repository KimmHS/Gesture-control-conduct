# Report 117 - Full Test, Release, And Status Rerun

## Purpose

The latest request was to run the whole test path again. This report records the current executable verification state after Report 116.

## Commands Run

```text
PYTHONPATH=. python -m unittest discover tests -v
scripts/run_tcn_strict_post_arrival_goal.sh --dry-run
python tools/check_tcn_live_release_manifest.py --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json --output-json outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_fulltest_latest.json --output-md outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_fulltest_latest.md --fail-on-no-go
python tools/evaluate_tcn_handmark_csv_stream_set.py --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json --csv-root dataset/static_variants_80,dataset/transitions --device cuda:0 --stable-only --margins 0,0.5,1,2,3 --output-json outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.json --output-md outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.md --output-rows outputs/right_conducting/tcn_alltest_latest/stream_set_rows_fulltest_latest.jsonl
python tools/check_motionbert_handmark_csv_stream_set_gate.py --score-json outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.json --margin-seconds 3.0 --min-sample-count 1000 --min-eval-session-count 10 --min-tempo-acc 0.98 --min-gain-acc 0.95 --min-recall-80 0.9 --min-recall-100 0.9 --min-recall-120 0.9 --max-false-switches-per-min 0.5 --max-missed-switch-count 0 --output-json outputs/right_conducting/tcn_alltest_latest/stream_set_gate_fulltest_latest.json --output-md outputs/right_conducting/tcn_alltest_latest/stream_set_gate_fulltest_latest.md
python tools/check_right_conducting_strict_data_contract.py --scope-json outputs/right_conducting/tcn_alltest_latest/current_strict_heldout_scope.json --target-static-root dataset/strict_heldout_static_v1 --target-transition-root dataset/strict_heldout_transitions_v1 --output-json outputs/right_conducting/tcn_alltest_latest/current_strict_data_contract_fulltest_latest.json --output-md outputs/right_conducting/tcn_alltest_latest/current_strict_data_contract_fulltest_latest.md
python tools/summarize_tcn_right_conducting_goal_status.py --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json --gate-json outputs/right_conducting/tcn_alltest_latest/stream_set_gate_fulltest_latest.json --readiness-json outputs/right_conducting/tcn_alltest_latest/stream_readiness.json --benchmark-json outputs/right_conducting/tcn_alltest_latest/stream_benchmark.json --strict-preflight-json outputs/right_conducting/tcn_alltest_latest/current_strict_preflight.json --strict-static-root dataset/strict_heldout_static_v1 --strict-transition-root dataset/strict_heldout_transitions_v1 --output-json outputs/right_conducting/tcn_alltest_latest/tcn_goal_status_fulltest_latest.json --output-md outputs/right_conducting/tcn_alltest_latest/tcn_goal_status_fulltest_latest.md
python tools/export_tcn_current_status.py --goal-status-json outputs/right_conducting/tcn_alltest_latest/tcn_goal_status_fulltest_latest.json --release-validation-json outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_fulltest_latest.json --strict-preflight-json outputs/right_conducting/tcn_alltest_latest/current_strict_preflight.json --strict-data-contract-json outputs/right_conducting/tcn_alltest_latest/current_strict_data_contract_fulltest_latest.json --output-json outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.json --output-md outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.md
```

## Result

```text
full unittest: Ran 275 tests in 56.925s, OK
strict post-arrival wrapper dry-run: 13 linked steps, OK
TCN release manifest validation: GO
TCN supplied-set stream score: 15 CSV, 11 scoreable sessions
TCN supplied-set gate at margin 3s: GO, sample_count 1824, tempo_acc 1.0, gain_acc 1.0
strict data contract on current strict roots: NO_GO, P0 0/8
current status snapshot: IN_PROGRESS, live GO, strict heldout NO_GO
```

## Updated Artifacts

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_fulltest_latest.json
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_fulltest_latest.md
outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.json
outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.md
outputs/right_conducting/tcn_alltest_latest/stream_set_rows_fulltest_latest.jsonl
outputs/right_conducting/tcn_alltest_latest/stream_set_gate_fulltest_latest.json
outputs/right_conducting/tcn_alltest_latest/stream_set_gate_fulltest_latest.md
outputs/right_conducting/tcn_alltest_latest/current_strict_data_contract_fulltest_latest.json
outputs/right_conducting/tcn_alltest_latest/current_strict_data_contract_fulltest_latest.md
outputs/right_conducting/tcn_alltest_latest/tcn_goal_status_fulltest_latest.json
outputs/right_conducting/tcn_alltest_latest/tcn_goal_status_fulltest_latest.md
outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.json
outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.md
```

## Interpretation

The code/test path is clean and the selected TCN live bundle still validates as release-ready for the current live artifact contract. The full goal remains `IN_PROGRESS` because strict heldout roots are still absent and the strict data contract remains `NO_GO`.
