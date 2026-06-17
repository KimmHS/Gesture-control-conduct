# Strict Heldout Preflight Gate

## Why

The goal runner already supports strict independence, strict scope audit, replay, failure diagnosis, live-output conversion, live replay gate, and goal status. The missing guard was a cheap preflight check between scope audit and replay.

This report adds that guard so a strict replay claim is only attempted after:

```text
heldout independence: GO
strict heldout scope: GO
P0 missing capture count: 0
```

## Added

```text
lib/right_conducting/strict_heldout_preflight.py
tools/check_right_conducting_strict_heldout_preflight.py
tools/run_right_conducting_goal.py step: strict-heldout-preflight
```

The CLI supports:

```text
--independence-json
--scope-json
--missing-checklist-json
--output-json
--output-md
--fail-on-no-go
```

`--fail-on-no-go` is optional. Use it when the next steps are expensive and should stop immediately if strict heldout is not ready.

## Current Eval Result

Artifacts:

```text
outputs/right_conducting/current_eval_roots_strict_preflight.json
outputs/right_conducting/current_eval_roots_strict_preflight.md
```

Result:

| metric | value |
|---|---:|
| status | NO_GO |
| independence_status | GO |
| scope_status | NO_GO |
| p0_complete | False |
| p0_required | 8 |
| p0_present | 0 |
| p0_missing | 8 |
| p0_capture_count | 8 |

Interpretation:

```text
The current eval roots are independent, but they are not in the required strict 2/3-beat P0 scope.
Do not run or report replay from these roots as strict heldout evidence.
Record the P0 checklist under dataset/strict_heldout_static_v1 and dataset/strict_heldout_transitions_v1 first.
```

## Command Used

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence,strict-heldout-scope,strict-heldout-missing-checklist,strict-heldout-preflight \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/evaluation,dataset/evaluation_transitions \
  --heldout-independence-output-json outputs/right_conducting/current_eval_roots_independence_preflight_chain.json \
  --heldout-independence-output-md outputs/right_conducting/current_eval_roots_independence_preflight_chain.md \
  --heldout-scope-output-json outputs/right_conducting/current_eval_roots_scope_preflight_chain.json \
  --heldout-scope-output-md outputs/right_conducting/current_eval_roots_scope_preflight_chain.md \
  --heldout-target-static-root dataset/strict_heldout_static_v1 \
  --heldout-target-transition-root dataset/strict_heldout_transitions_v1 \
  --heldout-missing-output-json outputs/right_conducting/current_eval_roots_strict_missing_checklist_preflight_chain.json \
  --heldout-missing-output-md outputs/right_conducting/current_eval_roots_strict_missing_checklist_preflight_chain.md \
  --heldout-preflight-output-json outputs/right_conducting/current_eval_roots_strict_preflight.json \
  --heldout-preflight-output-md outputs/right_conducting/current_eval_roots_strict_preflight.md
```

## Strict Replay Chain After New Data

After the missing P0 cases are recorded:

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence,strict-heldout-scope,strict-heldout-missing-checklist,strict-heldout-preflight,replay-selected,diagnose-replay,live-output,live-replay-gate,goal-status \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/strict_heldout_static_v1,dataset/strict_heldout_transitions_v1 \
  --heldout-preflight-fail-on-no-go \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext \
  --motionbert-replay-stable-only \
  --live-replay-gate-require-independence
```

## Verification

```bash
python -m py_compile lib/right_conducting/strict_heldout_preflight.py tools/check_right_conducting_strict_heldout_preflight.py tools/run_right_conducting_goal.py
python -m unittest discover -s tests -p 'test_strict_heldout_preflight.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
```

Result:

```text
test_strict_heldout_preflight.py: 3 OK
test_goal_command_cli.py: 32 OK
```
