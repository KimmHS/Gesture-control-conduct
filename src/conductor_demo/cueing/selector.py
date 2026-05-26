from __future__ import annotations

from conductor_demo.app.state import CueState
from conductor_demo.vision.tracker import TrackedHand


class CueSelector:
    """Select one of N cue targets from the cue hand's x-position."""

    def __init__(
        self,
        slot_count: int,
        labels: tuple[str, ...],
        selection_hold_seconds: float,
        boundary_margin_ratio: float,
        enabled: bool = True,
    ) -> None:
        if slot_count <= 0:
            raise ValueError("slot_count must be positive")

        self.enabled = enabled
        self.slot_count = slot_count
        self.labels = self._normalize_labels(slot_count=slot_count, labels=labels)
        self.selection_hold_seconds = max(selection_hold_seconds, 0.0)
        self.boundary_margin_ratio = max(boundary_margin_ratio, 0.0)

        self._selected_index: int | None = None
        self._pending_index: int | None = None
        self._pending_since: float | None = None
        self._last_tracking_ok = False
        self._last_visible = False
        self._last_x_px: float | None = None
        self._last_frame_width = 0

    def reset(self) -> None:
        self._selected_index = None
        self._pending_index = None
        self._pending_since = None
        self._last_tracking_ok = False
        self._last_visible = False
        self._last_x_px = None
        self._last_frame_width = 0

    def current(self, selection_progress: float = 0.0) -> CueState:
        return CueState(
            enabled=self.enabled,
            tracking_ok=self._last_tracking_ok,
            visible=self._last_visible,
            selected_index=self._selected_index,
            selected_label=self._label_for(self._selected_index),
            pending_index=self._pending_index,
            pending_label=self._label_for(self._pending_index) if self._pending_index is not None else None,
            selection_progress=max(0.0, min(1.0, selection_progress)),
            cue_x_px=self._last_x_px,
            frame_width=self._last_frame_width,
            slot_count=self.slot_count,
            labels=self.labels,
        )

    def update(
        self,
        hand: TrackedHand | None,
        frame_width: int,
        timestamp: float,
    ) -> CueState:
        self._last_frame_width = max(frame_width, 0)
        self._last_visible = bool(hand is not None and hand.mode != "lost" and hand.wrist_px is not None)
        self._last_tracking_ok = bool(hand is not None and hand.mode == "live" and hand.tracking_ok and hand.wrist_px)
        self._last_x_px = float(hand.wrist_px[0]) if self._last_visible and hand and hand.wrist_px else None

        if not self.enabled or not self._last_tracking_ok or self._last_x_px is None or self._last_frame_width <= 0:
            self._pending_index = None
            self._pending_since = None
            return self.current()

        x_px = max(0.0, min(self._last_x_px, max(self._last_frame_width - 1, 0)))
        candidate_index = self._candidate_index(x_px=x_px, frame_width=self._last_frame_width)
        if self._selected_index is None:
            self._selected_index = candidate_index
            self._pending_index = None
            self._pending_since = None
            return self.current(selection_progress=1.0)

        if candidate_index == self._selected_index:
            self._pending_index = None
            self._pending_since = None
            return self.current(selection_progress=1.0)

        if self._pending_index != candidate_index:
            self._pending_index = candidate_index
            self._pending_since = timestamp
            return self.current(selection_progress=0.0)

        elapsed = max(timestamp - (self._pending_since or timestamp), 0.0)
        if elapsed >= self.selection_hold_seconds:
            self._selected_index = candidate_index
            self._pending_index = None
            self._pending_since = None
            return self.current(selection_progress=1.0)

        progress = (
            1.0
            if self.selection_hold_seconds == 0.0
            else min(elapsed / self.selection_hold_seconds, 1.0)
        )
        return self.current(selection_progress=progress)

    def _candidate_index(self, x_px: float, frame_width: int) -> int:
        raw_index = self._slot_index_for_x(x_px=x_px, frame_width=frame_width)
        if self._selected_index is None:
            return raw_index

        slot_width = frame_width / self.slot_count
        margin = slot_width * self.boundary_margin_ratio
        selected_left = self._selected_index * slot_width
        selected_right = selected_left + slot_width
        if selected_left - margin <= x_px < selected_right + margin:
            return self._selected_index
        return raw_index

    def _slot_index_for_x(self, x_px: float, frame_width: int) -> int:
        slot_width = max(frame_width / self.slot_count, 1.0)
        return min(int(x_px / slot_width), self.slot_count - 1)

    def _label_for(self, index: int | None) -> str:
        if index is None or index < 0 or index >= len(self.labels):
            return "-"
        return self.labels[index]

    def _normalize_labels(self, slot_count: int, labels: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(label.strip() or f"Inst {index + 1}" for index, label in enumerate(labels[:slot_count]))
        if len(normalized) >= slot_count:
            return normalized
        padded = list(normalized)
        for index in range(len(normalized), slot_count):
            padded.append(f"Inst {index + 1}")
        return tuple(padded)
