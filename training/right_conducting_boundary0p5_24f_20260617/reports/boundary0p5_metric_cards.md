# Boundary 0.5s Metric Cards

All cards use the same fields. `precision`, `recall`, and `F1 score` are tempo macro metrics.

## Recommended Under-2s Cards

────────────────────────────────────────────────────────────────────────
   Model                 MotionBERT
   Window                24f
   Sec                   1.6
   Margin                0.5s
   Samples               1377
   CV tempo              0.7068
   CV gain               0.9789
   Eval tempo@0.5        0.8947
   Eval gain@0.5         0.9985
   Precision             0.8748
   Recall                0.8593
   F1 score              0.8659
   r80                   0.8986
   r120                  0.9643
   Smoothed false/min    5.98
   Scope                 MotionBERT: broader_devset

────────────────────────────────────────────────────────────────────────
   Model                 TCN quick-probe
   Window                24f
   Sec                   1.6
   Margin                0.5s
   Samples               2346
   CV tempo              -
   CV gain               -
   Eval tempo@0.5        0.9996
   Eval gain@0.5         1.0000
   Precision             0.9998
   Recall                0.9995
   F1 score              0.9996
   r80                   1.0000
   r120                  0.9985
   Smoothed false/min    0.00
   Scope                 TCN quick-probe: deployment_fit_quick_probe

## All Cards

────────────────────────────────────────────────────────────────────────
   Model                 MotionBERT
   Window                9f
   Sec                   0.6
   Margin                0.5s
   Samples               1482
   CV tempo              0.6166
   CV gain               0.9421
   Eval tempo@0.5        0.7510
   Eval gain@0.5         0.9919
   Precision             0.5433
   Recall                0.5352
   F1 score              0.5375
   r80                   0.6183
   r120                  0.8811
   Smoothed false/min    9.44
   Scope                 MotionBERT: broader_devset

────────────────────────────────────────────────────────────────────────
   Model                 MotionBERT
   Window                12f
   Sec                   0.8
   Margin                0.5s
   Samples               1461
   CV tempo              0.6406
   CV gain               0.9541
   Eval tempo@0.5        0.7673
   Eval gain@0.5         0.9979
   Precision             0.5531
   Recall                0.5324
   F1 score              0.5392
   r80                   0.6320
   r120                  0.9383
   Smoothed false/min    8.15
   Scope                 MotionBERT: broader_devset

────────────────────────────────────────────────────────────────────────
   Model                 MotionBERT
   Window                15f
   Sec                   1.0
   Margin                0.5s
   Samples               1440
   CV tempo              0.6443
   CV gain               0.9689
   Eval tempo@0.5        0.7993
   Eval gain@0.5         0.9979
   Precision             0.7713
   Recall                0.7551
   F1 score              0.7580
   r80                   0.6308
   r120                  0.9573
   Smoothed false/min    9.33
   Scope                 MotionBERT: broader_devset

────────────────────────────────────────────────────────────────────────
   Model                 MotionBERT
   Window                18f
   Sec                   1.2
   Margin                0.5s
   Samples               1419
   CV tempo              0.6530
   CV gain               0.9804
   Eval tempo@0.5        0.8266
   Eval gain@0.5         0.9986
   Precision             0.6046
   Recall                0.5961
   F1 score              0.5979
   r80                   0.7076
   r120                  0.9394
   Smoothed false/min    8.03
   Scope                 MotionBERT: broader_devset

────────────────────────────────────────────────────────────────────────
   Model                 MotionBERT
   Window                24f
   Sec                   1.6
   Margin                0.5s
   Samples               1377
   CV tempo              0.7068
   CV gain               0.9789
   Eval tempo@0.5        0.8947
   Eval gain@0.5         0.9985
   Precision             0.8748
   Recall                0.8593
   F1 score              0.8659
   r80                   0.8986
   r120                  0.9643
   Smoothed false/min    5.98
   Scope                 MotionBERT: broader_devset

────────────────────────────────────────────────────────────────────────
   Model                 MotionBERT
   Window                30f
   Sec                   2.0
   Margin                0.5s
   Samples               1335
   CV tempo              0.7149
   CV gain               0.9907
   Eval tempo@0.5        0.9011
   Eval gain@0.5         1.0000
   Precision             0.6594
   Recall                0.6677
   F1 score              0.6628
   r80                   0.9452
   r120                  0.9051
   Smoothed false/min    4.09
   Scope                 MotionBERT: broader_devset

────────────────────────────────────────────────────────────────────────
   Model                 MotionBERT
   Window                45f
   Sec                   3.0
   Margin                0.5s
   Samples               1230
   CV tempo              0.7545
   CV gain               0.9975
   Eval tempo@0.5        0.9659
   Eval gain@0.5         1.0000
   Precision             0.9562
   Recall                0.9606
   F1 score              0.9571
   r80                   0.9065
   r120                  1.0000
   Smoothed false/min    1.20
   Scope                 MotionBERT: broader_devset

────────────────────────────────────────────────────────────────────────
   Model                 MotionBERT
   Window                60f
   Sec                   4.0
   Margin                0.5s
   Samples               1125
   CV tempo              0.7389
   CV gain               0.9974
   Eval tempo@0.5        0.9289
   Eval gain@0.5         1.0000
   Precision             0.9219
   Recall                0.9101
   F1 score              0.9131
   r80                   0.8429
   r120                  1.0000
   Smoothed false/min    3.27
   Scope                 MotionBERT: broader_devset

────────────────────────────────────────────────────────────────────────
   Model                 MotionBERT
   Window                90f
   Sec                   6.0
   Margin                0.5s
   Samples               915
   CV tempo              0.7466
   CV gain               0.9981
   Eval tempo@0.5        0.9770
   Eval gain@0.5         1.0000
   Precision             0.9714
   Recall                0.9677
   F1 score              0.9691
   r80                   0.9964
   r120                  0.9890
   Smoothed false/min    0.64
   Scope                 MotionBERT: broader_devset

────────────────────────────────────────────────────────────────────────
   Model                 MotionBERT
   Window                120f
   Sec                   8.0
   Margin                0.5s
   Samples               705
   CV tempo              0.7111
   CV gain               1.0000
   Eval tempo@0.5        0.9887
   Eval gain@0.5         1.0000
   Precision             0.9822
   Recall                0.9899
   F1 score              0.9858
   r80                   0.9810
   r120                  0.9887
   Smoothed false/min    0.00
   Scope                 MotionBERT: broader_devset

────────────────────────────────────────────────────────────────────────
   Model                 TCN quick-probe
   Window                9f
   Sec                   0.6
   Margin                0.5s
   Samples               2471
   CV tempo              -
   CV gain               -
   Eval tempo@0.5        0.9466
   Eval gain@0.5         0.9996
   Precision             0.9245
   Recall                0.9430
   F1 score              0.9332
   r80                   0.9479
   r120                  0.9502
   Smoothed false/min    27.72
   Scope                 TCN quick-probe: deployment_fit_quick_probe

────────────────────────────────────────────────────────────────────────
   Model                 TCN quick-probe
   Window                12f
   Sec                   0.8
   Margin                0.5s
   Samples               2446
   CV tempo              -
   CV gain               -
   Eval tempo@0.5        0.9501
   Eval gain@0.5         0.9996
   Precision             0.9131
   Recall                0.9696
   F1 score              0.9373
   r80                   0.9185
   r120                  0.9972
   Smoothed false/min    29.17
   Scope                 TCN quick-probe: deployment_fit_quick_probe

────────────────────────────────────────────────────────────────────────
   Model                 TCN quick-probe
   Window                15f
   Sec                   1.0
   Margin                0.5s
   Samples               2421
   CV tempo              -
   CV gain               -
   Eval tempo@0.5        0.9876
   Eval gain@0.5         1.0000
   Precision             0.9804
   Recall                0.9866
   F1 score              0.9835
   r80                   0.9854
   r120                  0.9957
   Smoothed false/min    6.66
   Scope                 TCN quick-probe: deployment_fit_quick_probe

────────────────────────────────────────────────────────────────────────
   Model                 TCN quick-probe
   Window                18f
   Sec                   1.2
   Margin                0.5s
   Samples               2396
   CV tempo              -
   CV gain               -
   Eval tempo@0.5        0.9979
   Eval gain@0.5         1.0000
   Precision             0.9986
   Recall                0.9950
   F1 score              0.9968
   r80                   0.9993
   r120                  1.0000
   Smoothed false/min    1.34
   Scope                 TCN quick-probe: deployment_fit_quick_probe

────────────────────────────────────────────────────────────────────────
   Model                 TCN quick-probe
   Window                24f
   Sec                   1.6
   Margin                0.5s
   Samples               2346
   CV tempo              -
   CV gain               -
   Eval tempo@0.5        0.9996
   Eval gain@0.5         1.0000
   Precision             0.9998
   Recall                0.9995
   F1 score              0.9996
   r80                   1.0000
   r120                  0.9985
   Smoothed false/min    0.00
   Scope                 TCN quick-probe: deployment_fit_quick_probe

────────────────────────────────────────────────────────────────────────
   Model                 TCN quick-probe
   Window                30f
   Sec                   2.0
   Margin                0.5s
   Samples               2296
   CV tempo              -
   CV gain               -
   Eval tempo@0.5        1.0000
   Eval gain@0.5         1.0000
   Precision             1.0000
   Recall                1.0000
   F1 score              1.0000
   r80                   1.0000
   r120                  1.0000
   Smoothed false/min    0.00
   Scope                 TCN quick-probe: deployment_fit_quick_probe

────────────────────────────────────────────────────────────────────────
   Model                 TCN quick-probe
   Window                45f
   Sec                   3.0
   Margin                0.5s
   Samples               2171
   CV tempo              -
   CV gain               -
   Eval tempo@0.5        1.0000
   Eval gain@0.5         1.0000
   Precision             1.0000
   Recall                1.0000
   F1 score              1.0000
   r80                   1.0000
   r120                  1.0000
   Smoothed false/min    0.00
   Scope                 TCN quick-probe: deployment_fit_quick_probe

────────────────────────────────────────────────────────────────────────
   Model                 TCN quick-probe
   Window                60f
   Sec                   4.0
   Margin                0.5s
   Samples               2046
   CV tempo              -
   CV gain               -
   Eval tempo@0.5        1.0000
   Eval gain@0.5         1.0000
   Precision             1.0000
   Recall                1.0000
   F1 score              1.0000
   r80                   1.0000
   r120                  1.0000
   Smoothed false/min    0.00
   Scope                 TCN quick-probe: deployment_fit_quick_probe

────────────────────────────────────────────────────────────────────────
   Model                 TCN quick-probe
   Window                90f
   Sec                   6.0
   Margin                0.5s
   Samples               1796
   CV tempo              -
   CV gain               -
   Eval tempo@0.5        1.0000
   Eval gain@0.5         1.0000
   Precision             1.0000
   Recall                1.0000
   F1 score              1.0000
   r80                   1.0000
   r120                  1.0000
   Smoothed false/min    0.00
   Scope                 TCN quick-probe: deployment_fit_quick_probe

────────────────────────────────────────────────────────────────────────
   Model                 TCN quick-probe
   Window                120f
   Sec                   8.0
   Margin                0.5s
   Samples               1546
   CV tempo              -
   CV gain               -
   Eval tempo@0.5        1.0000
   Eval gain@0.5         1.0000
   Precision             1.0000
   Recall                1.0000
   F1 score              1.0000
   r80                   1.0000
   r120                  1.0000
   Smoothed false/min    0.00
   Scope                 TCN quick-probe: deployment_fit_quick_probe
