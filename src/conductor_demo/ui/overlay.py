from __future__ import annotations

from typing import Any

from conductor_demo.app.state import AppState, HandRoleState
from conductor_demo.motion.buffer import MotionBuffer
from conductor_demo.vision.tracker import TrackingResult, TrackedHand


TEMPO_COLOR = (0, 190, 255)
DYNAMICS_COLOR = (255, 210, 60)
CUE_COLOR = (70, 225, 130)
HOLD_COLOR = (0, 215, 255)
LOW_CONF_COLOR = (255, 200, 0)
SEARCH_COLOR = (120, 120, 220)


def _require_cv2() -> Any:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("OpenCV is required. Install dependencies with `pip install -r requirements.txt`.") from exc
    return cv2


class OverlayRenderer:
    """Presentation-friendly live overlay for the conducting demo."""

    def __init__(self, app_name: str, show_landmarks: bool = True, show_help: bool = True) -> None:
        self.app_name = app_name
        self.show_landmarks = show_landmarks
        self.show_help = show_help

    def render_status(
        self,
        app_state: AppState,
        camera_status: str,
        tracker_status: str,
        motion_status: str,
    ) -> str:
        lines = [
            self.app_name,
            f"camera: {camera_status}",
            f"tracker: {tracker_status}",
            motion_status,
            (
                f"roles: right tempo+dynamics={app_state.tempo_hand.status_text} "
                f"left cue={app_state.cue_hand.status_text}"
            ),
            (
                f"cue: target={app_state.cue.selected_label} "
                f"active={len(app_state.cue.active_indices)}/{app_state.cue.slot_count} "
                f"pending={app_state.cue.pending_label or '-'} "
                f"progress={app_state.cue.selection_progress:.2f}"
            ),
            (
                f"playback: state={app_state.playback.mode} "
                f"track={app_state.playback.track_name} "
                f"bpm={app_state.playback.bpm:.0f} "
                f"rate={app_state.playback.rate:.2f} "
                f"volume={app_state.playback.volume:.2f} "
                f"pos={app_state.playback.position_seconds:.1f}/{app_state.playback.duration_seconds:.1f}s"
            ),
            (
                f"tempo: rate={app_state.tempo.rate:.2f} "
                f"raw={app_state.tempo.raw_rate:.2f} "
                f"energy={app_state.tempo.motion_energy_px:.1f}px "
                f"norm={app_state.tempo.normalized_motion:.2f}"
            ),
            (
                f"dynamics: intensity={app_state.dynamics.intensity:.2f} "
                f"raw={app_state.dynamics.raw_intensity:.2f} "
                f"span={app_state.dynamics.span_px:.1f}px"
            ),
            (
                f"calibration: active={app_state.calibration.active} "
                f"calibrated={app_state.calibration.calibrated} "
                f"progress={app_state.calibration.progress:.2f}"
            ),
            f"fallback: {app_state.fallback_hint}",
        ]
        return "\n".join(lines)

    def draw_debug(
        self,
        frame: Any,
        tracking: TrackingResult,
        app_state: AppState,
        trail_length: int,
        motion_buffer: MotionBuffer | None = None,
        tempo_motion_buffer: MotionBuffer | None = None,
        dynamics_motion_buffer: MotionBuffer | None = None,
    ) -> Any:
        canvas = frame.copy()

        self._draw_tracking_annotations(
            canvas=canvas,
            tracking=tracking,
            trail_length=trail_length,
            motion_buffer=motion_buffer,
            tempo_motion_buffer=tempo_motion_buffer,
            dynamics_motion_buffer=dynamics_motion_buffer,
        )
        self._draw_header(canvas)
        self._draw_status_stack(canvas, tracking, app_state)

        meter_y = canvas.shape[0] - 86
        if self.show_help:
            self._draw_help_strip(canvas, app_state)
            meter_y = canvas.shape[0] - 150

        self._draw_cue_selector(
            canvas=canvas,
            app_state=app_state,
            top_left=(24, meter_y - 86),
            size=(520, 64),
        )
        self._draw_meter(
            canvas=canvas,
            label=f"Right-Hand Tempo x{app_state.playback.rate:.2f}",
            value=app_state.tempo.normalized_motion,
            top_left=(24, meter_y),
            size=(320, 18),
            color=TEMPO_COLOR,
        )
        self._draw_meter(
            canvas=canvas,
            label=f"Right-Hand Dynamics {app_state.dynamics.intensity * 100:.0f}%",
            value=app_state.dynamics.intensity,
            top_left=(24, meter_y + 40),
            size=(320, 18),
            color=DYNAMICS_COLOR,
        )
        return canvas

    def _draw_tracking_annotations(
        self,
        canvas: Any,
        tracking: TrackingResult,
        trail_length: int,
        motion_buffer: MotionBuffer | None = None,
        tempo_motion_buffer: MotionBuffer | None = None,
        dynamics_motion_buffer: MotionBuffer | None = None,
    ) -> None:
        if tempo_motion_buffer is not None or dynamics_motion_buffer is not None:
            self._draw_trail(canvas, tempo_motion_buffer, trail_length, TEMPO_COLOR)
            self._draw_trail(canvas, dynamics_motion_buffer, trail_length, DYNAMICS_COLOR)
        else:
            self._draw_trail(canvas, motion_buffer, trail_length, (120, 180, 255))

        hands = list(tracking.hands.values()) if tracking.hands else []
        if not hands and tracking.bbox is not None:
            hands = [
                TrackedHand(
                    label=tracking.active_hand or "Hand",
                    tracking_ok=tracking.tracking_ok,
                    mode=tracking.mode,
                    confidence=tracking.confidence,
                    wrist_px=tracking.wrist_px,
                    raw_wrist_px=tracking.raw_wrist_px,
                    hand_scale_px=tracking.hand_scale_px,
                    bbox=tracking.bbox,
                    landmarks_px=tracking.landmarks_px,
                )
            ]

        for hand in hands:
            self._draw_hand(canvas, hand)

    def _draw_trail(
        self,
        canvas: Any,
        motion_buffer: MotionBuffer | None,
        trail_length: int,
        color: tuple[int, int, int],
    ) -> None:
        if motion_buffer is None:
            return

        cv2 = _require_cv2()
        points = motion_buffer.points(limit=trail_length)
        if len(points) < 2:
            return

        for index in range(1, len(points)):
            blend = index / max(len(points) - 1, 1)
            trail_color = (
                int(color[0] * (0.45 + 0.55 * blend)),
                int(color[1] * (0.45 + 0.55 * blend)),
                int(color[2] * (0.45 + 0.55 * blend)),
            )
            thickness = 1 + int(3 * blend)
            cv2.line(canvas, points[index - 1], points[index], trail_color, thickness, cv2.LINE_AA)

    def _draw_hand(self, canvas: Any, hand: TrackedHand) -> None:
        cv2 = _require_cv2()
        color = self._hand_color(hand)

        if self.show_landmarks and hand.landmarks_px:
            for point in hand.landmarks_px:
                cv2.circle(canvas, point, 2, (210, 210, 210), -1, cv2.LINE_AA)

        if hand.bbox is not None:
            x1, y1, x2, y2 = hand.bbox
            cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)
            self._draw_badge(canvas, self._hand_badge(hand), (x1, max(8, y1 - 30)), color)

        if hand.wrist_px is not None:
            wrist = (int(hand.wrist_px[0]), int(hand.wrist_px[1]))
            if hand.raw_wrist_px is not None:
                raw_wrist = (int(hand.raw_wrist_px[0]), int(hand.raw_wrist_px[1]))
                cv2.circle(canvas, raw_wrist, 4, color, -1, cv2.LINE_AA)
            cv2.circle(canvas, wrist, 18, color, 2, cv2.LINE_AA)
            cv2.circle(canvas, wrist, 8, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.circle(canvas, wrist, 3, color, -1, cv2.LINE_AA)

    def _draw_header(self, canvas: Any) -> None:
        self._draw_panel(canvas, (18, 18), (480, 74))
        cv2 = _require_cv2()
        cv2.putText(canvas, self.app_name, (34, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.95, (255, 255, 255), 2, cv2.LINE_AA)
        subtitle = "Right hand shapes tempo and dynamics, left hand is reserved for cueing"
        cv2.putText(canvas, subtitle, (34, 77), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1, cv2.LINE_AA)

    def _draw_status_stack(self, canvas: Any, tracking: TrackingResult, app_state: AppState) -> None:
        width = 336
        x = canvas.shape[1] - width - 18
        y = 18
        gap = 14

        if app_state.calibration.enabled:
            calibration_title, calibration_value, calibration_detail, calibration_color = self._calibration_status(app_state)
            self._draw_info_card(
                canvas=canvas,
                top_left=(x, y),
                size=(width, 96),
                title=calibration_title,
                value=calibration_value,
                detail=calibration_detail,
                accent=calibration_color,
            )
            self._draw_meter(
                canvas=canvas,
                label="",
                value=app_state.calibration.progress if app_state.calibration.active else float(app_state.calibration.calibrated),
                top_left=(x + 18, y + 62),
                size=(width - 36, 14),
                color=calibration_color,
            )
            y += 96 + gap

        tracking_title, tracking_detail, tracking_color = self._tracking_status(tracking, app_state)
        self._draw_info_card(
            canvas=canvas,
            top_left=(x, y),
            size=(width, 92),
            title="Tracking",
            value=tracking_title,
            detail=tracking_detail,
            accent=tracking_color,
        )

        y += 92 + gap
        tempo_detail = (
            f"Right hand {app_state.tempo_hand.status_text}  "
            f"Energy {app_state.tempo.motion_energy_px:.0f}px  "
            f"Gate {app_state.tempo.floor_px:.0f}-{app_state.tempo.ceiling_px:.0f}px"
        )
        self._draw_info_card(
            canvas=canvas,
            top_left=(x, y),
            size=(width, 92),
            title="Tempo",
            value=f"{app_state.playback.bpm:.0f} BPM",
            detail=tempo_detail,
            accent=TEMPO_COLOR,
        )
        self._draw_meter(
            canvas=canvas,
            label="",
            value=app_state.tempo.normalized_motion,
            top_left=(x + 18, y + 58),
            size=(width - 36, 14),
            color=TEMPO_COLOR,
        )

        y += 92 + gap
        dynamics_detail = (
            f"Right hand {app_state.dynamics_hand.status_text}  "
            f"Span {app_state.dynamics.span_px:.0f}/{app_state.dynamics.reference_span_px:.0f}px  "
            f"Vol {app_state.playback.volume * 100:.0f}%"
        )
        self._draw_info_card(
            canvas=canvas,
            top_left=(x, y),
            size=(width, 92),
            title="Dynamics",
            value=f"{app_state.dynamics.intensity * 100:.0f}%",
            detail=dynamics_detail,
            accent=DYNAMICS_COLOR,
        )
        self._draw_meter(
            canvas=canvas,
            label="",
            value=app_state.dynamics.intensity,
            top_left=(x + 18, y + 58),
            size=(width - 36, 14),
            color=DYNAMICS_COLOR,
        )

        y += 92 + gap
        playback_color = self._playback_state_color(app_state.playback.mode)
        playback_detail = (
            f"{app_state.playback.track_name}  "
            f"{app_state.playback.position_seconds:.1f}/{app_state.playback.duration_seconds:.1f}s"
        )
        self._draw_info_card(
            canvas=canvas,
            top_left=(x, y),
            size=(width, 98),
            title="Playback",
            value=app_state.playback.status_text,
            detail=playback_detail,
            accent=playback_color,
        )
        progress = 0.0
        if app_state.playback.duration_seconds > 0:
            progress = app_state.playback.position_seconds / app_state.playback.duration_seconds
        self._draw_meter(
            canvas=canvas,
            label="",
            value=progress,
            top_left=(x + 18, y + 64),
            size=(width - 36, 14),
            color=playback_color,
        )

    def _draw_help_strip(self, canvas: Any, app_state: AppState) -> None:
        cv2 = _require_cv2()
        panel_height = 64
        top_left = (18, canvas.shape[0] - panel_height - 18)
        size = (canvas.shape[1] - 36, panel_height)
        self._draw_panel(canvas, top_left, size, alpha=0.7)
        x, y = top_left

        if app_state.calibration.active:
            primary = app_state.calibration.status_detail
            secondary = f"Calibration {app_state.calibration.progress * 100:.0f}% complete. Keep your right hand visible."
        elif app_state.calibration.enabled and not app_state.calibration.calibrated:
            primary = "Press C for right-hand calibration before you start"
            secondary = "Hold your right hand still briefly, then conduct naturally with that hand"
        else:
            primary = "Right hand controls tempo and dynamics. Left hand is reserved for cueing."
            secondary = self._short_instructions(app_state)
        cv2.putText(canvas, primary, (x + 16, y + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(canvas, secondary, (x + 16, y + 49), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)

    def _draw_cue_selector(
        self,
        canvas: Any,
        app_state: AppState,
        top_left: tuple[int, int],
        size: tuple[int, int],
    ) -> None:
        cue = app_state.cue
        if not cue.enabled or cue.slot_count <= 0:
            return

        cv2 = _require_cv2()
        x, y = top_left
        width, height = size
        self._draw_panel(canvas, top_left, size)
        cv2.rectangle(canvas, (x, y), (x + width, y + height), CUE_COLOR, 2)

        target_text = f"Cue Target: {cue.selected_label}"
        if cue.pending_label is not None:
            target_text += f"  ->  {cue.pending_label}"
        cv2.putText(canvas, target_text, (x + 14, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1, cv2.LINE_AA)

        lane_x = x + 12
        lane_y = y + 30
        lane_width = width - 24
        lane_height = 22
        slot_width = lane_width / cue.slot_count

        for index, label in enumerate(cue.labels[: cue.slot_count]):
            x1 = int(lane_x + index * slot_width)
            x2 = int(lane_x + (index + 1) * slot_width)
            is_active = index in cue.active_indices
            fill = (55, 55, 55) if not is_active else (36, 92, 58)
            border = (130, 130, 130)
            text_color = (210, 210, 210)
            if cue.selected_index == index:
                fill = CUE_COLOR if is_active else (160, 110, 32)
                border = CUE_COLOR
                text_color = (15, 15, 15) if is_active else (245, 245, 245)
            elif cue.pending_index == index:
                fill = (
                    int(45 + CUE_COLOR[0] * cue.selection_progress),
                    int(45 + CUE_COLOR[1] * cue.selection_progress),
                    int(45 + CUE_COLOR[2] * cue.selection_progress),
                )
                border = CUE_COLOR
                text_color = (20, 20, 20) if cue.selection_progress > 0.65 else (230, 230, 230)

            cv2.rectangle(canvas, (x1, lane_y), (x2, lane_y + lane_height), fill, -1)
            cv2.rectangle(canvas, (x1, lane_y), (x2, lane_y + lane_height), border, 2)
            cv2.putText(
                canvas,
                label,
                (x1 + 8, lane_y + 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.42,
                text_color,
                1,
                cv2.LINE_AA,
            )

        if cue.tracking_ok and cue.cue_x_px is not None and cue.frame_width > 0:
            normalized = max(0.0, min(cue.cue_x_px / cue.frame_width, 1.0))
            marker_x = int(lane_x + normalized * lane_width)
            cv2.line(canvas, (marker_x, lane_y - 4), (marker_x, lane_y + lane_height + 4), (255, 255, 255), 2, cv2.LINE_AA)

        footer = "Move the left wrist across 5 lanes, Q toggles selected group, A restores all"
        if cue.pending_label is not None:
            footer = f"Switching to {cue.pending_label} {cue.selection_progress * 100:.0f}%"
        elif cue.tracking_ok:
            status = "active" if cue.selected_index in cue.active_indices else "muted"
            footer = f"Selected {cue.selected_label} ({status})"
        cv2.putText(canvas, footer, (x + 14, y + height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (220, 220, 220), 1, cv2.LINE_AA)

    def _draw_info_card(
        self,
        canvas: Any,
        top_left: tuple[int, int],
        size: tuple[int, int],
        title: str,
        value: str,
        detail: str,
        accent: tuple[int, int, int],
    ) -> None:
        cv2 = _require_cv2()
        x, y = top_left
        width, height = size
        self._draw_panel(canvas, top_left, size)
        cv2.rectangle(canvas, (x, y), (x + width, y + height), accent, 2)
        cv2.putText(canvas, title.upper(), (x + 16, y + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (215, 215, 215), 1, cv2.LINE_AA)
        cv2.putText(canvas, value, (x + 16, y + 54), cv2.FONT_HERSHEY_SIMPLEX, 0.9, accent, 2, cv2.LINE_AA)
        cv2.putText(canvas, detail[:60], (x + 16, y + height - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (235, 235, 235), 1, cv2.LINE_AA)

    def _draw_panel(
        self,
        canvas: Any,
        top_left: tuple[int, int],
        size: tuple[int, int],
        alpha: float = 0.6,
        fill: tuple[int, int, int] = (20, 20, 20),
    ) -> None:
        cv2 = _require_cv2()
        x, y = top_left
        width, height = size
        overlay = canvas.copy()
        cv2.rectangle(overlay, (x, y), (x + width, y + height), fill, -1)
        cv2.addWeighted(overlay, alpha, canvas, 1.0 - alpha, 0.0, canvas)

    def _draw_badge(
        self,
        canvas: Any,
        text: str,
        top_left: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        cv2 = _require_cv2()
        x, y = top_left
        width = max(110, 16 + len(text) * 9)
        height = 24
        self._draw_panel(canvas, (x, y), (width, height), alpha=0.78)
        cv2.rectangle(canvas, (x, y), (x + width, y + height), color, 2)
        cv2.putText(canvas, text, (x + 8, y + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)

    def _tracking_status(
        self,
        tracking: TrackingResult,
        app_state: AppState,
    ) -> tuple[str, str, tuple[int, int, int]]:
        right = app_state.tempo_hand
        left = app_state.cue_hand
        if right.tracking_ok and left.tracking_ok:
            detail = (
                f"Right control {right.confidence * 100:.0f}%  "
                f"Left cue {left.confidence * 100:.0f}%"
            )
            return "CONTROL + CUE", detail, (40, 220, 80)
        if right.mode == "hold":
            return "HOLD", "Right-hand control briefly dropped. Last stable wrist is being held.", HOLD_COLOR
        if right.tracking_ok:
            detail = f"Right control {right.confidence * 100:.0f}%  Left cue {left.status_text}"
            return "CONTROL READY", detail, (40, 220, 80)
        if right.mode == "live" or left.mode == "live":
            detail = (
                f"Right control {right.status_text}  "
                f"Left cue {left.status_text}"
            )
            return "PARTIAL", detail, LOW_CONF_COLOR
        if tracking.debug_message:
            return "SEARCHING", "Show your right hand clearly to the camera", SEARCH_COLOR
        return "SEARCHING", "Show your right hand clearly to the camera", SEARCH_COLOR

    def _hand_color(self, hand: TrackedHand) -> tuple[int, int, int]:
        if hand.mode == "hold":
            return HOLD_COLOR
        if hand.mode == "live" and not hand.tracking_ok:
            return LOW_CONF_COLOR
        if hand.label == "Right":
            return TEMPO_COLOR
        if hand.label == "Left":
            return CUE_COLOR
        return SEARCH_COLOR

    def _hand_badge(self, hand: TrackedHand) -> str:
        role = "TEMPO/DYN" if hand.label == "Right" else "CUE" if hand.label == "Left" else "HAND"
        return f"{hand.label.upper()} {role}"

    def _playback_state_color(self, mode: str) -> tuple[int, int, int]:
        if mode == "playing":
            return (40, 220, 80)
        if mode == "paused":
            return HOLD_COLOR
        if mode == "ended":
            return (255, 180, 0)
        if mode == "error":
            return (60, 60, 240)
        return (180, 180, 180)

    def _calibration_status(self, app_state: AppState) -> tuple[str, str, str, tuple[int, int, int]]:
        calibration = app_state.calibration
        if calibration.active:
            return (
                "Calibration",
                calibration.status_text,
                calibration.status_detail,
                TEMPO_COLOR,
            )
        if calibration.calibrated:
            tempo_gate = "-"
            if calibration.tempo_motion_floor_px is not None and calibration.tempo_motion_ceiling_px is not None:
                tempo_gate = f"{calibration.tempo_motion_floor_px:.0f}-{calibration.tempo_motion_ceiling_px:.0f}px"
            detail = (
                f"Right range {calibration.comfortable_motion_span_px or 0.0:.0f}px  "
                f"Right gate {tempo_gate}  Press C to recalibrate"
            )
            return ("Calibration", "CALIBRATED", detail, (40, 220, 120))
        return (
            "Calibration",
            "READY",
            "Press C to calibrate right-hand tempo and dynamics",
            (180, 180, 180),
        )

    def _short_instructions(self, app_state: AppState) -> str:
        if app_state.calibration.enabled:
            return "C calibrate   Q cue toggle   A all on   S start   P pause   G resume   [ ] tempo trim"
        return "Q cue toggle   A all on   S start   P pause   G resume   [ ] tempo trim"

    def _draw_meter(
        self,
        canvas: Any,
        label: str,
        value: float,
        top_left: tuple[int, int],
        size: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        cv2 = _require_cv2()
        x, y = top_left
        width, height = size
        clamped = max(0.0, min(1.0, value))
        fill_width = int(width * clamped)

        if label:
            cv2.putText(canvas, label, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.rectangle(canvas, (x, y), (x + width, y + height), (180, 180, 180), 2)
        if fill_width > 0:
            cv2.rectangle(canvas, (x + 2, y + 2), (x + fill_width - 2, y + height - 2), color, -1)
