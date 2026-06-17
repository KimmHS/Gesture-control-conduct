# Handmark CSV Stream Set Gate

## Purpose

Report 75 produced a raw handmark CSV aggregate stream score. This report adds a machine-readable GO/NO_GO gate so the handmark-only live probe has a reproducible pass line.

The gate is for fixed-camera deployment-fit only. It does not convert the result into strict heldout generalization.

## New Tool

```text
tools/check_motionbert_handmark_csv_stream_set_gate.py
lib/right_conducting/handmark_csv_stream_gate.py
tests/test_handmark_csv_stream_gate.py
```

## Command

```bash
python tools/check_motionbert_handmark_csv_stream_set_gate.py \
  --score-json outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.json \
  --margin-seconds 3 \
  --min-sample-count 1000 \
  --min-eval-session-count 10 \
  --min-tempo-acc 0.98 \
  --min-gain-acc 0.95 \
  --min-recall-80 0.90 \
  --min-recall-100 0.90 \
  --min-recall-120 0.90 \
  --max-false-switches-per-min 0.5 \
  --max-missed-switch-count 0 \
  --output-json outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.json \
  --output-md outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.md
```

## Result

```text
status: GO
selected_margin_seconds: 3.0
input_mask_mode: right_arm_only
csv_count: 15
eval_session_count: 11
sample_count: 1824
```

| check | value | threshold | status |
|---|---:|---:|---|
| tempo_acc | 0.9989 | >= 0.9800 | PASS |
| gain_acc | 1.0000 | >= 0.9500 | PASS |
| tempo_80_recall | 0.9983 | >= 0.9000 | PASS |
| tempo_100_recall | 1.0000 | >= 0.9000 | PASS |
| tempo_120_recall | 1.0000 | >= 0.9000 | PASS |
| false_switches_per_min | 0.1230 | <= 0.5000 | PASS |
| missed_switch_count | 0 | <= 0 | PASS |

## Artifacts

```text
gate_json: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.json
gate_md: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.md
score_json: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.json
```

## Verification

```bash
python -m py_compile lib/right_conducting/handmark_csv_stream_gate.py tools/check_motionbert_handmark_csv_stream_set_gate.py
PYTHONPATH=. python tests/test_handmark_csv_stream_gate.py
python -m json.tool outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.json
```

All checks passed.

## Interpretation

For the current fixed-camera 2/3-beat handmark-only deployment-fit scope, the right-arm-only probe now has:

```text
raw CSV stream score: GO
raw CSV stream gate: GO
runtime benchmark: GO
old independent 222455 stress: NO_GO
strict heldout scope: NO_GO
```

So it is a practical handmark-only live probe, but the final report must still say that strict heldout generalization is pending.
