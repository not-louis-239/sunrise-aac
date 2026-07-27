# key widget module

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


from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

import pygame as pg
from pygame import Rect
from pygame.font import Font

from sunrise.ui.constants import BORDER_WIDTH, UI_MARGIN_S
from sunrise.ui.themes import Theme, ThemeKey
from sunrise.ui.elements._img_cache import img_cache

from .ui_buttons import RectangularUIButton


@dataclass
class KBState:
    # KB state object that Key objects can hook into
    shifting: bool = False
    caps_lock: bool = False

    def reset(self) -> None:
        self.shifting = False
        self.caps_lock = False


class KBAction(Enum):
    SHIFT = auto()
    CAPS_LOCK = auto()
    RETURN = auto()
    BACKSPACE = auto()


class Key(RectangularUIButton):
    def __init__(
            self, *, flex: float = 1,
            font: Font, inset: int = UI_MARGIN_S,
            fixed_size: tuple[int, int] | None = None, img_path: Path | None = None,
            k_fg: ThemeKey = ThemeKey.FG, k_fg_active: ThemeKey = ThemeKey.FG_ACTIVE,
            k_bg: ThemeKey = ThemeKey.BG, k_bg_active: ThemeKey = ThemeKey.BG_ACTIVE,
            k_border: ThemeKey = ThemeKey.BORDER, border_w: int = BORDER_WIDTH,
            kb_state: KBState,
            char: str | None = None,
            shift_char: str | None = None,
            kb_action: KBAction | None = None,
            ignore_caps_lock: bool = False,
            override_display_text: str | None = None,
            size_is_fixed: bool = False
        ) -> None:
        super().__init__(flex=flex, font=font, inset=inset, fixed_size=fixed_size, img_path=img_path, k_fg=k_fg, k_fg_active=k_fg_active, k_bg=k_bg, k_bg_active=k_bg_active, k_border=k_border, border_w=border_w)

        self.kb_state = kb_state
        self.char = char
        self.shift_char = shift_char

        self.kb_action = kb_action
        self.ignore_caps_lock = ignore_caps_lock

        self.override_display_text = override_display_text
        self.size_is_fixed = size_is_fixed

    def _get_text_size(self) -> tuple[int, int]:
        if self.override_display_text:
            w, h = self.font.size(self.override_display_text)
            return w + 2 * self.inset, h + 2 * self.inset

        w1, h = self.font.size(self.char or "")
        w2 = self.font.size(self.shift_char or "")[0]

        return (max(w1, w2) + 2 * self.inset, h + 2 * self.inset)

    def preferred_size(self) -> tuple[int, int]:
        return self.fixed_size or self._get_text_size()

    def layout(self, rect: Rect) -> None:
        self.rect = rect

    def draw(self, surface: pg.Surface, current_theme: Theme) -> None:
        # Draw background
        pg.draw.rect(surface, current_theme[self.k_bg], self.rect)

        # Draw icon if applicable
        if self.img_path is not None:
            img_surf = img_cache.get_tinted_scaled_img(self.img_path, current_theme[self.k_fg], self._preferred_icon_size())
            surface.blit(img_surf, img_surf.get_rect(center=self.rect.center))

        # Draw border
        pg.draw.rect(surface, current_theme[self.k_border], self.rect, width=self.border_w)

        # Draw text if applicable
        if self.override_display_text:
            text = self.override_display_text
        elif self.kb_state.caps_lock and not self.ignore_caps_lock or self.kb_state.shifting:
            text = self.shift_char
        else:
            text = self.char

        text_surface = self.font.render(text, True, current_theme[self.k_fg])
        surface.blit(text_surface, text_surface.get_rect(center=self.rect.center))
