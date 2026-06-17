# Report 103 - Strict Script CSV Autodiscovery

## Purpose

Reduce the chance of a post-arrival execution mistake when strict transition CSV filenames differ from the placeholder path. The strict post-arrival script now auto-discovers a representative transition CSV from the strict transition root if `STRICT_STREAM_CSV` is not explicitly set.

## Code Change

Updated:

```text
scripts/run_tcn_strict_post_arrival_goal.sh
tests/test_goal_command_cli.py
```

CSV selection order:

```text
1. Use STRICT_STREAM_CSV if the environment variable is set.
2. Else use dataset/strict_heldout_transitions_v1/P0_transition_120_to_80_to_120_beat2_small.csv if it exists.
3. Else use the first sorted *.csv directly under STRICT_TRANSITION_ROOT.
4. Else keep the placeholder path for dry-run visibility.
```

## Test Guard

Added:

```text
test_tcn_strict_post_arrival_script_auto_discovers_transition_csv
```

The test creates a temporary strict transition root with two CSV files, leaves `STRICT_STREAM_CSV` unset, runs:

```bash
bash scripts/run_tcn_strict_post_arrival_goal.sh --dry-run
```

and verifies that the generated dry-run command uses the first sorted CSV.

## Verification

Focused verification:

```bash
python -m py_compile tests/test_goal_command_cli.py tools/run_right_conducting_goal.py
bash -n scripts/run_tcn_strict_post_arrival_goal.sh
PYTHONPATH=. python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
```

Result:

```text
test_goal_command_cli.py: 42 OK
```

Full verification:

```bash
PYTHONPATH=. python -m unittest discover tests -v
```

Result:

```text
Ran 263 tests in 58.555s
OK
```

## Decision

The strict post-arrival script is more robust for the likely real data layout where CSV filenames are session-style names. Manual override remains available through `STRICT_STREAM_CSV`. The active goal is still not complete until strict heldout roots exist and the strict chain passes.
