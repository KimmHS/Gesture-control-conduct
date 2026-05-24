import unittest

from conductor_demo.app.runner import AppRunner
from conductor_demo.config.defaults import AppConfig, MidiConfig
from conductor_demo.main import build_parser


class AppMidiConfigTests(unittest.TestCase):
    def test_default_midi_config_is_disabled(self):
        config = AppConfig()

        self.assertIsInstance(config.midi, MidiConfig)
        self.assertFalse(config.midi.enabled)
        self.assertIsNone(config.midi.port_name)
        self.assertEqual(config.midi.midi_file_path, "assets/audio/Symphony7_2.mid")
        self.assertEqual(config.midi.expression_cc, 11)

    def test_parser_accepts_macos_midi_flags(self):
        args = build_parser().parse_args(
            [
                "--midi-out",
                "IAC Driver Bus 1",
                "--midi-file",
                "assets/audio/Symphony7_2.mid",
            ]
        )

        self.assertEqual(args.midi_out, "IAC Driver Bus 1")
        self.assertEqual(args.midi_file, "assets/audio/Symphony7_2.mid")

    def test_runner_initializes_mapping_score_and_midi_output(self):
        config = AppConfig()
        config.midi.enabled = True
        config.midi.port_name = "IAC Driver Bus 1"
        runner = AppRunner(config, self_test=True)
        try:
            self.assertIn("Left", runner.motion_by_hand)
            self.assertIn("Right", runner.motion_by_hand)
            self.assertEqual(runner.mapping_state.selected_section.value, "TUTTI")
            self.assertEqual(runner.score_state.total_score, 0)
            self.assertTrue(runner.midi_out.enabled)
            self.assertEqual(runner.midi_out.port_name, "IAC Driver Bus 1")
        finally:
            runner.music.close()


if __name__ == "__main__":
    unittest.main()
