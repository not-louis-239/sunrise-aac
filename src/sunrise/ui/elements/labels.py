# labels

# repo at: https://github.com/not-louis-239/sunrise-aac
# Copyright (C) 2026 Louis Masarei-Boulton <243234869+not-louis-239@users.noreply.github.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pygame as pg

from sunrise.ui.themes import Theme, ThemeKey
from .widget import Widget


class Label(Widget):
    def __init__(
            self, *, text: str = "", font: pg.font.Font, k_fg: ThemeKey = ThemeKey.FG
        ) -> None:
        super().__init__()
        self.text = text
        self.font = font
        self.k_fg = k_fg

    def set_text(self, text: str) -> None:
        self.text = text

    def preferred_size(self) -> tuple[int, int]:
        w, h = self.font.size(self.text)
        return (w, h)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect

    def draw(self, surface: pg.Surface, current_theme: Theme) -> None:
        # Draws text aligned within `self`'s rect
        font_surface = self.font.render(self.text, True, current_theme[self.k_fg])
        surface.blit(font_surface, self.rect)
