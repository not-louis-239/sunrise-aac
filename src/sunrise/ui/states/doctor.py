# doctor state for linting the internal language tree and revealing issues
# such as unreachable nodes

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

from sunrise.core.bus import EventID
from sunrise.ui.states.base_states import State, StateID
from sunrise.ui.themes import ThemeKey
from sunrise.ui.constants import ICON_SIZE, UI_MARGIN, WN_H, WN_W
from sunrise.ui.elements import Panel, HBox, VBox, Spacer, Label, CircularUIButton

if TYPE_CHECKING:
    from sunrise.core.aac import AAC



class DoctorState(State):
    def __init__(self, aac_inst: AAC) -> None:
        super().__init__(aac_inst)

        # Close button
        self.close_button = CircularUIButton(
            r=ICON_SIZE // 2, font=self.aac_inst.assets.fonts.ui_button_font,
            img_path=self.aac_inst.assets.images.exit_icon, border_w=0, k_fg=ThemeKey.FG_ERROR
        )

        self.panel = Panel(
            horiz_padding=UI_MARGIN,
            vert_padding=UI_MARGIN,
            child=VBox(
                gap=UI_MARGIN,
                children=[
                    HBox(
                        gap=UI_MARGIN,
                        children=[
                            Label(font=self.aac_inst.assets.fonts.ui_text_font_m, text="Doctor"),
                            Spacer(flex=1),
                            self.close_button
                        ]
                    ),
                    Spacer(flex=1)
                ]
            )
        )

        self.panel.layout(pg.Rect(UI_MARGIN, UI_MARGIN, WN_W - 2 * UI_MARGIN, WN_H - 2 * UI_MARGIN))

    def take_input(self, keys: ScancodeWrapper, events: list[Event], dt_s: float) -> None:
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.close_button.check_click(event.pos):
                    self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.TALK)

    def update(self, dt_s: float) -> None:
        pass

    def draw(self, screen: Surface) -> None:
        theme = self.aac_inst.get_current_theme()
        screen.fill(theme[ThemeKey.BG])

        self.panel.draw(surface=screen, current_theme=theme)
