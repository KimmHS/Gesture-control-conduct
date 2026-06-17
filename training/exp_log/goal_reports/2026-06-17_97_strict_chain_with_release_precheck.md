# Report 97 - Strict Chain With Release Precheck

## Purpose

Create the final strict post-arrival dry-run with release validation as the first fail-fast step. This keeps the selected TCN release package validated before any strict heldout scoring starts.

## Dry-Run Artifacts

```text
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_post_arrival_goal_dryrun.json
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_post_arrival_goal_dryrun.md
```

## Chain Order

```text
tcn-release-validate --fail-on-no-go
heldout-independence
strict-heldout-scope
strict-heldout-missing-checklist
strict-heldout-preflight --fail-on-no-go
tcn-handmark-csv-stream
tcn-handmark-csv-set-score
tcn-handmark-csv-set-gate
tcn-handmark-csv-benchmark
tcn-handmark-stream-readiness with stream/stdin JSONL output contract
tcn-goal-status --fail-on-in-progress
```

Confirmed from dry-run JSON:

```text
first_step: tcn_release_validate
last_step: tcn_goal_status
release_precheck_fail_on_no_go: true
```

## Why Release Validation Is First

`tcn_live_release_manifest.json` describes the selected runnable package and references the checkpoint, live manifest, score gate, readiness, output contract, and current goal status. If that package is stale or internally inconsistent, strict heldout scoring should not start. The strict data score is still judged at the end by `tcn-goal-status`.

## Verification

```text
python -m py_compile tools/run_right_conducting_goal.py tests/test_goal_command_cli.py
PYTHONPATH=. python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
```

Result:

```text
test_goal_command_cli.py: 40 OK
full unittest suite: 261 OK, 56.241s
```

## Decision

For future strict data arrival, prefer the release-precheck dry-run over the older Report 93 final chain. Current completion is still blocked by missing strict heldout roots.
