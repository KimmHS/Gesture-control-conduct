# Live Replay Gate

## Scope

```text
date: 2026-06-17
selected bundle: outputs/right_conducting/selected_motionbert_static80_transitions_live45f
replay source: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_transitions_stable.json
metric mode: smoothed
```

## Added Tooling

```text
lib/right_conducting/live_replay_gate.py
tools/check_right_conducting_live_replay_gate.py
tools/run_right_conducting_goal.py --steps live-replay-gate
tests/test_live_replay_gate.py
```

The gate checks:

```text
tempo_acc >= 0.85
gain_acc >= 0.90
false_switches_per_min <= 0.50
missed_switch_count <= 0
switch_delay_p90_s <= 1.00
row_count >= 1
eval_session_count >= 1
heldout_independence_status == GO   # only when --require-independence is set
```

## Current Selected Bundle

Deployment-fit gate:

```bash
python tools/check_right_conducting_live_replay_gate.py \
  --replay-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_transitions_stable.json \
  --independence-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f/heldout_independence_static80_transitions.json \
  --output-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_replay_gate_transitions_deployment.json \
  --output-md outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_replay_gate_transitions_deployment.md
```

Strict heldout gate:

```bash
python tools/check_right_conducting_live_replay_gate.py \
  --replay-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_transitions_stable.json \
  --independence-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f/heldout_independence_static80_transitions.json \
  --require-independence \
  --output-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_replay_gate_transitions_strict.json \
  --output-md outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_replay_gate_transitions_strict.md
```

Result:

| gate | require independence | status | tempo_acc | gain_acc | false/min | missed | p90 delay | reason |
|---|---|---|---:|---:|---:|---:|---:|---|
| deployment-fit | false | GO | 0.9893 | 1.0000 | 0.0000 | 0 | 0.5938 | replay thresholds pass |
| strict heldout | true | NO_GO | 0.9893 | 1.0000 | 0.0000 | 0 | 0.5938 | heldout independence is NO_GO |

## Next Strict Heldout Command

After recording a new transition heldout root:

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence,replay-selected,live-replay-gate \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/evaluation_transitions_v1 \
  --heldout-independence-output-json outputs/right_conducting/strict_heldout_transition_independence_v1.json \
  --heldout-independence-output-md outputs/right_conducting/strict_heldout_transition_independence_v1.md \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f \
  --motionbert-replay-eval-root dataset/evaluation_transitions_v1 \
  --motionbert-replay-stable-only \
  --motionbert-replay-output-json outputs/right_conducting/strict_heldout_transition_replay_v1.json \
  --motionbert-replay-output-md outputs/right_conducting/strict_heldout_transition_replay_v1.md \
  --motionbert-replay-output-rows outputs/right_conducting/strict_heldout_transition_replay_v1_rows.jsonl \
  --live-replay-gate-output-json outputs/right_conducting/strict_heldout_transition_live_gate_v1.json \
  --live-replay-gate-output-md outputs/right_conducting/strict_heldout_transition_live_gate_v1.md \
  --live-replay-gate-require-independence
```

Pass line:

```text
strict_heldout_transition_independence_v1.json status == GO
strict_heldout_transition_live_gate_v1.json status == GO
```

## Artifacts

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_replay_gate_transitions_deployment.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_replay_gate_transitions_deployment.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_replay_gate_transitions_strict.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_replay_gate_transitions_strict.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_structure.md
```
