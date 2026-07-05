import sys
import unittest
from pathlib import Path

import pygame as pg

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sunrise.ui.elements.alignment_boxes import HBox
from sunrise.ui.elements.widget import Widget


class RecordingWidget(Widget):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.events: list[str] = []

    def preferred_size(self) -> tuple[int, int]:
        return (0, 0)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect

    def draw(self, surface: pg.Surface, current_theme) -> None:
        self.events.append(f"{self.name}:draw")

    def draw_overlay(self, surface: pg.Surface, current_theme) -> None:
        self.events.append(f"{self.name}:overlay")


class DrawOrderTests(unittest.TestCase):
    def test_overlay_draws_after_all_regular_draws(self) -> None:
        pg.init()

        first = RecordingWidget("first")
        second = RecordingWidget("second")
        box = HBox(children=[first, second])

        box.draw(pg.Surface((100, 100)), {})

        self.assertEqual(
            first.events + second.events,
            ["first:draw", "second:draw", "first:overlay", "second:overlay"],
        )


if __name__ == "__main__":
    unittest.main()
