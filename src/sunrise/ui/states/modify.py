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

from sunrise.ui.themes import ThemeKey
from sunrise.ui.elements.input_boxes import InputBox
from sunrise.core.load_nodes import Button
from sunrise.core.bus import EventID
from sunrise.ui.states.base_states import State, StateID
from sunrise.ui.elements.ui_buttons import CircularUIButton

from sunrise.ui.constants import WN_W, WN_H, UI_MARGIN, ICON_SIZE

if TYPE_CHECKING:
    from sunrise.core.aac import AAC

class ModifyState(State):
    def __init__(self, aac_inst: AAC) -> None:
        super().__init__(aac_inst)
        self.aac_inst.bus.subscribe(EventID.SET_MODIFY_BUTTON, self.set_button_to_modify)
        self.popup_rect = pg.Rect(UI_MARGIN, UI_MARGIN, WN_W - UI_MARGIN * 2, WN_H - UI_MARGIN * 2)

        # Button = existing button to modify
        # None   = no button was selected, so making a new one
        self.button_to_modify: Button | None = None

        ## Set up UI popup

        # Close and proceed buttons
        self.close_button = CircularUIButton(font=self.aac_inst.assets.fonts.ui_button_font, r=ICON_SIZE // 2)
        self.proceed_button = CircularUIButton(font=self.aac_inst.assets.fonts.ui_button_font, r=ICON_SIZE // 2)

        # TODO: finish the UI popup setup

    def set_button_to_modify(self, button: Button | None, coords: tuple[int, int] | None = None) -> None:
        # Set the button
        self.button_to_modify = button

        # Pre-fill input fields if the button exists, else leave them blank
        # TODO: Implement this part of the function

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

    def draw(self, screen: Surface) -> None:
        # Get current theme and draw popup
        theme = self.aac_inst.get_current_theme()
        screen.fill(theme[ThemeKey.BG])
