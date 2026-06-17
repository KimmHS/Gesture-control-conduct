# Report 39 — Devset Edge-Case Audit

## Scope

Report 38 showed that 5-GPU MotionBERT head hparam tuning did not solve heldout tempo stability.

The next bottleneck is data coverage:

```text
222455 eval: candidates collapse away from 120 BPM
dataset/transitions: candidates recover 120 moderately but miss 80 BPM
```

This report fixes the next data request into an auditable checklist.

## New Tool

Added:

```text
tools/audit_right_conducting_devset_edges.py
```

Integrated into:

```text
tools/run_right_conducting_goal.py --steps devset-audit
tools/run_right_conducting_goal.py --steps motionbert-devset-score
tools/run_right_conducting_goal.py --steps devset-gate
```

Purpose:

```text
Check whether required P0/P1/P2 devset edge cases are present.
Match static cases by bpm_target, meter_beats, dynamics_condition.
Match transition cases by meta.json bpm_schedule, meter_beats, dynamics_condition.
```

Command:

```bash
python tools/audit_right_conducting_devset_edges.py \
  --static-root dataset/static_variants_80 \
  --transition-root dataset/transitions \
  --output-json outputs/right_conducting/devset_edge_case_audit.json \
  --output-md outputs/right_conducting/devset_edge_case_audit.md
```

Equivalent goal-runner command:

```bash
python tools/run_right_conducting_goal.py \
  --steps devset-audit \
  --devset-static-root dataset/static_variants_80 \
  --devset-transition-root dataset/transitions \
  --devset-output-json outputs/right_conducting/devset_edge_case_audit.json \
  --devset-output-md outputs/right_conducting/devset_edge_case_audit.md \
  --output-json outputs/right_conducting/right_conducting_goal_devset_audit.json \
  --output-md outputs/right_conducting/right_conducting_goal_devset_audit.md
```

Artifacts:

```text
outputs/right_conducting/devset_edge_case_audit.json
outputs/right_conducting/devset_edge_case_audit.md
outputs/right_conducting/right_conducting_goal_devset_audit.json
outputs/right_conducting/right_conducting_goal_devset_audit.md
```

## Current Audit Result

```text
static_root_exists: false
transition_root_exists: true
static_session_count: 0
transition_session_count: 11
p0_complete: false
```

Priority summary:

| priority | required | present | missing |
|---|---:|---:|---:|
| P0 | 10 | 4 | 6 |
| P1 | 4 | 4 | 0 |
| P2 | 2 | 0 | 2 |

Interpretation:

```text
P0 transition coverage is already present.
P0 static 80 BPM coverage is missing.
The next dataset request should be 80 static variants first.
```

## Required Next Data

P0 static:

```text
- 80 BPM / 2 beat / large / fixed camera / high arm
- 80 BPM / 2 beat / small / fixed camera / high arm
- 80 BPM / 3 beat / large / fixed camera / low arm
- 80 BPM / 3 beat / small / fixed camera / low arm
- 80 BPM / 4 beat / large / fixed camera / neutral arm
- 80 BPM / 4 beat / small / fixed camera / neutral arm
```

P0 transition:

```text
- 120 -> 80 -> 120 / 2 beat / large
- 120 -> 80 -> 120 / 2 beat / small
- 120 -> 80 -> 120 / 4 beat / large
- 120 -> 80 -> 120 / 4 beat / small
```

The transition items are already satisfied in `dataset/transitions`; keep them in the gate because they are the minimum heldout down-transition target.

## Recording Guide

Added:

```text
TRANSITION_RECORDING_GUIDE.md
```

It records:

```text
do not press R/[ /]
use automatic start and automatic BPM schedule
transition timeline: 0s source, 15s target, 30s source, 46s stop
score original artifacts only
exclude eval-local augmentation
```

## Gate

Before another 5-GPU MotionBERT sweep:

```text
P0 complete: true
80 static recall >= 0.6
120 -> 80 held tail 80 recall >= 0.5 after transition_margin_seconds=3
gain_acc >= 0.8
```

If 80 static recall fails after these takes, the next step is not more head hparam tuning. It should move down to model/input design: temporal features, beat-phase auxiliary target, soft BPM distribution loss, or stronger tempo-normalized representation.

## Post-Capture MotionBERT Score Command

After P0 static data is copied into `dataset/static_variants_80`, run coverage, score, and gate together:

```bash
python tools/run_right_conducting_goal.py \
  --steps devset-audit,motionbert-devset-score,devset-gate \
  --head-output-dir outputs/right_conducting/motionbert_head_after_supply \
  --devset-static-root dataset/static_variants_80 \
  --devset-transition-root dataset/transitions \
  --devset-output-json outputs/right_conducting/devset_edge_case_audit.json \
  --devset-output-md outputs/right_conducting/devset_edge_case_audit.md \
  --devset-static-score-prefix outputs/right_conducting/motionbert_devset_static_score \
  --devset-transition-score-prefix outputs/right_conducting/motionbert_devset_transition_score \
  --devset-gate-output-prefix outputs/right_conducting/motionbert_devset_gate \
  --window-frames 60 \
  --stride-frames 3 \
  --device cuda:0 \
  --output-json outputs/right_conducting/right_conducting_goal_devset_pipeline.json \
  --output-md outputs/right_conducting/right_conducting_goal_devset_pipeline.md
```

Expected outputs for `60f`:

```text
outputs/right_conducting/motionbert_devset_static_score_60f.json
outputs/right_conducting/motionbert_devset_static_score_60f.md
outputs/right_conducting/motionbert_devset_transition_score_60f.json
outputs/right_conducting/motionbert_devset_transition_score_60f.md
outputs/right_conducting/motionbert_devset_gate_60f.json
outputs/right_conducting/motionbert_devset_gate_60f.md
```

Static scoring uses `--margins 0` because there are no BPM changes. Transition scoring keeps `0,0.5,1,2,3` margin sweep.
The devset gate checks `P0 complete`, static 80 recall, transition 80 recall at margin 3s, and gain accuracy.

## Selection Guard

`select_right_conducting_model_candidate.py` now accepts:

```text
--devset-gate-jsons
--require-devset-gate
```

When `run_right_conducting_goal.py` runs `devset-gate,gate,select` together, the selection command automatically passes the matching devset gate JSON and requires it to be `GO`.

Dry-run:

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

This prevents a model from being exported as selected when the regular score gate is `GO` but fixed-camera devset stability is `NO_GO`.

## Verification

```bash
python -m compileall -q tools/audit_right_conducting_devset_edges.py
python -m compileall -q tools/run_right_conducting_goal.py tests/test_goal_command_cli.py
python tools/audit_right_conducting_devset_edges.py --help
python tools/audit_right_conducting_devset_edges.py \
  --output-json outputs/right_conducting/devset_edge_case_audit.json \
  --output-md outputs/right_conducting/devset_edge_case_audit.md
python tools/run_right_conducting_goal.py \
  --dry-run \
  --steps devset-audit \
  --devset-static-root dataset/static_variants_80 \
  --devset-transition-root dataset/transitions \
  --devset-output-json outputs/right_conducting/devset_edge_case_audit.json \
  --devset-output-md outputs/right_conducting/devset_edge_case_audit.md \
  --output-json outputs/right_conducting/right_conducting_goal_devset_audit_dryrun.json \
  --output-md outputs/right_conducting/right_conducting_goal_devset_audit_dryrun.md
python tools/run_right_conducting_goal.py \
  --dry-run \
  --steps motionbert-devset-score \
  --head-output-dir outputs/right_conducting/motionbert_head_after_supply \
  --devset-static-root dataset/static_variants_80 \
  --devset-transition-root dataset/transitions \
  --devset-static-score-prefix outputs/right_conducting/motionbert_devset_static_score \
  --devset-transition-score-prefix outputs/right_conducting/motionbert_devset_transition_score \
  --window-frames 60 \
  --stride-frames 3 \
  --device cuda:0 \
  --output-json outputs/right_conducting/right_conducting_goal_motionbert_devset_score_dryrun.json \
  --output-md outputs/right_conducting/right_conducting_goal_motionbert_devset_score_dryrun.md
python tools/run_right_conducting_goal.py \
  --dry-run \
  --steps devset-audit,motionbert-devset-score,devset-gate \
  --head-output-dir outputs/right_conducting/motionbert_head_after_supply \
  --devset-static-root dataset/static_variants_80 \
  --devset-transition-root dataset/transitions \
  --devset-output-json outputs/right_conducting/devset_edge_case_audit.json \
  --devset-output-md outputs/right_conducting/devset_edge_case_audit.md \
  --devset-static-score-prefix outputs/right_conducting/motionbert_devset_static_score \
  --devset-transition-score-prefix outputs/right_conducting/motionbert_devset_transition_score \
  --devset-gate-output-prefix outputs/right_conducting/motionbert_devset_gate \
  --window-frames 60 \
  --stride-frames 3 \
  --device cuda:0 \
  --output-json outputs/right_conducting/right_conducting_goal_devset_pipeline_dryrun.json \
  --output-md outputs/right_conducting/right_conducting_goal_devset_pipeline_dryrun.md
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
python -m unittest discover -s tests -p 'test_model_selection.py' -v
python -m unittest discover -s tests -p 'test_devset_gate.py' -v
```

Status:

```text
compile: OK
audit run: OK
goal runner dry-run: OK
test_devset_edge_audit.py: 4 OK
test_devset_gate.py: 4 OK
test_model_selection.py: 4 OK
test_goal_command_cli.py: 17 OK
python -m unittest discover -s tests -p 'test_*.py' -v: 129 OK
```
