from __future__ import annotations

import unittest
from dataclasses import dataclass

from conductor_demo.motion.buffer import MotionBuffer, MotionSample
from conductor_demo.game.two_hand_mapping import (
    Section,
    TwoHandMapper,
    make_zones,
)


@dataclass(slots=True)
class FakeHand:
    landmarks_px: list[tuple[int, int]]
    wrist_px: tuple[float, float]
    hand_scale_px: float = 60.0
    handedness_score: float = 0.9


def fake_hand(
    *,
    index_tip: tuple[int, int] = (0, 0),
    wrist: tuple[float, float] = (0.0, 0.0),
    hand_scale_px: float = 60.0,
) -> FakeHand:
    landmarks = [(0, 0)] * 21
    landmarks[8] = index_tip
    landmarks[0] = (int(wrist[0]), int(wrist[1]))
    return FakeHand(
        landmarks_px=landmarks,
        wrist_px=wrist,
        hand_scale_px=hand_scale_px,
    )


def append_motion(
    buffer: MotionBuffer,
    points: list[tuple[float, float, float]],
) -> None:
    for timestamp, x, y in points:
        buffer.append(
            MotionSample(
                x=x,
                y=y,
                timestamp=timestamp,
                confidence=0.9,
                raw_x=x,
                raw_y=y,
                is_live=True,
            )
        )


class TwoHandMapperTests(unittest.TestCase):
    def test_left_index_tip_selects_section_after_dwell(self):
        mapper = TwoHandMapper()
        frame_size = (1000, 500)
        zones = make_zones(*frame_size)
        rect = zones[Section.STRINGS]
        left = fake_hand(index_tip=((rect.x1 + rect.x2) // 2, (rect.y1 + rect.y2) // 2))
        right_motion = MotionBuffer()

        first = mapper.update(
            frame_size=frame_size,
            timestamp=1.00,
            left_hand=left,
            right_hand=None,
            right_motion=right_motion,
        )
        second = mapper.update(
            frame_size=frame_size,
            timestamp=1.30,
            left_hand=left,
            right_hand=None,
            right_motion=right_motion,
        )

        self.assertEqual(first.selected_section, Section.TUTTI)
        self.assertEqual(second.selected_section, Section.STRINGS)
        self.assertEqual(second.left_gesture, "LH_POINT_STRINGS")

    def test_right_wrist_span_maps_to_loud_expression(self):
        mapper = TwoHandMapper()
        right_motion = MotionBuffer()
        append_motion(
            right_motion,
            [
                (2.00, 100.0, 100.0),
                (2.10, 180.0, 100.0),
                (2.20, 260.0, 100.0),
            ],
        )
        right = fake_hand(wrist=(260.0, 100.0), hand_scale_px=60.0)

        state = mapper.update(
            frame_size=(1000, 500),
            timestamp=2.20,
            left_hand=None,
            right_hand=right,
            right_motion=right_motion,
        )

        self.assertEqual(state.selected_section, Section.TUTTI)
        self.assertEqual(state.right_dynamic_label, "LOUD")
        self.assertGreaterEqual(state.right_intensity, 0.9)
        self.assertEqual(state.section_expression[Section.TUTTI.value], 127)
        self.assertEqual(state.command, "CMD_SET_TUTTI_EXPRESSION_127")

    def test_downward_right_wrist_motion_triggers_one_downbeat_per_cooldown(self):
        mapper = TwoHandMapper()
        right_motion = MotionBuffer()
        append_motion(
            right_motion,
            [
                (3.00, 200.0, 100.0),
                (3.08, 200.0, 160.0),
                (3.16, 200.0, 220.0),
            ],
        )
        right = fake_hand(wrist=(200.0, 220.0), hand_scale_px=60.0)

        first = mapper.update(
            frame_size=(1000, 500),
            timestamp=3.16,
            left_hand=None,
            right_hand=right,
            right_motion=right_motion,
        )
        second = mapper.update(
            frame_size=(1000, 500),
            timestamp=3.20,
            left_hand=None,
            right_hand=right,
            right_motion=right_motion,
        )

        self.assertTrue(first.downbeat)
        self.assertEqual(first.command, "CMD_CUE_TUTTI")
        self.assertFalse(second.downbeat)

    def test_missing_left_hand_falls_back_to_tutti_after_hold_timeout(self):
        mapper = TwoHandMapper()
        frame_size = (1000, 500)
        zones = make_zones(*frame_size)
        rect = zones[Section.BRASS]
        left = fake_hand(index_tip=((rect.x1 + rect.x2) // 2, (rect.y1 + rect.y2) // 2))
        right_motion = MotionBuffer()

        mapper.update(
            frame_size=frame_size,
            timestamp=1.00,
            left_hand=left,
            right_hand=None,
            right_motion=right_motion,
        )
        selected = mapper.update(
            frame_size=frame_size,
            timestamp=1.30,
            left_hand=left,
            right_hand=None,
            right_motion=right_motion,
        )
        held = mapper.update(
            frame_size=frame_size,
            timestamp=1.70,
            left_hand=None,
            right_hand=None,
            right_motion=right_motion,
        )
        fallback = mapper.update(
            frame_size=frame_size,
            timestamp=2.20,
            left_hand=None,
            right_hand=None,
            right_motion=right_motion,
        )

        self.assertEqual(selected.selected_section, Section.BRASS)
        self.assertEqual(held.selected_section, Section.BRASS)
        self.assertEqual(fallback.selected_section, Section.TUTTI)


if __name__ == "__main__":
    unittest.main()
