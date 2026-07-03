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

from typing import TYPE_CHECKING

import pygame as pg
from pygame import Surface
from pygame.event import Event
from pygame.key import ScancodeWrapper

from crystallinium.text_utils import draw_text

from sunrise.ui.elements import (
    Panel,
    HBox,
    VBox,
    SBox,
    Icon,
    Spacer,
    Label,
    HAlign,
    VAlign,
    RectangularUIButton,
    CircularUIButton
)
from .base_states import State, StateID
from sunrise.core.bus import EventID
from sunrise.core.asset_manager import PropertyIconID
from sunrise.core.load_nodes import Button, save_language_tree
from sunrise.ui.constants import WN_W, WN_H, UI_MARGIN, ICON_SIZE, BORDER_WIDTH
from sunrise.ui.utils import crop_text_to_fit
from sunrise.ui.themes import ThemeKey


if TYPE_CHECKING:
    from sunrise.core.aac import AAC


def _make_icon(self: InspectState, *, prop: PropertyIconID) -> Icon:
    return Icon(img_path=self.aac_inst.assets.images.property_icons[prop], size=(ICON_SIZE, ICON_SIZE), k_fg=ThemeKey.FG)


class InspectState(State):
    def __init__(self, aac_inst: AAC) -> None:
        super().__init__(aac_inst)
        self.button: Button | None = None  # the button that `self` is currently inspecting
        self.node_label: str | None = None
        self.aac_inst.bus.subscribe(EventID.SET_INSPECT_BUTTON, self.set_button_and_node)

        ### Initialise UI components - components that need to be interacted with by `self` are bound as attributes
        self.black_overlay_surface = pg.Surface((WN_W, WN_H), pg.SRCALPHA)
        self.black_overlay_surface.fill((0, 0, 0, 128))

        ## Confirmation Dialog

        # Yes and No buttons
        self.yes_button = RectangularUIButton(text="Yes", font=self.aac_inst.assets.fonts.ui_button_font, inset=UI_MARGIN, k_fg=ThemeKey.FG_ERROR)
        self.no_button = RectangularUIButton(text="No", font=self.aac_inst.assets.fonts.ui_button_font, inset=UI_MARGIN)

        # "Are you sure?" popup
        self.confirmation_title = Label(font=self.aac_inst.assets.fonts.title_font)
        self.confirm_dialog = Panel(
            horiz_padding=UI_MARGIN,
            vert_padding=UI_MARGIN,
            child=VBox(
                gap=UI_MARGIN,
                children=[
                    self.confirmation_title,
                    HBox(
                        children=[
                            self.yes_button,
                            self.no_button
                        ]
                    )
                ]
            )
        )

        ## Main Panel

        # Title label
        self.title = Label(font=self.aac_inst.assets.fonts.title_font)

        # Close/continue buttons
        self.close_button = CircularUIButton(font=self.aac_inst.assets.fonts.ui_button_font, inset=UI_MARGIN, img_path=self.aac_inst.assets.images.exit_icon)
        self.continue_button = CircularUIButton(font=self.aac_inst.assets.fonts.ui_button_font, inset=UI_MARGIN, img_path=self.aac_inst.assets.images.proceed_icon)

        # Move, modify, delete buttons
        self.move_button = RectangularUIButton(text="Move", font=self.aac_inst.assets.fonts.ui_button_font, inset=UI_MARGIN)
        self.modify_button = RectangularUIButton(text="Modify", font=self.aac_inst.assets.fonts.ui_button_font, inset=UI_MARGIN)
        self.delete_button = RectangularUIButton(text="Delete", font=self.aac_inst.assets.fonts.ui_button_font, inset=UI_MARGIN)

        self.property_hboxes: list[HBox] = [
            HBox(
                padding=UI_MARGIN,
                children=[
                    _make_icon(self, prop=prop),
                    SBox(
                        forced_width=180,
                        h_align=HAlign.LEFT,
                        v_align=VAlign.CENTRE,
                        child=Label(font=self.aac_inst.assets.fonts.ui_text_font, text=text),
                    ),
                    Label(font=self.aac_inst.assets.fonts.ui_text_font),
                    Spacer(flex=1)
                ]
            ) for prop, text in [
                (PropertyIconID.TEXT, "word:"),
                (PropertyIconID.DEST, "dest:"),
                (PropertyIconID.FUNC, "func:"),
                (PropertyIconID.IMAGE, "image:"),
                (PropertyIconID.TYPE, "type:"),
            ]
        ]

        # Putting together the main panel
        self.popup = Panel(
            horiz_padding=UI_MARGIN,
            vert_padding=UI_MARGIN,

            # Main VBox
            child=VBox(
                padding=UI_MARGIN,
                children=[
                    # Header HBox
                    HBox(
                        children=[
                            self.title,
                            Spacer(flex=1),
                            self.close_button,
                        ]
                    ),

                    # Content VBox
                    VBox(
                        gap=UI_MARGIN,
                        children=self.property_hboxes  # type: ignore
                    ),

                    # Content -> Buttons Spacer
                    Spacer(flex=1),

                    # Buttons HBox
                    HBox(
                        children=[
                            self.move_button,
                            self.modify_button,
                            self.delete_button,
                        ]
                    )
                ]
            )
        )

    def _refresh_property_labels(self) -> None:
        button = self.button
        if button is None:
            return

        word = button.word
        dest = str(button.dest) if button.dest is not None else None
        func = button.func
        image_path = button.img
        btype = button.type

        for text, hbox in zip([word, dest, func, image_path, btype], self.property_hboxes):
            label = hbox.children[0]
            assert isinstance(label, Label)
            if text is not None:
                label.set_text(text)
                label.set_fg_theme_key(ThemeKey.FG)
            else:
                label.set_text("n/a")
                label.set_fg_theme_key(ThemeKey.FG_DISABLED)

    def set_button_and_node(self, button: Button, node_label: str) -> None:
        self.button = button
        self.node_label = node_label
        self._refresh_property_labels()

    def update(self, dt_s: float) -> None:
        pass

    def _handle_left_click(self, event: pg.event.Event) -> None:
        if self.button is None:
            return

        if self.in_delete_confirmation:
            if self.yes_button.check_click(event.pos):
                self.in_delete_confirmation = False
                self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.TALK)

                if (
                    self.button is not None
                    and (node_str := self.aac_inst.engine.get_node_for_button(self.button)) is not None
                    and self.button in (node_buttons := self.aac_inst.engine.tree.nodes[node_str].buttons)
                ):
                    node_buttons.remove(self.button)
                    save_language_tree(lt=self.aac_inst.engine.tree)
            if self.no_button.check_click(event.pos):
                self.in_delete_confirmation = False
            return

        # close button
        if self.close_button.check_click(event.pos):
            self.in_delete_confirmation = False
            self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.TALK)

        # modify, move, delete
        if self.modify_button.check_click(event.pos):
            if not self.button.immutable:
                self.aac_inst.bus.emit(EventID.SET_MODIFY_BUTTON, button=self.button)
                self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.MODIFY)
        if self.delete_button.check_click(event.pos):
            if not self.button.immutable:
                self.in_delete_confirmation = True
        if self.move_button.check_click(event.pos):
            self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.TALK)
            self.aac_inst.bus.emit(EventID.SET_MOVE_STATE, button=self.button)

    def take_input(self, keys: ScancodeWrapper, events: list[Event], dt_s: float) -> None:
        if self.button is None:
            return

        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_left_click(event)

    def draw(self, screen: Surface) -> None:
        theme = self.aac_inst.get_current_theme()
        screen.fill(theme[ThemeKey.BG])

        if not self.button:
            return

        self.popup.draw(screen, current_theme=theme)

        if self.in_delete_confirmation:
            screen.blit(self.black_overlay_surface, (0, 0))
            self.confirm_dialog.draw(screen, current_theme=theme)
