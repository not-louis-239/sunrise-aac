# module for storing image container class

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

import pygame as pg

from sunrise.core.custom_types import Colour, IntCoord2
from sunrise.ui.utils import make_tinted_surface


type _TintSizeCtx = tuple[Colour, IntCoord2]
type _TintSizeCache = dict[_TintSizeCtx, pg.Surface]  # {(colour, size): tinted_surface}


class ImageContainer:
    """Class for storing a base image, plus tinted and scaled versions.
    Derivatives of the original image are cached to avoid wasteful recalculations."""

    def __init__(self, img_path: Path, start_size: IntCoord2):
        self.img_path = img_path

        self._base_cache: pg.Surface = pg.image.load(str(self.img_path)).convert_alpha()  # the untinted, unscaled original image - not to be modified after it is set
        self._base_cache = pg.transform.scale(self._base_cache, start_size)
        self.start_size = start_size

        self._tint_size_cache: _TintSizeCache = {}

    def get_tinted_scaled_img(self, colour: Colour, size: IntCoord2) -> pg.Surface:
        """Get an image tinted and scaled to a specific colour and size."""

        key: _TintSizeCtx = (colour, size)

        if key not in self._tint_size_cache:
            self._tint_size_cache[key] = make_tinted_surface(
                surface=self._base_cache, colour=colour,
                size=size if size != self.start_size else None  # skip resizing if the requested size is the same as the original size
            )

        return self._tint_size_cache[key]
