# Report 77 - Goal Runner Handmark CSV Set Gate

## Purpose

Raw handmark CSV stream-set scoring and gate evaluation were implemented in Reports 75 and 76, but the reproducible goal runner only exposed single-session CSV streaming. This report adds the aggregate CSV stream-set score/gate path to `tools/run_right_conducting_goal.py`.

This keeps the final live-input check executable from one goal command:

```text
raw handmark CSV roots
-> exported MotionBERT live manifest
-> frame-by-frame stream replay
-> margin sweep score
-> margin-3 gate
```

## Added Goal Steps

```text
handmark-csv-stream-set-score
handmark-csv-stream-set-gate
```

New CLI arguments:

```text
--handmark-csv-set-root
--handmark-csv-set-stable-only
--handmark-csv-set-margins
--handmark-csv-set-score-json
--handmark-csv-set-score-md
--handmark-csv-set-rows-jsonl
--handmark-csv-set-gate-json
--handmark-csv-set-gate-md
--handmark-csv-set-gate-margin-seconds
--handmark-csv-set-gate-min-sample-count
--handmark-csv-set-gate-min-eval-session-count
--handmark-csv-set-gate-min-tempo-acc
--handmark-csv-set-gate-min-gain-acc
--handmark-csv-set-gate-min-recall-80
--handmark-csv-set-gate-min-recall-100
--handmark-csv-set-gate-min-recall-120
--handmark-csv-set-gate-max-false-switches-per-min
--handmark-csv-set-gate-max-missed-switch-count
```

## Reproducible Command

Dry-run artifact:

```text
outputs/right_conducting/right_conducting_goal_handmark_csv_set_gate_dryrun.json
outputs/right_conducting/right_conducting_goal_handmark_csv_set_gate_dryrun.md
```

Command:

```bash
python tools/run_right_conducting_goal.py \
  --dry-run \
  --steps handmark-csv-stream-set-score,handmark-csv-stream-set-gate \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe \
  --handmark-csv-set-root dataset/static_variants_80,dataset/transitions \
  --handmark-csv-set-stable-only \
  --handmark-csv-set-score-json outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.json \
  --handmark-csv-set-score-md outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.md \
  --handmark-csv-set-rows-jsonl outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_rows.jsonl \
  --handmark-csv-set-gate-json outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.json \
  --handmark-csv-set-gate-md outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.md \
  --output-json outputs/right_conducting/right_conducting_goal_handmark_csv_set_gate_dryrun.json \
  --output-md outputs/right_conducting/right_conducting_goal_handmark_csv_set_gate_dryrun.md
```

To execute instead of dry-run, remove `--dry-run`.

## Gate Criteria

Default gate target:

```text
transition margin: 3s
sample_count >= 1000
eval_session_count >= 10
smoothed tempo_acc >= 0.98
smoothed gain_acc >= 0.95
per-class recall 80/100/120 >= 0.90
false_switches_per_min <= 0.50
missed_switch_count == 0
```

Current Report 76 result:

```text
status: GO
sample_count: 1824
smoothed tempo_acc: 0.9989
smoothed gain_acc: 1.0000
r80/r100/r120: 0.9983 / 1.0000 / 1.0000
false_switches_per_min: 0.1230
missed_switch_count: 0
```

## 5-GPU Hparam Context

The broad GPU sweep has already been executed and documented:

```text
Report 47: static80 + transition 5-GPU sweep
Report 59: extended 5-GPU sweep, 34 additional candidates, 54 total candidates
```

Current selected deployment-fit bundle remains:

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext
```

Right-arm-only handmark probe bundle:

```text
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe
```

Current GPU availability check:

```text
cuda:0..4 are visible RTX 3090 GPUs and were idle during this report.
```

## Verification

Commands:

```bash
python -m py_compile tools/run_right_conducting_goal.py
PYTHONPATH=. python tests/test_goal_command_cli.py
python -m json.tool outputs/right_conducting/right_conducting_goal_handmark_csv_set_gate_dryrun.json
```

Result:

```text
tests/test_goal_command_cli.py: 37 tests OK
dry-run JSON: valid
```

## Caveat

This gate is still deployment-fit for the fixed-camera handmark stream set. It does not replace strict heldout evaluation. Strict generalization remains `NO_GO` until new in-scope heldout sessions are recorded outside the staged training manifest and pass independence, scope, replay, and live gates.
