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
from sunrise.ui.utils import crop_text_to_fit
from .widget import Widget


class Label(Widget):
    def __init__(
            self, *, flex: float = 0, text: str = "", font: pg.font.Font, inset: int = 0,
            k_fg: ThemeKey = ThemeKey.FG, k_bg: ThemeKey | None = None, k_border: ThemeKey = ThemeKey.BORDER, border_w: int = 0
        ) -> None:
        super().__init__(flex=flex)
        self.text = text
        self.font = font
        self.inset = inset
        self.k_fg = k_fg

        self.k_bg = k_bg
        self.k_border = k_border
        self.border_w = border_w

    def set_fg_theme_key(self, k_fg: ThemeKey) -> None:
        self.k_fg = k_fg

    def set_text(self, text: str) -> None:
        self.text = text

    def preferred_size(self) -> tuple[int, int]:
        text_w, text_h = self.font.size(self.text)
        return (text_w + 2 * self.inset, text_h + 2 * self.inset)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect

    def draw(self, surface: pg.Surface, current_theme: Theme) -> None:
        # Draw background if applicable
        if self.k_bg is not None:
            pg.draw.rect(surface, current_theme[self.k_bg], self.rect)

        # Draw text aligned within `self`'s rect
        text = crop_text_to_fit(self.text, self.font, self.rect.width - 2 * self.inset)
        font_surface = self.font.render(text, True, current_theme[self.k_fg])
        surface.blit(font_surface, self.rect.inflate(-2 * self.inset, -2 * self.inset))

        # Draw border if applicable
        if self.border_w > 0:
            pg.draw.rect(surface, current_theme[self.k_border], self.rect, self.border_w)

