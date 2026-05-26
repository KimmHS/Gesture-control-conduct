from __future__ import annotations

import argparse
import logging

from conductor_demo.app.runner import AppRunner
from conductor_demo.config.loader import load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Conductor demo")
    parser.add_argument(
        "--config",
        help="Reserved for a future external config file. Defaults are used for now.",
    )
    parser.add_argument(
        "--camera-index",
        type=int,
        help="Override the default webcam device index.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        help="Run for a fixed number of frames and exit.",
    )
    parser.add_argument(
        "--demo-track",
        help="Override the default demo WAV track path.",
    )
    parser.add_argument(
        "--no-swap-hands",
        action="store_true",
        help="Keep MediaPipe's original left/right labels without swapping them.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run a synthetic one-frame smoke test without opening the webcam.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def main() -> int:
    args = build_parser().parse_args()
    configure_logging(args.verbose)

    config = load_config(args.config)
    if args.camera_index is not None:
        config.vision.camera_index = args.camera_index
    if args.demo_track:
        config.music.demo_track_path = args.demo_track
    config.vision.swap_left_right_labels = not args.no_swap_hands

    runner = AppRunner(
        config,
        max_frames=args.max_frames,
        self_test=args.self_test,
    )
    return runner.run()
