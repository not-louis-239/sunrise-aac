# asset_manager.py - Asset Manager

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


from pathlib import Path
from enum import StrEnum

import pygame as pg

from sunrise.ui.utils import make_tinted_surface
from sunrise.core.paths import FONTS_DIR, UI_IMAGES_DIR
from sunrise.ui.themes import THEMES, Theme
from sunrise.ui.constants import ICON_SIZE


class PropertyIconID(StrEnum):
    TEXT = "text"
    DEST = "dest"
    FUNC = "func"
    IMAGE = "image"
    LABEL = "label"
    MAP_PIN = "map_pin"
    TYPE = "type"
    COORDS = "coords"
    FONT_SIZE = "font_size"


class Fonts:
    def __init__(self) -> None:
        self.talk_button_font_path: Path = FONTS_DIR / "ComicNeue-Bold.ttf"
        self._ui_font_path: Path = FONTS_DIR / "AtkinsonHyperlegible-Regular.ttf"

        self.sentence_bar_font = pg.font.Font(self._ui_font_path, 35)

        self.default_talk_button_font_size = 21  # the separate size is needed somewhere so that's why it's stored as a separate attr


        self.ui_text_font_m = pg.font.Font(self._ui_font_path, 35)
        self.ui_text_font_s = pg.font.Font(self._ui_font_path, 22)
        self.title_font = pg.font.Font(self._ui_font_path, 45)
        self.ui_button_font = pg.font.Font(self._ui_font_path, 40)

class Images:
    def __init__(self) -> None:
        # {relative_fp, pg.Surface} pairs for buttons
        self.cache: dict[str, pg.Surface] = {}

        # paths
        self.exit_icon: Path = UI_IMAGES_DIR / "exit.png"
        self.proceed_icon: Path = UI_IMAGES_DIR / "proceed.png"
        self.lock_icon: Path = UI_IMAGES_DIR / "lock.png"
        self.warning_icon: Path = UI_IMAGES_DIR / "warning.png"

        self.property_icons: dict[PropertyIconID, Path] = {
            PropertyIconID.TEXT: UI_IMAGES_DIR / "text.png",
            PropertyIconID.DEST: UI_IMAGES_DIR / "dest.png",
            PropertyIconID.FUNC: UI_IMAGES_DIR / "func.png",
            PropertyIconID.IMAGE: UI_IMAGES_DIR / "image.png",
            PropertyIconID.LABEL: UI_IMAGES_DIR / "label.png",
            PropertyIconID.MAP_PIN: UI_IMAGES_DIR / "map_pin.png",
            PropertyIconID.TYPE: UI_IMAGES_DIR / "type.png",
            PropertyIconID.COORDS: UI_IMAGES_DIR / "coords.png",
            PropertyIconID.FONT_SIZE: UI_IMAGES_DIR / "font_size.png"
        }

class Assets:
    def __init__(self) -> None:
        self.fonts = Fonts()
        self.images = Images()
