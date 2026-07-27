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
from sunrise.ui.utils import make_tinted_scaled_surface


type _TintSizeCtx = tuple[Path, Colour, IntCoord2]    # file path, tint, scale
type _TintSizeCache = dict[_TintSizeCtx, pg.Surface]  # {(colour, size): tinted_surface}


class _ImageCache:
    """Class for storing a base image, plus tinted and scaled versions.
    Derivatives of the original image are cached to avoid wasteful recalculations."""

    def __init__(self):
        self.base_cache: dict[Path, pg.Surface] = {}  # the untinted, unscaled original image - not to be modified after it is set
        self.tint_scale_cache: _TintSizeCache = {}

    def get_tinted_scaled_img(self, fp: Path, colour: Colour, size: IntCoord2) -> pg.Surface:
        """Get an image tinted and scaled to a specific colour and size."""

        key: _TintSizeCtx = (fp, colour, size)

        if key not in self.tint_scale_cache:
            # Get the base cache first
            if fp not in self.base_cache:
                self.base_cache[fp] = pg.image.load(fp).convert_alpha()

            self.tint_scale_cache[key] = make_tinted_scaled_surface(
                surface=self.base_cache[fp], colour=colour,
                size=size if size != self.base_cache[fp].get_size() else None  # skip resizing if the requested size is the same as the original size
            )

        return self.tint_scale_cache[key]


img_cache = _ImageCache()
