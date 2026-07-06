# module to store helper functions for manipulating words, e.g. pluralisation, adding suffixes and prefixes properly, etc.

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

_IRREGULAR_PLURALS: dict[str, str] = {
    "man": "men",
    "woman": "women",
    "child": "children",
    "mouse": "mice",
    "goose": "geese",
    "foot": "feet",
    "tooth": "teeth",
    "ox": "oxen",
}

def pluralise_word(word: str) -> str:
    """Convert an English word to its plural.
    Note though that this ISN'T PERFECT, OK?"""
    
    if not word:
        return word

    lower = word.lower()

    # Irregular forms first
    if lower in _IRREGULAR_PLURALS:
        return _IRREGULAR_PLURALS[lower]

    # Common suffix rules
    if lower.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    if re.search(r"[^aeiou]y$", lower):
        return word[:-1] + "ies"
    if lower.endswith("f"):
        return word[:-1] + "ves"
    if lower.endswith("fe"):
        return word[:-2] + "ves"

    return word + "s"
