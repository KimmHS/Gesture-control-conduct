from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from math import hypot
from typing import Any

from conductor_demo.motion.buffer import MotionBuffer


INDEX_TIP = 8


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class Section(str, Enum):
    NONE = "NONE"
    STRINGS = "STRINGS"
    WOODWINDS = "WOODWINDS"
    BRASS = "BRASS"
    PERCUSSION = "PERCUSSION"
    TUTTI = "TUTTI"


PLAYABLE_SECTIONS = [
    Section.STRINGS,
    Section.WOODWINDS,
    Section.BRASS,
    Section.PERCUSSION,
    Section.TUTTI,
]


@dataclass(frozen=True, slots=True)
class Rect:
    x1: int
    y1: int
    x2: int
    y2: int

    def contains(self, point: tuple[int, int]) -> bool:
        x, y = point
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2


@dataclass(slots=True)
class MappingState:
    selected_section: Section = Section.TUTTI
    left_gesture: str = "LH_LOST"
    right_gesture: str = "RH_LOST"
    right_dynamic_label: str = "NORMAL"
    right_intensity: float = 0.0
    downbeat: bool = False
    command: str = "CMD_NONE"
    last_feedback: str = "READY"
    section_expression: dict[str, int] = field(
        default_factory=lambda: {
            section.value: 80 for section in PLAYABLE_SECTIONS
        }
    )


def make_zones(width: int, height: int) -> dict[Section, Rect]:
    margin = int(width * 0.04)
    gap = int(width * 0.015)
    top_y1 = int(height * 0.05)
    top_y2 = int(height * 0.22)
    zone_w = int((width - 2 * margin - 3 * gap) / 4)

    zones: dict[Section, Rect] = {}
    for index, section in enumerate(
        [
            Section.STRINGS,
            Section.WOODWINDS,
            Section.BRASS,
            Section.PERCUSSION,
        ]
    ):
        x1 = margin + index * (zone_w + gap)
        zones[section] = Rect(x1, top_y1, x1 + zone_w, top_y2)

    zones[Section.TUTTI] = Rect(
        int(width * 0.36),
        int(height * 0.27),
        int(width * 0.64),
        int(height * 0.39),
    )
    return zones


class TwoHandMapper:
    """Map left-hand section selection and right-hand conducting motion."""

    def __init__(self) -> None:
        self.state = MappingState()
        self.left_dwell_seconds = 0.25
        self.left_hold_seconds = 0.75
        self.downbeat_window_seconds = 0.24
        self.downbeat_cooldown_seconds = 0.30
        self.min_downward_velocity_px_s = 240.0
        self._candidate_section = Section.NONE
        self._candidate_since = 0.0
        self._last_left_target_time = 0.0
        self._last_downbeat_time = -999.0

    def reset(self) -> None:
        self.state = MappingState()
        self._candidate_section = Section.NONE
        self._candidate_since = 0.0
        self._last_left_target_time = 0.0
        self._last_downbeat_time = -999.0

    def update(
        self,
        *,
        frame_size: tuple[int, int],
        timestamp: float,
        left_hand: Any | None,
        right_hand: Any | None,
        right_motion: MotionBuffer,
    ) -> MappingState:
        width, height = frame_size
        zones = make_zones(width, height)
        pointed_section = self._left_pointing_target(left_hand=left_hand, zones=zones)
        self._update_selected_section(pointed_section=pointed_section, timestamp=timestamp)

        if left_hand is None:
            self.state.left_gesture = "LH_LOST"
        elif pointed_section == Section.NONE:
            self.state.left_gesture = "LH_IDLE"
        else:
            self.state.left_gesture = f"LH_POINT_{pointed_section.value}"

        if right_hand is None:
            self.state.right_gesture = "RH_LOST"
            self.state.right_dynamic_label = "LOST"
            self.state.right_intensity = 0.0
            self.state.downbeat = False
            self.state.command = "CMD_NONE"
            self.state.last_feedback = "RIGHT HAND LOST"
            return self._snapshot()

        intensity, dynamic_label = self._right_intensity(
            right_hand=right_hand,
            right_motion=right_motion,
            timestamp=timestamp,
        )
        downbeat = self._right_downbeat(
            right_hand=right_hand,
            right_motion=right_motion,
            timestamp=timestamp,
        )

        selected = self.state.selected_section
        if selected == Section.NONE:
            selected = Section.TUTTI

        expression_value = int(round(30 + intensity * 97))
        expression_value = int(clamp(expression_value, 0, 127))

        if selected == Section.TUTTI:
            for section in PLAYABLE_SECTIONS:
                self.state.section_expression[section.value] = expression_value
        else:
            self.state.section_expression[selected.value] = expression_value

        self.state.right_intensity = intensity
        self.state.right_dynamic_label = dynamic_label
        self.state.downbeat = downbeat

        if downbeat:
            self.state.right_gesture = "RH_DOWNBEAT"
            self.state.command = f"CMD_CUE_{selected.value}"
            self.state.last_feedback = f"CUE {selected.value}"
        else:
            self.state.right_gesture = f"RH_DYN_{dynamic_label}"
            self.state.command = f"CMD_SET_{selected.value}_EXPRESSION_{expression_value}"
            self.state.last_feedback = f"{selected.value} {dynamic_label} {expression_value}"

        return self._snapshot()

    def _snapshot(self) -> MappingState:
        return replace(
            self.state,
            section_expression=dict(self.state.section_expression),
        )

    def _left_pointing_target(
        self,
        *,
        left_hand: Any | None,
        zones: dict[Section, Rect],
    ) -> Section:
        if left_hand is None:
            return Section.NONE

        landmarks = getattr(left_hand, "landmarks_px", None)
        if not landmarks or len(landmarks) <= INDEX_TIP:
            return Section.NONE

        index_tip = landmarks[INDEX_TIP]
        for section, rect in zones.items():
            if rect.contains(index_tip):
                return section
        return Section.NONE

    def _update_selected_section(
        self,
        *,
        pointed_section: Section,
        timestamp: float,
    ) -> None:
        if pointed_section == Section.NONE:
            if timestamp - self._last_left_target_time > self.left_hold_seconds:
                self.state.selected_section = Section.TUTTI
            return

        self._last_left_target_time = timestamp
        if pointed_section != self._candidate_section:
            self._candidate_section = pointed_section
            self._candidate_since = timestamp
            return

        if timestamp - self._candidate_since >= self.left_dwell_seconds:
            self.state.selected_section = pointed_section

    def _right_intensity(
        self,
        *,
        right_hand: Any,
        right_motion: MotionBuffer,
        timestamp: float,
    ) -> tuple[float, str]:
        samples = right_motion.recent_samples(now=timestamp, window_seconds=0.35)
        if len(samples) < 3:
            return 0.0, "SOFT"

        xs = [sample.x for sample in samples]
        ys = [sample.y for sample in samples]
        span = hypot(max(xs) - min(xs), max(ys) - min(ys))
        hand_scale_px = getattr(right_hand, "hand_scale_px", None) or 50.0
        reference_span = max(hand_scale_px * 2.4, 70.0)
        intensity = clamp(span / reference_span, 0.0, 1.0)

        if intensity < 0.35:
            label = "SOFT"
        elif intensity < 0.65:
            label = "NORMAL"
        else:
            label = "LOUD"
        return intensity, label

    def _right_downbeat(
        self,
        *,
        right_hand: Any,
        right_motion: MotionBuffer,
        timestamp: float,
    ) -> bool:
        if timestamp - self._last_downbeat_time < self.downbeat_cooldown_seconds:
            return False

        samples = right_motion.recent_samples(
            now=timestamp,
            window_seconds=self.downbeat_window_seconds,
        )
        if len(samples) < 3:
            return False

        first = samples[0]
        latest = samples[-1]
        dt = max(1e-3, latest.timestamp - first.timestamp)
        dy = latest.y - first.y

        xs = [sample.x for sample in samples]
        ys = [sample.y for sample in samples]
        x_span = max(xs) - min(xs)
        y_span = max(ys) - min(ys)

        hand_scale_px = getattr(right_hand, "hand_scale_px", None) or 50.0
        motion_floor = max(hand_scale_px * 0.75, 45.0)
        is_downbeat = (
            dy > motion_floor * 0.60
            and y_span > motion_floor
            and y_span > x_span * 1.10
            and dy / dt > self.min_downward_velocity_px_s
        )

        if is_downbeat:
            self._last_downbeat_time = timestamp
        return is_downbeat


def draw_mapping_overlay(
    frame: Any,
    state: MappingState,
    score_state: Any | None = None,
) -> Any:
    try:
        import cv2
    except ImportError:
        return frame

    height, width = frame.shape[:2]
    zones = make_zones(width, height)

    for section, rect in zones.items():
        selected = section == state.selected_section
        color = (80, 220, 80) if selected else (120, 120, 120)
        thickness = 3 if selected else 1
        cv2.rectangle(frame, (rect.x1, rect.y1), (rect.x2, rect.y2), color, thickness)

        value = state.section_expression.get(section.value, 0)
        cv2.putText(
            frame,
            f"{section.value} {value}",
            (rect.x1 + 8, rect.y1 + 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2,
            cv2.LINE_AA,
        )
        meter_width = int((rect.x2 - rect.x1 - 16) * value / 127)
        cv2.rectangle(
            frame,
            (rect.x1 + 8, rect.y2 - 20),
            (rect.x1 + 8 + meter_width, rect.y2 - 8),
            color,
            -1,
        )

    status = (
        f"Selected {state.selected_section.value} | "
        f"L {state.left_gesture} | R {state.right_gesture} | {state.command}"
    )
    status_y = max(96, height - 210)
    cv2.putText(
        frame,
        status,
        (24, status_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    if score_state is not None:
        score_line = (
            f"Score: {score_state.total_score:04d} | "
            f"Beat: {score_state.beat_index:02d} | "
            f"Target: {score_state.target_section} {score_state.target_dynamic}"
        )
        cv2.putText(
            frame,
            score_line,
            (24, max(68, status_y - 30)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (255, 230, 120),
            2,
            cv2.LINE_AA,
        )

    return frame
