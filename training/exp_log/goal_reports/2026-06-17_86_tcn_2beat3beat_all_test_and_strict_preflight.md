# 2026-06-17 Report 86 - TCN 2/3-Beat All Test And Strict Preflight

## Scope

Run the selected TCN manifest through the full live-facing test chain while explicitly excluding the leftover 4-beat CSV files under `dataset/transitions`.

This report separates two claims:

```text
fixed-camera supplied 2/3-beat deployment set: GO
strict independent heldout: NO_GO, missing heldout roots and P0 coverage
```

## Inputs

Selected runtime manifest:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
```

Scored CSV set:

```text
dataset/static_variants_80/**/*.csv
dataset/transitions/**/*.csv
excluding any CSV whose filename contains beat4
```

Resolved count:

```text
csv_count: 11
eval_session_count: 11
```

The four root-level 4-beat CSV files in `dataset/transitions` are intentionally excluded from this all-test run.

## Command

```bash
CSV_LIST=$(python - <<'PY'
from pathlib import Path
paths = []
for root in [Path("dataset/static_variants_80"), Path("dataset/transitions")]:
    for p in sorted(root.rglob("*.csv")):
        if "beat4" in p.name:
            continue
        paths.append(str(p))
print(",".join(paths))
PY
)

python tools/run_right_conducting_goal.py \
  --steps tcn-handmark-csv-stream,tcn-handmark-csv-set-score,tcn-handmark-csv-set-gate,tcn-handmark-csv-benchmark,tcn-handmark-stream-readiness \
  --tcn-manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --handmark-csv-stream-csv dataset/transitions/session_20260617_022415_bpm120to120_beat2_small.csv \
  --handmark-csv-set-root "$CSV_LIST" \
  --handmark-csv-set-stable-only \
  --device cuda:0
```

## Fixed-Camera 2/3-Beat Result

Margin 3.0s, stable-only:

| metric | value |
|---|---:|
| csv_count | 11 |
| eval_session_count | 11 |
| sample_count | 1824 |
| mixed_bpm_excluded_count | 204 |
| transition_margin_excluded_count | 423 |
| smoothed tempo_acc | 1.0000 |
| smoothed gain_acc | 1.0000 |
| 80 BPM recall | 1.0000 |
| 100 BPM recall | 1.0000 |
| 120 BPM recall | 1.0000 |
| bpm_mae_window | 0.0000 |
| false_switches_per_min | 0.0000 |
| missed_switch_count | 0.0000 |
| gate_status | GO |
| readiness_status | GO |

Latency:

| metric | value |
|---|---:|
| stream rows | 216 |
| invalid outputs | 0 |
| benchmark p90 ms | 1.6854 |
| benchmark headroom ratio | 118.6673 |

Artifacts:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_summary.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_set_score.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_set_score.md
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_set_gate.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_set_gate.md
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_benchmark.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_benchmark.md
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness.md
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_goal_runner_chain.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_goal_runner_chain.md
```

## Strict Heldout Preflight

Strict heldout command was also run against the planned heldout roots:

```text
dataset/strict_heldout_static_v1
dataset/strict_heldout_transitions_v1
```

Result:

| check | value |
|---|---|
| strict preflight status | NO_GO |
| independence status | NO_GO |
| scope status | NO_GO |
| P0 required | 8 |
| P0 present | 0 |
| P0 missing | 8 |
| missing heldout roots | dataset/strict_heldout_static_v1, dataset/strict_heldout_transitions_v1 |

Artifacts:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_strict_heldout_independence_preflight.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_strict_heldout_scope_preflight.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_strict_heldout_missing_checklist_preflight.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_strict_heldout_preflight.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_strict_heldout_goal_preflight_chain.json
```

## Verification

```text
PYTHONPATH=. python -m unittest discover tests -v
```

Result:

```text
full unittest suite: 248 OK in 53.643s
```

## Decision

Use the selected TCN manifest as the current live-facing fixed-camera runtime:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
```

Do not present the score as strict generalization. The next strict claim requires new independent fixed-camera heldout data under the planned strict heldout roots, then the same manifest-based score/gate/benchmark/readiness chain.
