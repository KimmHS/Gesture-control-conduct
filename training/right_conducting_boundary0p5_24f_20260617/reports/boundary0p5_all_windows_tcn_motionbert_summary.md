# Boundary 0.5s TCN/MotionBERT Sweep Summary

## Policy
- Label-boundary uncertainty: total 1.0s, implemented as transition +/-0.5s.
- Training drops any window overlapping a BPM transition +/-0.5s. Devset transition rows below use the same 0.5s margin.
- Live timing policy: trailing window, no future frames; prediction timestamp is the window end frame.
- Stride: 3 frames at about 15 fps = 0.2s update interval.
- `strict 222455` is the legacy single-session score-gate eval: `dataset/evaluation/session_20260616_222455_bpm120_beat4_large`, `eval_stable_only=True`, no transition margin. It is not the broader devset.

## Readout
- Under 2s, MotionBERT's best short-window candidate is 24f (1.6s): CV tempo 0.7068, devset@0.5 tempo 0.8947, false/min 5.98. It still fails the strict 222455 score gate.
- If longer windows are allowed, MotionBERT 120f (8.0s) is the strongest devset row by transition tempo: 0.9887, false/min 0.00. This also fails strict 222455.
- TCN quick-probe is same-root train/eval evidence, not heldout evidence. In that scope, 24f (1.6s) is the shortest under-2s row with <=1 false switch/min at margin 0.5.
- Automatic candidate selection remains NO_GO because every MotionBERT candidate fails the strict 222455 score gate, mainly 120 BPM recall and transition tempo/BPM MAE.

## MotionBERT: Short Windows (<2s)
| window | seconds | train kept | boundary dropped | CV tempo | strict222455 tempo | strict 120 recall | devset@0.5 tempo | devset r80 | devset r120 | false/min | devset gate | score gate |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 9f | 0.6s | 10885 | 112 | 0.6166 | 0.2211 | 0.0127 | 0.7510 | 0.6183 | 0.8811 | 9.44 | GO | NO_GO |
| 12f | 0.8s | 10836 | 126 | 0.6406 | 0.2371 | 0.0255 | 0.7673 | 0.6320 | 0.9383 | 8.15 | GO | NO_GO |
| 15f | 1.0s | 10787 | 140 | 0.6443 | 0.2882 | 0.0064 | 0.7993 | 0.6308 | 0.9573 | 9.33 | GO | NO_GO |
| 18f | 1.2s | 10738 | 154 | 0.6530 | 0.2772 | 0.0065 | 0.8266 | 0.7076 | 0.9394 | 8.03 | GO | NO_GO |
| 24f | 1.6s | 10640 | 182 | 0.7068 | 0.2545 | 0.0065 | 0.8947 | 0.8986 | 0.9643 | 5.98 | GO | NO_GO |

## MotionBERT: 2s+ Windows
| window | seconds | train kept | boundary dropped | CV tempo | strict222455 tempo | strict 120 recall | devset@0.5 tempo | devset r80 | devset r120 | false/min | devset gate | score gate |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 30f | 2.0s | 10542 | 210 | 0.7149 | 0.2051 | 0.0000 | 0.9011 | 0.9452 | 0.9051 | 4.09 | GO | NO_GO |
| 45f | 3.0s | 10297 | 280 | 0.7545 | 0.3140 | 0.0068 | 0.9659 | 0.9065 | 1.0000 | 1.20 | GO | NO_GO |
| 60f | 4.0s | 10052 | 350 | 0.7389 | 0.3251 | 0.0071 | 0.9289 | 0.8429 | 1.0000 | 3.27 | GO | NO_GO |
| 90f | 6.0s | 9562 | 490 | 0.7466 | 0.2817 | 0.0000 | 0.9770 | 0.9964 | 0.9890 | 0.64 | GO | NO_GO |
| 120f | 8.0s | 9072 | 630 | 0.7111 | 0.2344 | 0.0000 | 0.9887 | 0.9810 | 0.9887 | 0.00 | GO | NO_GO |

## TCN Quick-Probe: Short Windows (<2s)
| window | seconds | train kept | boundary dropped | eval@0.5 samples | smoothed tempo | r80 | r100 | r120 | false/min | p90 delay | scope |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 9f | 0.6s | 2471 | 76 | 2471 | 0.9595 | 0.9568 | 0.9483 | 0.9696 | 27.72 | 0.80s | deployment_fit_quick_probe |
| 12f | 0.8s | 2446 | 76 | 2446 | 0.9571 | 0.9288 | 1.0000 | 0.9972 | 29.17 | 0.70s | deployment_fit_quick_probe |
| 15f | 1.0s | 2421 | 76 | 2421 | 0.9930 | 0.9916 | 0.9858 | 0.9986 | 6.66 | 0.30s | deployment_fit_quick_probe |
| 18f | 1.2s | 2396 | 76 | 2396 | 0.9975 | 0.9986 | 0.9892 | 0.9986 | 1.34 | 0.20s | deployment_fit_quick_probe |
| 24f | 1.6s | 2346 | 76 | 2346 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 | 0.00s | deployment_fit_quick_probe |

## TCN Quick-Probe: 2s+ Windows
| window | seconds | train kept | boundary dropped | eval@0.5 samples | smoothed tempo | r80 | r100 | r120 | false/min | p90 delay | scope |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 30f | 2.0s | 2296 | 76 | 2296 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 | 0.00s | deployment_fit_quick_probe |
| 45f | 3.0s | 2171 | 76 | 2171 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 | 0.00s | deployment_fit_quick_probe |
| 60f | 4.0s | 2046 | 76 | 2046 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 | 0.00s | deployment_fit_quick_probe |
| 90f | 6.0s | 1796 | 76 | 1796 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 | 0.00s | deployment_fit_quick_probe |
| 120f | 8.0s | 1546 | 76 | 1546 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 | 0.00s | deployment_fit_quick_probe |

## Candidate Selection
- Regular-window selection: NO_GO (0/5 GO candidates).
- Short-window selection: NO_GO (0/5 GO candidates).

## Artifact Roots
- motionbert_regular_train: `outputs/right_conducting/boundary0p5_5gpu_motionbert_train_run.json`
- motionbert_regular_devset: `outputs/right_conducting/boundary0p5_5gpu_motionbert_devset_run.json`
- motionbert_short_train: `outputs/right_conducting/boundary0p5_shortwin_5gpu_motionbert_train_run.json`
- motionbert_short_devset: `outputs/right_conducting/boundary0p5_shortwin_5gpu_motionbert_devset_run.json`
- tcn_regular_root: `outputs/right_conducting/tcn_boundary0p5_quick_probe_20260617`
- tcn_short_root: `outputs/right_conducting/tcn_boundary0p5_shortwin_quick_probe_20260617`

