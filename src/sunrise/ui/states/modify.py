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
from sunrise.ui.elements import Panel, Label, HBox, VBox, SBox, Icon, Spacer, InputBox, HAlign, VAlign, Dropdown, RectangularUIButton
from sunrise.core.asset_manager import PropertyIconID
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

        # Title label
        self.title_label = Label(text="Modify Button", font=self.aac_inst.assets.fonts.title_font, flex=1)

        # Close and proceed buttons
        self.close_button = CircularUIButton(font=self.aac_inst.assets.fonts.ui_button_font, r=ICON_SIZE // 2, img_path=self.aac_inst.assets.images.exit_icon, border_w=0, k_fg=ThemeKey.FG_ERROR)
        self.proceed_button = CircularUIButton(font=self.aac_inst.assets.fonts.ui_button_font, r=ICON_SIZE // 2, img_path=self.aac_inst.assets.images.proceed_icon, border_w=0, k_fg=ThemeKey.FG_SUCCESS)

        # Input widgets and widgets that need to be updated for each button
        self.label_input_box = InputBox(flex=1, font=self.aac_inst.assets.fonts.ui_text_font_m, inset=UI_MARGIN)
        self.node_input_box = InputBox(flex=1, font=self.aac_inst.assets.fonts.ui_text_font_m, inset=UI_MARGIN)
        self.dest_input_box = InputBox(flex=1, font=self.aac_inst.assets.fonts.ui_text_font_m, inset=UI_MARGIN)
        self.img_path_input_box = InputBox(flex=1, font=self.aac_inst.assets.fonts.ui_text_font_m, inset=UI_MARGIN)
        self.word_input_box = InputBox(flex=1, font=self.aac_inst.assets.fonts.ui_text_font_m, inset=UI_MARGIN)
        self.type_input_box = InputBox(flex=1, font=self.aac_inst.assets.fonts.ui_text_font_m, inset=UI_MARGIN)

        func_options_dict: dict[str, str | None] = {str(v): v for v in [*self.aac_inst.engine.get_func_options()]}
        func_options_dict[""] = None  # empty string as stand-in for None
        self.func_dropdown = Dropdown(flex=1, font=self.aac_inst.assets.fonts.ui_text_font_m, inset=UI_MARGIN, options=func_options_dict, sentinel="none")

        self.coords_label = Label(font=self.aac_inst.assets.fonts.ui_text_font_m)
        self.move_button = RectangularUIButton(font=self.aac_inst.assets.fonts.ui_text_font_m, text="Move", inset=UI_MARGIN)

        # Put together the main panel
        self.popup = Panel(
            horiz_padding=UI_MARGIN,
            vert_padding=UI_MARGIN,

            # Main VBox
            child=VBox(
                gap=UI_MARGIN,
                children=[
                    # Title HBox
                    HBox(
                        children=[
                            self.title_label,
                            self.close_button
                        ]
                    ),

                    # Content VBox
                    VBox(
                        gap=UI_MARGIN,
                        children=[
                            # 1st row
                            HBox(
                                gap=UI_MARGIN,
                                children=[
                                    Icon(img_path=self.aac_inst.assets.images.property_icons[PropertyIconID.LABEL], size=(ICON_SIZE, ICON_SIZE), k_fg=ThemeKey.FG),
                                    self.label_input_box,
                                    Icon(img_path=self.aac_inst.assets.images.property_icons[PropertyIconID.COORDS], size=(ICON_SIZE, ICON_SIZE), k_fg=ThemeKey.FG),
                                    SBox(child=self.coords_label, forced_width=100, h_align=HAlign.CENTRE, v_align=VAlign.CENTRE),
                                    self.move_button
                                ]
                            ),
                            # 2nd row
                            HBox(
                                gap=UI_MARGIN,
                                children=[
                                    Icon(img_path=self.aac_inst.assets.images.property_icons[PropertyIconID.MAP_PIN], size=(ICON_SIZE, ICON_SIZE), k_fg=ThemeKey.FG),
                                    self.node_input_box,
                                    Icon(img_path=self.aac_inst.assets.images.proceed_icon, size=(ICON_SIZE, ICON_SIZE), k_fg=ThemeKey.FG),
                                    Icon(img_path=self.aac_inst.assets.images.property_icons[PropertyIconID.DEST], size=(ICON_SIZE, ICON_SIZE), k_fg=ThemeKey.FG),
                                    self.dest_input_box
                                ]
                            ),
                            # 3rd row
                            HBox(
                                gap=UI_MARGIN,
                                children=[
                                    Icon(img_path=self.aac_inst.assets.images.property_icons[PropertyIconID.IMAGE], size=(ICON_SIZE, ICON_SIZE), k_fg=ThemeKey.FG),
                                    self.img_path_input_box,
                                ]
                            ),
                            # 4th row
                            HBox(
                                gap=UI_MARGIN,
                                children=[
                                    Icon(img_path=self.aac_inst.assets.images.property_icons[PropertyIconID.TEXT], size=(ICON_SIZE, ICON_SIZE), k_fg=ThemeKey.FG),
                                    self.word_input_box,
                                    Icon(img_path=self.aac_inst.assets.images.property_icons[PropertyIconID.TYPE], size=(ICON_SIZE, ICON_SIZE), k_fg=ThemeKey.FG),
                                    self.type_input_box,
                                    Icon(img_path=self.aac_inst.assets.images.property_icons[PropertyIconID.FUNC], size=(ICON_SIZE, ICON_SIZE), k_fg=ThemeKey.FG),
                                    self.func_dropdown
                                ]
                            )
                        ]
                    ),

                    # Spacer
                    Spacer(flex=1),

                    # Proceed button at bottom
                    HBox(
                        children=[
                            Spacer(flex=1),
                            self.proceed_button
                        ]
                    )
                ]
            )
        )

        self._layout_widgets()

    def _layout_widgets(self) -> None:
        self.popup.layout(pg.Rect(UI_MARGIN, UI_MARGIN, WN_W - 2 * UI_MARGIN, WN_H - 2 * UI_MARGIN))

    def _set_coords_text(self, coords: tuple[int, int] | None) -> None:
        text = f"({coords[0]}, {coords[1]})" if coords is not None else ""
        if self.coords_label.text != text:
            self.coords_label.set_text(text)
            self._layout_widgets()

    def set_button_to_modify(self, button: Button | None, coords: tuple[int, int] | None = None) -> None:
        self.button_to_modify = button

        if self.button_to_modify is not None:
            # Update labels
            self.title_label.set_text(f"Modifying Button '{self.button_to_modify.label}'")
            self._set_coords_text(self.button_to_modify.coords)

            # Pre-fill input fields if the button exists, else leave them blank
            self.label_input_box.text = self.button_to_modify.label
            self.node_input_box.text = self.button_to_modify.node
            self.dest_input_box.text = str(self.button_to_modify.dest) if self.button_to_modify.dest is not None else ""
            self.img_path_input_box.text = self.button_to_modify.img if self.button_to_modify.img is not None else ""
            self.word_input_box.text = self.button_to_modify.word if self.button_to_modify.word is not None else ""
            self.type_input_box.text = self.button_to_modify.type
            self.func_dropdown.set_from_option_str(self.button_to_modify.func or "")
        else:
            self.title_label.set_text("Creating New Button")
            self._set_coords_text(coords)

        self._layout_widgets()

    def update(self, dt_s: float) -> None:
        if self.button_to_modify is not None:
            self._set_coords_text(self.button_to_modify.coords)

        self.func_dropdown.update(dt_s=dt_s)
        self.func_dropdown.update_hover_state(mouse_pos=pg.mouse.get_pos())

    def _handle_left_click(self, event: pg.event.Event) -> None:
        # Check for dropdown events first
        if self.func_dropdown.handle_left_click(event):
            return

        # Close button
        if self.close_button.check_click(event.pos):
            self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.TALK)
            return

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

            if event.type == pg.MOUSEWHEEL:
                self.func_dropdown.handle_scroll(event)

        for button in [
            self.label_input_box,
            self.node_input_box,
            self.dest_input_box,
            self.img_path_input_box,
            self.word_input_box,
            self.type_input_box,
        ]:
            button.handle_input(keys=keys, events=events, dt_s=dt_s)

    def draw(self, screen: Surface) -> None:
        # Get current theme and draw popup
        theme = self.aac_inst.get_current_theme()
        screen.fill(theme[ThemeKey.BG])

        self.popup.draw(screen, current_theme=theme)
