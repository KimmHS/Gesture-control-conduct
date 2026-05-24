import unittest

from conductor_demo.vision.tracker import HandObservation, TrackingResult


class TrackingResultTests(unittest.TestCase):
    def test_hands_default_is_empty_per_instance(self):
        first = TrackingResult()
        second = TrackingResult()

        first.hands["Left"] = HandObservation(
            label="Left",
            handedness_score=0.9,
            wrist_px=(10.0, 20.0),
            hand_scale_px=50.0,
            bbox=(0, 0, 30, 40),
            landmarks_px=[(10, 20)] * 21,
        )

        self.assertIn("Left", first.hands)
        self.assertNotIn("Left", second.hands)


if __name__ == "__main__":
    unittest.main()
