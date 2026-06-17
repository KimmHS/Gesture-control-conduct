# Strict Heldout Data Contract

This is the intake contract for the final strict-heldout validation of the selected TCN handmark live classifier.

## Purpose

The current selected model is live-ready on the supplied fixed-camera set, but the full goal is not complete until strict heldout data proves the same behavior on independent sessions. Put the new heldout files under the two roots below and then run the strict post-arrival command.

## Required Roots

```text
dataset/strict_heldout_static_v1
dataset/strict_heldout_transitions_v1
```

These roots must not contain sessions used in:

```text
dataset/recordings
dataset/static_variants_80
dataset/transitions
outputs/right_conducting/recordings_staged_static80_transitions_manifest.json
```

## Required P0 Cases

Static 80 BPM:

| root | bpm | meter | dynamics | expected condition |
|---|---:|---:|---|---|
| `dataset/strict_heldout_static_v1` | 80 | 2 | large | fixed camera, high arm |
| `dataset/strict_heldout_static_v1` | 80 | 2 | small | fixed camera, high arm |
| `dataset/strict_heldout_static_v1` | 80 | 3 | large | fixed camera, low arm |
| `dataset/strict_heldout_static_v1` | 80 | 3 | small | fixed camera, low arm |

Transition 120 -> 80 -> 120:

| root | source | target | return | meter | dynamics |
|---|---:|---:|---:|---:|---|
| `dataset/strict_heldout_transitions_v1` | 120 | 80 | 120 | 2 | large |
| `dataset/strict_heldout_transitions_v1` | 120 | 80 | 120 | 2 | small |
| `dataset/strict_heldout_transitions_v1` | 120 | 80 | 120 | 3 | large |
| `dataset/strict_heldout_transitions_v1` | 120 | 80 | 120 | 3 | small |

P1/P2 sessions can be recorded later, but they do not close the current P0 strict gate.

Recommended P0 stems:

```text
P0_static_80_beat2_large
P0_static_80_beat2_small
P0_static_80_beat3_large
P0_static_80_beat3_small
P0_transition_120_to_80_to_120_beat2_large
P0_transition_120_to_80_to_120_beat2_small
P0_transition_120_to_80_to_120_beat3_large
P0_transition_120_to_80_to_120_beat3_small
```

## File Layout

The TCN stream-set evaluator scans CSV files and expects each CSV to have a sibling processed session directory with the same stem.

Example:

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

For static takes:

```text
dataset/strict_heldout_static_v1/
  P0_static_80_beat2_large.csv
  P0_static_80_beat2_large/
    meta.json
    labels_frame.jsonl
    labels_window.jsonl
    pose_right_h36m_masked.npy
    right_rule_features.npy
```

The scope audit requires the original processed artifacts:

```text
meta.json
labels_frame.jsonl
labels_window.jsonl
pose_right_h36m_masked.npy
right_rule_features.npy
```

The stream score additionally needs the raw handmark CSV next to the processed session directory.

## Metadata Contract

Static `meta.json` must include:

```json
{
  "dataset_version": "right_conducting_v0",
  "recording_type": "tempo_static",
  "bpm_target": 80.0,
  "meter_beats": 2,
  "dynamics_condition": "large",
  "metronome_audio": true,
  "bpm_schedule": [],
  "camera_framing": "upper_body_with_both_shoulders",
  "fps_estimate": 15.0
}
```

Transition `meta.json` must include:

```json
{
  "dataset_version": "right_conducting_v0",
  "recording_type": "tempo_transition",
  "bpm_target": 120.0,
  "meter_beats": 2,
  "dynamics_condition": "small",
  "target_seconds": 46,
  "metronome_audio": true,
  "bpm_schedule": [
    {"time_seconds": 0.0, "bpm": 120.0},
    {"time_seconds": 15.0, "bpm": 80.0},
    {"time_seconds": 30.0, "bpm": 120.0}
  ],
  "camera_framing": "upper_body_with_both_shoulders",
  "fps_estimate": 15.0
}
```

The transition matcher uses `bpm_schedule`, `meter_beats`, and `dynamics_condition`, not the directory name.

## Label Contract

`labels_frame.jsonl` must reflect the actual per-frame BPM and dynamics labels.

For transition sessions, the expected timeline is:

```text
0s  <= t < 15s: source BPM
15s <= t < 30s: 80 BPM
30s <= t <= end: source BPM
```

The final score uses stable windows and margin sweep:

```text
stable_only: true
margins: 0, 0.5, 1, 2, 3 seconds
selected gate margin: 3 seconds
```

Mixed BPM windows and transition-margin windows are excluded from the selected classification score.

## Exclusions

Do not use evaluation-local augmentation for strict score:

```text
recommended_augmented_v0/
labels_tempo_augmented_15f.jsonl
tempo_augmented_15f.npy
label_backup*/
```

4-beat takes are useful stress evidence but do not satisfy the current P0 strict gate.

## Pass Line

The strict post-arrival chain must finish with:

```text
tcn-release-validate: GO
heldout-independence: GO
strict-heldout-scope: GO
strict-heldout-preflight: GO
tcn-handmark-csv-set-gate: GO
tcn-handmark-stream-readiness: GO
tcn-goal-status: COMPLETE
tcn-current-status: strict_heldout_status GO
```

Current stream-set gate thresholds:

```text
margin_seconds: 3.0
min_sample_count: 1000
min_eval_session_count: 10
min_tempo_acc: 0.98
min_gain_acc: 0.95
min_recall_80: 0.90
min_recall_100: 0.90
min_recall_120: 0.90
max_false_switches_per_min: 0.50
max_missed_switch_count: 0
```

## Commands

Before data arrives, check wiring:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh --dry-run
```

To check the strict data contract directly after `strict-heldout-scope` has produced a scope JSON:

```bash
python tools/check_right_conducting_strict_data_contract.py \
  --scope-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_heldout_scope.json \
  --output-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_data_contract.json \
  --output-md outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_data_contract.md \
  --fail-on-no-go
```

After data arrives, run:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh
```

If the default stream CSV does not exist, choose a real strict transition CSV:

```bash
STRICT_STREAM_CSV=dataset/strict_heldout_transitions_v1/<real_transition_file>.csv \
  scripts/run_tcn_strict_post_arrival_goal.sh
```

Expected final status artifact:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_current_status.json
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_current_status.md
```
