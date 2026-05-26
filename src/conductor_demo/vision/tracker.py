from __future__ import annotations

import logging
from dataclasses import dataclass, field
from math import hypot
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import numpy as np


LOGGER = logging.getLogger(__name__)

WRIST_INDEX = 0
INDEX_FINGER_MCP_INDEX = 5
MIDDLE_FINGER_MCP_INDEX = 9
PINKY_MCP_INDEX = 17
ROLE_LABELS = ("Right", "Left")
HAND_LANDMARKER_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)


def _require_cv2() -> Any:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("OpenCV is required. Install dependencies with `pip install -r requirements.txt`.") from exc
    return cv2


def _require_mediapipe() -> Any:
    try:
        import mediapipe as mp
    except ImportError as exc:
        raise RuntimeError("MediaPipe is required. Install dependencies with `pip install -r requirements.txt`.") from exc
    return mp


def _model_path() -> Path:
    return Path(__file__).resolve().parents[3] / "assets" / "models" / "hand_landmarker.task"


def _ensure_model_asset() -> Path:
    model_path = _model_path()
    if model_path.exists():
        return model_path

    model_path.parent.mkdir(parents=True, exist_ok=True)
    LOGGER.info("Downloading MediaPipe hand model to %s", model_path)
    try:
        with urlopen(HAND_LANDMARKER_MODEL_URL, timeout=20) as response, model_path.open("wb") as handle:
            handle.write(response.read())
    except Exception as exc:
        raise RuntimeError(
            "Missing MediaPipe hand model and automatic download failed. "
            f"Expected file: `{model_path}`"
        ) from exc
    return model_path


@dataclass(slots=True)
class HandObservation:
    label: str
    handedness_score: float
    wrist_px: tuple[float, float]
    hand_scale_px: float
    bbox: tuple[int, int, int, int]
    landmarks_px: list[tuple[int, int]]


@dataclass(slots=True)
class TrackingResult:
    tracking_ok: bool = False
    mode: str = "lost"
    hand_count: int = 0
    active_hand: str | None = None
    confidence: float = 0.0
    wrist_px: tuple[float, float] | None = None
    raw_wrist_px: tuple[float, float] | None = None
    hand_scale_px: float | None = None
    bbox: tuple[int, int, int, int] | None = None
    landmarks_px: list[tuple[int, int]] | None = None
    debug_message: str = "no hands"
    hands: dict[str, "TrackedHand"] = field(default_factory=dict)

    @property
    def tempo_hand(self) -> "TrackedHand | None":
        return self.hands.get("Right")

    @property
    def dynamics_hand(self) -> "TrackedHand | None":
        return self.hands.get("Left")

    @property
    def cue_hand(self) -> "TrackedHand | None":
        return self.hands.get("Left")


@dataclass(slots=True)
class TrackedHand:
    label: str
    tracking_ok: bool = False
    mode: str = "lost"
    confidence: float = 0.0
    wrist_px: tuple[float, float] | None = None
    raw_wrist_px: tuple[float, float] | None = None
    hand_scale_px: float | None = None
    bbox: tuple[int, int, int, int] | None = None
    landmarks_px: list[tuple[int, int]] | None = None
    debug_message: str = "not visible"


@dataclass(slots=True)
class _TrackedHandMemory:
    smoothed_wrist: tuple[float, float] | None = None
    raw_wrist: tuple[float, float] | None = None
    hand_scale_px: float | None = None
    bbox: tuple[int, int, int, int] | None = None
    landmarks_px: list[tuple[int, int]] | None = None
    confidence: float = 0.0
    last_seen_timestamp: float | None = None


class HandTracker:
    """MediaPipe-based hand tracker with stable per-hand wrist trajectories."""

    def __init__(
        self,
        detection_confidence: float,
        tracking_confidence: float,
        smoothing_alpha: float,
        hold_seconds: float,
        max_num_hands: int,
        model_complexity: int,
        hand_confidence_threshold: float,
        min_hand_scale_px: float,
        swap_left_right_labels: bool = False,
    ) -> None:
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence
        self.smoothing_alpha = smoothing_alpha
        self.hold_seconds = hold_seconds
        self.max_num_hands = max_num_hands
        self.model_complexity = model_complexity
        self.hand_confidence_threshold = hand_confidence_threshold
        self.min_hand_scale_px = min_hand_scale_px
        self.swap_left_right_labels = swap_left_right_labels

        self.running = False
        self._mp: Any | None = None
        self._hands: Any | None = None

        self._hand_states: dict[str, _TrackedHandMemory] = {}

    def start(self) -> None:
        mp = _require_mediapipe()
        model_path = _ensure_model_asset()

        self._mp = mp
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=self.max_num_hands,
            min_hand_detection_confidence=self.detection_confidence,
            min_hand_presence_confidence=self.tracking_confidence,
            min_tracking_confidence=self.tracking_confidence,
        )
        self._hands = mp.tasks.vision.HandLandmarker.create_from_options(options)
        self.running = True

    def stop(self) -> None:
        if self._hands is not None:
            self._hands.close()
        self._hands = None
        self.running = False

    def reset(self) -> None:
        self._hand_states.clear()

    def process(self, frame: Any, timestamp: float) -> TrackingResult:
        if not self.running or self._hands is None or self._mp is None:
            raise RuntimeError("HandTracker.process() called before tracker start.")

        cv2 = _require_cv2()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb_frame)
        results = self._hands.detect_for_video(mp_image, int(timestamp * 1000))
        height, width = frame.shape[:2]
        observations = self._extract_observations(results, width, height)
        observations_by_label = self._select_observations_by_label(observations)
        hands = {
            label: self._resolve_tracked_hand(
                label=label,
                observation=observations_by_label.get(label),
                timestamp=timestamp,
            )
            for label in ROLE_LABELS
        }
        live_hand_count = sum(1 for hand in hands.values() if hand.mode == "live")
        primary = self._select_primary_hand(hands)
        if primary is None:
            return TrackingResult(hand_count=live_hand_count, hands=hands)

        return TrackingResult(
            tracking_ok=primary.tracking_ok,
            mode=primary.mode,
            hand_count=live_hand_count,
            active_hand=primary.label if primary.mode != "lost" else None,
            confidence=primary.confidence,
            wrist_px=primary.wrist_px,
            raw_wrist_px=primary.raw_wrist_px,
            hand_scale_px=primary.hand_scale_px,
            bbox=primary.bbox,
            landmarks_px=primary.landmarks_px,
            debug_message=self._build_debug_message(hands),
            hands=hands,
        )

    def _extract_observations(self, results: Any, width: int, height: int) -> list[HandObservation]:
        if not results.hand_landmarks or not results.handedness:
            return []

        observations: list[HandObservation] = []
        for hand_landmark_set, handedness_set in zip(results.hand_landmarks, results.handedness):
            category = handedness_set[0] if handedness_set else None
            score = float(category.score) if category is not None else 0.0
            label = self._normalize_label(str(category.category_name) if category is not None else "Unknown")

            landmarks_px = [
                (
                    int(np.clip(landmark.x * width, 0, width - 1)),
                    int(np.clip(landmark.y * height, 0, height - 1)),
                )
                for landmark in hand_landmark_set
            ]
            xs = [point[0] for point in landmarks_px]
            ys = [point[1] for point in landmarks_px]
            bbox = (min(xs), min(ys), max(xs), max(ys))

            wrist_px = tuple(float(v) for v in landmarks_px[WRIST_INDEX])
            hand_scale_px = self._estimate_hand_scale(landmarks_px)
            observations.append(
                HandObservation(
                    label=label,
                    handedness_score=score,
                    wrist_px=wrist_px,
                    hand_scale_px=hand_scale_px,
                    bbox=bbox,
                    landmarks_px=landmarks_px,
                )
            )
        return observations

    def _select_observations_by_label(self, observations: list[HandObservation]) -> dict[str, HandObservation]:
        selected: dict[str, HandObservation] = {}
        for observation in observations:
            if observation.label not in ROLE_LABELS:
                continue
            current = selected.get(observation.label)
            if current is None or self._score_observation(observation) > self._score_observation(current):
                selected[observation.label] = observation
        return selected

    def _resolve_tracked_hand(
        self,
        label: str,
        observation: HandObservation | None,
        timestamp: float,
    ) -> TrackedHand:
        state = self._hand_states.get(label)
        if observation is not None:
            if state is None:
                state = _TrackedHandMemory()
                self._hand_states[label] = state

            raw_wrist = observation.wrist_px
            smoothed_wrist = self._smooth_wrist(label, raw_wrist)
            tracking_ok = (
                observation.handedness_score >= self.hand_confidence_threshold
                and observation.hand_scale_px >= self.min_hand_scale_px
            )

            state.raw_wrist = raw_wrist
            state.smoothed_wrist = smoothed_wrist
            state.hand_scale_px = observation.hand_scale_px
            state.bbox = observation.bbox
            state.landmarks_px = observation.landmarks_px
            state.confidence = observation.handedness_score
            state.last_seen_timestamp = timestamp

            return TrackedHand(
                label=label,
                tracking_ok=tracking_ok,
                mode="live",
                confidence=observation.handedness_score,
                wrist_px=smoothed_wrist,
                raw_wrist_px=raw_wrist,
                hand_scale_px=observation.hand_scale_px,
                bbox=observation.bbox,
                landmarks_px=observation.landmarks_px,
                debug_message=(
                    f"live {label.lower()} hand"
                    if tracking_ok
                    else f"low-confidence {label.lower()} hand"
                ),
            )

        if self._can_hold(label, timestamp) and state is not None:
            return TrackedHand(
                label=label,
                tracking_ok=False,
                mode="hold",
                confidence=max(state.confidence * 0.6, 0.0),
                wrist_px=state.smoothed_wrist,
                raw_wrist_px=state.raw_wrist,
                hand_scale_px=state.hand_scale_px,
                bbox=state.bbox,
                landmarks_px=state.landmarks_px,
                debug_message=f"holding last {label.lower()} hand after short tracking loss",
            )

        if label in self._hand_states:
            del self._hand_states[label]
        return TrackedHand(label=label, mode="lost", debug_message=f"{label.lower()} hand not visible")

    def _select_primary_hand(self, hands: dict[str, TrackedHand]) -> TrackedHand | None:
        if not hands:
            return None

        def hand_score(item: TrackedHand) -> tuple[int, int, float]:
            mode_score = {"live": 2, "hold": 1, "lost": 0}.get(item.mode, 0)
            return int(item.tracking_ok), mode_score, item.confidence

        return max(hands.values(), key=hand_score)

    def _score_observation(self, observation: HandObservation) -> float:
        size_score = min(observation.hand_scale_px / max(self.min_hand_scale_px * 2.0, 1.0), 1.0)
        score = 0.65 * observation.handedness_score + 0.35 * size_score
        state = self._hand_states.get(observation.label)
        if state is not None and state.smoothed_wrist is not None:
            distance = hypot(
                observation.wrist_px[0] - state.smoothed_wrist[0],
                observation.wrist_px[1] - state.smoothed_wrist[1],
            )
            distance_score = max(0.0, 1.0 - distance / max(observation.hand_scale_px * 4.0, 1.0))
            score += 0.35 * distance_score
        return score

    def _smooth_wrist(self, label: str, raw_wrist: tuple[float, float]) -> tuple[float, float]:
        state = self._hand_states.get(label)
        if state is None or state.smoothed_wrist is None:
            return raw_wrist

        alpha = float(np.clip(self.smoothing_alpha, 0.01, 1.0))
        previous = np.array(state.smoothed_wrist, dtype=np.float32)
        current = np.array(raw_wrist, dtype=np.float32)
        smoothed = previous + alpha * (current - previous)
        return float(smoothed[0]), float(smoothed[1])

    def _can_hold(self, label: str, timestamp: float) -> bool:
        state = self._hand_states.get(label)
        return (
            state is not None
            and state.last_seen_timestamp is not None
            and state.smoothed_wrist is not None
            and timestamp - state.last_seen_timestamp <= self.hold_seconds
        )

    def _build_debug_message(self, hands: dict[str, TrackedHand]) -> str:
        live_ok = [hand.label.lower() for hand in hands.values() if hand.mode == "live" and hand.tracking_ok]
        live_low = [hand.label.lower() for hand in hands.values() if hand.mode == "live" and not hand.tracking_ok]
        held = [hand.label.lower() for hand in hands.values() if hand.mode == "hold"]
        if len(live_ok) == 2:
            return "live right-hand control and left-hand cue tracking"
        if live_ok:
            return f"live {' + '.join(live_ok)} hand tracking"
        if live_low:
            return f"low-confidence {' + '.join(live_low)} hand tracking"
        if held:
            return f"holding {' + '.join(held)} hand after short tracking loss"
        return "no hands"

    def _estimate_hand_scale(self, landmarks_px: list[tuple[int, int]]) -> float:
        wrist = landmarks_px[WRIST_INDEX]
        index_mcp = landmarks_px[INDEX_FINGER_MCP_INDEX]
        pinky_mcp = landmarks_px[PINKY_MCP_INDEX]
        middle_mcp = landmarks_px[MIDDLE_FINGER_MCP_INDEX]

        distances = [
            hypot(wrist[0] - index_mcp[0], wrist[1] - index_mcp[1]),
            hypot(wrist[0] - pinky_mcp[0], wrist[1] - pinky_mcp[1]),
            hypot(index_mcp[0] - pinky_mcp[0], index_mcp[1] - pinky_mcp[1]),
            hypot(wrist[0] - middle_mcp[0], wrist[1] - middle_mcp[1]),
        ]
        return float(sum(distances) / len(distances))

    def _normalize_label(self, label: str) -> str:
        if not self.swap_left_right_labels:
            return label
        if label == "Left":
            return "Right"
        if label == "Right":
            return "Left"
        return label

    def describe(self) -> str:
        return (
            f"mediapipe-hands "
            f"det={self.detection_confidence:.2f} "
            f"track={self.tracking_confidence:.2f} "
            f"swap={self.swap_left_right_labels} "
            f"running={self.running}"
        )
