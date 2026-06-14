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

from sunrise.ui.elements.widget import DrawContext

from .widget import Widget


class Panel(Widget):
    def __init__(self, *, padding: int = 0, child: Widget) -> None:
        super().__init__()
        self.padding = padding
        self.child = child

    def preferred_size(self) -> tuple[int, int]:
        cw, ch = self.child.preferred_size()
        return (cw + 2 * self.padding, ch + 2 * self.padding)

    def layout(self, rect: pg.Rect) -> None:
        child_rect = rect.inflate(-2 * self.padding, -2 * self.padding)
        self.child.layout(child_rect)

    def draw(self, surface: pg.Surface, ctx: DrawContext) -> None:
        # background
        pg.draw.rect(surface, ctx.bg, self.rect)

        # border
        pg.draw.rect(surface, ctx.border, self.rect, ctx.border_w)

        # child
        self.child.draw(surface, ctx)
