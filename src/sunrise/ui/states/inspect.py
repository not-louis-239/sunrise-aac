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
    Icon,
    Spacer,
    Label,
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


def _make_icon(*, self: InspectState, prop: PropertyIconID) -> Icon:
    return Icon(img_path=self.aac_inst.assets.images.property_icons[prop], size=(ICON_SIZE, ICON_SIZE), k_fg=ThemeKey.FG)


class InspectState(State):
    def __init__(self, aac_inst: AAC) -> None:
        super().__init__(aac_inst)
        self.button: Button | None = None  # the button that `self` is currently inspecting
        self.node_label: str | None = None
        self.aac_inst.bus.subscribe(EventID.SET_INSPECT_BUTTON, self.set_button_and_node)

        ### Initialise UI components - components that need to be interacted with by `self` are bound as attributes

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

        self.word_hbox = HBox(
            padding=UI_MARGIN,
            children=[
                Icon(img_path=self.aac_inst.assets.images.property_icons[PropertyIconID.TEXT], size=(ICON_SIZE, ICON_SIZE), k_fg=ThemeKey.FG),
                SBox(

                )
            ]
        )

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
                    VBox(),

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

    def set_button_and_node(self, button: Button, node_label: str) -> None:
        self.button = button
        self.node_label = node_label

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

        # Draw the popup background rect
        pg.draw.rect(screen, theme.fg_colour, self.popup_rect, width=BORDER_WIDTH)

        # Draw the close button so users can actually get out!
        topleft = (self.popup_rect.right - 2 * self.close_button.r - UI_PADDING, self.popup_rect.top + UI_PADDING)
        screen.blit(self.aac_inst.assets.images.exit_icon[theme], topleft)

        # Draw the popup text
        text_left, text_top = self.popup_rect.topleft[0] + UI_PADDING, self.popup_rect.topleft[1] + UI_PADDING
        text = f"Button '{self.button.label}' in Node '{self.node_label}' at {self.button.coords}"
        text_max_width = int(self.popup_rect.width - 2 * self.close_button.r - 3 * UI_PADDING)
        text_cropped = crop_text_to_fit(text, self.title_font, text_max_width)

        text_surf = self.title_font.render(text_cropped, True, theme.fg_colour)
        screen.blit(text_surf, (text_left, text_top))

        base_x, base_y = (UI_PADDING + UI_MARGIN, int(WN_H * 0.15))
        value_offset = 150

        def draw_key_value_pair(k: object, v: object, pos: tuple[int, int]) -> None:
            px, py = pos

            draw_text(
                surface=screen, pos=(px + UI_MARGIN, py),
                horiz_align='left', vert_align='centre',
                font_family=self.title_font, text=str(k),
                colour=theme.fg_colour
            )

            if v is not None:
                v_str = str(v)
                v_col = theme.fg_colour
            else:
                v_str = "n/a"
                v_col = (*theme.fg_colour, 127)

            draw_text(
                surface=screen, pos=(px + UI_MARGIN + value_offset, py),
                horiz_align='left', vert_align='centre',
                font_family=self.title_font, text=v_str,
                colour=v_col
            )

        for i, (label, attr_value, icon_id) in enumerate((
            ("word:", self.button.word, PropertyIconID.TEXT),
            ("dest:", self.button.dest, PropertyIconID.DEST),
            ("func:", self.button.func, PropertyIconID.FUNC),
            ("image:", self.button.img, PropertyIconID.IMAGE),
            ("type:", self.button.type, PropertyIconID.TYPE),
        )):
            image = self.aac_inst.assets.images.property_icons[icon_id][theme]
            pos = base_x, base_y + i * UI_MARGIN
            img_rect = pg.Rect(0, 0, *image.get_size())
            img_rect.center = pos
            screen.blit(image, img_rect)
            draw_key_value_pair(k=label, v=attr_value, pos=pos)

        if self.button.immutable:
            draw_text(
                surface=screen, pos=(base_x, base_y + 5 * UI_MARGIN),
                horiz_align='left', vert_align='top',
                font_family=self.title_font, text="immutable",
                colour=theme.warn_colour
            )

        # Draw buttons
        for button, text in [
            (self.move_button, "Move"),
            (self.modify_button, "Modify"),
            (self.delete_button, "Delete")
        ]:
            if button == self.move_button:
                colour = theme.fg_colour
            elif button == self.modify_button:
                colour = (*theme.fg_colour, 127) if self.button.immutable else theme.fg_colour
            elif button == self.delete_button:
                colour = (*theme.err_colour, 127) if self.button.immutable else theme.err_colour
            else:
                colour = theme.fg_colour  # default so Pyright doesn't complain about possibly unbound variables

            # Now draw the buttons
            pg.draw.rect(screen, theme.fg_colour, button.rect, width=BORDER_WIDTH)
            draw_text(
                surface=screen, pos=button.rect.center, horiz_align='centre',
                vert_align='centre', font_family=self.button_font, text=text,
                colour=colour
            )

        if self.in_delete_confirmation:
            screen.blit(self.black_overlay_surface, (0, 0))

            pg.draw.rect(screen, theme.bg_colour, (WN_W * 0.08, WN_H * 0.4, WN_W * 0.84, WN_H * 0.3))
            pg.draw.rect(screen, theme.fg_colour, (WN_W * 0.08, WN_H * 0.4, WN_W * 0.84, WN_H * 0.3), width=BORDER_WIDTH)

            draw_text(
                surface=screen, pos=(int(WN_W * 0.5), int(WN_H * 0.5)),
                horiz_align='centre', vert_align='centre',
                font_family=self.title_font, text=f"Are you sure you want to delete '{self.button.label}'?",
                colour=theme.fg_colour
            )

            # Draw yes/no buttons
            pg.draw.rect(screen, theme.fg_colour, self.yes_button.rect, width=BORDER_WIDTH)
            draw_text(
                surface=screen, pos=self.yes_button.rect.center,
                horiz_align='centre', vert_align='centre',
                font_family=self.title_font, text=f"Yes",
                colour=theme.err_colour
            )

            pg.draw.rect(screen, theme.fg_colour, self.no_button.rect, width=BORDER_WIDTH)
            draw_text(
                surface=screen, pos=self.no_button.rect.center,
                horiz_align='centre', vert_align='centre',
                font_family=self.title_font, text=f"No",
                colour=theme.fg_colour
            )
