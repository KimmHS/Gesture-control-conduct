# Strict Heldout Missing Checklist Runner

## Why

The current selected MotionBERT bundle is `GO` for the fixed-camera live pilot, but strict heldout remains `NO_GO` because the available eval roots cover `0/8` current P0 2/3-beat heldout cases.

This step adds a concrete checklist artifact after strict scope audit so the next recording session can go directly toward the missing strict cases.

## Added

```text
lib/right_conducting/strict_heldout_checklist.py
tools/render_right_conducting_strict_heldout_checklist.py
tools/run_right_conducting_goal.py step: strict-heldout-missing-checklist
```

The new runner step reads a strict heldout scope audit JSON and writes:

```text
outputs/right_conducting/current_eval_roots_strict_missing_checklist.json
outputs/right_conducting/current_eval_roots_strict_missing_checklist.md
```

## Current Result

Current eval roots:

```text
dataset/evaluation
dataset/evaluation_transitions
```

Checklist summary:

| metric | value |
|---|---:|
| missing_count | 12 |
| P0 missing | 8 |
| P1 missing | 2 |
| P2 missing | 2 |
| target static root | `dataset/strict_heldout_static_v1` |
| target transition root | `dataset/strict_heldout_transitions_v1` |

P0 capture list:

| type | recording | schedule | output root |
|---|---|---|---|
| static | 80 BPM / 2 beat / large | static hold about 40s | `dataset/strict_heldout_static_v1` |
| static | 80 BPM / 2 beat / small | static hold about 40s | `dataset/strict_heldout_static_v1` |
| static | 80 BPM / 3 beat / large | static hold about 40s | `dataset/strict_heldout_static_v1` |
| static | 80 BPM / 3 beat / small | static hold about 40s | `dataset/strict_heldout_static_v1` |
| transition | 120 -> 80 -> 120 BPM / 2 beat / large | 0s:120, 15s:80, 30s:120, stop 46s | `dataset/strict_heldout_transitions_v1` |
| transition | 120 -> 80 -> 120 BPM / 2 beat / small | 0s:120, 15s:80, 30s:120, stop 46s | `dataset/strict_heldout_transitions_v1` |
| transition | 120 -> 80 -> 120 BPM / 3 beat / large | 0s:120, 15s:80, 30s:120, stop 46s | `dataset/strict_heldout_transitions_v1` |
| transition | 120 -> 80 -> 120 BPM / 3 beat / small | 0s:120, 15s:80, 30s:120, stop 46s | `dataset/strict_heldout_transitions_v1` |

## Command

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence,strict-heldout-scope,strict-heldout-missing-checklist \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/evaluation,dataset/evaluation_transitions \
  --heldout-independence-output-json outputs/right_conducting/current_eval_roots_independence_missing_checklist_chain.json \
  --heldout-independence-output-md outputs/right_conducting/current_eval_roots_independence_missing_checklist_chain.md \
  --heldout-scope-output-json outputs/right_conducting/current_eval_roots_scope_missing_checklist_chain.json \
  --heldout-scope-output-md outputs/right_conducting/current_eval_roots_scope_missing_checklist_chain.md \
  --heldout-target-static-root dataset/strict_heldout_static_v1 \
  --heldout-target-transition-root dataset/strict_heldout_transitions_v1 \
  --heldout-missing-output-json outputs/right_conducting/current_eval_roots_strict_missing_checklist.json \
  --heldout-missing-output-md outputs/right_conducting/current_eval_roots_strict_missing_checklist.md
```

## Recording Rules

```text
camera/distance: fixed
controls: do not press R, [, or ]
BPM: use automatic schedule only
audio: metronome on
scoring: exclude eval-local augmentation artifacts
```

## Next Gate

After recording those P0 roots outside the staged training manifest, run the full strict chain:

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence,strict-heldout-scope,strict-heldout-missing-checklist,replay-selected,diagnose-replay,live-output,live-replay-gate,goal-status \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/strict_heldout_static_v1,dataset/strict_heldout_transitions_v1 \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext \
  --motionbert-replay-stable-only \
  --live-replay-gate-require-independence
```

Pass requires all three:

```text
heldout independence: GO
strict heldout scope: GO
strict live replay gate: GO
```

## Verification

```bash
python -m py_compile lib/right_conducting/strict_heldout_checklist.py tools/render_right_conducting_strict_heldout_checklist.py tools/run_right_conducting_goal.py
python -m unittest discover -s tests -p 'test_strict_heldout_checklist.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
```

Result:

```text
test_strict_heldout_checklist.py: 2 OK
test_goal_command_cli.py: 31 OK
```
