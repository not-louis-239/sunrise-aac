# _base.py - module to contain the base State class

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

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import TYPE_CHECKING

import pygame as pg
from pygame.key import ScancodeWrapper

if TYPE_CHECKING:
    from sunrise.core.aac import AAC


class State(ABC):
    def __init__(self, aac_inst: AAC) -> None:
        self.aac_inst = aac_inst

    @abstractmethod
    def update(self, dt_s: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def take_input(self, keys: ScancodeWrapper, events: list[pg.event.Event], dt_s: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw(self, screen: pg.Surface) -> None:
        raise NotImplementedError


class StateID(StrEnum):
    INSPECT = "inspect"
    MODIFY = "modify"
    TALK = "talk"
    SETTINGS = "settings"
    DOCTOR = "doctor"
