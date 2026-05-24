from __future__ import annotations

from dataclasses import dataclass

from conductor_demo.game.two_hand_mapping import MappingState


SCRIPT = [
    ("STRINGS", "NORMAL"),
    ("STRINGS", "SOFT"),
    ("WOODWINDS", "SOFT"),
    ("BRASS", "LOUD"),
    ("STRINGS", "LOUD"),
    ("PERCUSSION", "LOUD"),
    ("TUTTI", "NORMAL"),
    ("TUTTI", "SOFT"),
]


def score_on_downbeat(state: MappingState, beat_index: int) -> int:
    expected_section, expected_dynamic = SCRIPT[beat_index % len(SCRIPT)]
    section_ok = state.selected_section.value == expected_section
    dynamic_ok = state.right_dynamic_label == expected_dynamic

    if section_ok and dynamic_ok:
        return 100
    if section_ok:
        return 75
    if dynamic_ok:
        return 55
    return 20


@dataclass(slots=True)
class ScoreState:
    beat_index: int = 0
    total_score: int = 0
    last_points: int = 0
    target_section: str = SCRIPT[0][0]
    target_dynamic: str = SCRIPT[0][1]


class ScoreKeeper:
    def __init__(self) -> None:
        self.state = ScoreState()

    def reset(self) -> None:
        self.state = ScoreState()

    def update(self, mapping_state: MappingState) -> ScoreState:
        if not mapping_state.downbeat:
            return self.state

        points = score_on_downbeat(mapping_state, self.state.beat_index)
        next_beat = self.state.beat_index + 1
        next_section, next_dynamic = SCRIPT[next_beat % len(SCRIPT)]
        self.state = ScoreState(
            beat_index=next_beat,
            total_score=self.state.total_score + points,
            last_points=points,
            target_section=next_section,
            target_dynamic=next_dynamic,
        )
        return self.state
