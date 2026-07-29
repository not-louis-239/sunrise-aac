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
from sunrise.core.lint_language_tree import Problem, Severity, lint_language_tree
from sunrise.ui.constants import BORDER_WIDTH, ICON_SIZE, UI_MARGIN_M, WN_H, WN_W
from sunrise.ui.elements import (
    CircularUIButton,
    HAlign,
    HBox,
    Icon,
    Label,
    Panel,
    RectangularUIButton,
    SBox,
    ScrollableDisplay,
    Spacer,
    VBox,
)
from sunrise.ui.states.base_states import State, StateID
from sunrise.ui.themes import ThemeKey

if TYPE_CHECKING:
    from sunrise.core.aac import AAC



class DoctorState(State):
    def __init__(self, aac_inst: AAC) -> None:
        super().__init__(aac_inst)

        # Errors VBox
        self.problems: dict[Problem, Label] = {}
        self.default_errors_display = [Label(font=self.aac_inst.assets.fonts.ui_text_font_m, text="Warnings will appear here.")]
        self.errors_vbox = VBox(padding=UI_MARGIN_M, gap=UI_MARGIN_M)
        self.errors_scroller = ScrollableDisplay(flex=1, child=self.errors_vbox)

        # Errors/warnings display
        self.num_errors_label = Label(font=self.aac_inst.assets.fonts.ui_button_font)
        self.num_warnings_label = Label(font=self.aac_inst.assets.fonts.ui_button_font)

        self.errors_warnings_counter = HBox(
            children=[
                Icon(img_path=self.aac_inst.assets.images.exit_icon, size=(ICON_SIZE, ICON_SIZE), k_fg=ThemeKey.FG_ERROR),
                Spacer(min_w=UI_MARGIN_M),
                SBox(forced_width=100, child=self.num_errors_label, h_align=HAlign.LEFT),
                Icon(img_path=self.aac_inst.assets.images.warning_icon, size=(ICON_SIZE, ICON_SIZE), k_fg=ThemeKey.FG_WARNING),
                Spacer(min_w=UI_MARGIN_M),
                SBox(forced_width=100, child=self.num_warnings_label, h_align=HAlign.LEFT),
            ]
        )

        # Close button
        self.close_button = CircularUIButton(
            r=ICON_SIZE // 2, font=self.aac_inst.assets.fonts.ui_button_font,
            img_path=self.aac_inst.assets.images.exit_icon, border_w=0, k_fg=ThemeKey.FG_ERROR
        )

        # Button to check the language tree
        self.check_button = RectangularUIButton(inset=UI_MARGIN_M, font=self.aac_inst.assets.fonts.ui_button_font, text="Check Language Tree")
        self.clear_button = RectangularUIButton(inset=UI_MARGIN_M, font=self.aac_inst.assets.fonts.ui_button_font, text="Clear Caches")

        self.panel = Panel(
            horiz_padding=UI_MARGIN_M,
            vert_padding=UI_MARGIN_M,
            child=VBox(
                gap=UI_MARGIN_M,
                children=[
                    HBox(
                        gap=UI_MARGIN_M,
                        children=[
                            Label(font=self.aac_inst.assets.fonts.title_font, text="Doctor"),
                            Spacer(flex=1),
                            self.close_button
                        ]
                    ),
                    HBox(
                        gap=UI_MARGIN_M,
                        children=[
                            self.check_button,
                            self.errors_warnings_counter,
                            Spacer(flex=1),
                            self.clear_button
                        ]
                    ),
                    self.errors_scroller
                ]
            )
        )

        self.panel.layout(pg.Rect(UI_MARGIN_M, UI_MARGIN_M, WN_W - 2 * UI_MARGIN_M, WN_H - 2 * UI_MARGIN_M))
        self._reset_error_display()

    def _reset_error_display(self) -> None:
        self.problems.clear()
        self.errors_vbox.children = self.default_errors_display  # type: ignore
        self.num_errors_label.set_text("-")
        self.num_errors_label.k_fg = ThemeKey.FG_DISABLED
        self.num_warnings_label.set_text("-")
        self.num_warnings_label.k_fg = ThemeKey.FG_DISABLED
        self.panel.layout(pg.Rect(UI_MARGIN_M, UI_MARGIN_M, WN_W - 2 * UI_MARGIN_M, WN_H - 2 * UI_MARGIN_M))

    def _refresh_error_display(self) -> None:
        """Check the language tree and update the errors display with appropriate elements, then
        re-layout."""

        problems = lint_language_tree(self.aac_inst.engine.tree)

        new_labels: list[Label] = []
        num_errors = 0
        num_warnings = 0

        for problem in problems:
            label = Label(
                font=self.aac_inst.assets.fonts.ui_text_font_s,
                inset=UI_MARGIN_M,
                border_w=BORDER_WIDTH,
                k_bg=ThemeKey.BG_ERROR if problem.severity == Severity.ERROR else ThemeKey.BG_WARNING,
                k_border=ThemeKey.FG_ERROR if problem.severity == Severity.ERROR else ThemeKey.FG_WARNING,
                text=str(problem)
            )

            new_labels.append(label)
            self.problems[problem] = label

            if problem.severity == Severity.ERROR:
                num_errors += 1
            else:
                num_warnings += 1

        new_labels.sort(key=lambda l: l.text)

        self.errors_vbox.children = new_labels  # type: ignore

        self.num_errors_label.set_text(str(num_errors))
        self.num_errors_label.k_fg = ThemeKey.FG if num_errors else ThemeKey.FG_DISABLED

        self.num_warnings_label.set_text(str(num_warnings))
        self.num_warnings_label.k_fg = ThemeKey.FG if num_warnings else ThemeKey.FG_DISABLED

        self.panel.layout(pg.Rect(UI_MARGIN_M, UI_MARGIN_M, WN_W - 2 * UI_MARGIN_M, WN_H - 2 * UI_MARGIN_M))

    def take_input(self, keys: ScancodeWrapper, events: list[Event], dt_s: float) -> None:
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.close_button.check_click(event.pos):
                    self._reset_error_display()
                    self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.TALK)
                if self.check_button.check_click(event.pos):
                    self._refresh_error_display()
                if self.clear_button.check_click(event.pos):
                    self.aac_inst.assets.images.cache.clear()

                # Clicking on an error leads directly to the offending
                # button, if it is specific to a button
                if self.errors_scroller.rect.collidepoint(event.pos):
                    for problem, label in self.problems.items():
                        mx, my = event.pos
                        x = mx - self.errors_scroller.rect.left - self.errors_scroller.padding
                        y = my - self.errors_scroller.rect.top - self.errors_scroller.padding + self.errors_scroller.scroll_physics.y

                        if (
                            label.rect.collidepoint(x, y)
                            and problem.button_label and problem.node_id
                            and (node := self.aac_inst.engine.tree.get(problem.node_id))
                            and (button := next((b for b in node.buttons if b.label == problem.button_label), None))
                        ):
                            self._reset_error_display()
                            self.aac_inst.bus.emit(EventID.STATE_CHANGE, new_state=StateID.INSPECT)
                            self.aac_inst.bus.emit(EventID.SET_INSPECT_BUTTON, button=button, node_label=problem.node_id)
                            break

            if event.type == pg.MOUSEWHEEL:
                self.errors_scroller.handle_scroll(event)

    def update(self, dt_s: float) -> None:
        self.errors_scroller.update(dt_s=dt_s)

    def draw(self, screen: Surface) -> None:
        theme = self.aac_inst.get_current_theme()
        screen.fill(theme[ThemeKey.BG])

        self.panel.draw(surface=screen, current_theme=theme)
