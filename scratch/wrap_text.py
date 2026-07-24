# test module to wrap some text

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


_TOKEN_SPLIT_RE = r"(\s+)"


def _tokenise(text: str) -> list[str]:
    if not any(c.isspace() for c in text):
        return list(text)
    return re.split(_TOKEN_SPLIT_RE, text)


def wrap_text(text: str, font: pg.font.Font, maxwidth: int) -> list[str]:
    """Wrap text to fixed-size rows each. This could be useful in something
    like a text box display where text wrapping is needed.
    Returns a list of text lines, each no wider than `maxwidth`."""

    if font.size(text)[0] < maxwidth:
        return [text]

    # tokens are required so that the wrapping doesn't cut words in half
    tokens = _tokenise(text)
    print(tokens)

    pos = 0
    lines: list[str] = []

    while pos < len(tokens):
        # Consume as many tokens as possible until we have to start a new line
        line = ""

        while pos < len(tokens):
            current_tok = tokens[pos]

            # If the token is hopelessly large for the line, cut it up into `maxwidth`-sized pieces and add them
            if font.size(current_tok)[0] > maxwidth:
                lines.extend(wrap_text(current_tok, font, maxwidth))
                continue

            test_width = font.size(line + current_tok)[0]
            if test_width > maxwidth:
                # If singular characters are too much, we just have to forcefully add them and move on
                if len(current_tok) == 1:
                    lines += current_tok
                    pos += 1
                break

            line += current_tok
            pos += 1

        lines.append(line)

        # If at the end of a line, consume spaces so that
        # the start of each line is never empty space
        while pos < len(tokens) and tokens[pos].isspace():
            pos += 1

    return lines

def _test():
    pg.font.init()
    font = pg.font.SysFont("Arial", 24)
    maxwidth = 100

    normal_text = "The quick brown fox   jumps over the   lazy\tdog."  # with some unusual spacing
    print(f"Testing text: {normal_text}")
    lines = wrap_text(normal_text, font, maxwidth)
    print(f"Wrapped lines: {lines}")

    big_word = "thisisaverylongword"
    print(f"Testing text: {big_word}")
    lines = wrap_text(big_word, font, maxwidth)
    print(f"Wrapped lines: {lines}")

if __name__ == "__main__":
    _test()