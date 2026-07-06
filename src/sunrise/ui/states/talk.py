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
import time

import pygame as pg
from pygame import Surface
from pygame.event import Event
from pygame.key import ScancodeWrapper

from crystallinium.text_utils import draw_text

from .base_states import State
from sunrise.ui.states.base_states import StateID
from sunrise.core.bus import EventID
from sunrise.core.load_nodes import Button, save_language_tree
from sunrise.core.paths import UI_IMAGES_DIR, get_image_path
from sunrise.core.asset_manager import Assets
from sunrise.core.constants import (
    MOVE_HOLD_DELAY,
)

from sunrise.ui.themes import ThemeKey
from sunrise.ui.elements import CircularUIButton
from sunrise.ui.utils import AmbientMessage
from sunrise.ui.constants import (
    SENTENCE_BAR_H,
    BUTTON_IMAGE_SIZE,
    UI_MARGIN,
    BUTTON_GRID_MARGIN,
    BORDER_WIDTH,
    ICON_SIZE,
    GRID_W,
    GRID_H,
    WN_W,
    WN_H
)

if TYPE_CHECKING:
    from sunrise.core.aac import AAC


def _resize_surface_to_fit(surface: pg.Surface, max_size: int) -> pg.Surface:
    """Resizes a surface to be as large as possible, ensuring neither width nor height
    exceeds max_size, while perfectly preserving the aspect ratio."""

    target_rect = pg.Rect(0, 0, max_size, max_size)
    current_rect = surface.get_rect()
    fitted_rect = current_rect.fit(target_rect)
    return pg.transform.smoothscale(surface, (fitted_rect.width, fitted_rect.height))


def _screen_to_grid_coord(screen_coords: tuple[int, int]) -> tuple[int, int] | None:
    """Get the corresponding button coordinates for a given screen coordinate.
    If there is no valid coordinate, return None."""

    x, y = screen_coords

    min_x = UI_MARGIN
    min_y = SENTENCE_BAR_H + UI_MARGIN

    # Calculate individual button dimensions
    area_w = WN_W - min_x
    area_h = WN_H - min_y
    button_w = area_w / GRID_W
    button_h = area_h / GRID_H

    # Is the click inside the grid at all?
    if x < min_x or x >= WN_W or y < min_y or y >= WN_H:
        return None

    # Derive the grid index directly using integer division
    bx = int((x - min_x) // button_w)
    by = int((y - min_y) // button_h)

    # Gaps between buttons where a click shouldn't trigger anything.
    button_start_x = min_x + bx * button_w
    button_start_y = min_y + by * button_h

    # Check if the click fell into the padding gap at the right or bottom of the button
    if (x >= button_start_x + (button_w - UI_MARGIN)) or (y >= button_start_y + (button_h - UI_MARGIN)):
        return None

    # Safety check to ensure floating-point rounding didn't push us out of bounds
    if 0 <= bx < GRID_W and 0 <= by < GRID_H:
        return bx, by

    return None


def _get_button_at_pos(buttons: list[Button], grid_coords: tuple[int, int]) -> Button | None:
    """Get the button at a specific grid position in a list of buttons.
    If no such button exists there in the list, return None.
    Assumes that grid_coords is the result of a screen-to-grid lookup
    (positive ints only in `grid_coords`, pls!)"""

    # we use modulo here to allow syntax like index -1 = last row/column
    for button in buttons:
        if (button.coords[0] % GRID_W, button.coords[1] % GRID_H) == grid_coords:
            return button
    return None


class _Renderer:
    def __init__(self, assets: Assets, aac_inst: AAC):
        self.aac_inst = aac_inst
        self.assets = assets
        self.ambient_msg = AmbientMessage()

    def retrieve_img(self, rel_path: str) -> Surface | None:
        """Load an image from an images manager and
        a relative path.
        Relative path is relative to assets/images,
        e.g. './food/apple.png'.
        If the file is not accessible (e.g. doesn't exist, permission denied, not a file),
        return None."""

        path = get_image_path(rel_path)

        if not path.exists():
            return None
        if not path.is_file():
            return None

        try:
            if rel_path not in self.assets.images.cache:
                img_loaded = pg.image.load(path).convert_alpha()
                img_loaded = _resize_surface_to_fit(img_loaded, BUTTON_IMAGE_SIZE)
                self.assets.images.cache[rel_path] = img_loaded
            return self.assets.images.cache[rel_path]
        except Exception:
            return None

    def _calculate_button_rect(self, button: Button) -> pg.Rect:
        bx, by = button.coords
        bx, by = bx % GRID_W, by % GRID_H  # normalise negative coordinates

        min_x = BUTTON_GRID_MARGIN
        min_y = SENTENCE_BAR_H + BUTTON_GRID_MARGIN

        # The size of the button area, minus the left/top margins
        area_w = WN_W - min_x
        area_h = WN_H - min_y

        button_w = area_w / GRID_W
        button_h = area_h / GRID_H

        screen_x = min_x + bx * button_w
        screen_y = min_y + by * button_h
        return pg.Rect(screen_x, screen_y, button_w - BUTTON_GRID_MARGIN, button_h - BUTTON_GRID_MARGIN)

    def _draw_button(self, screen: pg.Surface, button: Button) -> None:
        # Draw button rect
        rect = self._calculate_button_rect(button)

        theme = self.aac_inst.get_current_theme()
        colour = getattr(theme.fitzgerald_theme, button.type, theme.fitzgerald_theme.system)

        # Draw the actual rect first
        pg.draw.rect(screen, colour, rect)
        # Now border
        pg.draw.rect(screen, theme.mapping[ThemeKey.BORDER], rect, BORDER_WIDTH)

        # Now the image
        if button.img:
            img = self.retrieve_img(rel_path=str(button.img))
        else:
            img = None

        if img is not None:
            img_rect = img.get_rect()
            img_rect.center = (rect.centerx, int(rect.centery + self.aac_inst.assets.fonts.talk_button_font_size // 2))
            screen.blit(img, img_rect)

        # Now the text
        text_centre_x = rect.centerx
        if not img:
            text_y = rect.centery  # no image -> print text in centre of the rect
        else:
            text_y = rect.top

        # Draw the button label
        if img is None:
            if len(button.label) <= 2:
                font = self.aac_inst.assets.fonts.talk_button_font_xl
            elif len(button.label) <= 4:
                font = self.aac_inst.assets.fonts.talk_button_font_l
            elif len(button.label) <= 7:
                font = self.aac_inst.assets.fonts.talk_button_font_m
            else:
                font = self.aac_inst.assets.fonts.talk_button_font
        else:
            font = self.aac_inst.assets.fonts.talk_button_font

        # Decide the colour of the button foreground - grey it out if it is
        # a button that applies an inflection, but it is invalid for
        # the current word
        k_fg = ThemeKey.FG

        if button.func is not None and (inf := self.aac_inst.engine.INFLECTION_FUNCS.get(button.func)) is not None:
            if not self.aac_inst.engine.sentence_bar:
                k_fg = ThemeKey.FG_DISABLED
            else:
                last_word = self.aac_inst.engine.sentence_bar[-1]
                is_allowed = last_word.inflection_is_valid(inf)
                if not is_allowed:
                    k_fg = ThemeKey.FG_DISABLED

        draw_text(
            surface=screen, pos=(text_centre_x, text_y),
            horiz_align="centre", vert_align="top" if img else "centre", colour=theme[k_fg],
            text=str(button.label), font_family=font
        )

    def draw_sentence_bar(self, screen: pg.Surface, in_moving_state: bool, is_selecting_coords: bool) -> None:
        theme = self.aac_inst.get_current_theme()

        # Draw the line for the sentence bar
        pg.draw.line(screen, self.aac_inst.get_current_theme()[ThemeKey.FG], (0, SENTENCE_BAR_H), (WN_W, SENTENCE_BAR_H), 2)

        # If in moving state, display instructions in the sentence bar, then early return
        if is_selecting_coords:
            instruction_pos = (WN_W // 2, SENTENCE_BAR_H // 2)
            if self.ambient_msg.active:
                draw_text(
                    surface=screen, pos=instruction_pos,
                    horiz_align='centre', vert_align='centre',
                    font_family=self.assets.fonts.ui_text_font_s,
                    text=self.ambient_msg.text,
                    colour=theme[self.ambient_msg.k_fg]
                )
            else:
                draw_text(
                    surface=screen, pos=instruction_pos,
                    horiz_align='centre', vert_align='centre',
                    font_family=self.assets.fonts.ui_text_font_s,
                    text="Click on an empty spot to select a position for the button you are modifying, or Escape to cancel.",
                    colour=theme[ThemeKey.FG]
                )
            return

        if in_moving_state:
            instruction_pos = (WN_W // 2, SENTENCE_BAR_H // 2)
            draw_text(
                surface=screen, pos=instruction_pos,
                horiz_align='centre', vert_align='centre',
                font_family=self.assets.fonts.ui_text_font_s,
                text="Click on an empty spot to which to move the button, or an existing button to swap them, or Escape to cancel.",
                colour=theme[ThemeKey.FG]
            )
            return

        # Draw the sentence bar text
        sentence_bar_text = " ".join(str(w) for w in self.aac_inst.engine.sentence_bar)

        # rendering only the last 127 characters for performance
        # this is arbitrary but we expect here that a little kid might
        # spam the buttons on the AAC thousands of times
        # if not optimised, this could cause severe lag
        max_width = WN_W - 2 * UI_MARGIN
        text_surf = self.assets.fonts.sentence_bar_font.render(sentence_bar_text[-127:], True, theme[ThemeKey.FG])
        if (big_width := text_surf.get_width()) > max_width:
            excess = big_width - max_width
            crop_rect = pg.Rect(excess, 0, max_width, text_surf.get_height())
            text_surf = text_surf.subsurface(crop_rect)

        screen.blit(text_surf, text_surf.get_rect(left=UI_MARGIN, centery=SENTENCE_BAR_H / 2))

    def draw_buttons(self, screen: pg.Surface) -> None:
        for button in self.aac_inst.engine.current_buttons():
            self._draw_button(screen, button)

class TalkState(State):
    def __init__(self, aac_inst: AAC) -> None:
        super().__init__(aac_inst=aac_inst)
        self.aac_inst.bus.subscribe(EventID.SET_MOVE_STATE, self.set_button_to_move)
        self.aac_inst.bus.subscribe(EventID.SET_SELECTING_COORDS_FLAG, self.set_selecting_coords_flag)
        self.aac_inst.bus.subscribe(EventID.CLEAR_MOVE_STATE, self.clear_move_state)

        self.renderer = _Renderer(aac_inst.assets, aac_inst=aac_inst)
        self.button_to_move: Button | None = None
        self.button_hold_start_time: float | None = None
        self.last_clicked_pos: tuple[int, int] | None = None

        self.settings_button = CircularUIButton(r=ICON_SIZE // 2, img_path=UI_IMAGES_DIR / "gear.png", font=self.aac_inst.assets.fonts.ui_button_font)
        self.settings_button.layout(pg.Rect(WN_W - ICON_SIZE - UI_MARGIN, WN_H - ICON_SIZE - UI_MARGIN, ICON_SIZE, ICON_SIZE))
        self.is_selecting_coords: bool = False  # flag to store when the user is selecting coords from ModifyState

    def clear_move_state(self) -> None:
        """Clear all state related to entering move mode."""
        self.button_to_move = None
        self.is_selecting_coords = False
        self.last_clicked_pos = None
        self.button_hold_start_time = None

    def set_selecting_coords_flag(self) -> None:
        self.is_selecting_coords = True

    def set_button_to_move(self, button: Button) -> None:
        self.button_to_move = button

    def update(self, dt_s: float) -> None:
        if self.is_selecting_coords:
            self.renderer.ambient_msg.update(dt_s=dt_s)
        else:
            self.renderer.ambient_msg.clear()

        if self.aac_inst.engine.current_node == "HOME":
            self.settings_button.visible = True
            self.settings_button.active = True
        else:
            self.settings_button.visible = False
            self.settings_button.active = False

    def _handle_lmb_click(self, event: pg.event.Event) -> None:
        if self.settings_button.check_click(event.pos) and self.settings_button.visible:
            self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.SETTINGS)
            return

        button_grid_coord = _screen_to_grid_coord(event.pos)
        if button_grid_coord is None:
            return

        if self.is_selecting_coords:
            button = _get_button_at_pos(self.aac_inst.engine.current_buttons(), button_grid_coord)
            if button:
                # Button already exists there -> invalid coordinate
                self.renderer.ambient_msg.set_msg("This position is already occupied. Please choose an empty position.", k_fg=ThemeKey.FG_ERROR)
            else:
                self.clear_move_state()
                self.aac_inst.bus.emit(EventID.BROADCAST_TARGET_COORDS, coords=button_grid_coord)
                self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.MODIFY)
            return

        if self.button_to_move:
            button = _get_button_at_pos(self.aac_inst.engine.current_buttons(), button_grid_coord)
            if button:
                # Valid button - swap the button to move with the button that just got clicked
                button.coords, self.button_to_move.coords = self.button_to_move.coords, button.coords
            else:
                # No button exists at click location - move the button there
                self.button_to_move.coords = button_grid_coord

            save_language_tree(self.aac_inst.engine.tree)
            self.button_to_move = None
            self.button_hold_start_time = None
            return

    def _handle_rmb_click(self, event: pg.event.Event) -> None:
        if self.button_to_move:
            return

        button_coord = _screen_to_grid_coord(event.pos)

        # Coordinate doesn't correspond to a grid position - return
        if button_coord is None:
            return

        button = _get_button_at_pos(self.aac_inst.engine.current_buttons(), button_coord)
        if button:
            # button already exists - open the menu to inspect it
            node_name = self.aac_inst.engine.get_node_for_button(button)
            self.aac_inst.bus.emit(EventID.SET_INSPECT_BUTTON, button=button, node_label=node_name)
            self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.INSPECT)
        else:
            # button doesn't exist - open the menu to create a new button
            self.aac_inst.bus.emit(EventID.SET_MODIFY_BUTTON, button=button, node=self.aac_inst.engine.current_node, coords=button_coord)
            self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.MODIFY)

    def _handle_lmb_release(self, event: pg.event.Event) -> None:
        if self.button_hold_start_time is None or self.last_clicked_pos is None:
            return

        if self.button_to_move:
            dest_button_coord = _screen_to_grid_coord(event.pos)
            if dest_button_coord is None:
                return

            button = _get_button_at_pos(self.aac_inst.engine.current_buttons(), dest_button_coord)
            if button:
                button.coords, self.button_to_move.coords = self.button_to_move.coords, button.coords
            else:
                self.button_to_move.coords = dest_button_coord

            save_language_tree(self.aac_inst.engine.tree)
            self.button_to_move = None
            self.button_hold_start_time = None
            return

        held_duration = time.time() - self.button_hold_start_time
        if held_duration >= MOVE_HOLD_DELAY:
            grid_coord = _screen_to_grid_coord(self.last_clicked_pos)
            if grid_coord is not None and (button := _get_button_at_pos(self.aac_inst.engine.current_buttons(), grid_coord)):
                self.button_to_move = button
            return

        if self.settings_button.check_click(self.last_clicked_pos) and self.settings_button.visible:
            self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.SETTINGS)
            return

        pressed_button_coord = _screen_to_grid_coord(self.last_clicked_pos)
        if pressed_button_coord is None:
            return

        if self.is_selecting_coords:
            button = _get_button_at_pos(self.aac_inst.engine.current_buttons(), pressed_button_coord)
            if button:
                self.renderer.ambient_msg.set_msg(
                    "This position is already occupied. Please choose an empty position.",
                    k_fg=ThemeKey.FG_ERROR
                )
            else:
                self.clear_move_state()
                self.aac_inst.bus.emit(EventID.BROADCAST_TARGET_COORDS, coords=pressed_button_coord)
                self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.MODIFY)
            return

        if button := _get_button_at_pos(self.aac_inst.engine.current_buttons(), pressed_button_coord):
            self.aac_inst.engine.on_button_press(button)

    def take_input(self, keys: ScancodeWrapper, events: list[Event], dt_s: float) -> None:
        for event in events:
            # If in moving state, press Escape to cancel
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                if self.is_selecting_coords:
                    self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.MODIFY)
                self.clear_move_state()

            # Handle mouse clicks
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # Left click
                self.button_hold_start_time = time.time()
                self.last_clicked_pos = event.pos
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                # Right click
                self._handle_rmb_click(event)
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self._handle_lmb_release(event)
                self.last_clicked_pos = None
                self.button_hold_start_time = None

    def draw(self, screen: Surface) -> None:
        # Retrieve current theme and fill with background colour
        theme = self.aac_inst.get_current_theme()
        screen.fill(theme[ThemeKey.BG])

        # Draw sentence bar
        self.renderer.draw_sentence_bar(
            screen,
            in_moving_state=(
                self.button_to_move is not None
                or self.button_hold_start_time is not None and time.time() - self.button_hold_start_time > MOVE_HOLD_DELAY
            ),
            is_selecting_coords=self.is_selecting_coords
        )

        # Draw each of the buttons on the screen
        self.renderer.draw_buttons(screen)

        self.settings_button.draw(screen, current_theme=theme)
