# module for scroll physics class
# to be used by scrollable UI elements

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

SCROLL_IMPULSE = 50    # pix/s
SCROLL_FRICTION = 0.935  # proportion of velocity dissipated per second
EPS = 1e-6


class ScrollPhysics:
    def __init__(self, *, y_min: int = 0, y_max: int) -> None:
        self.y: float = y_min
        self.y_min: int = y_min
        self.y_max: int = y_max

        self.vel_y: float = 0.0

    def handle_scroll(self, event: pg.event.Event) -> None:
        self.vel_y -= event.y * SCROLL_IMPULSE

    def update(self, dt_s: float) -> None:
        # Friction
        self.vel_y *= (1 - SCROLL_FRICTION) ** dt_s
        if abs(self.vel_y) < EPS:
            self.vel_y = 0.0

        # Integrate
        self.y += self.vel_y * dt_s

        # Clamp y-values
        if self.y < self.y_min:
            self.y = self.y_min
            self.vel_y = 0.0
        if self.y > self.y_max:
            self.y = self.y_max
            self.vel_y = 0.0
