# Report 43 - Experiment Readiness Gate

## Scope

Report 42 listed the planned experiments. This report adds a small readiness gate that reads the current coverage/devset gate artifacts and answers:

```text
What can be run now?
What is blocked?
What is the next action?
```

## Added Files

```text
lib/right_conducting/experiment_readiness.py
tools/check_right_conducting_experiment_readiness.py
tests/test_experiment_readiness.py
```

Updated:

```text
tools/run_right_conducting_goal.py
tests/test_goal_command_cli.py
```

New goal step:

```text
experiment-readiness
```

## Current Readiness Result

Command:

```bash
python tools/check_right_conducting_experiment_readiness.py \
  --coverage-json outputs/right_conducting/devset_edge_case_audit.json \
  --devset-gate-json outputs/right_conducting/motionbert_devset_gate_60f.json \
  --output-json outputs/right_conducting/experiment_readiness.json \
  --output-md outputs/right_conducting/experiment_readiness.md
```

Current output:

```text
status: WAIT_FOR_STATIC_80_DATA
p0_complete: false
devset_gate_present: false
next_action: collect fixed-camera 80 BPM static variants under dataset/static_variants_80
```

Experiment queue:

| experiment | state |
|---|---|
| devset-audit | READY |
| fixed-camera-80-static-capture | NEEDED |
| motionbert-devset-score | BLOCKED |
| devset-gate | BLOCKED |
| 5gpu-motionbert-sweep | BLOCKED |
| selected-motionbert-export | BLOCKED |

## Goal Runner Usage

Standalone readiness:

```bash
python tools/run_right_conducting_goal.py \
  --steps experiment-readiness \
  --devset-output-json outputs/right_conducting/devset_edge_case_audit.json \
  --devset-gate-output-prefix outputs/right_conducting/motionbert_devset_gate \
  --readiness-output-json outputs/right_conducting/experiment_readiness.json \
  --readiness-output-md outputs/right_conducting/experiment_readiness.md \
  --window-frames 60
```

After new fixed-camera static data is copied in:

```bash
python tools/run_right_conducting_goal.py \
  --steps devset-audit,experiment-readiness \
  --devset-static-root dataset/static_variants_80 \
  --devset-transition-root dataset/transitions \
  --devset-requirements docs/exp/right_conducting_required_data_manifest.json \
  --devset-output-json outputs/right_conducting/devset_edge_case_audit.json \
  --devset-output-md outputs/right_conducting/devset_edge_case_audit.md \
  --readiness-output-json outputs/right_conducting/experiment_readiness.json \
  --readiness-output-md outputs/right_conducting/experiment_readiness.md \
  --window-frames 60
```

## Policy

```text
Do not run another broad 5-GPU MotionBERT sweep while readiness status is WAIT_FOR_STATIC_80_DATA.
```

The immediate next step is still data capture, not model tuning.

## Verification

Focused checks:

```bash
python -m compileall -q lib/right_conducting/experiment_readiness.py tools/check_right_conducting_experiment_readiness.py tools/run_right_conducting_goal.py tests/test_experiment_readiness.py tests/test_goal_command_cli.py

python -m unittest discover -s tests -p 'test_experiment_readiness.py' -v

python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
```

Focused result:

```text
test_experiment_readiness.py: 4 OK
test_goal_command_cli.py: 18 OK
```

Full regression:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Full result:

```text
Ran 136 tests in 24.621s
OK
```
