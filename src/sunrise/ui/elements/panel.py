# panels for UI

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

from sunrise.ui.constants import BORDER_WIDTH
from sunrise.ui.themes import Theme, ThemeKey

from .widget import Widget


class Panel(Widget):
    def __init__(
            self, *,
            horiz_padding: int = 0, vert_padding: int = 0, child: Widget,
            k_bg: ThemeKey = ThemeKey.BG, k_border: ThemeKey = ThemeKey.BORDER,
            border_w: int = BORDER_WIDTH
        ) -> None:
        super().__init__()
        self.horiz_padding = horiz_padding
        self.vert_padding = vert_padding
        self.child = child
        self.children = [child]
        child.parent = self

        self.k_bg = k_bg
        self.k_border = k_border
        self.border_w = border_w

    def preferred_size(self) -> tuple[int, int]:
        cw, ch = self.child.preferred_size()
        return (cw + 2 * self.horiz_padding, ch + 2 * self.vert_padding)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect
        child_rect = rect.inflate(-2 * self.horiz_padding, -2 * self.vert_padding)
        self.child.layout(child_rect)

    def draw(self, surface: pg.Surface, current_theme: Theme) -> None:
        # background
        pg.draw.rect(surface, current_theme[self.k_bg], self.rect)

        # border
        if self.border_w > 0:
            pg.draw.rect(surface, current_theme[self.k_border], self.rect, self.border_w)

        # child
        self.child.draw(surface=surface, current_theme=current_theme)

    def draw_overlay(self, surface: pg.Surface, current_theme: Theme) -> None:
        self.child.draw_overlay(surface=surface, current_theme=current_theme)
