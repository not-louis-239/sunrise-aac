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


from typing import TYPE_CHECKING

import pygame as pg
from pygame import Surface
from pygame.event import Event
from pygame.key import ScancodeWrapper

from sunrise.ui.elements.input_boxes import InputBox
from sunrise.core.load_nodes import Button
from sunrise.core.bus import EventID
from sunrise.ui.states.base_states import State, StateID
from sunrise.ui.elements.ui_buttons import CircularUIButton

from sunrise.ui.constants import WN_W, WN_H, UI_MARGIN_S, ICON_SIZE, BORDER_WIDTH

if TYPE_CHECKING:
    from sunrise.core.aac import AAC

class ModifyState(State):
    def __init__(self, aac_inst: AAC) -> None:
        super().__init__(aac_inst)
        self.aac_inst.bus.subscribe(EventID.SET_MODIFY_BUTTON, self.set_button_to_modify)
        self.popup_rect = pg.Rect(UI_MARGIN_S, UI_MARGIN_S, WN_W - UI_MARGIN_S * 2, WN_H - UI_MARGIN_S * 2)

        self.close_button = CircularUIButton(r=ICON_SIZE // 2)
        self.proceed_button = CircularUIButton(r=ICON_SIZE // 2)

        # Button = existing button to modify
        # None   = no button was selected, so making a new one
        self.button_to_modify: Button | None = None

        self.input_box_font = pg.font.Font(self.aac_inst.assets.fonts.ui_font, 32)

        box_h = int(WN_H * 0.08)
        box_y = UI_MARGIN_S + UI_MARGIN
        row_x = UI_MARGIN_S + UI_MARGIN

        # Row 1 - input box and path/to/image box
        width = int(WN_W * 0.25)
        self.label_input_box = InputBox(row_x, box_y, width, box_h, font=self.input_box_font)
        row_x += width + UI_MARGIN
        width = int(WN_W * 0.55)
        self.path_input_box = InputBox(row_x, box_y, width, box_h, font=self.input_box_font)

    def set_button_to_modify(self, button: Button | None, coords: tuple[int, int] | None = None) -> None:
        # Set the button
        self.button_to_modify = button

        # Pre-fill input fields

    def update(self, dt_s: float) -> None:
        pass

    def _handle_left_click(self, event: pg.event.Event) -> None:
        # Close button
        if self.close_button.check_click(event.pos):
            self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.TALK)

        # Proceed button
        if self.proceed_button.check_click(event.pos):
            # Existing button - update button attributes
            if self.button_to_modify is not None:
                ...  # TODO

            # Creating a new button - save before emitting state change
            else:
                ...  # TODO

            self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.TALK)

    def take_input(self, keys: ScancodeWrapper, events: list[Event], dt_s: float) -> None:
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_left_click(event)
        self.label_input_box._handle_input(keys=keys, events=events, dt_s=dt_s)

    def draw(self, screen: Surface) -> None:
        # Get current theme and draw popup
        theme = self.aac_inst.get_current_theme()
        screen.fill(theme.bg_colour)
        pg.draw.rect(screen, theme.fg_colour, self.popup_rect, BORDER_WIDTH)

        # Close button
        rect = pg.Rect(0, 0, *self.aac_inst.assets.images.exit_icon[theme].get_size())
        rect.center = (self.close_button.centre_x, self.close_button.centre_y)
        screen.blit(self.aac_inst.assets.images.exit_icon[theme], rect)

        # Proceed button
        rect = pg.Rect(0, 0, *self.aac_inst.assets.images.exit_icon[theme].get_size())
        rect.center = (self.proceed_button.centre_x, self.proceed_button.centre_y)
        screen.blit(self.aac_inst.assets.images.proceed_icon[theme], rect)

        # Draw input fields
        self.label_input_box.draw(
            screen,
            bg_active_colour=theme.bg_colour,
            bg_inactive_colour=theme.bg_colour,
            fg_colour=theme.fg_colour,
            border_colour=theme.fg_colour
        )
        self.path_input_box.draw(
            screen,
            bg_active_colour=theme.bg_colour,
            bg_inactive_colour=theme.bg_colour,
            fg_colour=theme.fg_colour,
            border_colour=theme.fg_colour
        )
