# constants.py - program constants specifically for UI stuff
# because UI stuff cluttering the other constants.py module is stinky

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


# Window size
WN_W, WN_H = 1280, 720

# UI margin presets
UI_MARGIN = int(WN_W * 0.04)

# Other visual settings
GRID_W, GRID_H = 10, 6  # size of the talk grid in buttons
BORDER_WIDTH = 2        # border width for UI elements

# Sizes
SENTENCE_BAR_H = 80
BUTTON_IMAGE_SIZE = int((WN_H - SENTENCE_BAR_H - UI_MARGIN) / GRID_H * 0.65)
ICON_SIZE = int(WN_W * 0.025)  # size for UI icons

# Allowed button types - Only these button types will have a supporting colour.
#                        Unwhitelisted button types will default to the `default` colour
#                        and will display a warning when the LanguageTree is linted.
ALLOWED_BUTTON_TYPES = [
    "pronoun",
    "noun",
    "verb",
    "descriptor",
    "social",
    "syntax",
    "system",
    "folder",
    "default"
]
