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


class Fonts:
    def __init__(self) -> None:
        self._button_font_path: Path = FONTS_DIR / "ComicNeue-Bold.ttf"
        self._ui_font_path: Path = FONTS_DIR / "AtkinsonHyperlegible-Regular.ttf"

        self.sentence_bar_font = pg.font.Font(self._ui_font_path, 60)
        self.talk_button_font = pg.font.Font(self._button_font_path, 16)
        self.ui_text_font = pg.font.Font(self._ui_font_path, 35)
        self.title_font = pg.font.Font(self._ui_font_path, 60)
        self.ui_button_font = pg.font.Font(self._ui_font_path, 40)

class Images:
    def __init__(self) -> None:
        # {relative_fp, pg.Surface} pairs
        self.cache: dict[str, pg.Surface] = {}

        # paths
        self.exit_icon: Path = UI_IMAGES_DIR / "exit.png"
        self.proceed_icon: Path = UI_IMAGES_DIR / "proceed.png"
        self.lock_icon: Path = UI_IMAGES_DIR / "lock.png"

        self.property_icons: dict[str, Path] = {
            PropertyIconID.TEXT: UI_IMAGES_DIR / "text.png",
            PropertyIconID.DEST: UI_IMAGES_DIR / "dest.png",
            PropertyIconID.FUNC: UI_IMAGES_DIR / "func.png",
            PropertyIconID.IMAGE: UI_IMAGES_DIR / "image.png",
            PropertyIconID.LABEL: UI_IMAGES_DIR / "label.png",
            PropertyIconID.MAP_PIN: UI_IMAGES_DIR / "map_pin.png",
            PropertyIconID.TYPE: UI_IMAGES_DIR / "type.png"
        }

    def _load(
            self, path: Path, *,
            colour_attr: str = "fg_colour", size: tuple[int, int] = (ICON_SIZE, ICON_SIZE)
        ) -> dict[Theme, pg.Surface]:
        """Loads an image from a path, and in accordance with a list of themes,
        makes a coloured version for the specified `colour_attr` while simultaneously
        scaling it to a certain `size`. Returns {themes: coloured surfaces}.
        Default attr is `fg_colour` if `colour_attr` is not specified or found."""
        img_raw = pg.image.load(path).convert_alpha()
        img_scaled = pg.transform.scale(img_raw, size)

        img_dict: dict[Theme, pg.Surface] = {}
        for theme in THEMES:
            tinted = make_tinted_surface(img_scaled, getattr(theme, colour_attr, theme.fg_colour))
            img_dict[theme] = tinted

        return img_dict

class Assets:
    def __init__(self) -> None:
        self.fonts = Fonts()
        self.images = Images()
