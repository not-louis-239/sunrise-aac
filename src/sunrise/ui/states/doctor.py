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


from pygame import Surface
from pygame.event import Event
from pygame.key import ScancodeWrapper

from .base_states import State
from sunrise.ui.themes import ThemeKey


class DoctorState(State):
    def take_input(self, keys: ScancodeWrapper, events: list[Event], dt_s: float) -> None:
        pass

    def update(self, dt_s: float) -> None:
        pass

    def draw(self, screen: Surface) -> None:
        theme = self.aac_inst.get_current_theme()
        screen.fill(theme[ThemeKey.BG])
