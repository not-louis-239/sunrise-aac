from collections.abc import Sequence
from enum import StrEnum
from typing import TypeVar

import pygame as pg
from pygame import Surface

from sunrise.ui.constants import BORDER_WIDTH, WN_H
from sunrise.ui.elements._scroll_physics import ScrollPhysics
from sunrise.ui.themes import Theme, ThemeKey
from sunrise.ui.utils import crop_text_to_fit

from ._dummy_surface import DUMMY_SURFACE
from .widget import Widget

DROPDOWN_TRIANGLE_SIZE = 20

T = TypeVar("T")

class _DropdownDisplayStatus(StrEnum):
    DOWNWARD = "DOWNWARD"
    UPWARD = "UPWARD"
    DOWNWARD_SCROLL = "DOWNWARD_SCROLL"
    UPWARD_SCROLL = "UPWARD_SCROLL"


class Dropdown[T](Widget):
    def __init__(
            self, *,
            flex: float = 0,
            options: dict[str, T],  # {label: value}
            font: pg.font.Font,
            inset: int = 0,
            sentinel: str = "",  # sentinel label to display for (1) values in `options` that have empty labels and (2) when such a value is selected
            k_bg: ThemeKey = ThemeKey.BG,
            k_fg: ThemeKey = ThemeKey.FG,
            k_border: ThemeKey = ThemeKey.BORDER,
            k_bg_hover_options: ThemeKey = ThemeKey.BG_ACTIVE,
            k_fg_hover_options: ThemeKey = ThemeKey.FG_ACTIVE
        ) -> None:
        """Dropdown UI element."""

        super().__init__(flex=flex)
        if not options:
            raise ValueError("Dropdown requires at least one option")

        self.options = options

        self.hovered_idx: int = -1
        self.chosen_idx: int = 0
        self.status: _DropdownDisplayStatus = _DropdownDisplayStatus.DOWNWARD

        # size of the options widget that is shown on-screen - it's a placeholder that gets evaluated at layout() time
        self.options_rect = pg.Rect(0, 0, 0, 0)

        # placeholder that gets evaluated at draw() time, but it prevents pg.Surface() churn which is wasteful
        # a new surface will only be created if self.options_surface doesn't meet size requirements after a self._reevaluate_status() call
        self.options_surface = DUMMY_SURFACE

        # needed to tell `self` when the `options_surface` is dirty
        self.last_theme: Theme | None = None
        self.last_hovered_idx: int | None = self.chosen_idx

        self.font = font
        self.inset = inset
        self.sentinel = sentinel
        self.k_bg = k_bg
        self.k_fg = k_fg
        self.k_border = k_border
        self.k_bg_hover_options = k_bg_hover_options
        self.k_fg_hover_options = k_fg_hover_options

        self.scroll_physics = ScrollPhysics(y_max=self._scroll_max())
        self._reevaluate_status()

    def _labels(self) -> list[str]:
        """Returns a list of the labels of the options in `self`."""
        return list(self.options.keys())

    @property
    def selected_label(self) -> str:
        """Returns the label of the currently selected option."""
        return self._labels()[self.chosen_idx]

    @property
    def selected_value(self) -> T:
       """Returns the value of the currently selected option."""
       return self.options[self.selected_label]

    def _row_width(self) -> int:
        largest_w = max(self.font.size(opt)[0] for opt in self.options)  # for each option's label, get the largest width
        return largest_w + 3 * self.inset + DROPDOWN_TRIANGLE_SIZE

    def _row_height(self) -> int:
        """Height of a single row of the dropdown, including padding."""
        return self.font.get_height() + self.inset * 2

    def _dropdown_height(self) -> int:
        """Internal visual height of the full options list, excluding itself."""
        return self._row_height() * len(self.options)

    def _scroll_max(self) -> int:
        """Maximum vertical offset for the visible options list when it is scrollable."""
        return max(0, self._dropdown_height() - self.options_rect.height)

    def _reevaluate_status(self) -> None:
        """Set status to a _DropdownDisplayStatus based on positioning in the screen and whether
        `self` has enough room to extend upwards, downwards, or if it needs to be scrollable."""

        options_rect = pg.Rect(self.rect.left, self.rect.bottom, self.rect.width, self._dropdown_height())
        status = _DropdownDisplayStatus.DOWNWARD

        # If the options rect goes past the bottom of the screen, it's too big to extend downwards.
        # Try flipping so it opens upwards instead of opening downwards.
        if options_rect.bottom > WN_H:
            options_rect.top, options_rect.bottom = self.rect.top - self._dropdown_height(), self.rect.top
            status = _DropdownDisplayStatus.UPWARD

        # If it's still too large (the options rect's top is above the top of the screen), set it to scrollable
        if options_rect.top < 0:
            # Figure out whether top or bottom allows `self` more room
            # Prefer to droop downwards when there is an equal amount of space both above and below
            space_above = self.rect.top
            space_below = WN_H - self.rect.bottom

            if space_below >= space_above:
                options_rect.top = self.rect.bottom
                options_rect.height = WN_H - options_rect.top
                status = _DropdownDisplayStatus.DOWNWARD_SCROLL
            else:
               options_rect.top = 0
               options_rect.height = self.rect.top
               status = _DropdownDisplayStatus.UPWARD_SCROLL

        # Finally, set the attributes
        self.options_rect = options_rect
        self.status = status

        self.scroll_physics.y_max = self._scroll_max()

    def _refresh_options_surface_size(self) -> None:
        """If `self`'s options surface is of incorrect size, recreates it
        to be of the correct size."""
        correct_w, correct_h = self.rect.width, self._dropdown_height()

        w_dirty = self.options_surface.get_width() != correct_w
        h_dirty = self.options_surface.get_height() != correct_h

        if w_dirty or h_dirty:
            self.options_surface = pg.Surface((correct_w, correct_h))
            self.options_surface.fill((0, 0, 0))

    def _refresh_options_surface_content(self, current_theme: Theme) -> None:
        """If `self`'s `options_surface`'s content is dirty, redraws it.
        Assumes that the `options_surface` has already been resized to be correct."""

        if self.last_theme == current_theme and self.hovered_idx == self.last_hovered_idx:
           return

        row_h = self._row_height()
        self.options_surface.fill(current_theme[self.k_bg])

        for i, label in enumerate(self.options):
            row_rect = pg.Rect(0, i * row_h, self.rect.width, row_h)

            if i == self.hovered_idx:
                pg.draw.rect(self.options_surface, current_theme[self.k_bg_hover_options], row_rect)

            # Draw text aligned to left-centre
            text = crop_text_to_fit(label or self.sentinel, self.font, self.rect.width - self.inset * 2)
            text_surface = self.font.render(text, True, current_theme[self.k_fg_hover_options if i == self.hovered_idx else self.k_fg])
            self.options_surface.blit(text_surface, (self.inset, row_rect.top + (row_rect.height - text_surface.get_height()) // 2))

        self.last_theme = current_theme
        self.last_hovered_idx = self.hovered_idx

    def _refresh_options_surface(self, current_theme: Theme) -> None:
        """Recreates the options surface to be of correct size and redraws it, if required."""
        self._refresh_options_surface_size()
        self._refresh_options_surface_content(current_theme=current_theme)

    def _option_idx_at(self, mouse_pos: tuple[int, int]) -> int | None:
        """Returns the index of the option that the mouse is currently
        hovering over. If it doesn't correspond to a valid option,
        returns None."""

        if not self.options_rect.collidepoint(mouse_pos):
            return None

        row_h = self._row_height()

        # Non-scrollable cases
        if self.status in [
            _DropdownDisplayStatus.DOWNWARD,
            _DropdownDisplayStatus.UPWARD,
        ]:
            return (mouse_pos[1] - self.options_rect.top) // row_h

        # If the dropdown is scrollable...
        else:
            # true height = height accounting for scroll displacement
            true_h: float = self.scroll_physics.y + (mouse_pos[1] - self.options_rect.top)
            idx: int = int(true_h // row_h)
            return idx if 0 <= idx < len(self.options) else None

    def set_from_option_str(self, opt_label: str) -> None:
        """Set `self`'s option from an option string.
        If the option is not in `self`'s options, defaults to index 0."""

        if opt_label not in self.options:
            self.chosen_idx = 0
            return

        self.chosen_idx = self._labels().index(opt_label)

    def handle_scroll(self, event: pg.event.Event) -> bool:
        """Handles a scroll event and returns True if something happened, else False."""

        if not self.active:
            return False

        if self.status not in [_DropdownDisplayStatus.DOWNWARD_SCROLL, _DropdownDisplayStatus.UPWARD_SCROLL]:
            return False

        # Don't scroll if the mouse isn't hovering over the dropdown's options
        if not self.options_rect.collidepoint(pg.mouse.get_pos()):
            return False

        self.scroll_physics.handle_scroll(event)
        return True

    def handle_left_click(self, event: pg.event.Event) -> bool:
        """Handles a left-click and returns True if something happened, else False."""

        if self.rect.collidepoint(event.pos):
            self.active = not self.active
            return True

        if not self.active:
            return False

        self.hovered_idx = -1
        self.active = False

        option_idx = self._option_idx_at(event.pos)
        if option_idx is not None:
            self.chosen_idx = option_idx
            return True

        return False

    def preferred_size(self) -> tuple[int, int]:
        return (self._row_width(), self._row_height())

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect
        self._reevaluate_status()

    def _calc_triangle(self) -> Sequence[tuple[int, int]]:
        """Calculates the triangle for the dropdown button."""
        triangle_centre_x = self.rect.right - self.inset - DROPDOWN_TRIANGLE_SIZE // 2
        triangle_centre_y = self.rect.centery

        if self.active:
            pts = [
                (triangle_centre_x - DROPDOWN_TRIANGLE_SIZE // 2, triangle_centre_y + DROPDOWN_TRIANGLE_SIZE // 2),
                (triangle_centre_x + DROPDOWN_TRIANGLE_SIZE // 2, triangle_centre_y + DROPDOWN_TRIANGLE_SIZE // 2),
                (triangle_centre_x, triangle_centre_y - DROPDOWN_TRIANGLE_SIZE // 2)
            ]
        else:
            pts = [
                (triangle_centre_x - DROPDOWN_TRIANGLE_SIZE // 2, triangle_centre_y - DROPDOWN_TRIANGLE_SIZE // 2),
                (triangle_centre_x + DROPDOWN_TRIANGLE_SIZE // 2, triangle_centre_y - DROPDOWN_TRIANGLE_SIZE // 2),
                (triangle_centre_x, triangle_centre_y + DROPDOWN_TRIANGLE_SIZE // 2)
            ]

        return pts

    def _draw_dropdown_button(self, surface: Surface, current_theme: Theme) -> None:
        """Draws just the dropdown button and the currently selected option."""

        # Draw the dropdown button
        bg_colour = current_theme[self.k_bg]
        fg_colour = current_theme[self.k_fg]
        border_colour = current_theme[self.k_border]

        pg.draw.rect(surface, bg_colour, self.rect)
        pg.draw.rect(surface, border_colour, self.rect, BORDER_WIDTH)

        # Draw the selected option
        text = crop_text_to_fit(self.selected_label or self.sentinel, self.font, self.rect.width - self.inset * 2)
        text_surface = self.font.render(text, True, fg_colour)
        surface.blit(text_surface, (self.rect.left + self.inset, self.rect.top + (self.rect.height - text_surface.get_height()) // 2))

        # Draw the dropdown triangle
        pg.draw.polygon(surface, fg_colour, self._calc_triangle())

    def _draw_dropdown_options(self, surface: Surface, current_theme: Theme) -> None:
        """Draw the dropdown options"""

        # If the number of options to show is greater than what can fit
        # on the screen, attempt to show the options flipped upwards instead
        # Assumes that the `surface` parameter is the size of the application window
        # The status is updated in draw()

        # Draw dropdown options
        if self.status in [
            _DropdownDisplayStatus.DOWNWARD,
            _DropdownDisplayStatus.UPWARD
        ]:
            surface.blit(self.options_surface, self.options_rect)
        else:
            # Get the relevant part of `self`'s options surface
            relevant = pg.Rect(0, self.scroll_physics.y, self.options_rect.width, self.scroll_physics.y + self.options_rect.height)
            surface.blit(self.options_surface, self.options_rect, area=relevant)

        # Draw border
        pg.draw.rect(surface, current_theme[self.k_border], self.options_rect, width=BORDER_WIDTH)

    def draw(self, surface: Surface, current_theme: Theme) -> None:
        self._refresh_options_surface(current_theme=current_theme)
        self._draw_dropdown_button(surface, current_theme)

    def draw_overlay(self, surface: Surface, current_theme: Theme) -> None:
        if self.active:
            self._refresh_options_surface(current_theme=current_theme)
            self._draw_dropdown_options(surface, current_theme)

    def update(self, dt_s: float) -> None:
        self.scroll_physics.update(dt_s=dt_s)

    def update_hover_state(self, mouse_pos: tuple[int, int]) -> None:
        if self.active:
            option_idx = self._option_idx_at(mouse_pos)
            self.hovered_idx = option_idx if option_idx is not None else -1
        else:
            self.hovered_idx = -1
