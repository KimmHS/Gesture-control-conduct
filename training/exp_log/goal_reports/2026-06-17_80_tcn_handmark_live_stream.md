# Report 80 - TCN Handmark Live Stream

## Request

Continue toward the final stream goal by making the TCN probe usable on raw handmark CSV / stdin input, not only offline pose-window scoring.

## Decision

TCN now has a live handmark stream path.

This still does not replace the selected MotionBERT bundle as strict final evidence, because the score is deployment-fit. It does close the practical gap that TCN could only be scored offline before Report 80.

Practical TCN fallback:

```text
outputs/right_conducting/tcn_quick_probe_20260617/45f
```

## Implementation

New library:

```text
lib/right_conducting/tcn_live.py
```

New CLIs:

```text
tools/run_tcn_handmark_csv_stream.py
tools/evaluate_tcn_handmark_csv_stream_set.py
```

Runtime interface:

```text
predict_window(pose_window)
update(raw_prediction)
reset_smoother()
```

The TCN predictor uses the same online buffer and live output contract as the MotionBERT stream path:

```text
handmark CSV/stdin
-> H36M17 right-arm frame
-> OnlinePoseFrameStreamer
-> TCNLivePredictor
-> LiveSmoother
-> right_conducting_live_output_v1
```

Checkpoint loading explicitly uses `torch.load(..., weights_only=False)` because the TCN checkpoint stores numpy mean/std arrays.

## Handmark Stream Set Score

Command:

```bash
python tools/evaluate_tcn_handmark_csv_stream_set.py \
  --checkpoint outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_conducting_head.pt \
  --csv-root dataset/static_variants_80,dataset/transitions \
  --stable-only \
  --margins 0,0.5,1,2,3 \
  --device cuda:0 \
  --output-json outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_score.json \
  --output-md outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_score.md \
  --output-rows outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_rows.jsonl
```

| margin | samples | mixed | margin_excl | raw tempo | smooth tempo | smooth gain | false/min | p90 | r80 | r100 | r120 | bpm mae |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 2241 | 204 | 6 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 0.5 | 2172 | 204 | 75 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 1.0 | 2103 | 204 | 144 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 2.0 | 1964 | 204 | 283 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 3.0 | 1824 | 204 | 423 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

Artifacts:

```text
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_score.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_score.md
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_rows.jsonl
```

## Single Stream Smoke

Command:

```bash
python tools/run_tcn_handmark_csv_stream.py \
  --checkpoint outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_conducting_head.pt \
  --handmark-csv dataset/transitions/session_20260617_022415_bpm120to120_beat2_small.csv \
  --device cuda:0 \
  --output-jsonl outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_outputs.jsonl \
  --output-summary-json outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_summary.json \
  --manifest-output-json outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_live_manifest.json
```

Summary:

```text
schema: right_conducting_handmark_csv_stream_v1
output_schema: right_conducting_live_output_v1
row_count: 216
invalid_count: 0
held_invalid_count: 0
tempo_classes_present: [1, 3]
gain_classes_present: [0]
valid_right_arm_frame_ratio: 1.0000
```

Artifacts:

```text
outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_live_manifest.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_outputs.jsonl
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_summary.json
```

## Interpretation

TCN is now a practical live fallback candidate for fixed-camera handmark input.

Compared with the MotionBERT right-arm-only handmark probe, this TCN 45f checkpoint gives cleaner deployment-fit handmark set metrics on the current data:

```text
TCN 45f margin3 smooth tempo_acc: 1.0000
MotionBERT right-arm-only margin3 smooth tempo_acc: 0.9989
TCN 45f margin3 false/min: 0.0000
MotionBERT right-arm-only margin3 false/min: 0.1230
```

Do not claim strict generalization from this score. The same static80/transitions sessions were used to train this TCN checkpoint.

## Verification

```text
python -m py_compile \
  lib/right_conducting/tcn_live.py \
  tools/run_tcn_handmark_csv_stream.py \
  tools/evaluate_tcn_handmark_csv_stream_set.py \
  tools/run_tcn_right_conducting_quick_probe.py
PASS

PYTHONPATH=. python tests/test_tcn_live.py -v
Ran 3 tests
OK

PYTHONPATH=. python tests/test_handmark_csv_stream.py -v
Ran 7 tests
OK

PYTHONPATH=. python -m unittest discover tests -v
Ran 236 tests in 51.170s
OK

JSON artifact parse:
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_score.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_summary.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_live_manifest.json
PASS
```

## Next Gate

To promote TCN from fallback/probe to final selected model, run the same handmark stream set score on an independent fixed-camera heldout root that is not in the TCN training roots.
