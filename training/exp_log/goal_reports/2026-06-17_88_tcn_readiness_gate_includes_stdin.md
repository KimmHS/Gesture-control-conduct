# 2026-06-17 Report 88 - TCN Readiness Gate Includes Stdin

## Scope

Promote the stdin live smoke from a standalone report into the TCN readiness gate.

The final stream target is not just "can score a CSV file"; it needs to accept a live handmark producer stream. Therefore readiness now checks:

```text
score gate
realtime benchmark
file/CSV stream smoke
stdin live JSONL smoke
```

## Code Changes

```text
tools/check_tcn_handmark_stream_readiness.py
tools/run_right_conducting_goal.py
tests/test_tcn_live.py
tests/test_goal_command_cli.py
```

New readiness options:

```text
--stdin-summary-json
--min-stdin-rows
```

New goal runner options:

```text
--tcn-handmark-stream-readiness-stdin-summary-json
--tcn-handmark-stream-readiness-min-stdin-rows
```

## Selected Bundle Gate

Command:

```bash
python tools/run_right_conducting_goal.py \
  --steps tcn-handmark-stream-readiness \
  --tcn-handmark-csv-set-gate-json outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_set_gate.json \
  --tcn-handmark-csv-benchmark-json outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_benchmark.json \
  --tcn-handmark-csv-stream-summary-json outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_summary.json \
  --tcn-handmark-stream-readiness-stdin-summary-json outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_summary.json \
  --tcn-handmark-stream-readiness-json outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness_with_stdin.json \
  --tcn-handmark-stream-readiness-md outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness_with_stdin.md
```

Result:

| metric | value |
|---|---:|
| readiness status | GO |
| schema_version | `right_conducting_tcn_handmark_stream_readiness_v2` |
| benchmark p90 ms | 1.6854 |
| benchmark headroom ratio | 118.6673 |
| stream rows | 216 |
| stream invalid | 0 |
| stdin rows | 3 |
| stdin invalid | 0 |

Additional stdin checks:

| check | result |
|---|---|
| stdin_summary_schema | pass |
| stdin_output_schema | pass |
| stdin_summary_rows | pass |
| stdin_summary_invalid_count | pass |

Artifacts:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness_with_stdin.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness_with_stdin.md
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_readiness_with_stdin_goal_chain.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_readiness_with_stdin_goal_chain.md
```

## Verification

```text
python -m py_compile tools/check_tcn_handmark_stream_readiness.py tools/run_right_conducting_goal.py tests/test_tcn_live.py tests/test_goal_command_cli.py
PYTHONPATH=. python -m unittest discover -s tests -p 'test_tcn_live.py' -v
PYTHONPATH=. python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
PYTHONPATH=. python -m unittest discover tests -v
```

Result:

```text
test_tcn_live.py: 10 OK
test_goal_command_cli.py: 38 OK
full unittest suite: 250 OK in 56.184s
```

## Decision

The selected TCN runtime now has a stronger automatic readiness gate:

```text
fixed-camera score gate: GO
latency benchmark: GO
CSV stream smoke: GO
stdin live contract: GO
combined readiness with stdin: GO
strict independent heldout: still NO_GO
```

Strict heldout remains unchanged because the planned heldout roots are not present.
