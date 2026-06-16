# UI spacers

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


from pygame import Rect, Surface

from .widget import Widget, DrawContext


class Spacer(Widget):
    def __init__(self, *, flex: int = 0, min_w: int = 0, min_h: int = 0):
        super().__init__(flex=flex)
        self.min_w = min_w
        self.min_h = min_h

    def preferred_size(self) -> tuple[int, int]:
        return (self.min_w, self.min_h)

    def layout(self, rect: Rect) -> None:
        self.rect = rect  # I eat all the space, haha!

    def draw(self, surface: Surface, ctx: DrawContext) -> None:
        pass  # I'm just empty space, so nothing to see here!
