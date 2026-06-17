# Report 45 - Missing Devset Checklist

## Scope

The audit now knows which required cases are missing, but the raw audit table is not the most convenient recording checklist. This report adds a renderer that converts the current devset audit into a compact recording checklist.

## Added Files

```text
lib/right_conducting/devset_missing_checklist.py
tools/render_right_conducting_missing_devset_checklist.py
tests/test_devset_missing_checklist.py
```

Updated:

```text
tools/run_right_conducting_goal.py
tests/test_goal_command_cli.py
```

New goal step:

```text
devset-missing-checklist
```

## Current Output

Generated artifacts:

```text
outputs/right_conducting/devset_missing_checklist.json
outputs/right_conducting/devset_missing_checklist.md
```

Current summary:

```text
missing_count: 8
missing_by_priority: P0=6, P2=2
next_action: collect P0 missing cases under dataset/static_variants_80
```

P0 checklist:

```text
80 BPM / 2 beat / large / fixed camera high arm
80 BPM / 2 beat / small / fixed camera high arm
80 BPM / 3 beat / large / fixed camera low arm
80 BPM / 3 beat / small / fixed camera low arm
80 BPM / 4 beat / large / fixed camera neutral arm
80 BPM / 4 beat / small / fixed camera neutral arm
```

Lower-priority missing cases:

```text
80 -> 120 -> 80 BPM / 4 beat / large
80 -> 120 -> 80 BPM / 4 beat / small
```

## Commands

Standalone:

```bash
python tools/render_right_conducting_missing_devset_checklist.py \
  --audit-json outputs/right_conducting/devset_edge_case_audit.json \
  --output-json outputs/right_conducting/devset_missing_checklist.json \
  --output-md outputs/right_conducting/devset_missing_checklist.md
```

Goal runner:

```bash
python tools/run_right_conducting_goal.py \
  --steps devset-audit,devset-missing-checklist,experiment-readiness \
  --devset-static-root dataset/static_variants_80 \
  --devset-transition-root dataset/transitions \
  --devset-requirements docs/exp/right_conducting_required_data_manifest.json \
  --devset-output-json outputs/right_conducting/devset_edge_case_audit.json \
  --devset-output-md outputs/right_conducting/devset_edge_case_audit.md \
  --devset-missing-output-json outputs/right_conducting/devset_missing_checklist.json \
  --devset-missing-output-md outputs/right_conducting/devset_missing_checklist.md \
  --readiness-output-json outputs/right_conducting/experiment_readiness.json \
  --readiness-output-md outputs/right_conducting/experiment_readiness.md \
  --window-frames 60
```

## Verification

Focused checks:

```bash
python -m compileall -q lib/right_conducting/devset_missing_checklist.py tools/render_right_conducting_missing_devset_checklist.py tools/run_right_conducting_goal.py tests/test_devset_missing_checklist.py tests/test_goal_command_cli.py

python -m unittest discover -s tests -p 'test_devset_missing_checklist.py' -v

python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
```

Focused result:

```text
test_devset_missing_checklist.py: 3 OK
test_goal_command_cli.py: 19 OK
```

Full regression:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Full result:

```text
Ran 141 tests in 24.992s
OK
```
