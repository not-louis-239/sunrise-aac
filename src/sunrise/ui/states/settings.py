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
from pygame import Surface
from pygame.event import Event
from pygame.key import ScancodeWrapper

from sunrise.core.bus import EventID
from sunrise.ui.states.base_states import State, StateID
from sunrise.ui.elements import Panel, HBox, SBox, VAlign, VBox, Label, Spacer, Dropdown, CircularUIButton
from sunrise.ui.themes import THEMES, ThemeKey
from sunrise.ui.constants import UI_MARGIN_M, ICON_SIZE, WN_W, WN_H


class SettingsState(State):
    def __init__(self, aac_inst) -> None:
        super().__init__(aac_inst=aac_inst)

        ## Put together the UI panel

        # Proceed button
        self.proceed_button = CircularUIButton(r=ICON_SIZE // 2, font=self.aac_inst.assets.fonts.ui_text_font_m, img_path=self.aac_inst.assets.images.proceed_icon, k_fg=ThemeKey.FG_SUCCESS, border_w=0)

        # Theme dropdown
        self.theme_dropdown = Dropdown(options={theme.display_name: idx for idx, theme in enumerate(THEMES)}, font=self.aac_inst.assets.fonts.ui_text_font_m, inset=UI_MARGIN_M)
        self.theme_dropdown.set_from_option_str(THEMES[self.aac_inst.visuals.theme_idx].display_name)

        # Assemble the panel
        self.panel = Panel(
            horiz_padding=UI_MARGIN_M,
            vert_padding=UI_MARGIN_M,
            child=VBox(
                gap=UI_MARGIN_M,
                children=[
                    HBox(
                        gap=UI_MARGIN_M,
                        children=[
                            Label(text="Settings", font=self.aac_inst.assets.fonts.title_font),
                            Spacer(flex=1)
                        ]
                    ),
                    VBox(
                        gap=UI_MARGIN_M,
                        children=[
                            HBox(
                                gap=UI_MARGIN_M,
                                children=[
                                    SBox(
                                        child=Label(text="Theme", font=self.aac_inst.assets.fonts.ui_text_font_m),
                                        v_align=VAlign.CENTRE
                                    ),
                                    self.theme_dropdown,
                                ]
                            )
                        ]
                    ),
                    Spacer(flex=1),
                    HBox(
                        gap=UI_MARGIN_M,
                        children=[
                            Spacer(flex=1),
                            self.proceed_button
                        ]
                    )
                ]
            )
        )

        self.panel.layout(pg.Rect(UI_MARGIN_M, UI_MARGIN_M, WN_W - 2 * UI_MARGIN_M, WN_H - 2 * UI_MARGIN_M))

    def _proceed(self) -> None:
        self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.TALK)

    def update(self, dt_s: float) -> None:
        self.theme_dropdown.update(dt_s)
        self.theme_dropdown.update_hover_state(mouse_pos=pg.mouse.get_pos())

    def take_input(self, keys: ScancodeWrapper, events: list[Event], dt_s: float) -> None:
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.proceed_button.check_click(event.pos):
                    self._proceed()
                    continue

                # some settings can be applied immediately, such as theme changes
                if self.theme_dropdown.handle_left_click(event):
                    self.aac_inst.visuals.theme_idx = self.theme_dropdown.selected_value

            if event.type == pg.MOUSEWHEEL:
                self.theme_dropdown.handle_scroll(event)

    def draw(self, screen: Surface) -> None:
        theme = self.aac_inst.get_current_theme()
        screen.fill(theme[ThemeKey.BG])

        self.panel.draw(surface=screen, current_theme=theme)
        self.panel.draw_overlay(surface=screen, current_theme=theme)
