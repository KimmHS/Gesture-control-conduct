# Right Conducting Boundary0p5 24f Model Bundle

Policy: 24f / 1.6s trailing window, stride 3f / 0.2s, transition boundary margin +/-0.5s.

## MotionBERT

- Head: `motionbert_24f/all_train_head.pt`
- Backbone config: `motionbert_24f/MB_lite.yaml`
- Backbone checkpoint: `motionbert_24f/mb_lite_v0.pt`
- Feature mode: `mean_std_delta`
- Input mask mode: `as_is`

## TCN

- Checkpoint: `tcn_24f/tcn_conducting_head.pt`
- Includes model state, input mean/std, and config.

## Reports

- `reports/boundary0p5_compact_table.md`
- `reports/boundary0p5_metric_cards.md`
- `reports/augmentation_delay_smoothing_summary.md`
- `reports/boundary0p5_all_windows_tcn_motionbert_summary.md`
