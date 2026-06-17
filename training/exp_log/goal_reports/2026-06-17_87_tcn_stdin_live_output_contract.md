# 2026-06-17 Report 87 - TCN Stdin Live Output Contract

## Scope

Verify the final live-facing TCN path as a real pipe-style stream:

```text
handmark CSV/stdin
-> right-arm H36M17 masked online frame buffer
-> selected TCN manifest
-> right_conducting_live_output_v1 JSONL
-> MIDI tempo / velocity / CC11 fields
```

This is the runtime integration edge needed for a handmark producer process to feed the classifier continuously.

## Code Guard

Added a subprocess test that creates a temporary TCN bundle, pipes handmark CSV rows through stdin, writes live JSONL to stdout, and verifies:

```text
schema_version: right_conducting_live_output_v1
source_id: stdin_tcn_handmark_csv...
tempo.class_index present
gain.class_index present
midi.tempo_bpm present
summary schema: right_conducting_handmark_csv_stream_v1
```

Changed file:

```text
tests/test_tcn_live.py
```

## Selected Manifest Stdin Smoke

Command:

```bash
python tools/run_tcn_handmark_csv_stream.py \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --handmark-csv - \
  --output-jsonl outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_outputs.jsonl \
  --output-summary-json outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_summary.json \
  --device cuda:0 \
  --flush-each-output \
  --max-updates 3 \
  < dataset/transitions/session_20260617_022415_bpm120to120_beat2_small.csv
```

Result:

| metric | value |
|---|---:|
| row_count | 3 |
| invalid_count | 0 |
| held_invalid_count | 0 |
| frame_count | 51 |
| valid_right_arm_frame_count | 51 |
| valid_right_arm_frame_ratio | 1.0000 |
| tempo_classes_present | `[3]` |
| gain_classes_present | `[0]` |
| first_midi.tempo_bpm | 120.0000 |
| last_midi.tempo_bpm | 120.0000 |

Artifacts:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_outputs.jsonl
outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_summary.json
```

## Runtime Command

For an actual handmark producer process:

```bash
python your_handmark_producer.py | python tools/run_tcn_handmark_csv_stream.py \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --handmark-csv - \
  --output-jsonl - \
  --output-summary-json outputs/right_conducting/selected_tcn_handmark_live45f/live_stdin_summary.json \
  --device cuda:0 \
  --flush-each-output
```

The stream expects a CSV header containing at least:

```text
right_shoulder_x,right_shoulder_y,right_shoulder_conf,
right_elbow_x,right_elbow_y,right_elbow_conf,
right_wrist_x,right_wrist_y,right_wrist_conf
```

Optional reference columns are accepted when present:

```text
shoulder_center_x/y/conf
neck_x/y/conf
left_shoulder_x/y/conf
```

## Verification

```text
PYTHONPATH=. python -m unittest discover -s tests -p 'test_tcn_live.py' -v
PYTHONPATH=. python -m unittest discover tests -v
```

Result:

```text
test_tcn_live.py: 9 OK
full unittest suite: 249 OK in 57.979s
```

## Decision

The selected TCN path now has a tested pipe-style live contract. This strengthens the stream/runtime side of the goal, but it does not change the strict heldout status:

```text
fixed-camera live runtime: GO
stdin live contract: GO
strict independent heldout: NO_GO until new heldout roots are recorded
```
