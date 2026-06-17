# Deployment-Fit vs Current Eval Diagnosis

## Context

The extended 5-GPU sweep selected:

```text
bundle: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext
candidate: ext_e240_h512_lr3e3_s0_45f
window: 45 frames ~= 3s at current 15fps data
```

This report separates two different claims:

1. `dataset/static_variants_80` and `dataset/transitions` are deployment-fit fixed-camera checks. They are valid for the current live pilot, but they are not independent heldout generalization because these roots were part of the selected sweep source.
2. `dataset/evaluation,dataset/evaluation_transitions` are independent stress roots, but they are currently out of the required 2/3-beat P0 strict heldout scope and include label/scope caveats.

## Replay Diagnosis Artifacts

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_static80_stable_failure_diagnosis.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_static80_stable_failure_diagnosis.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_transitions_stable_failure_diagnosis.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_transitions_stable_failure_diagnosis.md
outputs/right_conducting/current_eval_roots_replay_failure_diagnosis_ext_chain.json
outputs/right_conducting/current_eval_roots_replay_failure_diagnosis_ext_chain.md
```

## Comparison

| scope | rows | sessions | smoothed tempo_acc | smoothed gain_acc | true tempo distribution | smoothed pred distribution | error runs | interpretation |
|---|---:|---:|---:|---:|---|---|---:|---|
| deployment static80 | 942 | 4 | 1.0000 | 1.0000 | 80:942 | 80:942 | 0 | expected constant 80 static behavior |
| deployment transitions | 1305 | 7 | 1.0000 | 1.0000 | 80:422, 100:252, 120:631 | 80:422, 100:252, 120:631 | 0 | current fixed-camera transition pilot passes |
| current eval roots | 544 | 2 | 0.1691 | 0.9412 | 80:16, 100:382, 120:146 | 60:11, 80:388, 100:145 | 9 | strict/stress replay fails |

## Current Eval Failure Shape

| session | rows | true tempo | smoothed pred tempo | tempo_acc | dominant issue |
|---|---:|---|---|---:|---|
| `session_20260616_222455_bpm120_beat4_large` | 258 | 80:16, 100:96, 120:146 | 60:11, 80:118, 100:129 | 0.2946 | 120 BPM has 0 smoothed recall |
| `session_20260616_215630_bpm100_beat4_large` | 286 | 100:286 | 80:270, 100:16 | 0.0559 | constant 100 label but near-collapse to 80; relabel/scope caveat remains |

The current eval replay therefore does not fail only at transition boundaries. It also fails on stable regions that are outside the current 2/3-beat fixed-camera deployment-fit scope.

## Decision

```text
live pilot status: GO
strict heldout status: NO_GO
```

Use the selected 45f ext bundle for the fixed-camera live pilot. Do not claim independent/general heldout robustness until a separate in-scope heldout root is recorded and kept out of the training manifest.

## Required Next Heldout

P0 strict heldout remains:

```text
static80 beat2 large/small
static80 beat3 large/small
transition 120 -> 80 -> 120 beat2 large/small
transition 120 -> 80 -> 120 beat3 large/small
```

The strict heldout scope audit currently reports:

```text
status: NO_GO
P0 present: 0 / 8
```

## Verification

```bash
python tools/diagnose_motionbert_replay_failures.py \
  --rows outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_static80_stable_rows.jsonl \
  --manifest outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_manifest.json \
  --output-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_static80_stable_failure_diagnosis.json \
  --output-md outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_static80_stable_failure_diagnosis.md

python tools/diagnose_motionbert_replay_failures.py \
  --rows outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_transitions_stable_rows.jsonl \
  --manifest outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_manifest.json \
  --output-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_transitions_stable_failure_diagnosis.json \
  --output-md outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_transitions_stable_failure_diagnosis.md
```
