# 2026-06-17 Report 82 - TCN Goal Runner Full Test

## Scope

Add the TCN handmark stream path to the reproducible goal runner and execute the full TCN stream test chain.

This is a fixed-camera deployment-fit check on the supplied `dataset/static_variants_80,dataset/transitions` data. It is not a strict independent heldout generalization claim.

## Code Changes

```text
tools/run_right_conducting_goal.py
tests/test_goal_command_cli.py
```

New goal runner steps:

```text
tcn-handmark-csv-stream
tcn-handmark-csv-set-score
tcn-handmark-csv-set-gate
tcn-handmark-csv-benchmark
tcn-handmark-stream-readiness
```

## Repro Command

```bash
python tools/run_right_conducting_goal.py \
  --steps tcn-handmark-csv-stream,tcn-handmark-csv-set-score,tcn-handmark-csv-set-gate,tcn-handmark-csv-benchmark,tcn-handmark-stream-readiness \
  --tcn-checkpoint outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_conducting_head.pt \
  --handmark-csv-stream-csv dataset/transitions/session_20260617_022415_bpm120to120_beat2_small.csv \
  --handmark-csv-set-root dataset/static_variants_80,dataset/transitions \
  --handmark-csv-set-stable-only \
  --device cuda:0 \
  --output-json outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_goal_runner_chain.json \
  --output-md outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_goal_runner_chain.md
```

## Results

Margin 3.0s score:

| metric | value |
|---|---:|
| csv_count | 15 |
| eval_session_count | 11 |
| sample_count | 1824 |
| mixed_bpm_excluded_count | 204 |
| transition_margin_excluded_count | 423 |
| smoothed tempo_acc | 1.0000 |
| smoothed gain_acc | 1.0000 |
| 80 BPM recall | 1.0000 |
| 100 BPM recall | 1.0000 |
| 120 BPM recall | 1.0000 |
| false_switches_per_min | 0.0000 |
| missed_switch_count | 0.0000 |

Readiness:

| check | value |
|---|---:|
| score gate | GO |
| stream readiness | GO |
| benchmark p90 ms | 1.9988 |
| benchmark headroom ratio | 100.0620 |
| single stream rows | 216 |
| invalid outputs | 0 |

## Artifacts

```text
outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_goal_runner_chain.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_goal_runner_chain.md
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_score.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_gate.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_benchmark.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_handmark_stream_readiness.json
```

## Verification

```text
python -m py_compile tools/run_right_conducting_goal.py tests/test_goal_command_cli.py
PYTHONPATH=. python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
PYTHONPATH=. python -m unittest discover tests -v
```

Result:

```text
test_goal_command_cli.py: 38 OK
full unittest suite: 239 OK
```

## Decision

TCN is now the strongest runnable fixed-camera live candidate. Keep MotionBERT reports as comparison/history, but use the TCN handmark runner chain for the current live-facing test path.

Strict heldout remains incomplete until independent fixed-camera sessions are captured and passed through the same score/gate/benchmark/readiness path.
