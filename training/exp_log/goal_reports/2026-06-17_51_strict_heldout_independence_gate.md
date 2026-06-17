# Strict Heldout Independence Gate

## Scope

```text
date: 2026-06-17
selected bundle: outputs/right_conducting/selected_motionbert_static80_transitions_live45f
current training manifest: outputs/right_conducting/recordings_staged_static80_transitions_manifest.json
current scored roots: dataset/static_variants_80, dataset/transitions
```

## Why This Exists

Report 50 made the exported 45f MotionBERT bundle usable for the fixed-camera live pilot: false switches dropped to zero after the live policy sweep.

That is still not independent generalization evidence because `dataset/static_variants_80` and `dataset/transitions` were included in the staged training source. This report adds an explicit gate that fails whenever heldout roots overlap with train roots or staged train sessions.

## Added Tooling

```text
lib/right_conducting/heldout_independence.py
tools/check_right_conducting_heldout_independence.py
tools/run_right_conducting_goal.py --steps heldout-independence
tests/test_heldout_independence.py
```

The audit checks:

```text
training_input_present
heldout_input_present
missing_train_inputs
missing_heldout_roots
no_train_heldout_root_conflict
no_session_path_overlap
no_session_name_overlap
```

## Current Audit

Command:

```bash
python tools/check_right_conducting_heldout_independence.py \
  --train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-roots dataset/static_variants_80,dataset/transitions \
  --output-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f/heldout_independence_static80_transitions.json \
  --output-md outputs/right_conducting/selected_motionbert_static80_transitions_live45f/heldout_independence_static80_transitions.md
```

Result:

| status | train sessions | heldout sessions | root conflicts | path overlaps | name overlaps |
|---|---:|---:|---:|---:|---:|
| NO_GO | 35 | 11 | 2 | 11 | 11 |

Interpretation:

```text
Current static80/transitions scores are deployment-fit only.
They should not be reported as strict heldout or independent generalization.
```

## Next Strict Heldout Command

After recording new fixed-camera heldout roots, run:

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/evaluation_stable_v1,dataset/evaluation_transitions_v1 \
  --heldout-independence-output-json outputs/right_conducting/strict_heldout_independence_v1.json \
  --heldout-independence-output-md outputs/right_conducting/strict_heldout_independence_v1.md
```

Pass line:

```text
status: GO
root_conflict_count: 0
path_overlap_count: 0
name_overlap_count: 0
```

Only after this passes should the selected live bundle be replayed on those roots and reported as strict heldout.

## Artifacts

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/heldout_independence_static80_transitions.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/heldout_independence_static80_transitions.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_structure.md
```
