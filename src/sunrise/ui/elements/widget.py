# base widget class

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


from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pygame as pg

from sunrise.core.custom_types import Colour, AColour


@dataclass(frozen=True, kw_only=True)
class DrawContext:
    # border
    border: Colour | AColour
    border_w: int = 2

    # background
    bg: Colour | AColour
    active_bg: Colour | AColour

    # foreground
    fg: Colour | AColour
    disabled_fg: Colour | AColour

    # typography
    font: pg.font.Font


class Widget(ABC):
    def __init__(self) -> None:
        # Where am I relative to the last `rect` from the last `layout()` call?
        # x, y = where am I relative to my parent's rect
        # w, h = how big do I get to be?
        self.rect: pg.Rect = pg.Rect(0, 0, 0, 0)

        # What's my family?
        self.children: list[Widget] = []
        self.parent: Widget | None = None

        # What's my current state?
        self.visible: bool = True            # Will I be visible?
        self.active: bool = False            # Will I accept user input?
        self.layout_is_dirty: bool = False   # Do I need to refresh my layout?

    @abstractmethod
    def preferred_size(self) -> tuple[int, int]:
        """If no one told me how big I have to be,
        then how big do I want to be?"""
        raise NotImplementedError

    @abstractmethod
    def layout(self, rect: pg.Rect) -> None:
        """Given that I have to fit into a `rect`-sized area,
        I must assign rects to myself and my children.
        This function assigns rects while propagating layout downwards,
        doesn't return anything."""
        raise NotImplementedError

    @abstractmethod
    def draw(self, surface: pg.Surface, ctx: DrawContext) -> None:
        """Draw myself to the screen."""
        raise NotImplementedError
