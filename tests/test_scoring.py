import unittest

from conductor_demo.game.scoring import ScoreKeeper, score_on_downbeat
from conductor_demo.game.two_hand_mapping import MappingState, Section


class ScoringTests(unittest.TestCase):
    def test_score_on_downbeat_rewards_section_and_dynamic_match(self):
        state = MappingState(
            selected_section=Section.STRINGS,
            right_dynamic_label="NORMAL",
        )

        self.assertEqual(score_on_downbeat(state, beat_index=0), 100)

    def test_score_on_downbeat_gives_partial_credit(self):
        section_only = MappingState(
            selected_section=Section.STRINGS,
            right_dynamic_label="LOUD",
        )
        dynamic_only = MappingState(
            selected_section=Section.BRASS,
            right_dynamic_label="NORMAL",
        )
        neither = MappingState(
            selected_section=Section.BRASS,
            right_dynamic_label="SOFT",
        )

        self.assertEqual(score_on_downbeat(section_only, beat_index=0), 75)
        self.assertEqual(score_on_downbeat(dynamic_only, beat_index=0), 55)
        self.assertEqual(score_on_downbeat(neither, beat_index=0), 20)

    def test_score_keeper_updates_only_on_downbeat(self):
        keeper = ScoreKeeper()
        no_downbeat = MappingState(
            selected_section=Section.STRINGS,
            right_dynamic_label="NORMAL",
            downbeat=False,
        )
        downbeat = MappingState(
            selected_section=Section.STRINGS,
            right_dynamic_label="NORMAL",
            downbeat=True,
        )

        first = keeper.update(no_downbeat)
        second = keeper.update(downbeat)

        self.assertEqual(first.total_score, 0)
        self.assertEqual(first.beat_index, 0)
        self.assertEqual(second.total_score, 100)
        self.assertEqual(second.beat_index, 1)
        self.assertEqual(second.last_points, 100)
        self.assertEqual(second.target_section, "STRINGS")
        self.assertEqual(second.target_dynamic, "SOFT")


if __name__ == "__main__":
    unittest.main()
