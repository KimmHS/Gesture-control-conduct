# Report 101 - Strict Post-Arrival Script

## Purpose

Turn the strict post-arrival TCN release-precheck chain into a single command. This avoids manually rebuilding the long Report 97 command after strict heldout data arrives.

## Added Script

```text
scripts/run_tcn_strict_post_arrival_goal.sh
```

Default behavior:

```text
release validation first
strict heldout independence/scope/missing/preflight
TCN strict handmark stream replay
TCN strict set score/gate
TCN benchmark
TCN readiness with stream/stdin output contract
TCN goal status last with --fail-on-in-progress
```

## Usage

Current dry-run check:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh --dry-run
```

After strict data arrives:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh
```

If the representative transition CSV has a different filename:

```bash
STRICT_STREAM_CSV=dataset/strict_heldout_transitions_v1/<real_transition_file>.csv \
  scripts/run_tcn_strict_post_arrival_goal.sh
```

Optional environment overrides:

```text
PYTHON
DEVICE
SELECTED_ROOT
STRICT_STATIC_ROOT
STRICT_TRANSITION_ROOT
STRICT_STREAM_CSV
TRAIN_MANIFEST
```

## Dry-Run Verification

Commands run:

```bash
bash -n scripts/run_tcn_strict_post_arrival_goal.sh
scripts/run_tcn_strict_post_arrival_goal.sh --dry-run
```

Dry-run artifact:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_post_arrival_goal_run.json
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_post_arrival_goal_run.md
```

Verified dry-run order:

```text
dry_run: True
command_count: 11
first step: tcn_release_validate
last step: tcn_goal_status
```

## Decision

Use this script as the preferred strict post-arrival command. It keeps the Report 97 release validation first and the Report 100 completion audit invariant at the end. The full goal remains active until the strict roots exist and this script completes with `tcn-goal-status` passing.
