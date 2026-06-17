# Current Eval Strict Chain Execution

## Summary

Report 65 added the full strict status runner chain as a dry-run path. This report executes the chain on the currently available eval roots to verify that the artifacts are produced end-to-end.

This is not final strict evidence. The current eval roots are independent from the staged train manifest, but they do not cover the current 2/3-beat fixed-camera P0 heldout scope.

```text
selected bundle: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext
eval roots: dataset/evaluation,dataset/evaluation_transitions
goal run: outputs/right_conducting/right_conducting_goal_current_eval_strict_chain.json
goal status: outputs/right_conducting/goal_status_current_eval_roots_ext_chain.json
final status: IN_PROGRESS
live pilot: GO
strict heldout: NO_GO
```

## Runner Fix

The heldout independence step now treats an explicit train manifest as authoritative. When `--heldout-train-manifests` is provided and `--heldout-train-roots` is not provided, the runner no longer silently adds the default `dataset/recordings` train root.

This changed the current eval independence count from the inflated mixed input count to the staged manifest count:

```text
train_session_count: 35
heldout_session_count: 2
root_conflict_count: 0
path_overlap_count: 0
name_overlap_count: 0
independence_status: GO
```

## Current Chain Result

| gate | status | key result |
|---|---|---|
| heldout independence | GO | train 35, heldout 2, no overlap |
| strict heldout scope | NO_GO | P0 coverage 0 / 8 |
| replay rows | generated | 544 rows across 2 sessions |
| replay failure diagnosis | generated | confusion/error-run/class-collapse report |
| live output JSONL | generated | 544 live output rows |
| live replay gate | NO_GO | tempo_acc 0.1691, false/min 5.7848, missed 1 |
| final goal status | IN_PROGRESS | live pilot GO, strict heldout NO_GO |

## Replay Metrics

| scope | rows | smoothed tempo_acc | smoothed gain_acc | false/min | missed |
|---|---:|---:|---:|---:|---:|
| all current eval roots | 544 | 0.1691 | 0.9412 | 5.7848 | 1 |
| 222455 eval stress | 258 | 0.2946 | 0.8760 | 10.5151 | 1 |
| 215630 eval transition | 286 | 0.0559 | 1.0000 | 1.0521 | 0 |

## Interpretation

The full current-eval chain is runnable and produces all required artifacts. The result remains a strict `NO_GO` for two independent reasons:

1. `strict_heldout_scope_go` is false because the current eval roots cover 0/8 required P0 heldout cases.
2. `strict_live_gate_go` is false because tempo accuracy and false switch rate fail by a wide margin on the available out-of-scope eval sessions.

The 215630 session is still not valid final score evidence because it was previously marked relabel/untrusted and does not satisfy the current 2/3-beat P0 heldout scope.

## Artifacts

```text
outputs/right_conducting/current_eval_roots_independence_ext_chain.json
outputs/right_conducting/current_eval_roots_scope_ext_chain.json
outputs/right_conducting/current_eval_roots_replay_ext_chain.json
outputs/right_conducting/current_eval_roots_replay_ext_chain.md
outputs/right_conducting/current_eval_roots_replay_ext_chain_rows.jsonl
outputs/right_conducting/current_eval_roots_replay_failure_diagnosis_ext_chain.json
outputs/right_conducting/current_eval_roots_replay_failure_diagnosis_ext_chain.md
outputs/right_conducting/current_eval_roots_live_outputs_ext_chain.jsonl
outputs/right_conducting/current_eval_roots_live_outputs_ext_chain_summary.json
outputs/right_conducting/current_eval_roots_live_gate_ext_chain.json
outputs/right_conducting/current_eval_roots_live_gate_ext_chain.md
outputs/right_conducting/goal_status_current_eval_roots_ext_chain.json
outputs/right_conducting/goal_status_current_eval_roots_ext_chain.md
outputs/right_conducting/right_conducting_goal_current_eval_strict_chain.json
outputs/right_conducting/right_conducting_goal_current_eval_strict_chain.md
```

## Verification

```bash
python -m py_compile tools/run_right_conducting_goal.py
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v

python tools/run_right_conducting_goal.py \
  --steps heldout-independence,strict-heldout-scope,replay-selected,diagnose-replay,live-output,live-replay-gate,goal-status \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/evaluation,dataset/evaluation_transitions \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext \
  --motionbert-replay-stable-only \
  --live-replay-gate-require-independence \
  --device cuda:0
```

Result:

```text
py_compile: OK
test_goal_command_cli.py: 29 OK
chain execution: OK
```
