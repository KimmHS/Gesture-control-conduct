from __future__ import annotations

from typing import Any

import numpy as np

from conductor_demo.app.state import AppState
from conductor_demo.motion.buffer import MotionBuffer
from conductor_demo.vision.tracker import TrackingResult


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
            f"{self.app_name}",
            f"camera: {camera_status}",
            f"tracker: {tracker_status}",
            motion_status,
            (
                f"playback: state={app_state.playback.mode} "
                f"track={app_state.playback.track_name} "
                f"bpm={app_state.playback.bpm:.0f} "
                f"rate={app_state.playback.rate:.2f} "
                f"volume={app_state.playback.volume:.2f} "
                f"pos={app_state.playback.position_seconds:.1f}/{app_state.playback.duration_seconds:.1f}s"
            ),
            f"dynamics: intensity={app_state.dynamics.intensity:.2f} raw={app_state.dynamics.raw_intensity:.2f}",
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
        motion_buffer: MotionBuffer,
        app_state: AppState,
        trail_length: int,
    ) -> Any:
        cv2 = _require_cv2()
        canvas = frame.copy()

        self._draw_tracking_annotations(canvas, tracking, motion_buffer, trail_length)
        self._draw_header(canvas, app_state)
        self._draw_status_stack(canvas, tracking, app_state)
        meter_y = canvas.shape[0] - 86
        if self.show_help:
            self._draw_help_strip(canvas, app_state)
            meter_y = canvas.shape[0] - 150
        self._draw_meter(
            canvas=canvas,
            label="Conducting Dynamics",
            value=app_state.dynamics.intensity,
            top_left=(24, meter_y),
            size=(300, 18),
            color=(0, 200, 255),
        )
        self._draw_meter(
            canvas=canvas,
            label=f"Volume {app_state.playback.volume * 100:.0f}%",
            value=app_state.playback.volume,
            top_left=(24, meter_y + 38),
            size=(300, 18),
            color=(40, 220, 120),
        )

        return canvas

    def _draw_tracking_annotations(
        self,
        canvas: Any,
        tracking: TrackingResult,
        motion_buffer: MotionBuffer,
        trail_length: int,
    ) -> None:
        cv2 = _require_cv2()
        points = motion_buffer.points(limit=trail_length)
        if len(points) > 1:
            for index in range(1, len(points)):
                blend = index / max(len(points) - 1, 1)
                color = (
                    int(40 + 120 * blend),
                    int(120 + 80 * blend),
                    int(255 - 40 * blend),
                )
                thickness = 1 + int(3 * blend)
                cv2.line(canvas, points[index - 1], points[index], color, thickness, cv2.LINE_AA)

        if self.show_landmarks and tracking.landmarks_px:
            for point in tracking.landmarks_px:
                cv2.circle(canvas, point, 2, (180, 180, 180), -1, cv2.LINE_AA)

        if tracking.bbox is not None:
            x1, y1, x2, y2 = tracking.bbox
            color = self._status_color(tracking.mode, tracking.tracking_ok)
            cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)
            badge_text, _, _ = self._tracking_status(tracking)
            self._draw_badge(canvas, badge_text, (x1, max(8, y1 - 30)), color)

        if tracking.wrist_px is not None:
            wrist = (int(tracking.wrist_px[0]), int(tracking.wrist_px[1]))
            color = self._status_color(tracking.mode, tracking.tracking_ok)
            if tracking.raw_wrist_px is not None:
                raw_wrist = (int(tracking.raw_wrist_px[0]), int(tracking.raw_wrist_px[1]))
                cv2.circle(canvas, raw_wrist, 4, (0, 140, 255), -1, cv2.LINE_AA)
            cv2.circle(canvas, wrist, 18, color, 2, cv2.LINE_AA)
            cv2.circle(canvas, wrist, 8, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.circle(canvas, wrist, 3, color, -1, cv2.LINE_AA)

    def _draw_header(self, canvas: Any, app_state: AppState) -> None:
        self._draw_panel(canvas, (18, 18), (420, 74))
        cv2 = _require_cv2()
        cv2.putText(canvas, self.app_name, (34, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.95, (255, 255, 255), 2, cv2.LINE_AA)
        subtitle = "Your conducting motion is shaping the music live"
        cv2.putText(canvas, subtitle, (34, 77), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1, cv2.LINE_AA)

    def _draw_status_stack(self, canvas: Any, tracking: TrackingResult, app_state: AppState) -> None:
        width = 316
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

        tracking_title, tracking_detail, tracking_color = self._tracking_status(tracking)
        self._draw_info_card(
            canvas=canvas,
            top_left=(x, y),
            size=(width, 86),
            title="Tracking",
            value=tracking_title,
            detail=tracking_detail,
            accent=tracking_color,
        )

        y += 86 + gap
        tempo_detail = f"Manual tempo keys [ ]  Rate x{app_state.playback.rate:.2f}"
        if (
            app_state.calibration.tempo_motion_floor_px is not None
            and app_state.calibration.tempo_motion_ceiling_px is not None
        ):
            tempo_detail = (
                f"Manual [ ]  Cue gate {app_state.calibration.tempo_motion_floor_px:.0f}-"
                f"{app_state.calibration.tempo_motion_ceiling_px:.0f}px  "
                f"x{app_state.playback.rate:.2f}"
            )
        self._draw_info_card(
            canvas=canvas,
            top_left=(x, y),
            size=(width, 86),
            title="Tempo",
            value=f"{app_state.playback.bpm:.0f} BPM",
            detail=tempo_detail,
            accent=(255, 190, 0),
        )

        y += 86 + gap
        dynamics_detail = f"Volume {app_state.playback.volume * 100:.0f}% from conducting intensity"
        self._draw_info_card(
            canvas=canvas,
            top_left=(x, y),
            size=(width, 92),
            title="Dynamics",
            value=f"{app_state.dynamics.intensity * 100:.0f}%",
            detail=dynamics_detail,
            accent=(0, 200, 255),
        )
        self._draw_meter(
            canvas=canvas,
            label="",
            value=app_state.dynamics.intensity,
            top_left=(x + 18, y + 58),
            size=(width - 36, 14),
            color=(0, 200, 255),
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
            secondary = f"Calibration {app_state.calibration.progress * 100:.0f}% complete. Keep your hand visible."
        elif app_state.calibration.enabled and not app_state.calibration.calibrated:
            primary = "Press C for a quick 3-second calibration before you start"
            secondary = "Hold still briefly, then move in your comfortable conducting range"
        else:
            primary = "Move your hand wider to raise dynamics and volume"
            secondary = self._short_instructions(app_state)
        cv2.putText(canvas, primary, (x + 16, y + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(canvas, secondary, (x + 16, y + 49), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)

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
        cv2.putText(canvas, detail[:56], (x + 16, y + height - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (235, 235, 235), 1, cv2.LINE_AA)

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
        width = max(94, 16 + len(text) * 9)
        height = 24
        self._draw_panel(canvas, (x, y), (width, height), alpha=0.78)
        cv2.rectangle(canvas, (x, y), (x + width, y + height), color, 2)
        cv2.putText(canvas, text, (x + 8, y + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)

    def _tracking_status(self, tracking: TrackingResult) -> tuple[str, str, tuple[int, int, int]]:
        if tracking.mode == "live" and tracking.tracking_ok:
            detail = f"{tracking.active_hand or 'Hand'} tracked  {tracking.confidence * 100:.0f}% confidence"
            return "TRACKING", detail, (40, 220, 80)
        if tracking.mode == "hold":
            detail = "Brief loss handled. Last stable wrist is being held"
            return "HOLD", detail, (0, 215, 255)
        if tracking.mode == "live":
            detail = f"Hand found but low confidence  {tracking.confidence * 100:.0f}%"
            return "LOW CONF", detail, (255, 200, 0)
        return "SEARCHING", "Show one clear conducting hand to the camera", (120, 120, 220)

    def _status_color(self, mode: str, tracking_ok: bool) -> tuple[int, int, int]:
        if mode == "live" and tracking_ok:
            return (40, 220, 40)
        if mode == "hold":
            return (0, 215, 255)
        if mode == "live":
            return (255, 200, 0)
        return (40, 40, 220)

    def _playback_state_color(self, mode: str) -> tuple[int, int, int]:
        if mode == "playing":
            return (40, 220, 80)
        if mode == "paused":
            return (0, 215, 255)
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
                (0, 200, 255),
            )
        if calibration.calibrated:
            tempo_gate = "-"
            if calibration.tempo_motion_floor_px is not None and calibration.tempo_motion_ceiling_px is not None:
                tempo_gate = f"{calibration.tempo_motion_floor_px:.0f}-{calibration.tempo_motion_ceiling_px:.0f}px"
            detail = (
                f"Range {calibration.comfortable_motion_span_px or 0.0:.0f}px  "
                f"Tempo gate {tempo_gate}  Press C to recalibrate"
            )
            return ("Calibration", "CALIBRATED", detail, (40, 220, 120))
        return (
            "Calibration",
            "READY",
            "Press C to capture your neutral pose and comfortable motion range",
            (180, 180, 180),
        )

    def _short_instructions(self, app_state: AppState) -> str:
        if app_state.calibration.enabled:
            return "C calibrate   S start   P pause   G resume   Space toggle   R reset   [ ] tempo"
        return "S start   P pause   G resume   Space toggle   R reset   [ ] tempo"

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
