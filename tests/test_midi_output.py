from __future__ import annotations

import unittest

from conductor_demo.game.two_hand_mapping import MappingState, Section
from conductor_demo.music.midi_output import MidiSectionOutput, SECTION_CHANNELS


class FakePort:
    def __init__(self) -> None:
        self.messages: list[dict[str, int | str]] = []
        self.closed = False

    def send(self, message: dict[str, int | str]) -> None:
        self.messages.append(message)

    def close(self) -> None:
        self.closed = True


def fake_message(message_type: str, **kwargs: int) -> dict[str, int | str]:
    return {"type": message_type, **kwargs}


class MidiSectionOutputTests(unittest.TestCase):
    def test_selected_section_expression_sends_cc11_to_section_channels(self):
        port = FakePort()
        output = MidiSectionOutput(enabled=True, message_factory=fake_message)
        output._port = port
        state = MappingState(selected_section=Section.STRINGS)
        state.section_expression[Section.STRINGS.value] = 112

        output.apply(state)

        self.assertEqual(
            port.messages,
            [
                {"type": "control_change", "channel": 7, "control": 11, "value": 112},
                {"type": "control_change", "channel": 8, "control": 11, "value": 112},
                {"type": "control_change", "channel": 10, "control": 11, "value": 112},
                {"type": "control_change", "channel": 11, "control": 11, "value": 112},
                {"type": "control_change", "channel": 12, "control": 11, "value": 112},
            ],
        )

    def test_section_channels_match_inspected_symphony7_midi_file(self):
        self.assertEqual(SECTION_CHANNELS["WOODWINDS"], [0, 1, 2, 3, 4, 5])
        self.assertEqual(SECTION_CHANNELS["PERCUSSION"], [6])
        self.assertEqual(SECTION_CHANNELS["STRINGS"], [7, 8, 10, 11, 12])
        self.assertEqual(SECTION_CHANNELS["BRASS"], [])

    def test_tutti_expression_sends_cc11_to_all_mapped_channels(self):
        port = FakePort()
        output = MidiSectionOutput(enabled=True, message_factory=fake_message)
        output._port = port
        state = MappingState(selected_section=Section.TUTTI)
        state.section_expression[Section.TUTTI.value] = 96

        output.apply(state)

        channels = [message["channel"] for message in port.messages]
        self.assertEqual(channels, [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12])
        self.assertTrue(all(message["value"] == 96 for message in port.messages))

    def test_same_value_is_not_resent(self):
        port = FakePort()
        output = MidiSectionOutput(enabled=True, message_factory=fake_message)
        output._port = port
        state = MappingState(selected_section=Section.PERCUSSION)
        state.section_expression[Section.PERCUSSION.value] = 88

        output.apply(state)
        output.apply(state)

        self.assertEqual(len(port.messages), 1)

    def test_disabled_or_unopened_output_does_nothing(self):
        disabled = MidiSectionOutput(enabled=False, message_factory=fake_message)
        unopened = MidiSectionOutput(enabled=True, message_factory=fake_message)
        state = MappingState(selected_section=Section.STRINGS)

        disabled.apply(state)
        unopened.apply(state)

        self.assertIsNone(disabled._port)
        self.assertIsNone(unopened._port)


if __name__ == "__main__":
    unittest.main()
