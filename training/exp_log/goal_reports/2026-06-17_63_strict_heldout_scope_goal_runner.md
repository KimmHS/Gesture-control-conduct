# Strict Heldout Scope Goal Runner

## Purpose

Report 62 added the strict heldout scope audit as a standalone tool. This report
connects it to the main goal runner so the next heldout dataset can be checked
with one reproducible command before any strict replay/gate claim is made.

## Added Runner Step

```text
step: strict-heldout-scope
tool: tools/audit_right_conducting_strict_heldout_scope.py
```

New CLI args:

```text
--heldout-scope-requirements
--heldout-scope-output-json
--heldout-scope-output-md
```

The step uses `--heldout-eval-roots` as its heldout roots. If
`heldout-independence` is also in `--steps`, it passes the generated independence
JSON into the scope audit automatically.

## Current Dry Run

```bash
python tools/run_right_conducting_goal.py \
  --dry-run \
  --steps heldout-independence,strict-heldout-scope \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/evaluation,dataset/evaluation_transitions \
  --heldout-independence-output-json outputs/right_conducting/strict_eval_roots_independence_ext.json \
  --heldout-independence-output-md outputs/right_conducting/strict_eval_roots_independence_ext.md \
  --heldout-scope-output-json outputs/right_conducting/strict_heldout_scope_audit_ext.json \
  --heldout-scope-output-md outputs/right_conducting/strict_heldout_scope_audit_ext.md \
  --output-json outputs/right_conducting/right_conducting_goal_strict_scope_dryrun.json \
  --output-md outputs/right_conducting/right_conducting_goal_strict_scope_dryrun.md
```

Dry-run command order:

```text
1. heldout_independence
2. strict_heldout_scope
```

Artifact:

```text
outputs/right_conducting/right_conducting_goal_strict_scope_dryrun.json
outputs/right_conducting/right_conducting_goal_strict_scope_dryrun.md
```

## Next Heldout Data Command

After recording a new heldout root, run:

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence,strict-heldout-scope \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots NEW_HELDOUT_STATIC_ROOT,NEW_HELDOUT_TRANSITION_ROOT \
  --heldout-independence-output-json outputs/right_conducting/strict_heldout_independence_v1.json \
  --heldout-independence-output-md outputs/right_conducting/strict_heldout_independence_v1.md \
  --heldout-scope-output-json outputs/right_conducting/strict_heldout_scope_v1.json \
  --heldout-scope-output-md outputs/right_conducting/strict_heldout_scope_v1.md \
  --output-json outputs/right_conducting/right_conducting_goal_strict_scope_v1.json \
  --output-md outputs/right_conducting/right_conducting_goal_strict_scope_v1.md
```

Only if `strict_heldout_scope_v1.json` is `GO`, run strict replay/gate:

```bash
python tools/run_right_conducting_goal.py \
  --steps replay-selected,live-output,live-replay-gate \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext \
  --motionbert-replay-eval-root NEW_HELDOUT_TRANSITION_ROOT \
  --motionbert-replay-stable-only \
  --motionbert-replay-output-json outputs/right_conducting/strict_heldout_transition_replay_v1.json \
  --motionbert-replay-output-md outputs/right_conducting/strict_heldout_transition_replay_v1.md \
  --motionbert-replay-output-rows outputs/right_conducting/strict_heldout_transition_replay_v1_rows.jsonl \
  --live-output-jsonl outputs/right_conducting/strict_heldout_transition_live_outputs_v1.jsonl \
  --live-output-summary-json outputs/right_conducting/strict_heldout_transition_live_outputs_v1_summary.json \
  --live-replay-gate-independence-json outputs/right_conducting/strict_heldout_independence_v1.json \
  --live-replay-gate-output-json outputs/right_conducting/strict_heldout_transition_live_gate_v1.json \
  --live-replay-gate-output-md outputs/right_conducting/strict_heldout_transition_live_gate_v1.md \
  --live-replay-gate-require-independence
```

## Verification

```bash
python -m py_compile tools/run_right_conducting_goal.py tools/audit_right_conducting_strict_heldout_scope.py
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
python -m unittest discover -s tests -p 'test_strict_heldout_scope_audit.py' -v
```

Result:

```text
py_compile: OK
test_goal_command_cli.py: 26 OK
test_strict_heldout_scope_audit.py: 3 OK
goal strict scope dry-run JSON: OK
```

## Status

```text
live_pilot_status: GO
strict_heldout_status: NO_GO
reason: runner is ready, but current heldout scope audit remains NO_GO until new in-scope heldout data is supplied.
```
