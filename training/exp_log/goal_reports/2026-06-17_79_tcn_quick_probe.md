# Report 79 - TCN Quick Probe

## Request

Run a quick TCN comparison in a new folder, using all available GPUs where useful.

## Decision

TCN was tested as a comparison probe.

It is not replacing the selected MotionBERT-Lite bundle yet, because this run is a deployment-fit probe: it trains and evaluates on the same fixed-camera processed roots.

Current selected live bundle remains:

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext
```

TCN probe folder:

```text
outputs/right_conducting/tcn_quick_probe_20260617
```

## Implementation

Script:

```text
tools/run_tcn_right_conducting_quick_probe.py
```

Model:

```text
input: [B, 9, T]
channels: right shoulder / right elbow / right wrist x 3 values
encoder: causal residual Conv1d TCN
heads: tempo 4-class, gain 2-class
loss: CE tempo + 0.5 CE gain
```

Data:

```text
dataset/static_variants_80
dataset/transitions
```

The probe uses original processed pose and frame labels only:

```text
pose_right_h36m_masked.npy
labels_frame.jsonl
```

Eval-local augmentation folders/files are not used.

## Commands

Five window sizes were run in parallel on cuda:0-4:

```bash
python tools/run_tcn_right_conducting_quick_probe.py \
  --roots dataset/static_variants_80,dataset/transitions \
  --output-dir outputs/right_conducting/tcn_quick_probe_20260617/45f \
  --window-frames 45 \
  --stride-frames 3 \
  --epochs 45 \
  --hidden-channels 64 \
  --levels 4 \
  --device cuda:1 \
  --margins 0,0.5,1,2,3 \
  --quiet
```

The same command shape was used for 30f, 60f, 90f, and 120f on the other GPUs.

## Score

| window | margin | samples | mixed excl | margin excl | raw tempo | smooth tempo | smooth gain | false/min | p90 delay | r80 | r100 | r120 | bpm mae |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 30 | 0.0 | 2360 | 134 | 12 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 30 | 3.0 | 1952 | 134 | 420 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 45 | 0.0 | 2235 | 204 | 12 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 45 | 3.0 | 1827 | 204 | 420 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 60 | 0.0 | 2110 | 274 | 12 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 60 | 3.0 | 1702 | 274 | 420 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 90 | 0.0 | 1860 | 414 | 12 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 90 | 3.0 | 1452 | 414 | 420 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 120 | 0.0 | 1610 | 554 | 12 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 120 | 3.0 | 1202 | 554 | 420 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

## Artifacts

```text
outputs/right_conducting/tcn_quick_probe_20260617/30f/tcn_conducting_head.pt
outputs/right_conducting/tcn_quick_probe_20260617/30f/scores.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_conducting_head.pt
outputs/right_conducting/tcn_quick_probe_20260617/45f/scores.json
outputs/right_conducting/tcn_quick_probe_20260617/60f/tcn_conducting_head.pt
outputs/right_conducting/tcn_quick_probe_20260617/60f/scores.json
outputs/right_conducting/tcn_quick_probe_20260617/90f/tcn_conducting_head.pt
outputs/right_conducting/tcn_quick_probe_20260617/90f/scores.json
outputs/right_conducting/tcn_quick_probe_20260617/120f/tcn_conducting_head.pt
outputs/right_conducting/tcn_quick_probe_20260617/120f/scores.json
```

## Verification

```text
python -m py_compile tools/run_tcn_right_conducting_quick_probe.py
PASS

TCN artifact validation
PASS

TCN score JSON parse
PASS

PYTHONPATH=. python -m unittest discover tests -v
Ran 233 tests in 45.839s
OK
```

## Interpretation

TCN can fit the current fixed-camera static80 + transition deployment set very easily.

After 3s transition margin exclusion, the 80 BPM middle segment is still classified correctly, so this probe does not show an 80 BPM tail failure on the deployment-fit data.

The margin logic was corrected in this report. With 3s margin, 420 transition-near windows are removed across window sizes.

This does not prove strict generalization. The probe still needs a true split where train roots and heldout roots do not overlap before it can replace the current selected MotionBERT bundle.

## Practical Candidate

If a TCN fallback is needed for speed, the 45f folder is the closest match to the current live MotionBERT context length:

```text
outputs/right_conducting/tcn_quick_probe_20260617/45f
```

For now, keep TCN as a comparison/fallback artifact, not the final selected model.
