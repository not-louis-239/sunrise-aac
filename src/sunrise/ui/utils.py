# module for UI utilities

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


import re

import pygame as pg
from dataclasses import dataclass

from sunrise.ui.themes import ThemeKey
from sunrise.ui.constants import DEFAULT_MESSAGE_DURATION
from sunrise.core.custom_types import Colour, IntCoord2


_TOKEN_SPLIT_RE = r"(\s+)"


@dataclass
class AmbientMessage:
    text: str = ""
    k_fg: ThemeKey = ThemeKey.FG
    duration: float = 0.0

    def set_msg(self, text: str, k_fg: ThemeKey, duration: float = DEFAULT_MESSAGE_DURATION) -> None:
        self.text = text
        self.k_fg = k_fg
        self.duration = duration

    def clear(self) -> None:
        self.set_msg("", ThemeKey.FG, 0.0)

    def update(self, dt_s: float) -> None:
        self.duration = max(0, self.duration - dt_s)
        if not self.active:
            self.clear()

    @property
    def active(self) -> bool:
        return self.duration > 0


def crop_text_to_fit(text: str, font: pg.font.Font, maxwidth: int) -> str:
    """Truncate the text string to fit within a given width.
    Truncates with '...' at the end if necessary.
    Returns an empty string if even an ellipsis doesn't fit."""

    if font.size(text)[0] <= maxwidth:  # font.size(...) returns (width, height)
        return text

    ELLIPSIS_CHAR = '…'
    if font.size(ELLIPSIS_CHAR)[0] > maxwidth:
        return ""

    known_good = ""

    # Try to test increasingly large strings of the original text
    # plus the ellipsis, until one is greater than maxwidth
    # then return the last known-good string

    for char in text:
        test_text = known_good + char + ELLIPSIS_CHAR
        if font.size(test_text)[0] > maxwidth:
            return known_good + ELLIPSIS_CHAR
        known_good += char

    return known_good


def make_tinted_surface(surface: pg.Surface, colour: Colour, size: IntCoord2 | None = None) -> pg.Surface:
    """Tints the given surface with a given colour and resizes it using
    pg.transform.scale() if a size is provided."""
    tinted = surface.copy()
    colour_surface = pg.Surface(tinted.get_size(), pg.SRCALPHA)
    colour_surface.fill(colour)
    tinted.blit(colour_surface, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

    if size:
        tinted = pg.transform.scale(tinted, size)

    return tinted


def _tokenise(text: str) -> list[str]:
    return re.split(_TOKEN_SPLIT_RE, text)

def wrap_text(text: str, font: pg.font.Font, maxwidth: int) -> list[str]:
    """Wrap text to fixed-size rows each. This could be useful in something
    like a text box display where text wrapping is needed.
    Returns a list of text lines, each no wider than `maxwidth`."""

    if font.size(text)[0] < maxwidth:
        return [text]

    # tokens are required so that the wrapping doesn't cut words in half
    tokens = _tokenise(text)

    space_left = maxwidth
    lines: list[str] = []
    current_line: str = ""
    pos = 0

    while pos < len(tokens):
        tok_width = font.size(tokens[pos])[0]

        if tok_width > maxwidth:
            # cut a token up into characters if it's hopelessly wide
            # to fit inside `maxwidth`
            # then we have to recalculate tok_width
            tokens[pos:pos + 1] = iter(tokens[pos])
            tok_width = font.size(tokens[pos])[0]

        if tok_width > space_left:
            lines.append(current_line)
            current_line = ""
            space_left = maxwidth
            while tokens[pos].isspace():
                pos += 1
            continue
        else:
            space_left -= tok_width
            current_line += tokens[pos]
            pos += 1

    lines.append(current_line)

    return lines
