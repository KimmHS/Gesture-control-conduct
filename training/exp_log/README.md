# Conducting Experiment Docs

이 폴더는 오른손 지휘 gesture로 MIDI `tempo`와 `dynamics`를 제어하는 실험 문서의 입구다.

## Start Here

| 문서 | 용도 |
|---|---|
| [current_status.md](current_status.md) | 현재 상태 한 장 요약: selected TCN bundle, score, strict blocker, 다음 명령 |
| [final_plan_motionbert_lite_conducting_control.md](final_plan_motionbert_lite_conducting_control.md) | 최종 canonical plan: MotionBERT-Lite frozen encoder + conducting head + MIDI control |
| [right_hand_conducting_experiment_overview.md](right_hand_conducting_experiment_overview.md) | 빠른 요약과 주요 링크 |
| [right_hand_conducting_scores.md](right_hand_conducting_scores.md) | current v0 baseline and MotionBERT-Lite head score table |
| [right_hand_conducting_model_card.md](right_hand_conducting_model_card.md) | current selected TCN 모델 구조, 파라미터, export artifact 설명 |
| [strict_heldout_data_contract.md](strict_heldout_data_contract.md) | strict heldout 데이터가 들어올 때 필요한 root/file/metadata/label/command contract |
| [contradictions.md](contradictions.md) | current v0와 final target 사이의 모순/주의점만 짧게 정리 |
| [mid_presentation_feedback.md](mid_presentation_feedback.md) | 발표/리뷰 피드백이 최종 실험 설계에 반영된 mapping |
| [dataset_shortage_action_plan.md](dataset_shortage_action_plan.md) | 데이터 부족 상황의 방법론 개선(Section A)과 추가 녹화 요청 리스트(Section B) |
| [right_conducting_required_data_manifest.json](right_conducting_required_data_manifest.json) | devset에 필요한 static/transition case와 gate threshold의 source manifest |
| [../../TRANSITION_RECORDING_GUIDE.md](../../TRANSITION_RECORDING_GUIDE.md) | fixed-camera 80 BPM static devset과 transition capture checklist |
| [goal_reports/2026-06-16_01_prompt_analysis_and_augmentation_survey.md](goal_reports/2026-06-16_01_prompt_analysis_and_augmentation_survey.md) | Goal 시작 리포트: 프롬프트 분석, augmentation survey, 단계별 gate |
| [goal_reports/2026-06-16_05_motionbert_smoke_and_head_training.md](goal_reports/2026-06-16_05_motionbert_smoke_and_head_training.md) | MotionBERT-Lite smoke, feature cache, conducting head 학습/평가 결과 |
| [goal_reports/2026-06-16_06_motionbert_representation_diagnosis.md](goal_reports/2026-06-16_06_motionbert_representation_diagnosis.md) | mean pooling 병목 진단, stats representation 실험, heldout 실패 결과 |
| [goal_reports/2026-06-16_07_heldout_stability_and_live_fallback.md](goal_reports/2026-06-16_07_heldout_stability_and_live_fallback.md) | 60-frame stable heldout 재평가와 live fallback 판단 |
| [goal_reports/2026-06-16_08_live_fallback_export.md](goal_reports/2026-06-16_08_live_fallback_export.md) | feature-baseline live fallback artifact/export 결과 |
| [goal_reports/2026-06-16_09_streaming_replay_metrics.md](goal_reports/2026-06-16_09_streaming_replay_metrics.md) | selected fallback의 streaming replay stability metric |
| [goal_reports/2026-06-17_10_calibration_and_second_eval_check.md](goal_reports/2026-06-17_10_calibration_and_second_eval_check.md) | 215630 eval 상태 확인과 stream policy sweep/calibration 결과 |
| [goal_reports/2026-06-17_11_replay_delay_diagnosis.md](goal_reports/2026-06-17_11_replay_delay_diagnosis.md) | live replay의 raw classifier delay와 smoothing delay 분리 진단 |
| [goal_reports/2026-06-17_12_30f_classifier_latency_probe.md](goal_reports/2026-06-17_12_30f_classifier_latency_probe.md) | 30-frame 후보로 classifier-side latency/stability tradeoff 확인 |
| [goal_reports/2026-06-17_13_temporal_feature_classifier_probe.md](goal_reports/2026-06-17_13_temporal_feature_classifier_probe.md) | causal temporal feature ridge classifier 구현/평가와 no-go 판단 |
| [goal_reports/2026-06-17_14_normalization_comparison.md](goal_reports/2026-06-17_14_normalization_comparison.md) | camera/right_shoulder/right_arm_length normalization 비교와 selected fallback 유지 판단 |
| [goal_reports/2026-06-17_15_missed_transition_diagnosis.md](goal_reports/2026-06-17_15_missed_transition_diagnosis.md) | missed `120 -> 80` 전환의 raw classifier/feature/centroid 원인 진단 |
| [goal_reports/2026-06-17_16_pose_invariant_feature_subset.md](goal_reports/2026-06-17_16_pose_invariant_feature_subset.md) | static pose mean 제거 후보 평가와 no-go 판단 |
| [goal_reports/2026-06-17_17_transition_margin_evaluation.md](goal_reports/2026-06-17_17_transition_margin_evaluation.md) | BPM 전환 지점 margin별 classification/replay 재평가 |
| [goal_reports/2026-06-17_18_hybrid_static_weight_classifier.md](goal_reports/2026-06-17_18_hybrid_static_weight_classifier.md) | static pose mean weighted hybrid classifier 평가와 no-go 판단 |
| [goal_reports/2026-06-17_19_class_balanced_ridge_feature_classifier.md](goal_reports/2026-06-17_19_class_balanced_ridge_feature_classifier.md) | class-balanced ridge feature classifier 평가와 no-go 판단 |
| [goal_reports/2026-06-17_20_80_bpm_feature_distribution_diagnosis.md](goal_reports/2026-06-17_20_80_bpm_feature_distribution_diagnosis.md) | 80 BPM tail의 train/eval feature distribution mismatch 진단 |
| [goal_reports/2026-06-17_21_tempo_stretch_coverage_sanity_check.md](goal_reports/2026-06-17_21_tempo_stretch_coverage_sanity_check.md) | train-only tempo-stretch augmentation coverage sanity check |
| [goal_reports/2026-06-17_22_eval_relabel_and_down_transition_data_decision.md](goal_reports/2026-06-17_22_eval_relabel_and_down_transition_data_decision.md) | evaluation session readiness audit와 down-transition 데이터/라벨 결정 |
| [goal_reports/2026-06-17_23_manual_timeline_relabel_helper.md](goal_reports/2026-06-17_23_manual_timeline_relabel_helper.md) | manual_timeline 기반 eval relabel dry-run helper |
| [goal_reports/2026-06-17_24_reproducible_goal_command.md](goal_reports/2026-06-17_24_reproducible_goal_command.md) | current audit/eval/replay/analyze 재현용 goal command |
| [goal_reports/2026-06-17_25_target80_combo_augmentation_candidate.md](goal_reports/2026-06-17_25_target80_combo_augmentation_candidate.md) | target 80 tempo+amplitude augmentation 후보의 coverage/offline/replay 평가 |
| [goal_reports/2026-06-17_26_motionbert_target80_combo_training.md](goal_reports/2026-06-17_26_motionbert_target80_combo_training.md) | target80 combo augmentation을 MotionBERT head 학습에 적용한 결과와 no-go 판단 |
| [goal_reports/2026-06-17_27_new_dataset_intake_gate.md](goal_reports/2026-06-17_27_new_dataset_intake_gate.md) | 새 데이터 공급 전 train/eval intake audit gate와 current baseline audit |
| [goal_reports/2026-06-17_28_new_dataset_staging_zip_gate.md](goal_reports/2026-06-17_28_new_dataset_staging_zip_gate.md) | 새 train root를 canonical recordings zip으로 staging하는 gate와 prepare smoke |
| [goal_reports/2026-06-17_29_after_supply_goal_runner.md](goal_reports/2026-06-17_29_after_supply_goal_runner.md) | 새 데이터 공급 후 intake/stage/prepare를 한 번에 실행하는 goal runner |
| [goal_reports/2026-06-17_30_after_supply_cache_train_runner.md](goal_reports/2026-06-17_30_after_supply_cache_train_runner.md) | 새 데이터 prepare 후 MotionBERT cache/train을 실행하는 goal runner |
| [goal_reports/2026-06-17_31_model_score_gate.md](goal_reports/2026-06-17_31_model_score_gate.md) | 학습된 모델을 selected live model로 올릴 수 있는지 판정하는 score gate |
| [goal_reports/2026-06-17_32_after_supply_detailed_eval_gate_runner.md](goal_reports/2026-06-17_32_after_supply_detailed_eval_gate_runner.md) | 새 데이터 학습 후 detailed eval과 score gate를 연결하는 goal runner |
| [goal_reports/2026-06-17_33_after_supply_5gpu_frame_sweep_runner.md](goal_reports/2026-06-17_33_after_supply_5gpu_frame_sweep_runner.md) | 새 데이터 공급 후 5-GPU window-frame sweep을 실행하는 goal runner |
| [goal_reports/2026-06-17_34_after_supply_model_selection_runner.md](goal_reports/2026-06-17_34_after_supply_model_selection_runner.md) | frame sweep score gate 결과를 모아 selected 후보를 고르는 selection runner |
| [goal_reports/2026-06-17_35_motionbert_selected_export_bundle.md](goal_reports/2026-06-17_35_motionbert_selected_export_bundle.md) | SELECTED MotionBERT 후보를 live bundle로 export하는 구조와 runner |
| [goal_reports/2026-06-17_36_motionbert_live_bundle_smoke.md](goal_reports/2026-06-17_36_motionbert_live_bundle_smoke.md) | exported MotionBERT live bundle을 runtime predictor로 smoke test하는 경로 |
| [goal_reports/2026-06-17_37_motionbert_live_bundle_replay.md](goal_reports/2026-06-17_37_motionbert_live_bundle_replay.md) | exported MotionBERT live bundle을 eval session에서 streaming replay하는 경로 |
| [goal_reports/2026-06-17_38_5gpu_hparam_sweep_transition_stress.md](goal_reports/2026-06-17_38_5gpu_hparam_sweep_transition_stress.md) | 5-GPU hparam sweep, 새 transition stress eval, 추가 devset edge case 정리 |
| [goal_reports/2026-06-17_39_devset_edge_case_audit.md](goal_reports/2026-06-17_39_devset_edge_case_audit.md) | fixed-camera devset edge-case audit tool과 현재 missing static 80 조건 |
| [goal_reports/2026-06-17_40_devset_gated_selection_guard.md](goal_reports/2026-06-17_40_devset_gated_selection_guard.md) | devset gate가 GO가 아니면 selected/export 후보를 막는 selection guard |
| [goal_reports/2026-06-17_41_static_devset_score_markdown.md](goal_reports/2026-06-17_41_static_devset_score_markdown.md) | static 80 devset score와 transition margin score의 markdown 해석 분리 |
| [goal_reports/2026-06-17_42_planned_experiments.md](goal_reports/2026-06-17_42_planned_experiments.md) | 앞으로 진행할 devset/gate/5-GPU/export 실험 순서와 pass line |
| [goal_reports/2026-06-17_43_experiment_readiness_gate.md](goal_reports/2026-06-17_43_experiment_readiness_gate.md) | 현재 산출물 기준으로 runnable/blocked 실험과 next action을 자동 판정 |
| [goal_reports/2026-06-17_44_scoreable_devset_artifact_audit.md](goal_reports/2026-06-17_44_scoreable_devset_artifact_audit.md) | devset case present 기준을 metadata match + original score artifacts로 강화 |
| [goal_reports/2026-06-17_45_missing_devset_checklist.md](goal_reports/2026-06-17_45_missing_devset_checklist.md) | audit 결과에서 현재 missing recording checklist를 자동 생성 |
| [goal_reports/2026-06-17_47_static80_transition_5gpu_hparam_sweep.md](goal_reports/2026-06-17_47_static80_transition_5gpu_hparam_sweep.md) | fixed-camera static80 + transition data로 5-GPU hparam sweep을 재실행하고 45f live MotionBERT bundle 선택 |
| [goal_reports/2026-06-17_48_selected_motionbert_live_replay.md](goal_reports/2026-06-17_48_selected_motionbert_live_replay.md) | 선택된 45f MotionBERT bundle을 full-backbone streaming replay로 검증하고 남은 weak edge 정리 |
| [goal_reports/2026-06-17_49_selected_motionbert_live_benchmark.md](goal_reports/2026-06-17_49_selected_motionbert_live_benchmark.md) | 선택된 45f MotionBERT bundle의 full-backbone inference latency와 200ms stream budget 통과 여부 |
| [goal_reports/2026-06-17_50_selected_motionbert_live_policy_sweep.md](goal_reports/2026-06-17_50_selected_motionbert_live_policy_sweep.md) | 선택된 45f bundle의 live policy를 sweep해서 transition false switch를 0으로 낮춘 결과 |
| [goal_reports/2026-06-17_51_strict_heldout_independence_gate.md](goal_reports/2026-06-17_51_strict_heldout_independence_gate.md) | 선택된 bundle의 현재 score가 strict heldout인지 자동 검사하고, 다음 heldout gate 명령을 고정 |
| [goal_reports/2026-06-17_52_live_replay_gate.md](goal_reports/2026-06-17_52_live_replay_gate.md) | exported live replay를 tempo/gain/false switch/delay 기준으로 GO/NO_GO 판정하는 gate 추가 |
| [goal_reports/2026-06-17_53_goal_status_dashboard.md](goal_reports/2026-06-17_53_goal_status_dashboard.md) | selected bundle의 live pilot/strict heldout/benchmark/artifact 상태를 한 화면에 요약 |
| [goal_reports/2026-06-17_54_live_output_contract.md](goal_reports/2026-06-17_54_live_output_contract.md) | selected bundle의 live/MIDI output schema와 sample artifact 고정 |
| [goal_reports/2026-06-17_55_live_output_replay_adapter.md](goal_reports/2026-06-17_55_live_output_replay_adapter.md) | replay rows를 live/MIDI output schema JSONL로 변환하는 adapter 추가 |
| [goal_reports/2026-06-17_56_label_free_pose_stream_runtime.md](goal_reports/2026-06-17_56_label_free_pose_stream_runtime.md) | label 없는 pose stream 입력에서 live/MIDI output JSONL 생성 경로 추가 |
| [goal_reports/2026-06-17_57_online_pose_frame_buffer.md](goal_reports/2026-06-17_57_online_pose_frame_buffer.md) | frame-by-frame online buffer stream과 window-scan 결과 일치 검증 |
| [goal_reports/2026-06-17_58_pose_quality_gate.md](goal_reports/2026-06-17_58_pose_quality_gate.md) | 오른팔 confidence dropout 상황의 invalid/hold runtime gate 추가 |
| [goal_reports/2026-06-17_59_extended_5gpu_hparam_sweep.md](goal_reports/2026-06-17_59_extended_5gpu_hparam_sweep.md) | 5-GPU 확장 hparam sweep 34개 추가, 총 54개 후보 비교, 새 45f live bundle export/replay/benchmark |
| [goal_reports/2026-06-17_60_ext_label_free_online_pose_stream.md](goal_reports/2026-06-17_60_ext_label_free_online_pose_stream.md) | 새 45f ext bundle을 label-free window scan, online frame buffer, pose-quality hold gate로 검증 |
| [goal_reports/2026-06-17_61_available_strict_heldout_stress.md](goal_reports/2026-06-17_61_available_strict_heldout_stress.md) | 사용 가능한 독립 evaluation stress replay: 222455는 독립성 GO지만 strict live gate NO_GO |
| [goal_reports/2026-06-17_62_strict_heldout_scope_audit.md](goal_reports/2026-06-17_62_strict_heldout_scope_audit.md) | strict heldout root가 현재 2/3박 fixed-camera P0 scope를 덮는지 자동 판정하는 audit 추가 |
| [goal_reports/2026-06-17_63_strict_heldout_scope_goal_runner.md](goal_reports/2026-06-17_63_strict_heldout_scope_goal_runner.md) | strict heldout independence와 scope audit을 한 goal runner step으로 연결 |
| [goal_reports/2026-06-17_64_goal_status_strict_scope_gate.md](goal_reports/2026-06-17_64_goal_status_strict_scope_gate.md) | selected ext bundle의 goal status에 strict heldout scope gate를 연결 |
| [goal_reports/2026-06-17_65_strict_goal_status_runner_chain.md](goal_reports/2026-06-17_65_strict_goal_status_runner_chain.md) | strict heldout scope/replay/live gate/final goal status를 한 runner chain으로 연결 |
| [goal_reports/2026-06-17_66_current_eval_strict_chain_execution.md](goal_reports/2026-06-17_66_current_eval_strict_chain_execution.md) | current eval roots에서 strict status chain을 실제 실행하고 NO_GO 원인 기록 |
| [goal_reports/2026-06-17_67_replay_failure_diagnosis.md](goal_reports/2026-06-17_67_replay_failure_diagnosis.md) | current eval replay 실패를 confusion/error-run/class-collapse 기준으로 진단 |
| [goal_reports/2026-06-17_68_deployment_vs_current_eval_diagnosis.md](goal_reports/2026-06-17_68_deployment_vs_current_eval_diagnosis.md) | deployment-fit 통과와 current eval 실패를 분리해서 strict claim 범위 정리 |
| [goal_reports/2026-06-17_69_strict_heldout_missing_checklist_runner.md](goal_reports/2026-06-17_69_strict_heldout_missing_checklist_runner.md) | strict heldout P0 missing cases를 녹화 체크리스트로 자동 렌더링 |
| [goal_reports/2026-06-17_70_strict_heldout_preflight_gate.md](goal_reports/2026-06-17_70_strict_heldout_preflight_gate.md) | strict replay 전 independence/scope/P0 checklist preflight gate 추가 |
| [goal_reports/2026-06-17_71_live_runtime_readiness_gate.md](goal_reports/2026-06-17_71_live_runtime_readiness_gate.md) | final stream path용 live runtime readiness gate 추가 |
| [goal_reports/2026-06-17_72_jsonl_stdin_pose_stream_adapter.md](goal_reports/2026-06-17_72_jsonl_stdin_pose_stream_adapter.md) | JSONL/stdin H36M17 frame stream adapter와 selected bundle smoke 결과 |
| [goal_reports/2026-06-17_73_handmark_csv_stream_adapter.md](goal_reports/2026-06-17_73_handmark_csv_stream_adapter.md) | raw handmark recording CSV/stdin stream adapter와 reference-joint caveat |
| [goal_reports/2026-06-17_74_right_arm_only_input_mask_probe.md](goal_reports/2026-06-17_74_right_arm_only_input_mask_probe.md) | right-arm-only input mask sweep와 handmark-only fixed-camera probe bundle |
| [goal_reports/2026-06-17_75_raw_handmark_csv_stream_set_score.md](goal_reports/2026-06-17_75_raw_handmark_csv_stream_set_score.md) | raw handmark CSV 전체 set의 stream aggregate score와 margin sweep |
| [goal_reports/2026-06-17_76_handmark_csv_stream_set_gate.md](goal_reports/2026-06-17_76_handmark_csv_stream_set_gate.md) | raw handmark CSV stream set score를 GO/NO_GO로 판정하는 gate |
| [goal_reports/2026-06-17_77_goal_runner_handmark_csv_set_gate.md](goal_reports/2026-06-17_77_goal_runner_handmark_csv_set_gate.md) | handmark CSV stream set score/gate를 한 번에 재현하는 goal runner step |
| [goal_reports/2026-06-17_78_final_score_and_model_report.md](goal_reports/2026-06-17_78_final_score_and_model_report.md) | current final score/model report와 selected MotionBERT bundle 결정 |
| [goal_reports/2026-06-17_79_tcn_quick_probe.md](goal_reports/2026-06-17_79_tcn_quick_probe.md) | TCN 30/45/60/90/120f quick probe, margin sweep, artifact/test 결과 |
| [goal_reports/2026-06-17_80_tcn_handmark_live_stream.md](goal_reports/2026-06-17_80_tcn_handmark_live_stream.md) | TCN 45f handmark CSV/stdin live stream path와 set score |
| [goal_reports/2026-06-17_81_tcn_handmark_stream_readiness_gate.md](goal_reports/2026-06-17_81_tcn_handmark_stream_readiness_gate.md) | TCN handmark stream score gate + latency benchmark + readiness GO |
| [goal_reports/2026-06-17_106_full_test_and_tcn_alltest_rerun.md](goal_reports/2026-06-17_106_full_test_and_tcn_alltest_rerun.md) | 최신 전체 unittest + selected TCN supplied-set rerun + strict preflight 상태 |
| [goal_reports/2026-06-17_107_current_status_exporter.md](goal_reports/2026-06-17_107_current_status_exporter.md) | goal/release/preflight JSON에서 current status snapshot을 재생성하는 exporter |
| [goal_reports/2026-06-17_108_tcn_current_status_goal_runner_step.md](goal_reports/2026-06-17_108_tcn_current_status_goal_runner_step.md) | `tcn-current-status` goal runner step으로 dashboard snapshot 재생성 |
| [goal_reports/2026-06-17_109_strict_post_arrival_current_status_snapshot.md](goal_reports/2026-06-17_109_strict_post_arrival_current_status_snapshot.md) | strict post-arrival wrapper가 성공 시 current status snapshot까지 생성 |
| [goal_reports/2026-06-17_110_selected_tcn_model_card_refresh.md](goal_reports/2026-06-17_110_selected_tcn_model_card_refresh.md) | model card entry point를 selected TCN 기준으로 갱신 |
| [goal_reports/2026-06-17_111_current_goal_evidence_audit.md](goal_reports/2026-06-17_111_current_goal_evidence_audit.md) | current goal 요구사항별 evidence audit: live/release GO, strict heldout NO_GO |
| [goal_reports/2026-06-17_112_strict_post_arrival_dryrun_recheck.md](goal_reports/2026-06-17_112_strict_post_arrival_dryrun_recheck.md) | strict 데이터 도착 후 실행할 final TCN chain dry-run 재검증 |
| [goal_reports/2026-06-17_113_strict_heldout_data_contract.md](goal_reports/2026-06-17_113_strict_heldout_data_contract.md) | strict heldout root/file/metadata/label contract를 한 문서로 고정 |
| [goal_reports/2026-06-17_114_strict_data_contract_gate.md](goal_reports/2026-06-17_114_strict_data_contract_gate.md) | strict heldout CSV sibling/data contract를 fail-fast gate로 goal runner에 연결 |
| [goal_reports/2026-06-17_115_current_strict_data_contract_snapshot.md](goal_reports/2026-06-17_115_current_strict_data_contract_snapshot.md) | 현재 strict root 부재 상태에서 data contract gate가 NO_GO/P0 0-8을 내는 증거 |
| [goal_reports/2026-06-17_116_current_status_includes_data_contract.md](goal_reports/2026-06-17_116_current_status_includes_data_contract.md) | TCN current-status snapshot에 strict data-contract status/artifact를 포함 |
| [goal_reports/2026-06-17_117_full_test_release_and_status_rerun.md](goal_reports/2026-06-17_117_full_test_release_and_status_rerun.md) | 전체 unittest, strict wrapper dry-run, release validation, current-status snapshot 재실행 |
| [goal_reports/2026-06-17_118_score_doc_and_runner_order_refresh.md](goal_reports/2026-06-17_118_score_doc_and_runner_order_refresh.md) | score 문서가 Report 117 artifact를 가리키게 갱신하고 strict runner 순서 표기를 정리 |
| [goal_reports/2026-06-17_119_tcn_handoff_and_model_card_refresh.md](goal_reports/2026-06-17_119_tcn_handoff_and_model_card_refresh.md) | TCN handoff runbook/model card 상단 evidence를 최신 fulltest artifact로 갱신 |
| [goal_reports/2026-06-17_120_submission_and_presentation_refresh.md](goal_reports/2026-06-17_120_submission_and_presentation_refresh.md) | 제출 포맷/발표 요약을 selected TCN + latest fulltest evidence 기준으로 갱신 |
| [goal_reports/2026-06-17_121_tcn_release_docs_consistency_gate.md](goal_reports/2026-06-17_121_tcn_release_docs_consistency_gate.md) | selected TCN release docs가 latest fulltest artifact와 일치하는지 자동 검사하는 gate 추가 |
| [goal_reports/2026-06-17_122_goal_runner_tcn_release_docs_step.md](goal_reports/2026-06-17_122_goal_runner_tcn_release_docs_step.md) | `tcn-release-docs` step을 goal runner에 연결하고 전체 unittest 281개 재검증 |

## What To Check

| 질문 | 바로 볼 곳 |
|---|---|
| 최종 목표가 뭐야? | final plan의 `Goal` |
| 최종 모델 방향은 뭐야? | final plan의 `Final Decision`, `Model` |
| train dataset은 뭐야? | final plan의 `Dataset` |
| 1명 pilot은 얼마나 찍어? | final plan의 `Pilot Dataset` |
| 최종 dataset 규모는? | final plan의 `Final Dataset Scale` |
| annotation은 어떻게 해? | final plan의 `Annotation` |
| augmentation은 어떻게 해? | final plan의 `Augmentation` |
| split은 어떻게 해? | final plan의 `Split Policy` |
| 현재 한계는 뭐야? | final plan의 `Current Risks and Required Reporting` |
| current/final이 섞이는 모순은? | `contradictions.md` |
| 피드백은 어떻게 반영됐어? | `mid_presentation_feedback.md` |
| 데이터가 부족하면 뭘 시도해? | `dataset_shortage_action_plan.md`의 `Section A` |
| 사용자에게 어떤 추가 녹화를 요청해? | `outputs/right_conducting/current_eval_roots_strict_missing_checklist.md`, `outputs/right_conducting/devset_missing_checklist.md`, `TRANSITION_RECORDING_GUIDE.md` |
| strict heldout 데이터는 어디에 어떻게 넣어? | `strict_heldout_data_contract.md` |
| 앞으로 어떤 실험을 돌려? | `goal_reports/2026-06-17_42_planned_experiments.md` |
| 지금 당장 어떤 실험이 runnable/block 됐어? | `outputs/right_conducting/experiment_readiness.md`, `goal_reports/2026-06-17_43_experiment_readiness_gate.md` |
| streaming runtime은? | final plan의 `Streaming Runtime` |
| final stream path readiness는? | `outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.md`, `goal_reports/2026-06-17_71_live_runtime_readiness_gate.md` |
| JSONL/stdin pose stream은? | `goal_reports/2026-06-17_72_jsonl_stdin_pose_stream_adapter.md`, `tools/run_motionbert_pose_jsonl_stream.py` |
| raw handmark CSV/stdin stream은? | `goal_reports/2026-06-17_73_handmark_csv_stream_adapter.md`, `tools/run_motionbert_handmark_csv_stream.py` |
| raw handmark CSV 전체 set gate 명령은? | `goal_reports/2026-06-17_77_goal_runner_handmark_csv_set_gate.md`, `outputs/right_conducting/right_conducting_goal_handmark_csv_set_gate_dryrun.md` |
| TCN도 전체 돌렸어? | `goal_reports/2026-06-17_79_tcn_quick_probe.md`, `outputs/right_conducting/tcn_quick_probe_20260617` |
| TCN handmark live stream은? | `goal_reports/2026-06-17_80_tcn_handmark_live_stream.md`, `tools/run_tcn_handmark_csv_stream.py`, `tools/evaluate_tcn_handmark_csv_stream_set.py` |
| TCN handmark stream readiness는? | `goal_reports/2026-06-17_81_tcn_handmark_stream_readiness_gate.md`, `outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_handmark_stream_readiness.md` |
| 최신 전체 테스트와 TCN rerun 결과는? | `goal_reports/2026-06-17_106_full_test_and_tcn_alltest_rerun.md`, `outputs/right_conducting/tcn_alltest_latest` |
| 최종 모델 구조/파라미터는? | `right_hand_conducting_model_card.md`, `outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_structure.md` |
| 현재 goal을 완료로 닫을 수 있어? | `goal_reports/2026-06-17_111_current_goal_evidence_audit.md` |
| 현재 상태 dashboard를 재생성하려면? | `tools/export_tcn_current_status.py`, `outputs/right_conducting/tcn_alltest_latest/current_status_snapshot.md` |
| goal runner로 dashboard를 재생성하려면? | `tools/run_right_conducting_goal.py --steps tcn-current-status`, `outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.md` |
| strict 데이터 도착 후 최종 current snapshot까지 만들려면? | `scripts/run_tcn_strict_post_arrival_goal.sh`, `goal_reports/2026-06-17_112_strict_post_arrival_dryrun_recheck.md` |
| strict 데이터 파일/metadata 형식은? | `strict_heldout_data_contract.md` |
| strict CSV sibling까지 자동 검사해? | `tools/check_right_conducting_strict_data_contract.py`, `goal_reports/2026-06-17_114_strict_data_contract_gate.md` |
| 현재 strict data contract 결과는? | `outputs/right_conducting/tcn_alltest_latest/current_strict_data_contract.md`, `goal_reports/2026-06-17_115_current_strict_data_contract_snapshot.md` |
| current status가 data contract도 보여줘? | `outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.md`, `goal_reports/2026-06-17_116_current_status_includes_data_contract.md` |
| 최신 전체 테스트 재실행 결과는? | `goal_reports/2026-06-17_117_full_test_release_and_status_rerun.md`, `outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.md` |
| score 문서와 strict runner 순서도 최신이야? | `right_hand_conducting_scores.md`, `goal_reports/2026-06-17_118_score_doc_and_runner_order_refresh.md` |
| live handoff 문서와 model card도 최신이야? | `tcn_live_handoff_runbook.md`, `right_hand_conducting_model_card.md`, `goal_reports/2026-06-17_119_tcn_handoff_and_model_card_refresh.md` |
| 제출/발표 문서도 selected TCN 기준이야? | `final_report_submission_format.md`, `presentation_training_summary.md`, `goal_reports/2026-06-17_120_submission_and_presentation_refresh.md` |
| TCN release 문서들이 서로 일관적인지 자동 검사해? | `tools/check_tcn_release_docs.py`, `outputs/right_conducting/tcn_alltest_latest/release_docs_check.md`, `goal_reports/2026-06-17_121_tcn_release_docs_consistency_gate.md` |
| release-docs gate도 goal runner에서 실행돼? | `tools/run_right_conducting_goal.py --steps tcn-release-docs`, `outputs/right_conducting/tcn_alltest_latest/release_docs_goal_chain.md`, `goal_reports/2026-06-17_122_goal_runner_tcn_release_docs_step.md` |
| MIDI mapping은? | final plan의 `MIDI Control Mapping` |
| git에 어떤 파일들이 들어가야 해? | final plan의 `Folder Structure` |
| 한 번에 실행하는 명령은? | final plan의 `Goal Command` |

## Current Important Paths

```text
dataset/recordings.zip
dataset/recordings
dataset/transitions
dataset/static_variants_80
docs/exp/right_conducting_required_data_manifest.json
outputs/right_conducting/recordings_staged_current.zip
outputs/right_conducting/devset_edge_case_audit.json
outputs/right_conducting/devset_edge_case_audit.md
outputs/right_conducting/devset_missing_checklist.json
outputs/right_conducting/devset_missing_checklist.md
outputs/right_conducting/experiment_readiness.json
outputs/right_conducting/experiment_readiness.md
outputs/right_conducting/right_conducting_goal_devset_audit_dryrun.json
outputs/right_conducting/right_conducting_goal_devset_audit_dryrun.md
outputs/right_conducting/right_conducting_goal_motionbert_devset_score_dryrun.json
outputs/right_conducting/right_conducting_goal_motionbert_devset_score_dryrun.md
outputs/right_conducting/right_conducting_goal_devset_pipeline_dryrun.json
outputs/right_conducting/right_conducting_goal_devset_pipeline_dryrun.md
outputs/right_conducting/right_conducting_goal_devset_selection_dryrun.json
outputs/right_conducting/right_conducting_goal_devset_selection_dryrun.md
outputs/right_conducting/hparam_sweep_static80_transitions_20260617.json
outputs/right_conducting/hparam_sweep_static80_transitions_20260617.md
outputs/right_conducting/hparam_sweep_static80_transitions_extended_20260617.json
outputs/right_conducting/hparam_sweep_static80_transitions_extended_20260617.md
outputs/right_conducting/model_candidate_selection_ext_live45f.json
outputs/right_conducting/model_candidate_selection_ext_live45f.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_manifest.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_structure.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_head.pt
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_static80_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_transitions_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_static80_stable_failure_diagnosis.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/replay_transitions_stable_failure_diagnosis.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/benchmark_transitions_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_replay_gate_transitions_deployment.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_output_contract.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_outputs_static80_stable.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_outputs_transitions_stable.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/pose_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/pose_stream_transition_022517_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/online_pose_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/online_pose_stream_transition_022517_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/online_pose_stream_comparison.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/degraded_online_pose_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/degraded_online_pose_stream_transition_022517_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/jsonl_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/jsonl_stream_transition_022415_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/handmark_csv_ref_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/handmark_csv_ref_stream_transition_022415_summary.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/motionbert_conducting_live_manifest.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_transition_022415_summary.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/live_replay_gate_deployment_fit.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_score.md
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.json
outputs/right_conducting/selected_motionbert_right_arm_only_live45f_probe/handmark_csv_stream_set_gate.md
outputs/right_conducting/tcn_quick_probe_20260617
outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_live_manifest.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_score.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_stream_set_gate.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_benchmark.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/handmark_csv_transition_022415_summary.json
outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_handmark_stream_readiness.json
outputs/right_conducting/right_conducting_goal_handmark_csv_set_gate_dryrun.json
outputs/right_conducting/right_conducting_goal_handmark_csv_set_gate_dryrun.md
outputs/right_conducting/strict_static_eval_independence_ext.json
outputs/right_conducting/strict_transition_eval_independence_ext.json
outputs/right_conducting/strict_eval_roots_independence_ext.json
outputs/right_conducting/strict_heldout_scope_audit_ext.json
outputs/right_conducting/strict_heldout_scope_audit_ext.md
outputs/right_conducting/right_conducting_goal_strict_scope_dryrun.json
outputs/right_conducting/right_conducting_goal_strict_scope_dryrun.md
outputs/right_conducting/right_conducting_goal_strict_status_dryrun.json
outputs/right_conducting/right_conducting_goal_strict_status_dryrun.md
outputs/right_conducting/current_eval_roots_independence_ext_chain.json
outputs/right_conducting/current_eval_roots_scope_ext_chain.json
outputs/right_conducting/current_eval_roots_replay_ext_chain.json
outputs/right_conducting/current_eval_roots_replay_failure_diagnosis_ext_chain.json
outputs/right_conducting/current_eval_roots_replay_failure_diagnosis_ext_chain.md
outputs/right_conducting/current_eval_roots_strict_missing_checklist.json
outputs/right_conducting/current_eval_roots_strict_missing_checklist.md
outputs/right_conducting/current_eval_roots_strict_preflight.json
outputs/right_conducting/current_eval_roots_strict_preflight.md
outputs/right_conducting/current_eval_roots_live_gate_ext_chain.json
outputs/right_conducting/goal_status_current_eval_roots_ext_chain.json
outputs/right_conducting/right_conducting_goal_current_eval_strict_chain.json
outputs/right_conducting/strict_heldout_222455_ext_replay.json
outputs/right_conducting/strict_heldout_222455_ext_live_gate.json
outputs/right_conducting/strict_heldout_222455_ext_live_outputs_summary.json
outputs/right_conducting/goal_status_selected_motionbert_live45f_ext.json
outputs/right_conducting/goal_status_selected_motionbert_live45f_ext.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_structure.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_head.pt
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_static80_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_transitions_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/policy_sweep_transitions_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/benchmark_transitions_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/heldout_independence_static80_transitions.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_replay_gate_transitions_deployment.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_replay_gate_transitions_strict.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_output_contract.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_output_contract.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_output_sample.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_outputs_static80_stable.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_outputs_static80_stable_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_outputs_transitions_stable.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_outputs_transitions_stable_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/pose_stream_static80_035040_live_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/pose_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/pose_stream_transition_022517_live_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/pose_stream_transition_022517_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_static80_035040_live_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_transition_022517_live_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_transition_022517_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_comparison.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/degraded_online_pose_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/degraded_online_pose_stream_transition_022517_summary.json
outputs/right_conducting/goal_status_selected_motionbert_live45f.json
outputs/right_conducting/goal_status_selected_motionbert_live45f.md
checkpoint/MB_lite.yaml
checkpoint/mb_lite_v0.pt
checkpoint/latest_epoch (1).bin  # original filename
dataset/evaluation/session_20260616_222455_bpm120_beat4_large
dataset/evaluation_transitions/session_20260616_215630_bpm100_beat4_large  # relabel 전까지 score 제외
```

## Current v0 Scope

```text
fps: about 15
tempo bins: 60 / 80 / 100 / 120
default window: 60 frames ~= 4s
120-frame windows: ~= 8s ablation on current data
goal command script: scripts/run_right_conducting_goal.sh
```

## Goal Reports

```text
01: goal_reports/2026-06-16_01_prompt_analysis_and_augmentation_survey.md
02: goal_reports/2026-06-16_02_dataset_audit.md
03: goal_reports/2026-06-16_03_dataset_preparation_and_augmentation.md
04: goal_reports/2026-06-16_04_baseline_training_and_evaluation.md
05: goal_reports/2026-06-16_05_motionbert_smoke_and_head_training.md
06: goal_reports/2026-06-16_06_motionbert_representation_diagnosis.md
07: goal_reports/2026-06-16_07_heldout_stability_and_live_fallback.md
08: goal_reports/2026-06-16_08_live_fallback_export.md
09: goal_reports/2026-06-16_09_streaming_replay_metrics.md
10: goal_reports/2026-06-17_10_calibration_and_second_eval_check.md
11: goal_reports/2026-06-17_11_replay_delay_diagnosis.md
12: goal_reports/2026-06-17_12_30f_classifier_latency_probe.md
13: goal_reports/2026-06-17_13_temporal_feature_classifier_probe.md
14: goal_reports/2026-06-17_14_normalization_comparison.md
15: goal_reports/2026-06-17_15_missed_transition_diagnosis.md
16: goal_reports/2026-06-17_16_pose_invariant_feature_subset.md
17: goal_reports/2026-06-17_17_transition_margin_evaluation.md
18: goal_reports/2026-06-17_18_hybrid_static_weight_classifier.md
19: goal_reports/2026-06-17_19_class_balanced_ridge_feature_classifier.md
20: goal_reports/2026-06-17_20_80_bpm_feature_distribution_diagnosis.md
21: goal_reports/2026-06-17_21_tempo_stretch_coverage_sanity_check.md
22: goal_reports/2026-06-17_22_eval_relabel_and_down_transition_data_decision.md
23: goal_reports/2026-06-17_23_manual_timeline_relabel_helper.md
24: goal_reports/2026-06-17_24_reproducible_goal_command.md
25: goal_reports/2026-06-17_25_target80_combo_augmentation_candidate.md
26: goal_reports/2026-06-17_26_motionbert_target80_combo_training.md
27: goal_reports/2026-06-17_27_new_dataset_intake_gate.md
28: goal_reports/2026-06-17_28_new_dataset_staging_zip_gate.md
29: goal_reports/2026-06-17_29_after_supply_goal_runner.md
30: goal_reports/2026-06-17_30_after_supply_cache_train_runner.md
31: goal_reports/2026-06-17_31_model_score_gate.md
32: goal_reports/2026-06-17_32_after_supply_detailed_eval_gate_runner.md
33: goal_reports/2026-06-17_33_after_supply_5gpu_frame_sweep_runner.md
34: goal_reports/2026-06-17_34_after_supply_model_selection_runner.md
35: goal_reports/2026-06-17_35_motionbert_selected_export_bundle.md
36: goal_reports/2026-06-17_36_motionbert_live_bundle_smoke.md
37: goal_reports/2026-06-17_37_motionbert_live_bundle_replay.md
38: goal_reports/2026-06-17_38_5gpu_hparam_sweep_transition_stress.md
39: goal_reports/2026-06-17_39_devset_edge_case_audit.md
40: goal_reports/2026-06-17_40_devset_gated_selection_guard.md
41: goal_reports/2026-06-17_41_static_devset_score_markdown.md
42: goal_reports/2026-06-17_42_planned_experiments.md
43: goal_reports/2026-06-17_43_experiment_readiness_gate.md
44: goal_reports/2026-06-17_44_scoreable_devset_artifact_audit.md
45: goal_reports/2026-06-17_45_missing_devset_checklist.md
47: goal_reports/2026-06-17_47_static80_transition_5gpu_hparam_sweep.md
48: goal_reports/2026-06-17_48_selected_motionbert_live_replay.md
49: goal_reports/2026-06-17_49_selected_motionbert_live_benchmark.md
50: goal_reports/2026-06-17_50_selected_motionbert_live_policy_sweep.md
51: goal_reports/2026-06-17_51_strict_heldout_independence_gate.md
52: goal_reports/2026-06-17_52_live_replay_gate.md
53: goal_reports/2026-06-17_53_goal_status_dashboard.md
54: goal_reports/2026-06-17_54_live_output_contract.md
55: goal_reports/2026-06-17_55_live_output_replay_adapter.md
56: goal_reports/2026-06-17_56_label_free_pose_stream_runtime.md
57: goal_reports/2026-06-17_57_online_pose_frame_buffer.md
58: goal_reports/2026-06-17_58_pose_quality_gate.md
59: goal_reports/2026-06-17_59_extended_5gpu_hparam_sweep.md
60: goal_reports/2026-06-17_60_ext_label_free_online_pose_stream.md
61: goal_reports/2026-06-17_61_available_strict_heldout_stress.md
62: goal_reports/2026-06-17_62_strict_heldout_scope_audit.md
63: goal_reports/2026-06-17_63_strict_heldout_scope_goal_runner.md
64: goal_reports/2026-06-17_64_goal_status_strict_scope_gate.md
65: goal_reports/2026-06-17_65_strict_goal_status_runner_chain.md
66: goal_reports/2026-06-17_66_current_eval_strict_chain_execution.md
67: goal_reports/2026-06-17_67_replay_failure_diagnosis.md
68: goal_reports/2026-06-17_68_deployment_vs_current_eval_diagnosis.md
69: goal_reports/2026-06-17_69_strict_heldout_missing_checklist_runner.md
70: goal_reports/2026-06-17_70_strict_heldout_preflight_gate.md
71: goal_reports/2026-06-17_71_live_runtime_readiness_gate.md
72: goal_reports/2026-06-17_72_jsonl_stdin_pose_stream_adapter.md
73: goal_reports/2026-06-17_73_handmark_csv_stream_adapter.md
74: goal_reports/2026-06-17_74_right_arm_only_input_mask_probe.md
75: goal_reports/2026-06-17_75_raw_handmark_csv_stream_set_score.md
76: goal_reports/2026-06-17_76_handmark_csv_stream_set_gate.md
77: goal_reports/2026-06-17_77_goal_runner_handmark_csv_set_gate.md
78: goal_reports/2026-06-17_78_final_score_and_model_report.md
79: goal_reports/2026-06-17_79_tcn_quick_probe.md
80: goal_reports/2026-06-17_80_tcn_handmark_live_stream.md
81: goal_reports/2026-06-17_81_tcn_handmark_stream_readiness_gate.md
99: goal_reports/2026-06-17_99_strict_heldout_current_preflight.md
100: goal_reports/2026-06-17_100_goal_completion_audit_matrix.md
101: goal_reports/2026-06-17_101_strict_post_arrival_script.md
102: goal_reports/2026-06-17_102_strict_script_test_guard.md
103: goal_reports/2026-06-17_103_strict_script_csv_autodiscovery.md
104: goal_reports/2026-06-17_104_current_release_status_snapshot.md
105: goal_reports/2026-06-17_105_current_status_dashboard.md
106: goal_reports/2026-06-17_106_full_test_and_tcn_alltest_rerun.md
107: goal_reports/2026-06-17_107_current_status_exporter.md
108: goal_reports/2026-06-17_108_tcn_current_status_goal_runner_step.md
109: goal_reports/2026-06-17_109_strict_post_arrival_current_status_snapshot.md
110: goal_reports/2026-06-17_110_selected_tcn_model_card_refresh.md
next: record independent fixed-camera heldout transitions, then rerun selection scoring as strict generalization evidence
```

Strict heldout independence command:

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/strict_heldout_static_v1,dataset/strict_heldout_transitions_v1 \
  --heldout-independence-output-json outputs/right_conducting/strict_heldout_independence_v1.json \
  --heldout-independence-output-md outputs/right_conducting/strict_heldout_independence_v1.md
```

Strict heldout replay + gate command:

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence,strict-heldout-scope,strict-heldout-missing-checklist,strict-heldout-preflight,replay-selected,diagnose-replay,live-output,live-replay-gate,goal-status \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/strict_heldout_static_v1,dataset/strict_heldout_transitions_v1 \
  --heldout-independence-output-json outputs/right_conducting/strict_heldout_transition_independence_v1.json \
  --heldout-independence-output-md outputs/right_conducting/strict_heldout_transition_independence_v1.md \
  --heldout-scope-output-json outputs/right_conducting/strict_heldout_scope_v1.json \
  --heldout-scope-output-md outputs/right_conducting/strict_heldout_scope_v1.md \
  --heldout-target-static-root dataset/strict_heldout_static_v1 \
  --heldout-target-transition-root dataset/strict_heldout_transitions_v1 \
  --heldout-missing-output-json outputs/right_conducting/strict_heldout_missing_checklist_v1.json \
  --heldout-missing-output-md outputs/right_conducting/strict_heldout_missing_checklist_v1.md \
  --heldout-preflight-output-json outputs/right_conducting/strict_heldout_preflight_v1.json \
  --heldout-preflight-output-md outputs/right_conducting/strict_heldout_preflight_v1.md \
  --heldout-preflight-fail-on-no-go \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext \
  --motionbert-replay-stable-only \
  --motionbert-replay-output-json outputs/right_conducting/strict_heldout_transition_replay_v1.json \
  --motionbert-replay-output-md outputs/right_conducting/strict_heldout_transition_replay_v1.md \
  --motionbert-replay-output-rows outputs/right_conducting/strict_heldout_transition_replay_v1_rows.jsonl \
  --replay-diagnosis-output-json outputs/right_conducting/strict_heldout_transition_replay_diagnosis_v1.json \
  --replay-diagnosis-output-md outputs/right_conducting/strict_heldout_transition_replay_diagnosis_v1.md \
  --live-output-jsonl outputs/right_conducting/strict_heldout_transition_live_outputs_v1.jsonl \
  --live-output-summary-json outputs/right_conducting/strict_heldout_transition_live_outputs_v1_summary.json \
  --live-replay-gate-output-json outputs/right_conducting/strict_heldout_transition_live_gate_v1.json \
  --live-replay-gate-output-md outputs/right_conducting/strict_heldout_transition_live_gate_v1.md \
  --live-replay-gate-require-independence \
  --goal-status-output-json outputs/right_conducting/goal_status_strict_heldout_v1.json \
  --goal-status-output-md outputs/right_conducting/goal_status_strict_heldout_v1.md
```

Next devset audit command:

```bash
python tools/run_right_conducting_goal.py \
  --steps devset-audit \
  --devset-static-root dataset/static_variants_80 \
  --devset-transition-root dataset/transitions \
  --devset-output-json outputs/right_conducting/devset_edge_case_audit.json \
  --devset-output-md outputs/right_conducting/devset_edge_case_audit.md \
  --output-json outputs/right_conducting/right_conducting_goal_devset_audit.json \
  --output-md outputs/right_conducting/right_conducting_goal_devset_audit.md
```

Post-capture MotionBERT devset score command:

```bash
python tools/run_right_conducting_goal.py \
  --steps devset-audit,motionbert-devset-score,devset-gate \
  --head-output-dir outputs/right_conducting/motionbert_head_after_supply \
  --devset-static-root dataset/static_variants_80 \
  --devset-transition-root dataset/transitions \
  --devset-output-json outputs/right_conducting/devset_edge_case_audit.json \
  --devset-output-md outputs/right_conducting/devset_edge_case_audit.md \
  --devset-static-score-prefix outputs/right_conducting/motionbert_devset_static_score \
  --devset-transition-score-prefix outputs/right_conducting/motionbert_devset_transition_score \
  --devset-gate-output-prefix outputs/right_conducting/motionbert_devset_gate \
  --window-frames 60 \
  --stride-frames 3 \
  --device cuda:0 \
  --output-json outputs/right_conducting/right_conducting_goal_devset_pipeline.json \
  --output-md outputs/right_conducting/right_conducting_goal_devset_pipeline.md
```

Selected-model guard:

```text
When `devset-gate,gate,select` are run together, selection requires the matching
devset gate to be GO before a MotionBERT candidate can become SELECTED.
```

## TCN Handmark Runner

Latest report:

```text
docs/exp/goal_reports/2026-06-17_82_tcn_goal_runner_full_test.md
docs/exp/goal_reports/2026-06-17_83_selected_tcn_live_bundle.md
docs/exp/goal_reports/2026-06-17_84_webcam_overlay_recovery_and_full_tests.md
docs/exp/goal_reports/2026-06-17_85_tcn_manifest_runtime_path.md
docs/exp/goal_reports/2026-06-17_86_tcn_2beat3beat_all_test_and_strict_preflight.md
docs/exp/goal_reports/2026-06-17_87_tcn_stdin_live_output_contract.md
docs/exp/goal_reports/2026-06-17_88_tcn_readiness_gate_includes_stdin.md
docs/exp/goal_reports/2026-06-17_89_tcn_strict_heldout_post_arrival_chain.md
docs/exp/goal_reports/2026-06-17_90_live_output_jsonl_contract_gate.md
docs/exp/goal_reports/2026-06-17_91_tcn_live_final_verification_snapshot.md
docs/exp/goal_reports/2026-06-17_92_tcn_goal_status_completion_audit.md
docs/exp/goal_reports/2026-06-17_93_strict_post_arrival_final_chain.md
docs/exp/goal_reports/2026-06-17_94_tcn_live_release_handoff.md
docs/exp/goal_reports/2026-06-17_95_tcn_live_release_manifest_validation.md
docs/exp/goal_reports/2026-06-17_96_tcn_release_validation_goal_runner.md
docs/exp/goal_reports/2026-06-17_97_strict_chain_with_release_precheck.md
docs/exp/goal_reports/2026-06-17_98_full_test_rerun.md
docs/exp/goal_reports/2026-06-17_99_strict_heldout_current_preflight.md
docs/exp/goal_reports/2026-06-17_100_goal_completion_audit_matrix.md
docs/exp/goal_reports/2026-06-17_101_strict_post_arrival_script.md
docs/exp/goal_reports/2026-06-17_102_strict_script_test_guard.md
docs/exp/goal_reports/2026-06-17_103_strict_script_csv_autodiscovery.md
docs/exp/goal_reports/2026-06-17_104_current_release_status_snapshot.md
docs/exp/goal_reports/2026-06-17_105_current_status_dashboard.md
```

Current selected TCN bundle:

```text
outputs/right_conducting/selected_tcn_handmark_live45f
manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
structure: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_structure.md
checkpoint: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_head.pt
release manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json
release manifest validation: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation.json
handoff runbook: docs/exp/tcn_live_handoff_runbook.md
```

Current fixed-camera TCN goal-runner chain:

```bash
python tools/run_right_conducting_goal.py \
  --steps tcn-handmark-csv-stream,tcn-handmark-csv-set-score,tcn-handmark-csv-set-gate,tcn-handmark-csv-benchmark,tcn-handmark-stream-readiness,export-tcn-selected \
  --tcn-checkpoint outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_conducting_head.pt \
  --handmark-csv-stream-csv dataset/transitions/session_20260617_022415_bpm120to120_beat2_small.csv \
  --handmark-csv-set-root dataset/static_variants_80,dataset/transitions \
  --handmark-csv-set-stable-only \
  --device cuda:0 \
  --tcn-export-dir outputs/right_conducting/selected_tcn_handmark_live45f
```

For latest scoring, use the manifest-based 2/3-beat-only chain below. The root-based command above is kept as the export chain history.

Current manifest-based runtime chain, 2/3-beat-only:

```bash
CSV_LIST=$(python - <<'PY'
from pathlib import Path
paths = []
for root in [Path("dataset/static_variants_80"), Path("dataset/transitions")]:
    for p in sorted(root.rglob("*.csv")):
        if "beat4" in p.name:
            continue
        paths.append(str(p))
print(",".join(paths))
PY
)

python tools/run_right_conducting_goal.py \
  --steps tcn-handmark-csv-stream,tcn-handmark-csv-set-score,tcn-handmark-csv-set-gate,tcn-handmark-csv-benchmark,tcn-handmark-stream-readiness \
  --tcn-manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --handmark-csv-stream-csv dataset/transitions/session_20260617_022415_bpm120to120_beat2_small.csv \
  --handmark-csv-set-root "$CSV_LIST" \
  --handmark-csv-set-stable-only \
  --device cuda:0
```

Current result:

```text
readiness: GO
stdin live contract: GO
readiness with output contract gate: GO
TCN goal status completion audit: IN_PROGRESS, live GO, strict heldout NO_GO
strict heldout final post-arrival chain: dry-run ready with output contract and completion audit
TCN release handoff: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json
TCN release validation: GO, error_count 0
TCN release validation goal runner: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_release_validation_goal_chain.json
strict release-precheck final chain: outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_post_arrival_goal_dryrun.json
latest full test rerun report: docs/exp/goal_reports/2026-06-17_98_full_test_rerun.md
latest strict heldout current preflight: docs/exp/goal_reports/2026-06-17_99_strict_heldout_current_preflight.md
latest completion audit matrix: docs/exp/goal_reports/2026-06-17_100_goal_completion_audit_matrix.md
strict post-arrival script: scripts/run_tcn_strict_post_arrival_goal.sh
strict post-arrival script test guard: docs/exp/goal_reports/2026-06-17_102_strict_script_test_guard.md
strict post-arrival CSV autodiscovery: docs/exp/goal_reports/2026-06-17_103_strict_script_csv_autodiscovery.md
latest release/status snapshot: docs/exp/goal_reports/2026-06-17_104_current_release_status_snapshot.md
current status dashboard: docs/exp/current_status.md
latest 2/3-beat-only all-test csv_count: 11
margin 3s samples: 1824
tempo_acc / gain_acc: 1.0000 / 1.0000
80/100/120 BPM recall: 1.0000 / 1.0000 / 1.0000
JSONL output contract errors: alltest 0, stdin 0
selected checkpoint benchmark p90: 2.2745 ms
manifest runtime benchmark p90: 1.7361 ms
2/3-beat-only all-test benchmark p90: 1.9984 ms
strict heldout preflight: NO_GO, P0 0/8
Report 99 strict heldout preflight: NO_GO, heldout roots missing, P0 0/8
focused tests: test_live_output_contract.py 8 OK, test_tcn_live.py 10 OK, test_goal_command_cli.py 42 OK, test_tcn_goal_status.py 4 OK, test_tcn_release_manifest.py 3 OK
latest full unittest suite: 281 OK, 58.072s after Report 122
latest focused runner test: 44 OK, 2.846s after Report 118
latest handoff/model-card assertion: handoff_model_card_latest_assertions_ok after Report 119
latest submission/presentation assertion: submission_presentation_latest_tcn_assertions_ok after Report 120
latest release docs gate: GO, 63 checks, 0 failed after Report 121
latest release docs goal runner step: GO, focused runner 45 OK after Report 122
```

Scope note: this is fixed-camera deployment-fit evidence on supplied data, not strict independent heldout generalization. The strict roots `dataset/strict_heldout_static_v1` and `dataset/strict_heldout_transitions_v1` are still absent.
