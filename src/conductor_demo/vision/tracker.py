from __future__ import annotations

import logging
from dataclasses import dataclass
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
    LOGGER.info("Downloading MediaPipe hand landmarker model to %s", model_path)
    with urlopen(HAND_LANDMARKER_MODEL_URL) as response, model_path.open("wb") as handle:
        handle.write(response.read())
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


class HandTracker:
    """MediaPipe-based conducting-hand tracker.

    The output is centered on one stable wrist trajectory rather than static
    hand-sign classification.
    """

    def __init__(
        self,
        detection_confidence: float,
        tracking_confidence: float,
        smoothing_alpha: float,
        hold_seconds: float,
        max_num_hands: int,
        model_complexity: int,
        hand_confidence_threshold: float,
    ) -> None:
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence
        self.smoothing_alpha = smoothing_alpha
        self.hold_seconds = hold_seconds
        self.max_num_hands = max_num_hands
        self.model_complexity = model_complexity
        self.hand_confidence_threshold = hand_confidence_threshold

        self.running = False
        self._mp: Any | None = None
        self._vision: Any | None = None
        self._base_options: Any | None = None
        self._hands: Any | None = None

        self._last_active_hand: str | None = None
        self._last_smoothed_wrist: tuple[float, float] | None = None
        self._last_raw_wrist: tuple[float, float] | None = None
        self._last_hand_scale_px: float | None = None
        self._last_bbox: tuple[int, int, int, int] | None = None
        self._last_landmarks_px: list[tuple[int, int]] | None = None
        self._last_confidence: float = 0.0
        self._last_seen_timestamp: float | None = None

    def start(self) -> None:
        mp = _require_mediapipe()
        model_path = _ensure_model_asset()

        self._mp = mp
        self._base_options = mp.tasks.BaseOptions
        self._vision = mp.tasks.vision
        options = self._vision.HandLandmarkerOptions(
            base_options=self._base_options(model_asset_buffer=model_path.read_bytes()),
            running_mode=self._vision.RunningMode.VIDEO,
            num_hands=self.max_num_hands,
            min_hand_detection_confidence=self.detection_confidence,
            min_hand_presence_confidence=self.tracking_confidence,
            min_tracking_confidence=self.tracking_confidence,
        )
        self._hands = self._vision.HandLandmarker.create_from_options(options)
        self.running = True

    def stop(self) -> None:
        if self._hands is not None:
            self._hands.close()
        self._hands = None
        self.running = False

    def reset(self) -> None:
        self._last_active_hand = None
        self._last_smoothed_wrist = None
        self._last_raw_wrist = None
        self._last_hand_scale_px = None
        self._last_bbox = None
        self._last_landmarks_px = None
        self._last_confidence = 0.0
        self._last_seen_timestamp = None

    def process(self, frame: Any, timestamp: float) -> TrackingResult:
        if not self.running or self._hands is None or self._mp is None:
            raise RuntimeError("HandTracker.process() called before tracker start.")

        cv2 = _require_cv2()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb_frame)
        results = self._hands.detect_for_video(mp_image, int(timestamp * 1000))
        height, width = frame.shape[:2]
        observations = self._extract_observations(results, width, height)

        if observations:
            active = self._select_active_hand(observations)
            confidence = active.handedness_score
            raw_wrist = active.wrist_px
            smoothed_wrist = self._smooth_wrist(raw_wrist)

            self._last_active_hand = active.label
            self._last_raw_wrist = raw_wrist
            self._last_smoothed_wrist = smoothed_wrist
            self._last_hand_scale_px = active.hand_scale_px
            self._last_bbox = active.bbox
            self._last_landmarks_px = active.landmarks_px
            self._last_confidence = confidence
            self._last_seen_timestamp = timestamp

            return TrackingResult(
                tracking_ok=confidence >= self.hand_confidence_threshold,
                mode="live",
                hand_count=len(observations),
                active_hand=active.label,
                confidence=confidence,
                wrist_px=smoothed_wrist,
                raw_wrist_px=raw_wrist,
                hand_scale_px=active.hand_scale_px,
                bbox=active.bbox,
                landmarks_px=active.landmarks_px,
                debug_message=(
                    f"live {active.label.lower()} hand"
                    if confidence >= self.hand_confidence_threshold
                    else f"low-confidence {active.label.lower()} hand"
                ),
            )

        if self._can_hold(timestamp):
            return TrackingResult(
                tracking_ok=False,
                mode="hold",
                hand_count=0,
                active_hand=self._last_active_hand,
                confidence=max(self._last_confidence * 0.6, 0.0),
                wrist_px=self._last_smoothed_wrist,
                raw_wrist_px=self._last_raw_wrist,
                hand_scale_px=self._last_hand_scale_px,
                bbox=self._last_bbox,
                landmarks_px=self._last_landmarks_px,
                debug_message="holding last wrist after short tracking loss",
            )

        self.reset()
        return TrackingResult()

    def _extract_observations(self, results: Any, width: int, height: int) -> list[HandObservation]:
        if not results.hand_landmarks or not results.handedness:
            return []

        observations: list[HandObservation] = []
        for hand_landmarks, handedness in zip(results.hand_landmarks, results.handedness):
            category = handedness[0] if handedness else None
            score = float(category.score) if category is not None else 0.0
            label = str(category.category_name) if category is not None else "Unknown"

            landmarks_px = [
                (
                    int(np.clip(landmark.x * width, 0, width - 1)),
                    int(np.clip(landmark.y * height, 0, height - 1)),
                )
                for landmark in hand_landmarks
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

    def _select_active_hand(self, observations: list[HandObservation]) -> HandObservation:
        best = observations[0]
        best_score = -1.0
        for observation in observations:
            size_score = min(observation.hand_scale_px / 140.0, 1.0)
            score = 0.7 * observation.handedness_score + 0.3 * size_score
            if observation.label == self._last_active_hand:
                score += 0.25
            if self._last_smoothed_wrist is not None:
                distance = hypot(
                    observation.wrist_px[0] - self._last_smoothed_wrist[0],
                    observation.wrist_px[1] - self._last_smoothed_wrist[1],
                )
                distance_score = max(0.0, 1.0 - distance / max(observation.hand_scale_px * 4.0, 1.0))
                score += 0.35 * distance_score
            if score > best_score:
                best_score = score
                best = observation
        return best

    def _smooth_wrist(self, raw_wrist: tuple[float, float]) -> tuple[float, float]:
        if self._last_smoothed_wrist is None:
            return raw_wrist

        alpha = float(np.clip(self.smoothing_alpha, 0.01, 1.0))
        previous = np.array(self._last_smoothed_wrist, dtype=np.float32)
        current = np.array(raw_wrist, dtype=np.float32)
        smoothed = previous + alpha * (current - previous)
        return float(smoothed[0]), float(smoothed[1])

    def _can_hold(self, timestamp: float) -> bool:
        return (
            self._last_seen_timestamp is not None
            and self._last_smoothed_wrist is not None
            and timestamp - self._last_seen_timestamp <= self.hold_seconds
        )

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

    def describe(self) -> str:
        return (
            f"mediapipe-task "
            f"det={self.detection_confidence:.2f} "
            f"track={self.tracking_confidence:.2f} "
            f"running={self.running}"
        )
