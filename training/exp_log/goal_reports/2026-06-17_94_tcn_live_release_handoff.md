# Report 94 - TCN Live Release Handoff

## Purpose

Collect the selected TCN model, live stream command, score evidence, output contract, and strict blocker into one handoff package.

## Added Artifacts

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json
docs/exp/tcn_live_handoff_runbook.md
```

## Release Status

```text
release_name: selected_tcn_handmark_live45f
status: LIVE_READY_STRICT_HELDOUT_PENDING
live_status: GO
strict_heldout_status: NO_GO
```

## Model Files

| artifact | path |
|---|---|
| live manifest | `outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json` |
| checkpoint | `outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_head.pt` |
| structure | `outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_structure.md` |
| release manifest | `outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json` |

Checkpoint SHA256:

```text
69f1918be6ac88da6d732748087bc2b1e66e56ee153ee384f3872c7a4eadaf98
```

## Live Command

```bash
python your_handmark_producer.py | python tools/run_tcn_handmark_csv_stream.py \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --handmark-csv - \
  --output-jsonl - \
  --output-summary-json outputs/right_conducting/selected_tcn_handmark_live45f/live_stdin_summary.json \
  --device cuda:0 \
  --flush-each-output
```

## Current Evidence

| check | value |
|---|---:|
| fixed-camera supplied-set score gate | GO |
| goal status | IN_PROGRESS |
| live_status | GO |
| strict_heldout_status | NO_GO |
| tempo_acc / gain_acc | 1.0000 / 1.0000 |
| benchmark p90 ms | 1.6854 |
| stream output contract errors | 0 |
| stdin output contract errors | 0 |

## Verification

```text
python -m json.tool outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json
```

## Decision

Use this bundle for the current fixed-camera live demo/runtime. Do not claim strict heldout completion until `dataset/strict_heldout_static_v1` and `dataset/strict_heldout_transitions_v1` are recorded and the Report 93 final chain passes.

