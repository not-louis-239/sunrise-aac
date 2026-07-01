# UI boxes

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


from enum import StrEnum

import pygame as pg

from sunrise.ui.themes import Theme

from .widget import Widget


class HAlign(StrEnum):
    LEFT = "left"
    CENTRE = "centre"
    RIGHT = "right"

class VAlign(StrEnum):
    TOP = "top"
    CENTRE = "centre"
    BOTTOM = "bottom"


class _Box(Widget):
    """Generic base class to store attributes common to both `HBox`es and `VBox`es"""

    def __init__(self, *, padding: int = 0, gap: int = 0, children: list[Widget] | None = None) -> None:
        """Initialises a new box.
        padding = space between the box's edge and the first or last child
        gap     = space between children in the box"""
        super().__init__()
        self.padding = padding
        self.gap = gap

        if children is not None:
            for child in children:
                self.add_child(child)

    def add_child(self, child: Widget) -> None:
        self.children.append(child)
        child.parent = self

    def draw(self, surface: pg.Surface, current_theme: Theme) -> None:
        for child in self.children:
            child.draw(surface=surface, current_theme=current_theme)

class HBox(_Box):
    """Horizontal box"""

    def preferred_size(self) -> tuple[int, int]:
        total_w = 0
        max_h = 0

        # calculate preferred size of children
        for child in self.children:
            w, h = child.preferred_size()
            total_w += w
            max_h = max(max_h, h)

        # add gap between children
        total_w += self.gap * max(0, len(self.children) - 1)

        # add padding
        total_w += self.padding * 2
        total_h = max_h + self.padding * 2

        return (total_w, total_h)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect

        # measure fixed sizes
        total_fixed_width = 0
        flex_children: list[Widget] = []

        for child in self.children:
            flex = child.flex
            if flex:
                flex_children.append(child)
                continue
            w, _ = child.preferred_size()
            total_fixed_width += w

        total_gaps = self.gap * max(0, len(self.children) - 1)

        remaining = rect.width - 2 * self.padding - total_fixed_width - total_gaps

        # assign flex space
        total_flex = sum(c.flex for c in flex_children)
        flex_widths = {}

        if total_flex > 0:
            for c in flex_children:
                flex_widths[c] = remaining * (c.flex / total_flex)

        # place children
        h = rect.height - 2 * self.padding
        x = rect.x + self.padding
        y = rect.y + self.padding

        for child in self.children:
            w, _ = child.preferred_size()

            if child in flex_widths:
                w = int(flex_widths[child])

            child_rect = pg.Rect(x, y, w, h)
            child.layout(child_rect)

            x += w + self.gap

class VBox(_Box):
    """Vertical box"""

    def preferred_size(self) -> tuple[int, int]:
        total_h = 0
        max_w = 0

        # calculate preferred size of children
        for child in self.children:
            w, h = child.preferred_size()
            total_h += h
            max_w = max(max_w, w)

        # add gaps
        total_h += self.gap * max(0, len(self.children) - 1)

        # add padding
        total_h += self.padding * 2
        total_w = max_w + self.padding * 2

        return total_w, total_h

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect

        total_fixed_height = 0
        flex_children = []

        for child in self.children:
            flex = child.flex
            if flex:
                flex_children.append(child)
            else:
                _, h = child.preferred_size()
                total_fixed_height += h

        total_gaps = self.gap * max(0, len(self.children) - 1)
        remaining = rect.height - 2 * self.padding - total_fixed_height - total_gaps

        total_flex = sum(c.flex for c in flex_children)
        flex_heights = {}

        # Assign flex space
        if total_flex > 0:
            for c in flex_children:
                flex_heights[c] = remaining * (c.flex / total_flex)

        # place children
        w = rect.width - 2 * self.padding
        x = rect.x + self.padding
        y = rect.y + self.padding

        for child in self.children:
            _, h = child.preferred_size()

            if child in flex_heights:
                h = int(flex_heights[child])

            child_rect = pg.Rect(x, y, w, h)
            child.layout(child_rect)

            y += h + self.gap

class SBox(_Box):
    """Sized box that forces its child into a fixed size, with alignment"""

    def __init__(
            self, child: Widget, *,
            forced_width: int | None, forced_height: int | None,
            h_align: HAlign = HAlign.CENTRE,
            v_align: VAlign = VAlign.CENTRE
        ) -> None:
        super().__init__()
        self.child = child
        self.forced_width = forced_width
        self.forced_height = forced_height
        self.h_align = h_align
        self.v_align = v_align

    def preferred_size(self) -> tuple[int, int]:
        # Ask the child what it wants, but override it if we have a forced constraint
        child_w, child_h = self.child.preferred_size()
        w = self.forced_width if self.forced_width is not None else child_w
        h = self.forced_height if self.forced_height is not None else child_h
        return (w, h)

    def layout(self, rect: pg.Rect):
        child_rect = rect.copy()

        # Clamp child width to forced width
        if self.forced_width is not None:
            child_rect.width = min(rect.width, self.forced_width)

        if self.forced_height is not None:
            child_rect.height = min(rect.height, self.forced_height)

        # Horizontal alignment
        match self.h_align:
            case HAlign.LEFT:
                child_rect.left = rect.left
            case HAlign.CENTRE:
                child_rect.centerx = rect.centerx
            case HAlign.RIGHT:
                child_rect.right = rect.right

        # Vertical alignment
        match self.v_align:
            case VAlign.TOP:
                child_rect.top = rect.top
            case VAlign.CENTRE:
                child_rect.centery = rect.centery
            case VAlign.BOTTOM:
                child_rect.bottom = rect.bottom

        self.rect = rect
        self.child.layout(child_rect)

    def draw(self, surface: pg.Surface, current_theme: Theme) -> None:
        self.child.draw(surface=surface, current_theme=current_theme)
