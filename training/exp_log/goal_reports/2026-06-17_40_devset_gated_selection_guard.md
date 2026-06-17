# Report 40 — Devset-Gated Selection Guard

## Scope

Report 39 added the fixed-camera devset coverage, MotionBERT devset scoring, and devset gate.

This report adds the final safety rule for selected-model export:

```text
A MotionBERT candidate cannot become SELECTED unless the matching devset gate is GO.
```

This prevents a model from passing the older CV/transition score gate while still failing fixed-camera 80 BPM stability.

## Code Changes

Updated:

```text
lib/right_conducting/model_selection.py
tools/select_right_conducting_model_candidate.py
tools/run_right_conducting_goal.py
```

New selection inputs:

```text
--devset-gate-jsons
--require-devset-gate
```

Goal runner behavior:

```text
If steps include devset-gate,gate,select together,
run_right_conducting_goal.py automatically passes the matching
motionbert_devset_gate_*f.json file into selection and enables --require-devset-gate.
```

## Selection Rule

Before:

```text
score gate GO
-> SELECTED candidate
-> export allowed
```

Now:

```text
score gate GO
AND matching devset gate GO
-> SELECTED candidate
-> export allowed
```

If the score gate is `GO` but the devset gate is `NO_GO`, selection returns:

```text
status: NO_GO
go_candidate_count: 0
failed_devset_checks: recorded per candidate
```

## Dry-Run

Command:

```bash
python tools/run_right_conducting_goal.py \
  --dry-run \
  --steps devset-gate,gate,select \
  --head-output-dir outputs/right_conducting/motionbert_head_after_supply \
  --gate-output-prefix outputs/right_conducting/model_gate_after_supply \
  --devset-static-score-prefix outputs/right_conducting/motionbert_devset_static_score \
  --devset-transition-score-prefix outputs/right_conducting/motionbert_devset_transition_score \
  --devset-gate-output-prefix outputs/right_conducting/motionbert_devset_gate \
  --selection-output-json outputs/right_conducting/model_candidate_selection_after_supply_devset_required.json \
  --selection-output-md outputs/right_conducting/model_candidate_selection_after_supply_devset_required.md \
  --window-frames 60 \
  --output-json outputs/right_conducting/right_conducting_goal_devset_selection_dryrun.json \
  --output-md outputs/right_conducting/right_conducting_goal_devset_selection_dryrun.md
```

Dry-run artifact:

```text
outputs/right_conducting/right_conducting_goal_devset_selection_dryrun.json
outputs/right_conducting/right_conducting_goal_devset_selection_dryrun.md
```

Generated selection command includes:

```text
--devset-gate-jsons outputs/right_conducting/motionbert_devset_gate_60f.json
--require-devset-gate
```

## Export Implication

The existing export command still refuses `NO_GO` selection files. Because selection now requires devset gate `GO`, export is indirectly protected:

```text
devset gate NO_GO
-> selection NO_GO
-> export_motionbert_selected_bundle.py refuses export
```

## Verification

```bash
python -m unittest discover -s tests -p 'test_model_selection.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
python -m unittest discover -s tests -p 'test_*.py' -v
python -m compileall -q \
  lib/right_conducting/model_selection.py \
  tools/select_right_conducting_model_candidate.py \
  tools/run_right_conducting_goal.py \
  tests/test_model_selection.py \
  tests/test_goal_command_cli.py
python -m json.tool outputs/right_conducting/right_conducting_goal_devset_selection_dryrun.json
```

Status:

```text
test_model_selection.py: 4 OK
test_goal_command_cli.py: 17 OK
full unittest: 129 OK
compileall: OK
dry-run JSON strict load: OK
```

## Current Next Action

Still unchanged:

```text
Collect fixed-camera 80 BPM static devset under dataset/static_variants_80.
Then run devset-audit,motionbert-devset-score,devset-gate before any MotionBERT export.
```
