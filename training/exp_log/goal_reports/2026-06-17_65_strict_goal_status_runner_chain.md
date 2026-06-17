# Strict Goal Status Runner Chain

## Summary

The goal runner now supports a final `goal-status` step. This connects strict heldout independence, strict heldout scope, replay, failure diagnosis, live-output conversion, live replay gate, and final goal status into one reproducible chain.

```text
new step: goal-status
status tool: tools/summarize_right_conducting_goal_status.py
dry-run artifact: outputs/right_conducting/right_conducting_goal_strict_status_dryrun.json
dry-run markdown: outputs/right_conducting/right_conducting_goal_strict_status_dryrun.md
```

## Added Behavior

`tools/run_right_conducting_goal.py` now:

- exposes `--goal-status-*` CLI flags;
- exposes `--replay-diagnosis-*` CLI flags;
- links `goal-status` to `live-replay-gate`, `heldout-independence`, and `strict-heldout-scope` outputs when they are in the same run;
- defaults strict replay to `--heldout-eval-roots` when `heldout-independence` is in the step list and no explicit `--motionbert-replay-eval-root` is provided.

`tools/replay_motionbert_live_bundle.py` now accepts comma-separated `--eval-root` values. This matters for strict heldout because static and transition heldout roots may be stored separately.

## Current Dry Run

```bash
python tools/run_right_conducting_goal.py \
  --dry-run \
  --steps heldout-independence,strict-heldout-scope,replay-selected,diagnose-replay,live-output,live-replay-gate,goal-status \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/evaluation,dataset/evaluation_transitions \
  --heldout-independence-output-json outputs/right_conducting/strict_eval_roots_independence_ext.json \
  --heldout-independence-output-md outputs/right_conducting/strict_eval_roots_independence_ext.md \
  --heldout-scope-output-json outputs/right_conducting/strict_heldout_scope_audit_ext.json \
  --heldout-scope-output-md outputs/right_conducting/strict_heldout_scope_audit_ext.md \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext \
  --motionbert-replay-stable-only \
  --motionbert-replay-output-json outputs/right_conducting/strict_heldout_eval_replay_ext.json \
  --motionbert-replay-output-md outputs/right_conducting/strict_heldout_eval_replay_ext.md \
  --motionbert-replay-output-rows outputs/right_conducting/strict_heldout_eval_replay_ext_rows.jsonl \
  --replay-diagnosis-output-json outputs/right_conducting/strict_heldout_eval_replay_diagnosis_ext.json \
  --replay-diagnosis-output-md outputs/right_conducting/strict_heldout_eval_replay_diagnosis_ext.md \
  --live-output-jsonl outputs/right_conducting/strict_heldout_eval_live_outputs_ext.jsonl \
  --live-output-summary-json outputs/right_conducting/strict_heldout_eval_live_outputs_ext_summary.json \
  --live-replay-gate-output-json outputs/right_conducting/strict_heldout_eval_live_gate_ext.json \
  --live-replay-gate-output-md outputs/right_conducting/strict_heldout_eval_live_gate_ext.md \
  --live-replay-gate-require-independence \
  --goal-status-output-json outputs/right_conducting/goal_status_strict_eval_ext.json \
  --goal-status-output-md outputs/right_conducting/goal_status_strict_eval_ext.md \
  --output-json outputs/right_conducting/right_conducting_goal_strict_status_dryrun.json \
  --output-md outputs/right_conducting/right_conducting_goal_strict_status_dryrun.md
```

The generated replay command uses both current heldout roots:

```text
--eval-root dataset/evaluation,dataset/evaluation_transitions
```

## Next Heldout Command

After recording new independent heldout roots, replace the two `NEW_HELDOUT_*` values and run without `--dry-run`:

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence,strict-heldout-scope,replay-selected,diagnose-replay,live-output,live-replay-gate,goal-status \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots NEW_HELDOUT_STATIC_ROOT,NEW_HELDOUT_TRANSITION_ROOT \
  --heldout-independence-output-json outputs/right_conducting/strict_heldout_independence_v1.json \
  --heldout-independence-output-md outputs/right_conducting/strict_heldout_independence_v1.md \
  --heldout-scope-output-json outputs/right_conducting/strict_heldout_scope_v1.json \
  --heldout-scope-output-md outputs/right_conducting/strict_heldout_scope_v1.md \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext \
  --motionbert-replay-stable-only \
  --motionbert-replay-output-json outputs/right_conducting/strict_heldout_replay_v1.json \
  --motionbert-replay-output-md outputs/right_conducting/strict_heldout_replay_v1.md \
  --motionbert-replay-output-rows outputs/right_conducting/strict_heldout_replay_v1_rows.jsonl \
  --replay-diagnosis-output-json outputs/right_conducting/strict_heldout_replay_diagnosis_v1.json \
  --replay-diagnosis-output-md outputs/right_conducting/strict_heldout_replay_diagnosis_v1.md \
  --live-output-jsonl outputs/right_conducting/strict_heldout_live_outputs_v1.jsonl \
  --live-output-summary-json outputs/right_conducting/strict_heldout_live_outputs_v1_summary.json \
  --live-replay-gate-output-json outputs/right_conducting/strict_heldout_live_gate_v1.json \
  --live-replay-gate-output-md outputs/right_conducting/strict_heldout_live_gate_v1.md \
  --live-replay-gate-require-independence \
  --goal-status-output-json outputs/right_conducting/goal_status_strict_heldout_v1.json \
  --goal-status-output-md outputs/right_conducting/goal_status_strict_heldout_v1.md
```

## Verification

```bash
python -m py_compile tools/run_right_conducting_goal.py tools/replay_motionbert_live_bundle.py tools/diagnose_motionbert_replay_failures.py
python -m unittest discover -s tests -p 'test_motionbert_replay.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
python -m unittest discover -s tests -p 'test_motionbert_replay_failure_diagnosis.py' -v
```

Result:

```text
py_compile: OK
test_motionbert_replay.py: 4 OK
test_goal_command_cli.py: 30 OK
test_motionbert_replay_failure_diagnosis.py: 3 OK
```

## Status

```text
runner readiness: GO
live pilot bundle: GO
strict heldout final status: still NO_GO until the new in-scope heldout roots exist and pass scope + replay gates
```
