import sys
import unittest
from unittest.mock import patch

from conductor_demo.vision.tracker import _require_mediapipe


class RuntimeDependencyTests(unittest.TestCase):
    def test_mediapipe_error_mentions_supported_python_versions(self):
        with patch.dict(sys.modules, {"mediapipe": None}):
            with self.assertRaises(RuntimeError) as context:
                _require_mediapipe()

        self.assertIn("Python 3.11 or 3.12", str(context.exception))


if __name__ == "__main__":
    unittest.main()
