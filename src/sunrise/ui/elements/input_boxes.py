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
from sunrise.core.problem_severity import Severity
from sunrise.ui.constants import BORDER_WIDTH, CURSOR_FLASH_INTERVAL, CURSOR_WIDTH
from sunrise.ui.themes import Theme, ThemeKey
from sunrise.ui.utils import get_text_surf, wrap_text

from .widget import Widget


class InputBox(Widget):
    def __init__(
            self, *,
            flex: float = 0, font: pg.font.Font, inset: int,
            k_bg: ThemeKey = ThemeKey.BG,
            k_bg_active: ThemeKey = ThemeKey.BG_ACTIVE,
            k_fg: ThemeKey = ThemeKey.FG,
            k_fg_active: ThemeKey = ThemeKey.FG_ACTIVE,
            k_cursor: ThemeKey = ThemeKey.FG,
            k_border: ThemeKey = ThemeKey.BORDER,
            k_bg_warning: ThemeKey = ThemeKey.BG_WARNING,
            k_bg_error: ThemeKey = ThemeKey.BG_ERROR,
            k_border_warning: ThemeKey = ThemeKey.FG_WARNING,
            k_border_error: ThemeKey = ThemeKey.FG_ERROR,
            k_sentinel: ThemeKey = ThemeKey.FG_DISABLED,  # sentinel to show in the input box when empty
            sentinel_text: str = "None",
            fixed_tooltip_width: int | None = None,
            border_w: int = BORDER_WIDTH
        ) -> None:
        # Creates a left-aligned InputBox

        super().__init__(flex=flex)
        self.text: str = ""
        self.font = font  # needed so that it can auto-adjust text width while drawing
        self.inset = inset
        self.active = False
        self.delete_timer: float = DELETE_DELAY
        self.cursor_flash_time: float = 0

        self.k_bg = k_bg
        self.k_bg_active = k_bg_active
        self.k_fg = k_fg
        self.k_fg_active = k_fg_active
        self.k_cursor = k_cursor
        self.k_border = k_border
        self.k_bg_warning = k_bg_warning
        self.k_bg_error = k_bg_error
        self.k_border_warning = k_border_warning
        self.k_border_error = k_border_error
        self.k_sentinel = k_sentinel

        self.severity: Severity = Severity.OK
        # Can be for error messages, but also can be used to display tooltips below `self` when `self.severity` is set to `OK`
        self.error_tooltip_msg: str | None = None

        self.sentinel_text = sentinel_text

        self.fixed_tooltip_width = fixed_tooltip_width
        self.border_w = border_w

    def set_error_msg(self, severity: Severity = Severity.OK, msg: str | None = None) -> None:
        self.severity = severity
        self.error_tooltip_msg = msg

    def clear_error_msg(self) -> None:
        self.severity = Severity.OK
        self.error_tooltip_msg = None

    def handle_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.event.Event], dt_s: float) -> None:
        if self.active:
            self.cursor_flash_time = (self.cursor_flash_time + dt_s) % CURSOR_FLASH_INTERVAL
        else:
            self.cursor_flash_time = 0

        # Handle KEYDOWN events
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.active = self.rect.collidepoint(event.pos)
                self.cursor_flash_time = 0
            elif event.type == pg.KEYDOWN:
                if self.active:
                    if event.key == pg.K_BACKSPACE:
                        self.text = self.text[:-1]
                        self.cursor_flash_time = 0
                    elif event.key not in (pg.K_RETURN, pg.K_ESCAPE, pg.K_TAB):
                        # Append character
                        self.text += event.unicode
                        self.cursor_flash_time = 0

        # Handle delete
        if keys[pg.K_BACKSPACE] and self.active:
            self.delete_timer -= dt_s
            if self.delete_timer <= 0:
                self.text = self.text[:-1]
                self.delete_timer += DELETE_INTERVAL
                self.cursor_flash_time = 0
        else:
            # If delete is not held down, reset the delete timer
            self.delete_timer = DELETE_DELAY

    def preferred_size(self) -> tuple[int, int]:
        return (0, self.font.get_height() + 2 * self.inset)

    def layout(self, rect) -> None:
        self.rect = rect

    def _draw_input_field(self, surface: pg.Surface, current_theme: Theme) -> None:
        """Draw the part of `self` that the user can click"""

        # Draw the background and border
        k_bg = self.k_bg_active if self.active else self.k_bg
        k_fg = self.k_sentinel if not self.text else self.k_fg_active if self.active else self.k_fg

        pg.draw.rect(surface, current_theme[k_bg], self.rect)

        # Text - rendering only last 255 chars for performance
        text = self.sentinel_text if not self.text else self.text[-255:]
        text_surf = get_text_surf(self.font, text, current_theme[k_fg])
        text_visual_width = self.rect.width - 2 * self.inset

        # Draw the text aligned to left-centre
        dest = (
            self.rect.x + self.inset,
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
            cursor_x = self.rect.x + self.inset + (0 if not self.text else min(text_visual_width, text_surf.get_width()))
            cursor_top_y = self.rect.centery - text_surf.get_height() // 2
            cursor_bot_y = self.rect.centery + text_surf.get_height() // 2
            pg.draw.line(surface, current_theme[self.k_cursor], (cursor_x, cursor_top_y), (cursor_x, cursor_bot_y), width=CURSOR_WIDTH)

        # Border
        match self.severity:
            case Severity.ERROR:
                border_colour = current_theme[self.k_border_error]
            case Severity.WARNING:
                border_colour = current_theme[self.k_border_warning]
            case Severity.OK:
                border_colour = current_theme[self.k_border]
            case _:
                border_colour = current_theme[self.k_border]

        pg.draw.rect(surface, border_colour, self.rect, width=self.border_w)

    def _draw_error_tooltip(self, surface: pg.Surface, current_theme: Theme) -> None:
        """Draws the error tooltip for the input field just below `self`,
        but skip drawing if `self` is not active."""

        if not self.active or not self.error_tooltip_msg:
            return

        match self.severity:
            case Severity.ERROR:
                border_colour = current_theme[self.k_border_error]
                tooltip_bg_colour = current_theme[self.k_bg_error]
            case Severity.WARNING:
                border_colour = current_theme[self.k_border_warning]
                tooltip_bg_colour = current_theme[self.k_bg_warning]
            case Severity.OK:
                border_colour = current_theme[self.k_border]
                tooltip_bg_colour = current_theme[self.k_bg]
            case _:
                border_colour = current_theme[self.k_border]
                tooltip_bg_colour = current_theme[self.k_bg]

        # Calculate tooltip width
        tooltip_w = self.fixed_tooltip_width or self.rect.w

        # Draw the text
        lines = wrap_text(text=self.error_tooltip_msg, font=self.font, maxwidth=tooltip_w - 2 * self.inset)
        font_h = self.font.get_height()
        text_height = font_h * len(lines)

        # Tooltip rect
        tooltip_rect = pg.Rect(self.rect.left, self.rect.bottom, tooltip_w, text_height + 2 * self.inset)

        start_x = self.rect.x + self.inset
        start_y = self.rect.bottom + self.inset

        fg_colour = current_theme[self.k_fg]

        # Draw background
        pg.draw.rect(surface, tooltip_bg_colour, tooltip_rect)

        # Draw text
        for lineno, line in enumerate(lines):
            surface.blit(get_text_surf(self.font, line, fg_colour), (start_x, start_y + font_h * lineno))

        # Draw the border
        pg.draw.rect(surface, border_colour, tooltip_rect, width=self.border_w)

    def draw(self, surface: pg.Surface, current_theme: Theme) -> None:
        self._draw_input_field(surface, current_theme)

    def draw_overlay(self, surface: pg.Surface, current_theme: Theme) -> None:
        self._draw_error_tooltip(surface, current_theme)
