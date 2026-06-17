# Report 81 - TCN Handmark Stream Readiness Gate

## Purpose

Report 80 proved that TCN can run from raw handmark CSV/stdin and produce `right_conducting_live_output_v1`.

Report 81 adds a readiness gate:

```text
handmark stream score gate
+ raw CSV stream latency benchmark
+ single stream smoke summary
-> TCN handmark stream readiness GO/NO_GO
```

## Artifacts

```text
score: outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_score.json
gate: outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_gate.json
benchmark: outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_benchmark.json
stream_summary: outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_summary.json
readiness: outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_handmark_stream_readiness.json
```

## Score Gate

Command:

```bash
python tools/check_motionbert_handmark_csv_stream_set_gate.py \
  --score-json outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_score.json \
  --margin-seconds 3 \
  --output-json outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_gate.json \
  --output-md outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_gate.md
```

Result:

```text
status: GO
margin: 3s
sample_count: 1824
smoothed tempo_acc: 1.0000
smoothed gain_acc: 1.0000
tempo_80/100/120 recall: 1.0000 / 1.0000 / 1.0000
false_switches_per_min: 0.0000
missed_switch_count: 0
```

## Latency Benchmark

Command:

```bash
python tools/benchmark_tcn_handmark_csv_stream.py \
  --checkpoint outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_conducting_head.pt \
  --handmark-csv dataset/transitions/session_20260617_022415_bpm120to120_beat2_small.csv \
  --device cuda:0 \
  --warmup-updates 10 \
  --output-json outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_benchmark.json \
  --output-md outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_benchmark.md
```

Result:

| update budget ms | output count | p90 ms | p95 ms | max ms | headroom | status |
|---:|---:|---:|---:|---:|---:|---|
| 200.0000 | 216 | 1.6180 | 1.6634 | 4.0563 | 123.6107 | PASS |

## Readiness Gate

Command:

```bash
python tools/check_tcn_handmark_stream_readiness.py \
  --gate-json outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_gate.json \
  --benchmark-json outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_benchmark.json \
  --stream-summary-json outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_summary.json \
  --output-json outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_handmark_stream_readiness.json \
  --output-md outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_handmark_stream_readiness.md
```

Result:

```text
status: GO
score_gate_go: true
benchmark_realtime_pass: true
benchmark_output_count: 216
stream_summary_rows: 216
stream_summary_invalid_count: 0
```

Selected metrics:

```json
{
  "gate_status": "GO",
  "benchmark_p90_ms": 1.617982517927885,
  "benchmark_headroom_ratio": 123.61072989597912,
  "stream_rows": 216,
  "stream_invalid_count": 0,
  "tempo_classes_present": [1, 3]
}
```

## Implementation Added

```text
tools/benchmark_tcn_handmark_csv_stream.py
tools/check_tcn_handmark_stream_readiness.py
tests/test_tcn_live.py
```

## Verification

```text
python -m py_compile \
  tools/check_tcn_handmark_stream_readiness.py \
  tools/benchmark_tcn_handmark_csv_stream.py
PASS

PYTHONPATH=. python tests/test_tcn_live.py -v
Ran 5 tests
OK

PYTHONPATH=. python -m unittest discover tests -v
Ran 238 tests in 52.524s
OK

JSON artifact parse:
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_gate.json -> GO
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_benchmark.json -> realtime PASS
outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_handmark_stream_readiness.json -> GO
PASS
```

## Interpretation

TCN 45f is now a practical fixed-camera handmark stream fallback candidate:

```text
raw handmark stream: GO
tempo/gain score gate: GO
latency budget: GO
readiness gate: GO
```

This is still deployment-fit, not strict heldout generalization. The final strict claim still requires an independent fixed-camera heldout root that is not used in TCN or MotionBERT training.
