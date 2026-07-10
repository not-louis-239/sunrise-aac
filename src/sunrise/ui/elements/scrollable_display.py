# vertically scrollable display

# TODO: one day we could merge this under Panel, such that if the content
# is too large to fit on the screen, then make it scrollable
# perhaps with `allow_horiz_scroll` and `allow_vert_scroll` parameters
# which, if enabled, would allow scrolling if content got too big

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

from sunrise.ui.themes import Theme
from sunrise.ui.elements._scroll_physics import ScrollPhysics
from sunrise.ui.elements.widget import Widget
from sunrise.ui.elements._dummy_surface import DUMMY_SURFACE


class ScrollableDisplay(Widget):
    """Creates a display that is vertically scrollable.
    Its height depends on the preferred size of the contents inside of the display."""
    def __init__(
            self, *,
            flex: int = 0, gap: int = 0, child: Widget, padding: int = 0
        ) -> None:
        super().__init__(flex=flex)
        self.padding = padding
        self.child = child
        self.children = [child]
        self.internal_rect = pg.Rect(0, 0, 0, 0)
        self.internal_surface: pg.Surface = DUMMY_SURFACE
        self.scroll_physics = ScrollPhysics(y_max=self._internal_dims()[1])
        self.gap = gap

    def _internal_dims(self) -> tuple[int, int]:
        """Get the preferred vertical size of all child components
        inside `self`, including gaps imposed by `self`, but
        excluding padding. This is the size required for `self`'s
        internal surface."""

        total_raw_height = sum(child.preferred_size()[1] for child in self.children)
        num_gaps = max(0, len(self.children) - 1)
        total_gap_h = self.gap * num_gaps

        total_internal_h = total_raw_height + total_gap_h
        total_internal_w = max(0, self.rect.width - 2 * self.padding)

        return total_internal_w, total_internal_h

    def _refresh_internal_surface(self, current_theme: Theme) -> None:
        """Redraws `self`'s internal surface. Could be expensive depending
        on what is inside `self`. """

        # Resize the surface if needed
        required_size = self._internal_dims()
        if required_size != self.internal_surface.get_size():
            self.internal_surface = pg.Surface(required_size)

        # Then redraw the content
        self.child.draw(surface=self.internal_surface, current_theme=current_theme)

    def update(self, dt_s: float) -> None:
        self.scroll_physics.update(dt_s=dt_s)

    def handle_scroll(self, event: pg.event.Event) -> None:
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.scroll_physics.handle_scroll(event)

    def preferred_size(self) -> tuple[int, int]:
        cw, ch = self.child.preferred_size()
        return cw + 2 * self.padding, ch + 2 * self.padding

    def layout(self, rect: pg.Rect) -> None:
        # Layout oneself to the rect to which it has been assigned (from a parent)
        # Then calculate the size of `self`'s internal rect and layout children according to it.
        self.rect = rect

        internal_w, internal_h = self._internal_dims()
        self.child.layout(pg.Rect(0, 0, internal_w, internal_h))

    def draw(self, surface: pg.Surface, current_theme: Theme) -> None:
        # Draw the content of `self` to the given surface.

        self._refresh_internal_surface(current_theme=current_theme)

        # Get the relevant part of `self`'s internal surface
        # and draw it on the given surface.
        relevant_rect = pg.Rect(0, self.scroll_physics.y, self.rect.width - 2 * self.padding, self.scroll_physics.y + self.rect.height - 2 * self.padding)
        surface.blit(self.internal_surface, dest=self.rect, area=relevant_rect)
