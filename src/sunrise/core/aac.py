# aac_main.py - module to store main AAC class
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
from pygame.key import ScancodeWrapper

from sunrise.core.asset_manager import Assets
from sunrise.core.bus import Bus, EventID
from sunrise.core.data_manager import load_config, save_config
from sunrise.core.diagnostics import DiagnosticsManager
from sunrise.core.engine import AACEngine
from sunrise.ui.states import (
    DoctorState,
    InspectState,
    ModifyState,
    SettingsState,
    State,
    TalkState,
)
from sunrise.ui.states.base_states import StateID
from sunrise.ui.themes import THEMES, Theme


class AAC:
    def __init__(self):
        # assets MUST be initialised first
        self.assets = Assets()

        # then config
        self.config = load_config()

        # then everything else
        self.diagnostics_manager = DiagnosticsManager(self)

        self.bus = Bus()
        self.bus.subscribe(EventID.STATE_CHANGE, self.change_state)

        self.engine = AACEngine()

        self.states: dict[StateID, State] = {
            StateID.INSPECT: InspectState(self),
            StateID.MODIFY: ModifyState(self),
            StateID.TALK: TalkState(self),
            StateID.SETTINGS: SettingsState(self),
            StateID.DOCTOR: DoctorState(self)
        }

        self.state: StateID = StateID.TALK

    def get_current_theme(self) -> Theme:
        return THEMES[self.config.theme_idx]

    def change_state(self, new_state: StateID) -> None:
       self.state = new_state

    def update(self, dt_s: float) -> None:
        self.states[self.state].update(dt_s=dt_s)

    def take_input(self, keys: ScancodeWrapper, events: list[pg.event.Event], dt_s: float) -> None:
        self.states[self.state].take_input(keys=keys, events=events, dt_s=dt_s)

    def quit(self) -> None:
        save_config(self)

    def draw(self, screen: pg.Surface) -> None:
        self.states[self.state].draw(screen=screen)
