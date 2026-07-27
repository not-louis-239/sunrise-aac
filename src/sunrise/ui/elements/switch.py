# module for switch widget

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
from pygame import Rect, Surface

from .widget import Widget
from sunrise.ui.themes import Theme, ThemeKey
from sunrise.ui.constants import BORDER_WIDTH
from sunrise.ui.utils import lerp, lerp_colours


SWITCH_DIMS = (80, 40)
SWITCH_BUTTON_SIZE = (24, 24)
SWITCH_ANIMATION_SPEED = 7


class Switch(Widget):
    def __init__(
            self, *, flex: float = 0,
            k_bg: ThemeKey = ThemeKey.BG, k_bg_active: ThemeKey = ThemeKey.FG_SUCCESS,
            k_fg: ThemeKey = ThemeKey.FG, k_border: ThemeKey = ThemeKey.BORDER,
            border_w: int = BORDER_WIDTH, enabled: bool = False
        ) -> None:
        super().__init__(flex=flex)

        self.k_bg = k_bg
        self.k_bg_active = k_bg_active
        self.k_fg = k_fg
        self.k_border = k_border
        self.border_w = border_w

        self.enabled: bool = enabled
        self.visual_state: float = 1 if enabled else 0

    def toggle(self) -> None:
        self.enabled = not self.enabled

    def check_click(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def update(self, dt_s: float) -> None:
        if self.enabled:
            self.visual_state = min(1, self.visual_state + SWITCH_ANIMATION_SPEED * dt_s)
        else:
            self.visual_state = max(0, self.visual_state - SWITCH_ANIMATION_SPEED * dt_s)

    def preferred_size(self) -> tuple[int, int]:
        return SWITCH_DIMS

    def layout(self, rect: Rect) -> None:
        self.rect = rect

    def draw(self, surface: Surface, current_theme: Theme) -> None:
        border_colour = current_theme[self.k_border]
        fg_colour = current_theme[self.k_fg]

        bg_inactive_colour = current_theme[self.k_bg]
        bg_active_colour = current_theme[self.k_bg_active]
        bg_colour = lerp_colours(bg_inactive_colour, bg_active_colour, self.visual_state)

        # Draw background
        pg.draw.rect(surface, bg_colour, self.rect, border_radius=SWITCH_DIMS[1] // 2)

        # Draw border
        pg.draw.rect(surface, border_colour, self.rect, border_radius=SWITCH_DIMS[1] // 2, width=self.border_w)

        # Draw switch button
        margin = (SWITCH_DIMS[1] - SWITCH_BUTTON_SIZE[1]) // 2
        button_left = lerp(self.rect.left + margin, self.rect.right - margin - SWITCH_BUTTON_SIZE[0], self.visual_state)
        button_rect = pg.Rect(button_left, self.rect.top + margin, *SWITCH_BUTTON_SIZE)
        pg.draw.rect(surface, fg_colour, button_rect, border_radius=SWITCH_BUTTON_SIZE[1] // 2)
