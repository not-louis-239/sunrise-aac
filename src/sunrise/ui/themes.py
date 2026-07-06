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


from enum import StrEnum
from dataclasses import dataclass, asdict

from sunrise.core.custom_types import Colour


class ThemeKey(StrEnum):
    # Background
    BG = "BG"
    BG_ACTIVE = "BG_ACTIVE"
    BG_WARNING = "BG_WARNING"
    BG_ERROR = "BG_ERROR"

    # Foreground
    FG = "FG"
    FG_DISABLED = "FG_DISABLED"
    FG_ACTIVE = "FG_ACTIVE"
    FG_ERROR_DISABLED = "FG_ERROR_DISABLED"
    FG_ERROR = "FG_ERROR"
    FG_ERROR_ACTIVE = "FG_ERROR_ACTIVE"
    FG_WARNING = "FG_WARNING"
    FG_WARNING_ACTIVE = "FG_WARNING_ACTIVE"
    FG_SUCCESS = "FG_SUCCESS"
    FG_SUCCESS_ACTIVE = "FG_SUCCESS_ACTIVE"

    # Border
    BORDER = "BORDER"


@dataclass(frozen=True, kw_only=True)
class Fitzgerald:
    pronoun: Colour
    noun: Colour
    verb: Colour
    descriptor: Colour
    social: Colour
    syntax: Colour
    system: Colour
    folder: Colour
    default: Colour


@dataclass(frozen=True, kw_only=True)
class Theme:
    display_name: str
    mapping: dict[ThemeKey, Colour]
    fitzgerald_theme: Fitzgerald

    def __getitem__(self, key: ThemeKey) -> Colour:
        """__getitem__() overload purely for making retrieving mapping contents easier"""
        return self.mapping[key]


# Themes
THEMES: list[Theme] = [
    # Light mode
    Theme(
        display_name="Light",
        mapping={
            ThemeKey.BG: (255, 255, 255),
            ThemeKey.BG_ACTIVE: (240, 240, 240),
            ThemeKey.BG_WARNING: (255, 231, 170),
            ThemeKey.BG_ERROR: (255, 170, 170),
            ThemeKey.FG: (0, 0, 0),
            ThemeKey.FG_DISABLED: (140, 140, 140),
            ThemeKey.FG_ACTIVE: (0, 0, 0),
            ThemeKey.FG_ERROR_DISABLED: (255, 140, 140),
            ThemeKey.FG_ERROR: (255, 0, 0),
            ThemeKey.FG_ERROR_ACTIVE: (255, 0, 0),
            ThemeKey.FG_WARNING: (255, 208, 0),
            ThemeKey.FG_WARNING_ACTIVE: (255, 208, 0),
            ThemeKey.FG_SUCCESS: (48, 220, 0),
            ThemeKey.FG_SUCCESS_ACTIVE: (48, 220, 0),
            ThemeKey.BORDER: (0, 0, 0)
        },
        fitzgerald_theme=Fitzgerald(
            pronoun=(255, 255, 180),
            noun=(255, 210, 180),
            verb=(180, 255, 180),
            descriptor=(180, 200, 255),
            social=(240, 180, 255),
            syntax=(190, 190, 190),
            system=(240, 240, 240),
            folder=(215, 215, 215),
            default=(255, 255, 255)
        )
    ),

    # Dark mode
    Theme(
        display_name="Dark",
        mapping={
            ThemeKey.BG: (30, 30, 30),
            ThemeKey.BG_ACTIVE: (55, 55, 55),
            ThemeKey.BG_WARNING: (138, 104, 30),
            ThemeKey.BG_ERROR: (138, 30, 30),
            ThemeKey.FG: (220, 220, 220),
            ThemeKey.FG_DISABLED: (100, 100, 100),
            ThemeKey.FG_ACTIVE: (220, 220, 220),
            ThemeKey.FG_ERROR_DISABLED: (100, 60, 60),
            ThemeKey.FG_ERROR: (220, 100, 100),
            ThemeKey.FG_ERROR_ACTIVE: (220, 100, 100),
            ThemeKey.FG_WARNING: (220, 180, 0),
            ThemeKey.FG_WARNING_ACTIVE: (220, 180, 0),
            ThemeKey.FG_SUCCESS: (154, 220, 127),
            ThemeKey.FG_SUCCESS_ACTIVE: (154, 220, 127),
            ThemeKey.BORDER: (220, 220, 220),
        },
        fitzgerald_theme=Fitzgerald(
            pronoun=(120, 120, 30),
            noun=(120, 70, 30),
            verb=(30, 120, 30),
            descriptor=(30, 50, 100),
            social=(85, 30, 100),
            syntax=(60, 60, 60),
            system=(40, 40, 40),
            folder=(50, 50, 50),
            default=(30, 30, 30),
        )
    )
]

# Runtime check that all `Theme`s are complete
bad: list[tuple[Theme, list[ThemeKey]]] = []  # (theme, missing_keys)

for theme in THEMES:
    missing_keys = [key for key in ThemeKey if key not in theme.mapping]
    if missing_keys:
        bad.append((theme, missing_keys))

if bad:
    err_msg = f"The following themes are missing required keys:\n\n"

    for theme, missing in bad:
        err_msg += f"{theme.display_name}:\n"
        err_msg += "".join(f"  - {key}\n" for key in missing)

    raise RuntimeError(err_msg)


def _test():
    BOLD = "\033[1m"
    RESET = "\033[0m"
    GREY_BG = "\033[48;2;120;120;120m"

    # Show the contents of each theme
    for theme in THEMES:
        name = theme.display_name

        print(f"\nTheme: {name}")
        print("Colours:")

        for k in ThemeKey:
            col = theme[k]
            r, g, b = col
            col_code = f"\033[38;2;{r};{g};{b}m"
            text = f"  {k}: {BOLD}{GREY_BG}{col_code}{col}{RESET}"
            print(text)

        for cat, col in asdict(theme.fitzgerald_theme).items():
            r, g, b = col
            col_code = f"\033[38;2;{r};{g};{b}m"
            text = f"  {cat}: {BOLD}{GREY_BG}{col_code}{col}{RESET}"
            print(text)

    # Test error handling with an incomplete theme
    try:
        bad = Theme(
            display_name="Incomplete",
            mapping={},
            fitzgerald_theme=Fitzgerald(
                pronoun=(100, 100, 50),
                noun=(100, 75, 50),
                verb=(50, 100, 50),
                descriptor=(50, 65, 100),
                social=(90, 50, 100),
                syntax=(70, 70, 70),
                system=(55, 55, 55),
                folder=(60, 60, 60),
                default=(0, 0, 0),
            )
        )
        print(bad.display_name)

    except RuntimeError as e:
        print(f"\nRuntimeError caught | {e}")

if __name__ == "__main__":
    _test()

