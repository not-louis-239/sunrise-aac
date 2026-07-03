# module for reusable input boxes

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
from sunrise.core.constants import DELETE_DELAY, DELETE_INTERVAL
from sunrise.ui.constants import BORDER_WIDTH, CURSOR_WIDTH, CURSOR_FLASH_INTERVAL

from .widget import Widget
from sunrise.ui.themes import Theme, ThemeKey


class InputBox(Widget):
    def __init__(
            self, *,
            flex: int = 0, min_size: tuple[int, int], font: pg.font.Font, inset: int,
            k_bg: ThemeKey = ThemeKey.BG,
            k_bg_active: ThemeKey = ThemeKey.BG_ACTIVE,
            k_fg: ThemeKey = ThemeKey.FG,
            k_fg_active: ThemeKey = ThemeKey.FG_ACTIVE,
            k_cursor: ThemeKey = ThemeKey.FG,
            k_border: ThemeKey = ThemeKey.BORDER,
            border_w: int = BORDER_WIDTH
        ) -> None:
        # Creates a left-aligned InputBox

        super().__init__(flex=flex)
        self.text = ""
        self.min_size = min_size
        self.font = font  # needed so that it can auto-adjust text width while drawing
        self.text_inset = inset
        self.active = False
        self.delete_timer: float = DELETE_DELAY
        self.cursor_flash_time: float = 0

        self.k_bg = k_bg
        self.k_bg_active = k_bg_active
        self.k_fg = k_fg
        self.k_fg_active = k_fg_active
        self.k_cursor = k_cursor
        self.k_border = k_border
        self.border_w = border_w

    def handle_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.event.Event], dt_s: float) -> None:
        if self.active:
            self.cursor_flash_time = (self.cursor_flash_time + dt_s) % CURSOR_FLASH_INTERVAL
        else:
            self.cursor_flash_time = 0

        # Handle KEYDOWN events
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.active = self.rect.collidepoint(event.pos)
            elif event.type == pg.KEYDOWN:
                if self.active:
                    if event.key == pg.K_BACKSPACE:
                        self.text = self.text[:-1]
                    elif event.key not in (pg.K_RETURN, pg.K_ESCAPE, pg.K_TAB):
                        # Append character
                        self.text += event.unicode

        # Handle delete
        if keys[pg.K_BACKSPACE]:
            self.delete_timer -= dt_s
            if self.delete_timer <= 0:
                self.text = self.text[:-1]
                self.delete_timer += DELETE_INTERVAL
        else:
            # If delete is not held down, reset the delete timer
            self.delete_timer = DELETE_DELAY

    def preferred_size(self) -> tuple[int, int]:
        return self.min_size

    def layout(self, rect) -> None:
        self.rect = rect

    def draw(self, surface: pg.Surface, current_theme: Theme) -> None:
        # Draw the background and border
        k_bg = self.k_bg_active if self.active else self.k_bg
        k_fg = self.k_fg_active if self.active else self.k_fg

        pg.draw.rect(surface, current_theme[k_bg], self.rect)

        # Text - rendering only last 127 chars for performance
        last_127_chars = self.text[-127:]
        text_surf = self.font.render(last_127_chars, True, current_theme[k_fg])
        text_visual_width = self.rect.width - 2 * self.text_inset

        # Draw the text aligned to left-centre
        dest = (
            self.rect.x + self.text_inset,
            self.rect.centery - text_surf.get_height() // 2,
        )
        source_rect = pg.Rect(
            max(0, text_surf.get_width() - text_visual_width),
            0,
            min(text_visual_width, text_surf.get_width()),
            text_surf.get_height()
        )

        surface.blit(text_surf, dest, source_rect)

        # Draw the cursor
        if self.active and self.cursor_flash_time < CURSOR_FLASH_INTERVAL * 0.5:
            cursor_x = self.rect.x + self.text_inset + min(text_visual_width, text_surf.get_width())
            cursor_top_y = self.rect.centery - text_surf.get_height() // 2
            cursor_bot_y = self.rect.centery + text_surf.get_height() // 2
            pg.draw.line(surface, current_theme[self.k_cursor], (cursor_x, cursor_top_y), (cursor_x, cursor_bot_y), width=CURSOR_WIDTH)

        # Border
        pg.draw.rect(surface, current_theme[self.k_border], self.rect, width=self.border_w)
