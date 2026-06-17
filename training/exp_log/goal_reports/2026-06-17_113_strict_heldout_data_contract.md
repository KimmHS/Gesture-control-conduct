# Report 113 - Strict Heldout Data Contract

## Purpose

The strict post-arrival command is wired and dry-run verified, but the user still needs a single contract for what data must be placed under the strict heldout roots. This report adds that contract.

## Added Document

```text
docs/exp/strict_heldout_data_contract.md
```

## Source Of Truth

The contract is derived from:

```text
docs/exp/right_conducting_required_data_manifest.json
tools/audit_right_conducting_strict_heldout_scope.py
tools/evaluate_tcn_handmark_csv_stream_set.py
scripts/run_tcn_strict_post_arrival_goal.sh
```

## What It Fixes

The existing tools already enforce coverage and preflight, but the requirements were spread across several files. The new contract makes these explicit:

```text
strict roots:
  dataset/strict_heldout_static_v1
  dataset/strict_heldout_transitions_v1

P0 required cases:
  4 static 80 BPM cases
  4 transition 120 -> 80 -> 120 cases

required processed artifacts:
  meta.json
  labels_frame.jsonl
  labels_window.jsonl
  pose_right_h36m_masked.npy
  right_rule_features.npy

stream-set score requirement:
  each CSV must have a sibling processed session directory with the same stem
```

## Critical Clarification

The strict scope audit checks processed artifacts, but the selected TCN stream-set score also needs raw handmark CSV files.

Expected layout:

```text
dataset/strict_heldout_transitions_v1/
  P0_transition_120_to_80_to_120_beat2_small.csv
  P0_transition_120_to_80_to_120_beat2_small/
    meta.json
    labels_frame.jsonl
    labels_window.jsonl
    pose_right_h36m_masked.npy
    right_rule_features.npy
```

## Completion Gate

After data arrives:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh
```

The goal remains incomplete until this chain reports:

```text
live_status: GO
release_validation_status: GO
strict_heldout_status: GO
status: COMPLETE
```

## Verification

```text
report113_strict_contract_assertions_ok
strict heldout contract links checked against current source files
Report 112 dry-run remains the executable wiring evidence
```
