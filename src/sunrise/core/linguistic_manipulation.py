# module to store helper functions for manipulating (English) words, e.g. pluralisation, adding suffixes and prefixes properly, etc.

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
from enum import StrEnum
from typing import Callable
from pathlib import Path

from sunrise.core.paths import LANGFILES_DIR


class Inflection(StrEnum):
    PLURAL = "plural"
    GERUND = "gerund"
    PAST = "past"
    POSSESSIVE = "possessive"


def _load_langfile_csv(filename: str) -> dict[str, str]:
    lut: dict[str, str] = {}

    p = LANGFILES_DIR / filename
    with open(p, "r", encoding="utf-8") as f:
        text = f.read()

    for line in text.splitlines():
        orig, inflected = line.split(",")
        lut[orig] = inflected

    return lut


_IRREGULAR_PLURALS: dict[str, str] = _load_langfile_csv("plurals.csv")
_IRREGULAR_GERUNDS: dict[str, str] = _load_langfile_csv("gerunds.csv")
_IRREGULAR_PAST: dict[str, str] = _load_langfile_csv("past_tenses.csv")


# Set up the function registry
_FUNC_DICT: dict[Inflection, Callable[[str], str]] = {}


def _register(inflection: Inflection):
    """Decorator to register a function for a specific inflection type."""
    def decorator(func: Callable[[str], str]) -> Callable[[str], str]:
        _FUNC_DICT[inflection] = func
        return func
    return decorator


def _apply_case(original: str, transformed: str) -> str:
    """Apply a case of word manipulation, preserving case as best as possible."""

    if not original:
        return transformed

    if original.isupper():
        return transformed.upper()
    if original[0].isupper():
        return transformed.capitalize()
    return transformed


@_register(Inflection.PLURAL)
def pluralise_word(word: str) -> str:
    """Convert an English word to its plural in a simple, extensible way."""
    if not word:
        return word

    lower = word.lower()

    if lower in _IRREGULAR_PLURALS:
        return _apply_case(word, _IRREGULAR_PLURALS[lower])

    if lower.endswith(("s", "x", "z", "ch", "sh")):
        return _apply_case(word, word + "es")
    if re.search(r"[^aeiou]y$", lower):
        return _apply_case(word, word[:-1] + "ies")
    if lower.endswith("f"):
        return _apply_case(word, word[:-1] + "ves")
    if lower.endswith("fe"):
        return _apply_case(word, word[:-2] + "ves")

    return _apply_case(word, word + "s")


@_register(Inflection.GERUND)
def gerundise_word(word: str) -> str:
    """Convert a verb to its gerund/continuous form."""
    if not word:
        return word

    lower = word.lower()

    if lower in _IRREGULAR_GERUNDS:
        return _apply_case(word, _IRREGULAR_GERUNDS[lower])

    if lower.endswith("ie"):
        return _apply_case(word, word[:-2] + "ying")
    if lower.endswith("e") and not lower.endswith(("ee", "ye")):
        return _apply_case(word, word[:-1] + "ing")
    if lower.endswith(("c", "g")) and len(lower) > 1:
        return _apply_case(word, word + "ing")
    if lower.endswith(("p", "t", "m", "n", "r")) and len(lower) > 1:
        last_letter = lower[-1]
        return _apply_case(word, word + last_letter + "ing")

    return _apply_case(word, word + "ing")


@_register(Inflection.PAST)
def past_tense_word(word: str) -> str:
    """Convert a verb to a simple past tense form."""
    if not word:
        return word

    lower = word.lower()

    if lower in _IRREGULAR_PAST:
        return _apply_case(word, _IRREGULAR_PAST[lower])

    if lower.endswith("e"):
        return _apply_case(word, word + "d")
    if re.search(r"[^aeiou]y$", lower):
        return _apply_case(word, word[:-1] + "ied")
    if lower.endswith(("p", "t", "m", "n", "r", "l")) and len(lower) > 1:
        if lower[-2] not in "aeiou":
            return _apply_case(word, word + "ed")
        else:
            last_letter = lower[-1]
            return _apply_case(word, word + last_letter + "ed")

    return _apply_case(word, word + "ed")


@_register(Inflection.POSSESSIVE)
def possessive_word(word: str) -> str:
    """Convert a noun to its possessive form."""
    if word.endswith("s"):
        return _apply_case(word, word + "'")
    else:
        return _apply_case(word, word + "'s")


def apply_inflection(word: str, form: Inflection = Inflection.PLURAL) -> str:
    """Apply a basic inflection based on an explicit form name."""
    return _FUNC_DICT[form](word)
