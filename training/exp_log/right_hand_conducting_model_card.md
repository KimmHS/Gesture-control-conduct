# Right-Hand Conducting Model Card

이 파일은 current selected live model과 이전 MotionBERT comparison 상태를 기록한다.

## Current Selected Model

```text
bundle_name: selected_tcn_handmark_live45f
manifest_model_name: tcn_right_conducting_live
model_type: causal_tcn_right_arm_pose
status: LIVE_READY_STRICT_HELDOUT_PENDING
live_status: GO
strict_heldout_status: NO_GO
selected_use: fixed-camera handmark CSV/stdin live tempo/gain classifier
```

Current selected live model is TCN, not MotionBERT. MotionBERT-Lite experiments remain documented below as historical comparison and fallback research context.

## Selected TCN Artifacts

```text
bundle: outputs/right_conducting/selected_tcn_handmark_live45f
manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
structure: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_structure.md
checkpoint: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_head.pt
release_manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json
release_validation: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_fulltest_latest.json
current_status_snapshot: outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.json
```

## Selected TCN Structure

```text
input: raw handmark CSV/stdin
pose window: [B, 45, 17, 3]
runtime tensor: [B, 9, 45]
right_arm_indices: [14, 15, 16]
fps: 15
stride_frames: 3
update_interval: about 0.2s
cold_start: about 3.0s
tempo_classes: 4
tempo_bins: 60 / 80 / 100 / 120
gain_classes: small / large
gain_mapping: small=0.25, large=0.85
architecture: ConductingTCN
input_channels: 9
hidden_channels: 64
levels: 4
kernel_size: 5
dropout: 0.1
trainable_parameter_count: 147910
loss_terms: CE tempo + 0.5 CE gain
normalization: checkpoint input_mean/input_std, shape [1, 9, 1]
```

## Selected TCN Runtime

Primary file/CSV mode:

```bash
python tools/run_tcn_handmark_csv_stream.py \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --handmark-csv <input.csv> \
  --output-jsonl <live_outputs.jsonl> \
  --flush-each-output
```

Pipe/stdin mode:

```bash
python your_handmark_producer.py | python tools/run_tcn_handmark_csv_stream.py \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --handmark-csv - \
  --output-jsonl - \
  --flush-each-output
```

Current status snapshot:

```bash
python tools/run_right_conducting_goal.py --steps tcn-current-status
```

Strict post-arrival final chain:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh
```

## Selected TCN Score

Latest supplied-set rerun:

```text
report: docs/exp/goal_reports/2026-06-17_117_full_test_release_and_status_rerun.md
score: outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.json
gate: outputs/right_conducting/tcn_alltest_latest/stream_set_gate_fulltest_latest.json
readiness: outputs/right_conducting/tcn_alltest_latest/stream_readiness.json
benchmark: outputs/right_conducting/tcn_alltest_latest/stream_benchmark.json
goal_status: outputs/right_conducting/tcn_alltest_latest/tcn_goal_status_fulltest_latest.json
current_status: outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.json
```

Selected 3s transition-margin row:

```text
csv_count: 15 discovered raw CSV files
eval_session_count: 11 scoreable processed sessions
beat4: excluded
stable_only: true
sample_count: 1824
tempo_acc: 1.0000
gain_acc: 1.0000
tempo_80_recall: 1.0000
tempo_100_recall: 1.0000
tempo_120_recall: 1.0000
bpm_mae_window: 0.0000
false_switches_per_min: 0.0000
missed_switch_count: 0
switch_delay_p90_s: 0.0000
benchmark_p90_ms: 1.9984
benchmark_headroom_ratio: 100.0821
stream_output_contract_errors: 0
stdin_output_contract_errors: 0
```

## Selected TCN Limitations

```text
This score is deployment-fit evidence on current fixed-camera supplied data.
It is not strict independent heldout evidence.
Strict heldout roots are still missing:
  dataset/strict_heldout_static_v1
  dataset/strict_heldout_transitions_v1
Current strict P0 coverage: 8 required / 0 present / 8 missing.
Final completion requires scripts/run_tcn_strict_post_arrival_goal.sh to pass after those roots are supplied.
```

## Historical MotionBERT Context

The sections below document the earlier MotionBERT-Lite plan, sweeps, and failure analysis. They are retained for traceability but are not the current selected live model.

## Required Fields

```text
model_name
checkpoint_path
motionbert_config
motionbert_checkpoint
backbone_frozen
head_architecture
trainable_parameter_count
window_frames
stride_frames
normalization
right_arm_indices
context_indices
loss_terms
augmentation_policy
streaming_policy
gain_mapping
known_limitations
```

## Current Required Notes

```text
Current workspace dataset is small and likely single-subject.
Current v0 data is about 15fps.
Current v0 tempo bins are 60/80/100/120 only.
120 frames on current v0 data is about 8s, not 4s.
Cross-subject generalization is not proven unless multi-person data is collected.
dataset/evaluation_transitions/session_20260616_215630_bpm100_beat4_large is excluded until relabeled.
```

## Latest Candidate Status

Report:

```text
docs/exp/goal_reports/2026-06-17_59_extended_5gpu_hparam_sweep.md
```

Latest score artifacts:

```text
outputs/right_conducting/hparam_sweep_static80_transitions_extended_20260617.json
outputs/right_conducting/hparam_sweep_static80_transitions_extended_20260617.md
outputs/right_conducting/model_candidate_selection_ext_live45f.json
```

Current decision:

```text
selected final deep model: selected for fixed-camera live pilot
selected MotionBERT replacement: GO
primary live candidate: ext_e240_h512_lr3e3_s0_45f
conservative 60f candidate: ext_e240_h512_lr3e3_s0_60f
previous selected_motionbert_static80_transitions_live45f is superseded for fixed-camera dev/live pilot.
```

TCN comparison probe:

```text
report: docs/exp/goal_reports/2026-06-17_79_tcn_quick_probe.md
handmark_stream_report: docs/exp/goal_reports/2026-06-17_80_tcn_handmark_live_stream.md
handmark_stream_readiness_report: docs/exp/goal_reports/2026-06-17_81_tcn_handmark_stream_readiness_gate.md
folder: outputs/right_conducting/tcn_quick_probe_20260617
practical_tcn_candidate: outputs/right_conducting/tcn_quick_probe_20260617/45f
model: causal residual Conv1d TCN
checkpoint: outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_conducting_head.pt
live_manifest: outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_live_manifest.json
handmark_stream_set_score: outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_score.json
handmark_stream_set_gate: outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_gate.json
handmark_stream_single_summary: outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_summary.json
handmark_stream_latency_benchmark: outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_benchmark.json
handmark_stream_readiness: outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_handmark_stream_readiness.json
window_frames: 45
score_scope: deployment-fit quick probe
margin3_smoothed_tempo_acc: 1.0000
margin3_smoothed_gain_acc: 1.0000
margin3_false_switches_per_min: 0.0000
handmark_stream_update_p90_ms: 1.6180
handmark_stream_update_budget_ms: 200.0000
selected_status: comparison/fallback only
replacement_decision: not replacing MotionBERT without a strict heldout split
```

Primary export:

```text
manifest: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_manifest.json
structure: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_structure.md
head_checkpoint: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_head.pt
full_backbone_smoke: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/smoke_full_backbone.json
static_replay: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_static80_stable.json
transition_replay: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_transitions_stable.json
static_replay_diagnosis: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_static80_stable_failure_diagnosis.json
transition_replay_diagnosis: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_transitions_stable_failure_diagnosis.json
benchmark: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/benchmark_transitions_stable.json
deployment_live_gate: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_replay_gate_transitions_deployment.json
live_runtime_readiness: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.json
live_output_contract: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_output_contract.json
live_output_sample: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_output_sample.json
live_output_static80_replay: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_outputs_static80_stable.jsonl
live_output_transition_replay: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_outputs_transitions_stable.jsonl
pose_stream_static80: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/pose_stream_static80_035040_summary.json
pose_stream_transition: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/pose_stream_transition_022517_summary.json
online_pose_stream_static80: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/online_pose_stream_static80_035040_summary.json
online_pose_stream_transition: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/online_pose_stream_transition_022517_summary.json
online_pose_stream_comparison: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/online_pose_stream_comparison.json
jsonl_pose_stream_static80: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/jsonl_stream_static80_035040_summary.json
jsonl_pose_stream_transition: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/jsonl_stream_transition_022415_summary.json
handmark_csv_stream_static80_ref: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/handmark_csv_ref_stream_static80_035040_summary.json
handmark_csv_stream_transition_ref: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/handmark_csv_ref_stream_transition_022415_summary.json
handmark_csv_stream_transition_right_arm_only_diagnostic: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/handmark_csv_stream_transition_022415_summary.json
pose_quality_static80: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/degraded_online_pose_stream_static80_035040_summary.json
pose_quality_transition: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/degraded_online_pose_stream_transition_022517_summary.json
goal_status: outputs/right_conducting/goal_status_selected_motionbert_live45f_ext.json
goal_status_md: outputs/right_conducting/goal_status_selected_motionbert_live45f_ext.md
```

Primary score on `dataset/transitions` after a 3s transition margin:

```text
window_frames: 45
window_seconds: about 3.0s at 15fps
epochs: 240
hidden_dim: 512
lr: 0.003
dropout: 0.1
weight_decay: 0.001
seed: 0
tempo_acc: 0.9989
bpm_mae_window: 0.0226
gain_acc: 1.0000
tempo_80_recall: 0.9953
tempo_100_recall: 1.0000
tempo_120_recall: 1.0000
smoothed_false_switches_per_min: 0.0000
smoothed_switch_delay_p90_s: 0.0000
status: GO
```

Full-backbone live replay:

```text
static80 smoothed tempo_acc: 1.0000
static80 smoothed gain_acc: 1.0000
static80 false_switches_per_min: 0.0000
static80 missed_switch_count: 0
transition smoothed tempo_acc: 1.0000
transition smoothed gain_acc: 1.0000
transition false_switches_per_min: 0.0000
transition missed_switch_count: 0
transition switch_delay_p90_s: 0.0000
deployment-fit replay diagnosis: no smoothed tempo error runs on static80 or transitions
current eval replay diagnosis: outputs/right_conducting/current_eval_roots_replay_failure_diagnosis_ext_chain.json
current eval interpretation: independent stress/scope replay fails and must not be used as a GO claim
```

Full-backbone benchmark:

```text
device: cuda:3
benchmark_windows: 1305
update_interval_ms: 200.0000
end_to_end_p90_ms: 11.6339
end_to_end_max_ms: 19.5126
headroom_ratio: 17.1911
status: PASS
```

Live runtime readiness:

```text
status: GO
contract: GO
deployment gate: GO
benchmark: GO
live output replay: GO
online pose stream: GO
JSONL pose stream: GO
handmark CSV stream: GO with reference joints
pose quality gate: GO
artifact: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.md
```

Label-free pose stream evidence:

```text
static80 high-arm small: 236 rows, tempo classes [1], smoothed tempo switches 0
transition 022517 beat3 small: 216 rows, tempo classes [1, 3], raw switches 9 -> smoothed switches 2
input: pose_right_h36m_masked.npy only, no labels_frame.jsonl
```

Online frame-buffer evidence:

```text
mode: online_buffer
static80 high-arm small: 236 rows, tempo classes [1], smoothed tempo switches 0
transition 022517 beat3 small: 216 rows, tempo classes [1, 3], raw switches 9 -> smoothed switches 2
window-scan vs online-buffer comparison: PASS, ignoring only source.source_id
cold start: 45 frames ~= 3.0s at 15fps
update interval: 3 frames ~= 0.2s at 15fps
```

JSONL/stdin frame-stream evidence:

```text
tool: tools/run_motionbert_pose_jsonl_stream.py
stdin mode: --pose-jsonl - --output-jsonl - --flush-each-output
static80 high-arm small: 750 input frames, 236 rows, tempo classes [1], smoothed tempo switches 0
transition 022415 beat2 small: 690 input frames, 216 rows, tempo classes [1, 3], smoothed tempo switches 2
input format: jsonl_h36m17_frame_stream
runtime mode: jsonl_online
```

Handmark CSV/stdin stream evidence:

```text
tool: tools/run_motionbert_handmark_csv_stream.py
stdin mode: --handmark-csv - --output-jsonl - --flush-each-output
required for deployment-equivalent MotionBERT input: reference joints 8/9/11, either in CSV columns or supplied by full pose tracker
static80 CSV + reference: 750 input frames, 236 rows, tempo classes [1], smoothed tempo switches 0
transition CSV + reference: 690 input frames, 216 rows, tempo classes [1, 3], smoothed tempo switches 2
right-arm-only CSV transition diagnostic: tempo classes [0, 2, 3], smoothed tempo switches 4
interpretation: right-arm-only CSV is executable but not stable enough for transition control claim
```

Right-arm-only handmark-only probe:

```text
report: docs/exp/goal_reports/2026-06-17_74_right_arm_only_input_mask_probe.md
manifest: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/motionbert_conducting_live_manifest.json
structure: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/motionbert_conducting_live_structure.md
head_checkpoint: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/motionbert_conducting_head.pt
input_mask_mode: right_arm_only
window_frames: 45
status: fixed-camera deployment-fit probe, not strict heldout replacement
deployment-fit smoothed tempo_acc: 0.9951
deployment-fit smoothed gain_acc: 1.0000
deployment-fit false_switches_per_min: 0.3681
deployment-fit p90 delay: 0.2734s
raw handmark static80 035040: 236 rows, tempo classes [1], smoothed switches 0
raw handmark transition 022415: 216 rows, tempo classes [1, 3], smoothed switches 2
raw handmark full CSV set score: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.json
raw handmark full CSV set report: docs/exp/goal_reports/2026-06-17_75_raw_handmark_csv_stream_set_score.md
raw handmark full CSV set gate: outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.json
raw handmark full CSV set gate report: docs/exp/goal_reports/2026-06-17_76_handmark_csv_stream_set_gate.md
raw handmark full CSV set goal runner: docs/exp/goal_reports/2026-06-17_77_goal_runner_handmark_csv_set_gate.md
raw handmark full CSV set goal dry-run: outputs/right_conducting/right_conducting_goal_handmark_csv_set_gate_dryrun.md
raw handmark full CSV set gate status: GO
raw handmark margin0 smoothed tempo_acc: 0.9955
raw handmark margin0 false_switches_per_min: 0.3689
raw handmark margin3 smoothed tempo_acc: 0.9989
raw handmark margin3 gain_acc: 1.0000
raw handmark margin3 r80/r100/r120: 0.9983 / 1.0000 / 1.0000
raw handmark margin3 false_switches_per_min: 0.1230
raw handmark margin3 missed_switch_count: 0
old 222455 stress: still NO_GO, 120 BPM recall almost zero
use case: only right shoulder / elbow / wrist are available and camera/distance/meter scope match the 2/3-beat fixed-camera setup
```

Pose quality gate:

```text
right_arm_indices: [14, 15, 16]
min_valid_right_arm_ratio: 0.8
right_arm_confidence_threshold: 0.0
invalid behavior: hold previous live output and set state.valid=false
degraded static80: 236 rows, invalid 28, held 28, tempo switches 0
degraded transition 022517: 216 rows, invalid 28, held 28, smoothed tempo switches 2
```

Strict heldout independence:

```text
available independent heldout status: GO for dataset/evaluation,dataset/evaluation_transitions
strict heldout scope audit: NO_GO
P0 in-scope heldout coverage: 0 / 8
strict live gate on 222455: NO_GO
goal status: IN_PROGRESS because strict_heldout_scope_go and strict_live_gate_go are both false
current eval strict chain: outputs/right_conducting/goal_status_current_eval_roots_ext_chain.json
current eval failure diagnosis: outputs/right_conducting/current_eval_roots_replay_failure_diagnosis_ext_chain.json
strict heldout missing checklist: outputs/right_conducting/current_eval_roots_strict_missing_checklist.md
strict heldout preflight gate: outputs/right_conducting/current_eval_roots_strict_preflight.md
strict heldout preflight status: NO_GO because independence is GO but strict scope is NO_GO and P0 coverage is 0/8.
current eval strict tempo_acc: 0.1691
current eval strict gain_acc: 0.9412
current eval strict false_switches_per_min: 5.7848
current eval diagnosis: 215630 true tempo is constant 100 but predicted 80 for 270/286 rows; 222455 120 BPM segment has 0 smoothed recall.
tempo_acc: 0.2946
gain_acc: 0.8760
false_switches_per_min: 10.5151
missed_switch_count: 1
interpretation: 222455 is a 4-beat/mixed-timeline stress session and fails; static80/transitions dev scores are deployment-fit, not broad heldout generalization.
next: record a 2/3-beat fixed-camera heldout transition root outside the staged training manifest, or intentionally add 4-beat support to training/dev.
```

Model-card implication:

```text
Current fixed-camera live pilot should use the exported 45f ext MotionBERT bundle.
The 60f ext candidate is the conservative accuracy top, but it uses about 4 seconds of context.
For the live-change goal, 45f is preferred because it uses about 3 seconds of context and still reaches zero smoothed false switches.
```

## Previous Candidate Status

Report:

```text
docs/exp/goal_reports/2026-06-17_47_static80_transition_5gpu_hparam_sweep.md
```

Latest score artifacts:

```text
outputs/right_conducting/hparam_sweep_static80_transitions_20260617.json
outputs/right_conducting/hparam_sweep_static80_transitions_20260617.md
```

Current decision:

```text
selected final deep model: selected for fixed-camera live pilot
selected MotionBERT replacement: GO
primary live candidate: static80_transitions_e120_h512_lr3e3_45f
conservative fallback candidate: static80_transitions_e160_h512_lr1e3_60f
```

Primary export:

```text
manifest: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json
structure: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_structure.md
head_checkpoint: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_head.pt
smoke: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/smoke_head_only.json
static_replay: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_static80_stable.json
transition_replay: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_transitions_stable.json
benchmark: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/benchmark_transitions_stable.json
policy_sweep: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/policy_sweep_transitions_stable.json
heldout_independence: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/heldout_independence_static80_transitions.json
deployment_live_gate: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_replay_gate_transitions_deployment.json
strict_live_gate: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_replay_gate_transitions_strict.json
live_output_contract: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_output_contract.json
live_output_sample: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_output_sample.json
live_output_static80_replay: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_outputs_static80_stable.jsonl
live_output_transition_replay: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_outputs_transitions_stable.jsonl
pose_stream_static80: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/pose_stream_static80_035040_summary.json
pose_stream_transition: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/pose_stream_transition_022517_summary.json
online_pose_stream_static80: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_static80_035040_summary.json
online_pose_stream_transition: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_transition_022517_summary.json
online_pose_stream_comparison: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_comparison.json
pose_quality_static80: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/degraded_online_pose_stream_static80_035040_summary.json
pose_quality_transition: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/degraded_online_pose_stream_transition_022517_summary.json
goal_status: outputs/right_conducting/goal_status_selected_motionbert_live45f.json
```

Primary score on `dataset/transitions` after a 3s transition margin:

```text
window_frames: 45
window_seconds: about 3.0s at 15fps
tempo_acc: 0.9943
bpm_mae_window: 0.1131
gain_acc: 1.0000
tempo_80_recall: 0.9810
tempo_100_recall: 0.9948
tempo_120_recall: 1.0000
smoothed_false_switches_per_min: 0.1993 before live policy sweep
smoothed_switch_delay_p90_s: 0.0000
status: GO
```

Selected live policy after replay sweep:

```text
switch_threshold: 0.72
fast_switch_threshold: 0.90
confirm_updates: 2
transition smoothed false_switches_per_min: 0.0000
transition smoothed switch_delay_p90_s: 0.5938
```

Full-backbone live replay:

```text
static80 smoothed tempo_acc: 1.0000
static80 smoothed gain_acc: 1.0000
static80 false_switches_per_min: 0.0000
static80 missed_switch_count: 0
transition smoothed tempo_acc: 0.9893
transition smoothed gain_acc: 1.0000
transition false_switches_per_min: 0.0000
transition missed_switch_count: 0
transition weak edge: session_20260617_022517_bpm120to120_beat3_small has the largest remaining delay, not a false switch.
```

Full-backbone benchmark:

```text
device: cuda:2
benchmark_windows: 1305
update_interval_ms: 200.0000
end_to_end_p90_ms: 12.1389
end_to_end_max_ms: 16.0964
headroom_ratio: 16.4759
status: PASS
```

Strict heldout independence:

```text
status: NO_GO
train_session_count: 35
heldout_session_count: 11
root_conflict_count: 2
path_overlap_count: 11
name_overlap_count: 11
interpretation: static80/transitions scores are deployment-fit, not independent heldout generalization.
```

Live replay gate:

```text
deployment-fit live gate: GO
strict heldout live gate: NO_GO
strict failure reason: heldout_independence_status is NO_GO
live thresholds: tempo_acc >= 0.85, gain_acc >= 0.90, false_switches_per_min <= 0.50,
                missed_switch_count <= 0, switch_delay_p90_s <= 1.00
```

Live output contract:

```text
schema_version: right_conducting_live_output_v1
tempo_bpm: smoothed bpm
velocity_scale: smoothed dynamics mapped to 0.35..1.00
cc11_expression: smoothed dynamics mapped to 32..127
cc7_volume: null
mapping source: demo-safe default, not calibration-derived
```

Live output replay adapter:

```text
static80 stable live output rows: 942
transition stable live output rows: 1305
static80 output tempo classes: [1]
transition output tempo classes: [1, 2, 3]
format: JSONL, one right_conducting_live_output_v1 payload per stream update
```

Label-free pose stream evidence:

```text
static80 high-arm small: 236 rows, tempo classes [1], smoothed tempo switches 0
transition 022517 beat3 small: 216 rows, tempo classes [1, 3], raw switches 6 -> smoothed switches 2
input: pose_right_h36m_masked.npy only, no labels_frame.jsonl
```

Online frame-buffer evidence:

```text
mode: online_buffer
static80 high-arm small: 236 rows, tempo classes [1], smoothed tempo switches 0
transition 022517 beat3 small: 216 rows, tempo classes [1, 3], raw switches 6 -> smoothed switches 2
window-scan vs online-buffer comparison: PASS, ignoring only source.source_id
cold start: 45 frames ~= 3.0s at 15fps
update interval: 3 frames ~= 0.2s at 15fps
```

Pose quality gate:

```text
right_arm_indices: [14, 15, 16]
min_valid_right_arm_ratio: 0.8
right_arm_confidence_threshold: 0.0
invalid behavior: hold previous live output and set state.valid=false
degraded static80: 236 rows, invalid 28, held 28, tempo switches 0
degraded transition 022517: 216 rows, invalid 28, held 28, smoothed tempo switches 2
```

Goal status dashboard:

```text
status: IN_PROGRESS
live_pilot_status: GO
strict_heldout_status: NO_GO
reason: strict heldout independence and strict live replay gate are still NO_GO.
```

Model-card implication:

```text
Current fixed-camera live pilot can use the exported 45f MotionBERT bundle.
60f baseline remains a conservative fallback, but the selected 45f bundle also has zero smoothed false switches after policy sweep.
120f rows are not selected as live primary because current v0 data is about 15fps, so 120 frames is about 8 seconds.
For independent generalization claims, record a new transition heldout set and keep it out of training.
```

Selection/export guard:

```text
MotionBERT selected replacement requires:
  regular score gate: GO
  fixed-camera devset gate: GO

If devset gate is NO_GO, select_right_conducting_model_candidate.py returns NO_GO
when --require-devset-gate is enabled, and export remains blocked.
```

Reference:

```text
docs/exp/goal_reports/2026-06-17_40_devset_gated_selection_guard.md
```

Path note:

```text
Historical sections below may still use the old short names session_20260616_222455_eval
and session_20260616_215630_eval. Current authoritative paths are:
dataset/evaluation/session_20260616_222455_bpm120_beat4_large
dataset/evaluation_transitions/session_20260616_215630_bpm100_beat4_large
```

## New Dataset Gate

Before replacing any selected artifact with a model trained on the supplied dataset, run:

```bash
python tools/audit_right_conducting_dataset_intake.py \
  --train-roots dataset/recordings \
  --eval-roots dataset/evaluation,dataset/evaluation_transitions,dataset/transitions \
  --output-json outputs/right_conducting/dataset_intake_after_transitions_schedule.json \
  --output-md outputs/right_conducting/dataset_intake_after_transitions_schedule.md
```

Current intake artifact:

```text
outputs/right_conducting/dataset_intake_after_transitions_schedule.json
outputs/right_conducting/dataset_intake_after_transitions_schedule.md
```

Then stage train roots into the zip format expected by current prepare/cache/train tools:

```bash
python tools/build_right_conducting_recordings_zip.py \
  --train-roots dataset/recordings,NEW_TRAIN_ROOT \
  --output-zip outputs/right_conducting/recordings_staged_after_supply.zip \
  --output-json outputs/right_conducting/recordings_staged_after_supply_manifest.json
```

Current staging smoke artifact:

```text
outputs/right_conducting/recordings_staged_current.zip
outputs/right_conducting/dataset_v0_60f_staged_current/manifest.json
```

Goal runner for supplied data:

```text
docs/exp/goal_reports/2026-06-17_29_after_supply_goal_runner.md
docs/exp/goal_reports/2026-06-17_30_after_supply_cache_train_runner.md
docs/exp/goal_reports/2026-06-17_31_model_score_gate.md
docs/exp/goal_reports/2026-06-17_32_after_supply_detailed_eval_gate_runner.md
docs/exp/goal_reports/2026-06-17_33_after_supply_5gpu_frame_sweep_runner.md
docs/exp/goal_reports/2026-06-17_34_after_supply_model_selection_runner.md
docs/exp/goal_reports/2026-06-17_35_motionbert_selected_export_bundle.md
docs/exp/goal_reports/2026-06-17_36_motionbert_live_bundle_smoke.md
docs/exp/goal_reports/2026-06-17_37_motionbert_live_bundle_replay.md
```

After-supply MotionBERT output targets:

```text
default cache: outputs/right_conducting/motionbert_cache_after_supply_60f/
default head: outputs/right_conducting/motionbert_head_after_supply_60f/
5-GPU sweep candidates: 30f / 60f / 90f / 120f / 150f
```

These are command targets, not selected final artifacts, until `scores.json` passes the heldout transition gate.

Selection gate:

```text
The selected final deep model must pass outputs/right_conducting/model_gate_after_supply_60f.json.
Default thresholds: cv_tempo_acc >= 0.70, transition_tempo_acc >= 0.60,
bpm_mae_window <= 10.0, gain_acc >= 0.80, tempo_80/120 recall >= 0.50.
For frame sweeps, outputs/right_conducting/model_candidate_selection_after_supply.json
must be SELECTED before any selected live artifact replacement.
If selected, MotionBERT live bundle target is:
outputs/right_conducting/selected_motionbert_after_supply/
Live smoke target:
outputs/right_conducting/motionbert_selected_live_smoke_after_supply.json
Live replay target:
outputs/right_conducting/motionbert_selected_live_replay_after_supply.json
```

Current baseline intake status:

```text
train_ready_count: 24
eval_scoreable_count: 11
eval_pending_relabel_count: 1
```

Model-card implication:

```text
The selected live fallback remains temporary because the supplied transition stress set
was registered and evaluated, but no MotionBERT candidate passed the heldout transition gate.
```

## Gain / Dynamics Mapping

Final model output:

```text
dynamics: continuous 0.0 ~ 1.0
```

MIDI mapping must record:

```text
velocity_scale_min
velocity_scale_max
CC11 expression_min
CC11 expression_max
calibration source or demo default source
```

If a baseline uses `small/large` classes, record the mapping values and state whether they are calibration-derived or demo defaults.

## Current Candidate Status

```text
selected final deep model: not selected yet
selected live fallback model: feature_baseline_live_v0
current best CV model: MotionBERT-Lite frozen + mean_std_delta cached head
current best transition tempo fallback: handcrafted_feature_ml
```

Current MotionBERT candidate:

```text
backbone_config: checkpoint/MB_lite.yaml
backbone_checkpoint: checkpoint/mb_lite_v0.pt
backbone_frozen: true
feature_mode: mean_std_delta
feature_dim: 2048
head_checkpoint: outputs/right_conducting/motionbert_head_v0_60f_stats_e80_h512/all_train_head.pt
train_window: 60 frames ~= 4s at current ~15fps
eval_transition_window: 120 frames ~= 8s from existing labels_window
```

Current scores:

```text
stats head cv_mean tempo_acc: 0.7178
stats head transition_eval_222455 120f tempo_acc: 0.2443
stats head transition_eval_222455_60f_stable tempo_acc: 0.3128
feature_baseline transition_eval_222455_60f_stable tempo_acc: 0.5514
```

Decision:

```text
Do not export the stats MotionBERT head as final live model yet.
Use handcrafted_feature_ml as fallback for transition tempo until heldout stability improves.
```

## Selected Live Fallback Export

```text
artifact: outputs/right_conducting/selected/feature_baseline_live_v0.json
structure: outputs/right_conducting/selected/feature_baseline_live_v0_structure.md
manifest: outputs/right_conducting/selected/selected_model_manifest.json
```

Fallback structure:

```text
pose window [60, 17, 3]
  -> 16 handcrafted right-arm motion features
  -> nearest-centroid tempo classifier
  -> nearest-centroid gain classifier
  -> LiveSmoother EMA + confidence hold + confirm switch
```

Fallback score:

```text
eval_set: transition_eval_222455_60f_stable
tempo_acc: 0.5514
bpm_mae_window: 10.6173
gain_acc: 0.7654
dynamics_mae_window: 0.1407
```

Streaming replay policy:

```text
switch_threshold: 0.15
fast_switch_threshold: 0.40
confirm_updates: 2
bpm_ema_alpha: 0.15
dynamics_ema_alpha: 0.10
```

Streaming replay score:

```text
artifact: outputs/right_conducting/stream_replay_222455_60f_tuned.json
raw tempo_acc: 0.4982
raw false_switches_per_min: 17.1243
smoothed tempo_acc: 0.4698
smoothed false_switches_per_min: 4.2811
smoothed switch_delay_mean_s: 7.6037
```

Replay delay diagnosis:

```text
artifact: outputs/right_conducting/stream_replay_222455_60f_tuned_analysis.json
true tempo switches: 2
raw reached: 1
raw missed: 1
100 -> 120 BPM raw delay: 6.6031s
100 -> 120 BPM smoothed delay: 7.6037s
smoothing extra delay: 1.0006s
120 -> 80 BPM: raw target not reached
```

Decision:

```text
Do not tune only the smoother next.
The raw classifier/fallback must improve switch detection first.
```

## Reproducible Goal Command

Current verified goal command:

```bash
bash scripts/run_right_conducting_goal.sh \
  --steps audit,eval,replay,analyze \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --window-frames 60 \
  --stride-frames 3 \
  --normalizations camera \
  --artifact outputs/right_conducting/selected/feature_baseline_live_v0.json \
  --switch-threshold 0.15 \
  --fast-switch-threshold 0.40 \
  --confirm-updates 2 \
  --output-json outputs/right_conducting/right_conducting_goal_run_222455_60f.json \
  --output-md outputs/right_conducting/right_conducting_goal_run_222455_60f.md
```

Run artifact:

```text
outputs/right_conducting/right_conducting_goal_run_222455_60f.json
```

Status:

```text
audit/eval/replay/analyze: GO
120 -> 80 robust live control: still NO-GO
```

## 30f Latency Probe

30f candidate artifacts:

```text
dataset: outputs/right_conducting/dataset_v0_30f/
fallback artifact: outputs/right_conducting/selected_30f/feature_baseline_live_v0_30f.json
sweep policy artifact: outputs/right_conducting/selected_30f_sweep/feature_baseline_live_v0_30f_sweep.json
baseline score: outputs/right_conducting/baseline_scores_v0_30f_eval30stable.json
replay score: outputs/right_conducting/stream_replay_222455_30f_selected.json
delay analysis: outputs/right_conducting/stream_replay_222455_30f_selected_analysis.json
```

30f stable heldout:

```text
tempo_acc: 0.4249
bpm_mae_window: 15.2381
gain_acc: 0.7875
dynamics_mae_window: 0.1275
```

30f selected sweep policy:

```text
switch_threshold: 0.35
fast_switch_threshold: 0.50
confirm_updates: 3
false_switches_per_min: 3.1002
reported switch_delay_mean_s: 0.0000
```

30f caveat:

```text
100 -> 120 BPM: smoothed output was already target before true switch
120 -> 80 BPM: raw target not reached
```

Decision:

```text
30f reduces raw latency but is not stable enough to replace 60f.
Keep 30f as a latency probe and move to temporal classifier / normalization comparison.
```

## Temporal Feature Ridge Probe

Artifact:

```text
outputs/right_conducting/temporal_30f_c5/temporal_feature_live_v0_30f_c5.json
```

Structure:

```text
30f pose window
  -> 16 handcrafted features
  -> causal context concat, context_size 5
  -> standardized ridge tempo classifier
  -> standardized ridge gain classifier
  -> LiveSmoother policy
```

Stored parameters:

```text
tempo_model.classes / mean / std / weights
gain_model.classes / mean / std / weights
base_feature_dim: 16
context_size: 5
feature_dim: 80
```

Heldout score:

```text
transition_eval_222455_30f_stable tempo_acc: 0.2491
bpm_mae_window: 16.3370
gain_acc: 0.7546
```

Replay:

```text
raw false_switches_per_min: 20.6677
raw switch_delay_p90_s: 27.6538
smoothed false_switches_per_min: 10.3338
smoothed switch_delay_p90_s: 30.4154
```

Decision:

```text
temporal_feature_ridge_v0_30f_c5: NO-GO
Reason: CV improves but heldout transition and live latency collapse.
```

## Normalization Probe

Compared input normalization:

```text
camera
right_shoulder
right_arm_length
```

Best stable tempo remains:

```text
60f camera tempo_acc: 0.5514
60f right_shoulder tempo_acc: 0.5473
60f right_arm_length tempo_acc: 0.4609
```

right_shoulder improves gain:

```text
60f camera gain_acc: 0.7654
60f right_shoulder gain_acc: 0.8066
30f camera gain_acc: 0.7875
30f right_shoulder gain_acc: 0.8059
```

Live replay result:

```text
60f right_shoulder smoothed tempo_acc: 0.4840
60f right_shoulder false_switches_per_min: 4.2811
60f right_shoulder missed switches: 1 / 2
30f right_shoulder smoothed tempo_acc: 0.3780
30f right_shoulder false_switches_per_min: 11.3672
30f right_shoulder missed switches: 1 / 2
```

Decision:

```text
Keep selected live fallback as 60f camera.
Do not export right_shoulder as the default live model yet.
Do not use right_arm_length normalization.
```

## Known Failure: Down-Transition

Current selected fallback misses the `120 -> 80` transition in `session_20260616_222455_eval`.

Evidence:

```text
60f stable 80 rows: 11
60f raw predictions in stable 80 rows: {100 BPM: 8, 120 BPM: 3}
30f stable 80 rows: 21
30f raw predictions in stable 80 rows: {100 BPM: 13, 120 BPM: 8}
```

Feature diagnosis:

```text
dominant_bpm is near 60 BPM for all tempo centroids
static relative pose means dominate class 1 vs class 2 distance
```

Deployment implication:

```text
Do not claim robust down-transition live control with the current fallback.
The next model candidate must reduce dependence on static pose means.
```

## Pose-Invariant Feature Subset Candidate

Artifact candidates:

```text
outputs/right_conducting/selected_60f_pose_invariant/feature_baseline_live_v0_60f_pose_invariant.json
outputs/right_conducting/selected_30f_pose_invariant/feature_baseline_live_v0_30f_pose_invariant.json
```

Structure:

```text
pose window
  -> 12 selected handcrafted motion features
  -> nearest-centroid tempo classifier
  -> nearest-centroid gain classifier
  -> LiveSmoother policy
```

Removed static mean features:

```text
rel_wrist_x_mean
rel_wrist_y_mean
rel_elbow_x_mean
rel_elbow_y_mean
```

Best diagnostic result:

```text
60f pose-invariant raw reached true switches: 2 / 2
60f pose-invariant raw 120 -> 80 delay: 3.8021s
```

Blocking result:

```text
60f selected fallback stable tempo_acc: 0.5514
60f pose-invariant stable tempo_acc: 0.4938
60f pose-invariant smoothed false_switches_per_min: 5.3513
60f pose-invariant smoothed missed switches: 1 / 2
```

Policy sweep result:

```text
false_switches_per_min can be reduced to 4.2811,
but switch_delay_mean_s becomes 17.0084.
```

Decision:

```text
pose_invariant feature subset: NO-GO as selected live model.
Keep it as a diagnostic result for the hybrid/weighted feature candidate.
Selected live fallback remains outputs/right_conducting/selected/feature_baseline_live_v0.json.
```

## Hybrid Static-Weighted Feature Candidate

Artifact candidates:

```text
outputs/right_conducting/selected_60f_hybrid_static025/feature_baseline_live_v0_60f_hybrid_static025.json
outputs/right_conducting/selected_60f_hybrid_static050/feature_baseline_live_v0_60f_hybrid_static050.json
outputs/right_conducting/selected_60f_hybrid_static075/feature_baseline_live_v0_60f_hybrid_static075.json
```

Structure:

```text
pose window [60, 17, 3]
  -> 16 handcrafted right-arm motion features
  -> nearest-centroid tempo/gain classifier
  -> lower distance weight for static pose mean features
  -> LiveSmoother policy
```

Static feature weights:

```text
hybrid_static025: 0.25
hybrid_static050: 0.50
hybrid_static075: 0.75
```

Best hybrid stable result:

```text
hybrid_static075 stable tempo_acc: 0.5226
hybrid_static075 stable bpm_mae: 11.5226
hybrid_static075 80 BPM recall: 0.0000
```

Replay result:

```text
hybrid_static075 raw false_switches_per_min: 12.8432
hybrid_static075 raw reached switches: 1 / 2
hybrid_static075 smoothed false_switches_per_min: 6.4216
hybrid_static075 smoothed reached switches: 1 / 2
```

Decision:

```text
hybrid_static feature weighting: NO-GO as selected live model.
Selected live fallback remains outputs/right_conducting/selected/feature_baseline_live_v0.json.
```

## Class-Balanced Ridge Feature Candidate

Candidate artifacts:

```text
outputs/right_conducting/linear_unweighted_60f_c1_a1/temporal_feature_live_v0_60f_c1_a1.json
outputs/right_conducting/linear_balanced_60f_c1_a0.1/temporal_feature_live_v0_60f_c1_a0.1_balanced.json
outputs/right_conducting/linear_balanced_60f_c1_a1/temporal_feature_live_v0_60f_c1_a1_balanced.json
outputs/right_conducting/linear_balanced_60f_c1_a10/temporal_feature_live_v0_60f_c1_a10_balanced.json
```

Structure:

```text
pose window [60, 17, 3]
  -> 16 handcrafted right-arm features
  -> standardized ridge classifier
  -> optional class_weight=balanced
```

Best balanced stable result:

```text
balanced a10 stable tempo_acc: 0.2840
balanced a10 stable bpm_mae: 15.5556
balanced a10 true 80 BPM predictions: {100: 5, 60: 6}
```

Replay result:

```text
balanced a10 raw false_switches_per_min: 20.3351
balanced a10 raw reached switches: 0 / 2
balanced a10 smoothed false_switches_per_min: 8.5621
balanced a10 smoothed reached switches: 0 / 2
```

Decision:

```text
class-balanced ridge feature classifier: NO-GO as selected live model.
Selected live fallback remains outputs/right_conducting/selected/feature_baseline_live_v0.json.
```

## 80 BPM Feature Distribution Limitation

Diagnostic artifact:

```text
outputs/right_conducting/feature_distribution_80_tail_60f.json
```

Stable `session_20260616_222455_eval` 80 BPM tail:

```text
sample_count: 11
nearest train class counts: {100 BPM: 8, 120 BPM: 3}
mean distance to train 80: 12.2489
mean distance to train 100: 6.9425
mean distance to train 120: 7.7321
```

Implication:

```text
The selected feature space does not cover this heldout 80 BPM tail.
This is why transition-margin filtering, static-feature weighting, and class-balanced ridge did not solve the 120 -> 80 miss.
```

Tempo-stretch diagnostic:

```text
mild speed_scales 0.92,1.10:
  stable eval 80 nearest train classes: {100 BPM: 7, 120 BPM: 4}

aggressive bridge speed_scales 0.80,0.667:
  stable eval 80 nearest train classes: {100 BPM: 11}
  distance to train 80 improves 12.2489 -> 9.1352
  but distance to train 100 remains lower at 7.1368
```

Decision:

```text
tempo-stretch-only augmentation is not enough evidence to update the selected live model.
```

## Target-80 Combo Augmentation Candidate

Diagnostic artifact:

```text
outputs/right_conducting/selected_60f_target80_combo_aug/feature_baseline_target80_combo_aug_60f.json
```

Augmentation:

```text
speed_scales: 0.80, 0.667
amplitude_scales: 1.15, 1.30
augmented_target_classes: 1 / 80 BPM
generated target80 windows: 9270
```

Coverage result on stable eval 80 tail:

```text
original nearest train classes: {100 BPM: 8, 120 BPM: 3}
target80 combo nearest train classes: {80 BPM: 9, 120 BPM: 2}
```

Offline stable score:

```text
original fallback tempo_acc: 0.5514
target80 combo tempo_acc: 0.5638
original 80 BPM recall: 0.0000
target80 combo 80 BPM recall: 0.8182
original bpm_mae: 10.6173
target80 combo bpm_mae: 11.1934
```

Replay result with selected-style policy:

```text
raw reached switches: 2 / 2
smoothed reached switches: 2 / 2
smoothed false_switches_per_min: 6.4216
```

Decision:

```text
target80 combo augmentation: useful next training direction.
target80 combo artifact: NO-GO as selected live model.
Reason: 100 BPM false 80 predictions increase and low-false-switch policy misses smoothed 120 -> 80.
Selected live fallback remains outputs/right_conducting/selected/feature_baseline_live_v0.json.
```

## MotionBERT Target-80 Combo Head

Candidate artifacts:

```text
outputs/right_conducting/motionbert_cache_v0_60f_stats_target80_combo/
outputs/right_conducting/motionbert_head_v0_60f_stats_target80_combo_e80_h512_eval60stable/all_train_head.pt
outputs/right_conducting/motionbert_head_v0_60f_stats_target80_combo_stride3_e80_h512_eval60stable/all_train_head.pt
outputs/right_conducting/motionbert_head_v0_60f_stats_target80_combo_stride10_e80_h512_eval60stable/all_train_head.pt
```

Best of these on current stable transition eval:

```text
candidate: target80 combo stride3
tempo_acc: 0.3539
bpm_mae_window: 16.2140
80 BPM recall: 0.8182
100 BPM recall: 0.8242
120 BPM recall: 0.0142
gain_acc: 0.7984
```

Decision:

```text
MotionBERT target80 combo head: NO-GO as selected live model.
Reason: 120 BPM recall collapses even when 80 BPM recall improves.
Keep selected live fallback as outputs/right_conducting/selected/feature_baseline_live_v0.json.
Rerun after the supplied new dataset is registered and split.
```

## Evaluation Coverage Status

Readiness artifact:

```text
outputs/right_conducting/eval_session_readiness_audit.json
```

Current scoreable transition sessions:

```text
session_20260616_222455_eval
```

Excluded transition sessions:

```text
session_20260616_215630_eval
```

Exclusion reason:

```text
manual_timeline.json is missing.
labels_frame.jsonl is constant 100 BPM for all 900 frames.
labels_window.jsonl is constant tempo_class 2 / 100 BPM for all 131 windows.
```

Model-card implication:

```text
The current selected artifact is a temporary live fallback,
not a proven robust down-transition controller.
```

Relabel helper status:

```text
tool: tools/relabel_right_conducting_eval_from_timeline.py
dry-run proof: outputs/right_conducting/relabel_dryrun_222455_60f/summary.json
status: ready for 215630 only after true timestamps are supplied
```

Policy selection:

```text
sweep_artifact: outputs/right_conducting/stream_policy_sweep_222455.json
constraint: false_switches_per_min <= 5.0
selected switch_threshold: 0.15
selected fast_switch_threshold: 0.40
selected confirm_updates: 2
```

Second eval status:

```text
session_20260616_215630_eval is still excluded.
manual_timeline.json is missing.
current labels are constant 100 BPM.
```

## Current TCN Live Candidate

Checkpoint:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_head.pt
```

Manifest and structure:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_structure.md
```

Runtime input:

```text
raw handmark CSV / stdin
right-arm H36M17 masked stream
window_frames: 45
stride_frames: 3
fps: 15
```

Architecture:

```text
ConductingTCN
input_channels: 9
hidden_channels: 64
levels: 4
kernel_size: 5
dropout: 0.1
tempo_classes: 4
gain_classes: 2
bpm_bins: 60 / 80 / 100 / 120
```

Readiness artifacts:

```text
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_gate.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_handmark_stream_readiness.json
outputs/right_conducting/selected_tcn_handmark_live45f/selected_stream_summary.json
outputs/right_conducting/selected_tcn_handmark_live45f/selected_stream_benchmark.json
outputs/right_conducting/selected_tcn_handmark_live45f/manifest_stream_set_gate.json
outputs/right_conducting/selected_tcn_handmark_live45f/manifest_stream_readiness.json
outputs/right_conducting/selected_tcn_handmark_live45f/manifest_stream_benchmark.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_set_score.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_set_gate.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_strict_heldout_preflight.json
outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_outputs.jsonl
outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_summary.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness_with_stdin.json
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_post_arrival_goal_dryrun.md
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_outputs_contract.json
outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_outputs_contract.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness_with_output_contract.json
outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.json
outputs/right_conducting/tcn_alltest_latest/stream_set_gate_fulltest_latest.json
outputs/right_conducting/tcn_alltest_latest/tcn_goal_status_fulltest_latest.json
outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.json
```

Primary runtime entrypoint:

```text
tools/run_tcn_handmark_csv_stream.py --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
```

Pipe-style runtime:

```text
python your_handmark_producer.py | python tools/run_tcn_handmark_csv_stream.py --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json --handmark-csv - --output-jsonl - --flush-each-output
```

Current status:

```text
fixed-camera deployment-fit: GO
stdin live contract: GO
JSONL output contract: GO
readiness with output contract gate: GO
latest all-test scope: 2/3-beat-only supplied fixed-camera CSVs, beat4 CSV excluded
latest all-test discovered raw CSV files: 15
latest all-test scoreable processed sessions: 11
latest all-test margin3 tempo_acc / gain_acc: 1.0000 / 1.0000
latest all-test benchmark p90: 1.9984 ms
stdin smoke rows / invalid: 3 / 0
strict independent heldout: incomplete
strict heldout preflight: NO_GO, P0 0/8
strict heldout post-arrival chain: dry-run ready
```

Use the TCN candidate as the current live-facing model path. Keep the MotionBERT-Lite head as documented comparison until independent heldout data is available.
