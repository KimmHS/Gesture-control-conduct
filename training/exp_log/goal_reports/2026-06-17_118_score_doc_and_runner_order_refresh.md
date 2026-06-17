# Report 118 - Score Doc And Runner Order Refresh

## Purpose

After Report 117, the latest supplied-set score artifacts existed, but the first score block in `right_hand_conducting_scores.md` still pointed primarily at the Report 106 artifact names. The goal runner help string also listed `strict-heldout-data-contract` before `strict-heldout-missing-checklist`, while the real post-arrival chain runs scope -> missing checklist -> data contract -> preflight.

This report records the cleanup so the docs and runner surface match the current execution path.

## Updated Files

```text
docs/exp/right_hand_conducting_scores.md
tools/run_right_conducting_goal.py
tests/test_goal_command_cli.py
```

## Score Doc Refresh

The latest TCN supplied-set rerun block now points at Report 117 artifacts:

```text
outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.json
outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.md
outputs/right_conducting/tcn_alltest_latest/stream_set_gate_fulltest_latest.json
outputs/right_conducting/tcn_alltest_latest/stream_set_gate_fulltest_latest.md
outputs/right_conducting/tcn_alltest_latest/tcn_goal_status_fulltest_latest.json
outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.json
```

It also distinguishes:

```text
csv_count: 15 discovered raw CSV files
scoreable processed sessions: 11
```

## Runner Order Refresh

The goal runner help surface now lists the strict chain in the same order used by the strict post-arrival wrapper:

```text
strict-heldout-scope
strict-heldout-missing-checklist
strict-heldout-data-contract
strict-heldout-preflight
```

## Verification

Focused goal runner tests:

```text
PYTHONPATH=. python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
Ran 44 tests in 2.846s
OK
```

Score doc assertion:

```text
scores_latest_report117_assertions_ok
```

Strict wrapper order assertion:

```text
strict_post_arrival_order_assertions_ok
```

Whitespace check:

```text
git diff --check
OK
```

## Current Status

This is a docs/runner-surface cleanup. It does not change model weights or score values. The selected TCN live path remains `GO` on the current supplied-set artifacts, and the overall goal remains `IN_PROGRESS` until strict heldout roots are supplied and pass the strict data contract/preflight/stream gates.
