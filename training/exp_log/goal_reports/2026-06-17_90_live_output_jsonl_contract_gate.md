# 2026-06-17 Report 90 - Live Output JSONL Contract Gate

## Scope

Add a concrete validator for the final runtime output rows.

The stream path now verifies not only summary counts, but each `right_conducting_live_output_v1` JSONL row used by downstream MIDI control.

## Code Changes

```text
lib/right_conducting/live_output_validation.py
tools/check_right_conducting_live_output_jsonl.py
tools/check_tcn_handmark_stream_readiness.py
tools/run_right_conducting_goal.py
tests/test_live_output_contract.py
tests/test_tcn_live.py
tests/test_goal_command_cli.py
```

The validator checks:

```text
schema_version
required top-level fields: source/time/tempo/gain/midi/state
tempo class range against bpm_bins
gain class range
midi tempo matches smoothed tempo
velocity scale / CC11 bounds
bpm_distribution shape and sum
source window/stride/fps consistency with manifest
state.valid type
```

## Selected Artifacts Validated

File stream output:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_outputs.jsonl
```

Stdin smoke output:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_outputs.jsonl
```

Validation artifacts:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_outputs_contract.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_outputs_contract.md
outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_outputs_contract.json
outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_outputs_contract.md
```

Results:

| output | rows | tempo classes | gain classes | errors | status |
|---|---:|---|---|---:|---|
| alltest stream | 216 | `[1, 3]` | `[0]` | 0 | GO |
| stdin smoke | 3 | `[3]` | `[0]` | 0 | GO |

## Readiness Gate V3

The TCN readiness gate now accepts:

```text
--stream-output-jsonl
--stdin-output-jsonl
--manifest
```

Selected readiness artifact:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness_with_output_contract.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness_with_output_contract.md
```

Result:

| metric | value |
|---|---:|
| readiness status | GO |
| schema_version | `right_conducting_tcn_handmark_stream_readiness_v3` |
| stream rows | 216 |
| stream invalid | 0 |
| stdin rows | 3 |
| stdin invalid | 0 |
| stream output contract errors | 0 |
| stdin output contract errors | 0 |
| benchmark p90 ms | 1.6854 |

## Commands

```bash
python tools/check_right_conducting_live_output_jsonl.py \
  --jsonl outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_outputs.jsonl \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --min-rows 100 \
  --fail-on-no-go

python tools/check_right_conducting_live_output_jsonl.py \
  --jsonl outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_outputs.jsonl \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --min-rows 1 \
  --fail-on-no-go
```

## Verification

```text
python -m py_compile lib/right_conducting/live_output_validation.py tools/check_right_conducting_live_output_jsonl.py tools/check_tcn_handmark_stream_readiness.py tools/run_right_conducting_goal.py tests/test_live_output_contract.py tests/test_tcn_live.py tests/test_goal_command_cli.py
PYTHONPATH=. python -m unittest discover -s tests -p 'test_live_output_contract.py' -v
PYTHONPATH=. python -m unittest discover -s tests -p 'test_tcn_live.py' -v
PYTHONPATH=. python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
PYTHONPATH=. python -m unittest discover tests -v
```

Result:

```text
test_live_output_contract.py: 8 OK
test_tcn_live.py: 10 OK
test_goal_command_cli.py: 38 OK
full unittest suite: 252 OK, 56.417s
```

## Decision

The selected TCN path now has an output contract gate for actual JSONL rows. The live-facing fixed-camera runtime is stronger:

```text
score gate: GO
benchmark: GO
CSV stream smoke: GO
stdin smoke: GO
JSONL output contract: GO
combined readiness v3: GO
strict independent heldout: still NO_GO
```
