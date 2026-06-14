# module for UI buttons
# these thingos are different from the other Button class as
# they are for UI menus, the other ones are for the AAC buttons

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


from abc import abstractmethod

import pygame as pg

from sunrise.ui.elements.widget import DrawContext

from .widget import Widget


class _UIButton(Widget):
    @abstractmethod
    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        raise NotImplementedError

class RectangularUIButton(_UIButton):
    def __init__(self, text: str, font: pg.font.Font, inset: int, fixed_size: tuple[int, int] | None = None) -> None:
        super().__init__()
        self.text = text
        self.font = font
        self.inset = inset
        self.fixed_size = fixed_size

    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def preferred_size(self) -> tuple[int, int]:
        if self.fixed_size is not None:
            return self.fixed_size

        fw, fh = self.font.size(self.text)
        return (fw + 2 * self.inset, fh + 2 * self.inset)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect

    def draw(self, surface: pg.Surface, ctx: DrawContext) -> None:
        # Draw the button's background
        bg_colour = ctx.active_bg if self.active else ctx.bg
        pg.draw.rect(surface, bg_colour, self.rect)

        # Draw border
        pg.draw.rect(surface, ctx.border, self.rect, width=ctx.border_w)

        # Draw text
        text_surface = ctx.font.render(self.text, True, ctx.fg if self.active else ctx.disabled_fg)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class CircularUIButton(_UIButton):
    def __init__(self, r: int) -> None:
        self.r = r

    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        return mouse_pos[0] ** 2 + mouse_pos[1] ** 2 <= self.r ** 2

    def preferred_size(self) -> tuple[int, int]:
        return (self.r * 2, self.r * 2)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect

    def draw(self, surface: pg.Surface, ctx: DrawContext) -> None:
        # Draw background
        pg.draw.circle(surface, ctx.active_bg if self.active else ctx.bg, self.rect.center, self.r)
