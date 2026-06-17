# Raw Handmark CSV Stream Set Score

## Purpose

Report 74 exported a `right_arm_only` probe for cases where live input has only right shoulder / elbow / wrist. This report scores that probe on the full raw handmark CSV set, not only on two smoke examples.

This is a deployment-fit score, not strict heldout. The processed 2/3-beat sessions are part of `outputs/right_conducting/recordings_staged_static80_transitions.zip`.

## New Tool

```text
tools/evaluate_motionbert_handmark_csv_stream_set.py
```

The tool:

- streams raw `.csv` rows through `tools/run_motionbert_handmark_csv_stream.py` equivalent runtime logic;
- uses the model output schema from the exported MotionBERT live manifest;
- attaches labels from each sibling processed session's original `labels_frame.jsonl`;
- supports `stable_only` and transition margin sweep;
- writes aggregate JSON, markdown, and per-window JSONL rows.

## Command

```bash
python tools/evaluate_motionbert_handmark_csv_stream_set.py \
  --manifest outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/motionbert_conducting_live_manifest.json \
  --csv-root dataset/static_variants_80,dataset/transitions \
  --device cuda:0 \
  --stable-only \
  --margins 0,0.5,1,2,3 \
  --output-json outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.json \
  --output-md outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.md \
  --output-rows outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_rows.jsonl
```

## Dataset Resolved By The Tool

| item | value |
|---|---:|
| CSV files found | 15 |
| scoreable processed sessions | 11 |
| skipped CSV-only beat4 sessions | 4 |
| window | 45 frames |
| stride | 3 frames |
| fps | 15 |
| input mask | `right_arm_only` |

The 4 skipped CSV-only sessions do not have processed `meta.json` / `labels_frame.jsonl` sibling directories, so they are not scoreable in this report.

## Margin Sweep

Primary metric is smoothed classification because the final live output uses the live smoother.

| margin_s | samples | mixed_excluded | margin_excluded | raw_tempo | smooth_tempo | smooth_gain | false/min | p90_s | missed | r80 | r100 | r120 | BPM MAE |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 2241 | 204 | 6 | 0.9946 | 0.9955 | 1.0000 | 0.3689 | 0.1400 | 0 | 0.9926 | 1.0000 | 1.0000 | 0.0982 |
| 0.5 | 2172 | 204 | 75 | 0.9968 | 0.9972 | 1.0000 | 0.3689 | 0.0000 | 0 | 0.9955 | 1.0000 | 1.0000 | 0.0552 |
| 1.0 | 2103 | 204 | 144 | 0.9971 | 0.9976 | 1.0000 | 0.2459 | 0.0000 | 0 | 0.9961 | 1.0000 | 1.0000 | 0.0476 |
| 2.0 | 1964 | 204 | 283 | 0.9980 | 0.9990 | 1.0000 | 0.1230 | 0.0000 | 0 | 0.9984 | 1.0000 | 1.0000 | 0.0204 |
| 3.0 | 1824 | 204 | 423 | 0.9978 | 0.9989 | 1.0000 | 0.1230 | 0.0000 | 0 | 0.9983 | 1.0000 | 1.0000 | 0.0219 |

## Worst Remaining Case

At 3s margin, the weakest session is:

```text
session: session_20260617_024003_bpm100to100_beat3_small
tempo_acc: 0.9841
r80: 0.9333
r100: 1.0000
error pattern: two 80 BPM windows predicted as 100 BPM
```

This means the remaining error is not a 120 BPM failure. It is a small number of 80 BPM windows in the `100 -> 80 -> 100` small-motion take being pulled toward 100.

## Interpretation

The raw handmark CSV path now has a set-level score, not only a smoke test. For the fixed-camera 2/3-beat deployment-fit scope:

- static 80 is stable;
- 120 -> 80 -> 120 transitions are stable after smoothing;
- 100 -> 80 -> 100 is also mostly stable, with the remaining error concentrated in one small-motion take;
- gain classification is saturated on this dataset;
- margin removal improves score, but even margin 0 remains high.

The strict limitation remains unchanged:

```text
This is not independent heldout.
The selected right-arm-only probe should not be reported as generalization-proven.
For strict reporting, record a new fixed-camera 2/3-beat heldout set outside the staged training zip.
```

## Artifacts

```text
score_json: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.json
score_md: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.md
rows_jsonl: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_rows.jsonl
```

## Pass Line

For fixed-camera handmark-only deployment-fit:

```text
margin 3s smoothed tempo_acc >= 0.98
margin 3s r80/r100/r120 >= 0.90
margin 3s gain_acc >= 0.95
margin 3s false_switches_per_min <= 0.5
margin 3s missed_switch_count == 0
```

Current result passes all of the above.
