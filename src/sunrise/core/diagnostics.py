# diagnostics module

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



import time
import math
from typing import TYPE_CHECKING
from dataclasses import dataclass

import pygame as pg
from pygame import Surface

from sunrise.ui.constants import WN_W, WN_H
from sunrise.ui.themes import Theme, ThemeKey

if TYPE_CHECKING:
    from sunrise.core.aac import AAC


_FPS_LINE_VALUES = [60, 30]
_DIAGNOSTICS_HEIGHT_PX_PER_S = 5_000
_MAX_GRAPH_HEIGHT = _DIAGNOSTICS_HEIGHT_PX_PER_S * 1 / min(fps for fps in _FPS_LINE_VALUES)

MAX_HISTORY_LEN = 100
_BAR_WIDTH = math.ceil(WN_W / MAX_HISTORY_LEN)


@dataclass
class Interval:
    t_i: float
    t_f: float

    @property
    def duration(self) -> float:
        return self.t_f - self.t_i


class IntervalContainer:
    def __init__(self) -> None:
        self.intervals: list[Interval] = []

    def record_interval(self, t_i: float, t_f: float) -> None:
        self.intervals.append(Interval(t_i=t_i, t_f=t_f))

    def prune(self, max_len: int) -> None:
        """Prune to keep only the most recent `max_len` intervals"""
        if max_len <= 0:
            raise ValueError("max_len must be a positive integer")

        self.intervals = self.intervals[-max_len:]

    def prune_seconds(self, t: float) -> None:
        """Prune intervals to only those whose initial time is within the last `t` seconds"""

        self.intervals = self.get_intervals_from_last(t)

    def get_intervals_from_last(self, t: float) -> list[Interval]:
        """Get all the time intervals whose initial time is within the last `t` seconds"""

        now = time.perf_counter()
        cutoff = now - t
        return [interval for interval in self.intervals if interval.t_i >= cutoff]

    def avg_freq_from_last(self, t: float) -> float:
        """Get the average frequency at which time intervals have been
        recorded in the last `t` seconds.
        Note that this is not the same as the average duration of each interval."""

        recent = self.get_intervals_from_last(t)

        if not recent:
            return 0  # no entries, so no valid frequency

        now = time.perf_counter()
        time_since_first = now - recent[0].t_i

        if time_since_first == 0:
            return 0  # guard against ZeroDivisionError

        return len(recent) / time_since_first

    def get_durations(self) -> list[float]:
        return [t.duration for t in self.intervals]

class DiagnosticsManager:
    def __init__(self, aac_inst: AAC) -> None:
        self.interval_container = IntervalContainer()
        self.aac_inst = aac_inst

        self.static_bg_surface = pg.Surface((WN_W, _MAX_GRAPH_HEIGHT), pg.SRCALPHA)
        self.static_bg_surface.fill((0, 0, 0, 127))

    def _draw_graph(self, surface: Surface, current_theme: Theme) -> None:
        surface.blit(self.static_bg_surface, (0, WN_H - _MAX_GRAPH_HEIGHT))

        for i, interval in enumerate(self.interval_container.intervals):
            bar_h = _DIAGNOSTICS_HEIGHT_PX_PER_S * interval.duration
            bar_left_x = WN_W * i / MAX_HISTORY_LEN
            pg.draw.rect(surface, current_theme[ThemeKey.FG_SUCCESS], (bar_left_x, WN_H - bar_h, _BAR_WIDTH, bar_h))

    def _draw_diagnostic_markers(self, surface: Surface, current_theme: Theme):
        fg_colour = current_theme[ThemeKey.FG]

        for fps_value in _FPS_LINE_VALUES:
            # Draw the line
            fps_height = WN_H - _DIAGNOSTICS_HEIGHT_PX_PER_S * (1 / fps_value)
            pg.draw.line(surface, fg_colour, (0, fps_height), (WN_W, fps_height), width=2)

            # Draw text just below the line
            text_surf = self.aac_inst.assets.fonts.diagnostics_font.render(f"{fps_value} FPS", True, fg_colour)
            surface.blit(text_surf, (0, fps_height))

    def draw_interval_graph(self, surface: Surface, current_theme: Theme) -> None:
        self._draw_graph(surface, current_theme)
        self._draw_diagnostic_markers(surface, current_theme)
