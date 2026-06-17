# Boundary 0.5s Compact Table

- Policy: transition boundary uncertainty total 1.0s, implemented as +/-0.5s.
- `precision`, `recall`, and `f1 score` are tempo macro metrics from raw/offline predictions at margin 0.5s.
- `false/min` is smoothed false tempo switches per minute.
- TCN has no CV fold metric in quick-probe artifacts, so `CV tempo` and `CV gain` are `-`.
- TCN `devset@0.5` columns are quick-probe margin 0.5 eval values, not broader devset values.

## MotionBERT

| window | sec | CV tempo | CV gain | devset@0.5 tempo | devset@0.5 gain | precision | recall | f1 score | r80 | r120 | false/min |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 9f | 0.6 | 0.6166 | 0.9421 | 0.7510 | 0.9919 | 0.5433 | 0.5352 | 0.5375 | 0.6183 | 0.8811 | 9.44 |
| 12f | 0.8 | 0.6406 | 0.9541 | 0.7673 | 0.9979 | 0.5531 | 0.5324 | 0.5392 | 0.6320 | 0.9383 | 8.15 |
| 15f | 1.0 | 0.6443 | 0.9689 | 0.7993 | 0.9979 | 0.7713 | 0.7551 | 0.7580 | 0.6308 | 0.9573 | 9.33 |
| 18f | 1.2 | 0.6530 | 0.9804 | 0.8266 | 0.9986 | 0.6046 | 0.5961 | 0.5979 | 0.7076 | 0.9394 | 8.03 |
| 24f | 1.6 | 0.7068 | 0.9789 | 0.8947 | 0.9985 | 0.8748 | 0.8593 | 0.8659 | 0.8986 | 0.9643 | 5.98 |
| 30f | 2.0 | 0.7149 | 0.9907 | 0.9011 | 1.0000 | 0.6594 | 0.6677 | 0.6628 | 0.9452 | 0.9051 | 4.09 |
| 45f | 3.0 | 0.7545 | 0.9975 | 0.9659 | 1.0000 | 0.9562 | 0.9606 | 0.9571 | 0.9065 | 1.0000 | 1.20 |
| 60f | 4.0 | 0.7389 | 0.9974 | 0.9289 | 1.0000 | 0.9219 | 0.9101 | 0.9131 | 0.8429 | 1.0000 | 3.27 |
| 90f | 6.0 | 0.7466 | 0.9981 | 0.9770 | 1.0000 | 0.9714 | 0.9677 | 0.9691 | 0.9964 | 0.9890 | 0.64 |
| 120f | 8.0 | 0.7111 | 1.0000 | 0.9887 | 1.0000 | 0.9822 | 0.9899 | 0.9858 | 0.9810 | 0.9887 | 0.00 |

## TCN Quick-Probe

| window | sec | CV tempo | CV gain | devset@0.5 tempo | devset@0.5 gain | precision | recall | f1 score | r80 | r120 | false/min |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 9f | 0.6 | - | - | 0.9466 | 0.9996 | 0.9245 | 0.9430 | 0.9332 | 0.9479 | 0.9502 | 27.72 |
| 12f | 0.8 | - | - | 0.9501 | 0.9996 | 0.9131 | 0.9696 | 0.9373 | 0.9185 | 0.9972 | 29.17 |
| 15f | 1.0 | - | - | 0.9876 | 1.0000 | 0.9804 | 0.9866 | 0.9835 | 0.9854 | 0.9957 | 6.66 |
| 18f | 1.2 | - | - | 0.9979 | 1.0000 | 0.9986 | 0.9950 | 0.9968 | 0.9993 | 1.0000 | 1.34 |
| 24f | 1.6 | - | - | 0.9996 | 1.0000 | 0.9998 | 0.9995 | 0.9996 | 1.0000 | 0.9985 | 0.00 |
| 30f | 2.0 | - | - | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 |
| 45f | 3.0 | - | - | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 |
| 60f | 4.0 | - | - | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 |
| 90f | 6.0 | - | - | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 |
| 120f | 8.0 | - | - | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 |

## Column Guide

- `window`: prediction window size in frames.
- `sec`: approximate window length in seconds at 15 fps.
- `CV tempo`: cross-validation tempo accuracy.
- `CV gain`: cross-validation gain accuracy.
- `devset@0.5 tempo`: tempo accuracy after excluding transition +/-0.5s samples.
- `devset@0.5 gain`: gain accuracy after excluding transition +/-0.5s samples.
- `precision`: tempo macro precision at margin 0.5s.
- `recall`: tempo macro recall at margin 0.5s.
- `f1 score`: tempo macro F1 at margin 0.5s.
- `r80`: 80 BPM recall at margin 0.5s.
- `r120`: 120 BPM recall at margin 0.5s.
- `false/min`: smoothed false tempo switches per minute.
