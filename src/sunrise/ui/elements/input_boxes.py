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

from .widget import Widget, DrawContext


DEFAULT_INPUT_WIDTH = 200

class InputBox(Widget):
    def __init__(self, font: pg.font.Font, text_inset: int) -> None:
        super().__init__()
        self.text = ""
        self.text_inset = text_inset
        self.font = font  # needed so that it can auto-adjust text width while drawing
        self.active = False
        self.delete_timer: float = DELETE_DELAY

    def _handle_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.event.Event], dt_s: float) -> None:
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
        if keys[pg.K_BACKSPACE]:
            self.delete_timer -= dt_s
            if self.delete_timer <= 0:
                self.text = self.text[:-1]
                self.delete_timer += DELETE_INTERVAL
        else:
            self.delete_timer = DELETE_DELAY

    def preferred_size(self) -> tuple[int, int]:
        w = DEFAULT_INPUT_WIDTH + 2 * self.text_inset
        h = self.font.get_linesize() + 2 * self.text_inset
        return (w, h)

    def draw(self, surface: pg.Surface, ctx: DrawContext) -> None:
        # Passing the colours into the method instead of
        # as attributes because these suckers shouldn't really need to know
        # what colour they are, and it makes multiple themes harder
        # because then you'd need to change the colour of the `InputBox`es
        # every time you wanted to change theme

        # Draw the background and border
        bg_colour = ctx.active_bg if self.active else ctx.bg
        pg.draw.rect(surface, bg_colour, self.rect)

        # Text
        last_127_chars = self.text[-127:]  # drawing only last 127 characters for performance
        text_surf = self.font.render(last_127_chars, True, ctx.fg)
        text_visual_width = self.rect.width - 2 * self.text_inset

        source_rect = pg.Rect(
            self.rect.x + self.text_inset,
            self.rect.centery - text_surf.get_height() // 2,
            min(text_visual_width, text_surf.get_width()),
            text_surf.get_height()
        )

        surface.blit(text_surf, source_rect)

        # Border
        pg.draw.rect(surface, ctx.border, self.rect, width=ctx.border_w)
