# icons

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

from .widget import Widget, DrawContext

class Icon(Widget):
    def __init__(self, *, img_path: Path, size: tuple[int, int]) -> None:
        super().__init__()
        self.img_path = img_path
        self.native_size = size  # remembers its original dimensions
        self.size = size  # changes dynamically
        self._cached: pg.Surface | None = None
        self._refresh_cache()

    def _refresh_cache(self) -> None:
        if self._cached is None or self._cached.get_size() != self.size:
            self._cached = pg.image.load(str(self.img_path)).convert_alpha()
            self._cached = pg.transform.scale(self._cached, self.size)

    def preferred_size(self) -> tuple[int, int]:
        return self.native_size

    def layout(self, rect: pg.Rect) -> None:
        # Uses shrink-to-fit behaviour, maintaining proportions

        native_w, native_h = self.native_size
        rect_w, rect_h = rect.size

        # Check if we actually need to shrink
        if native_w > rect_w or native_h > rect_h:
            # Calculate scale factors for both dimensions
            scale_w = rect_w / native_w
            scale_h = rect_h / native_h

            # Use the smaller scale factor to ensure it fits entirely (shrink-to-fit)
            scale = min(scale_w, scale_h)

            # Compute new integer dimensions
            new_w = int(native_w * scale)
            new_h = int(native_h * scale)
            self.size = (new_w, new_h)
        else:
            # If the rect is big enough, revert to native size
            self.size = self.native_size

        # Create the final rect and center it within the allocated space
        self.rect = pg.Rect((0, 0), self.size)
        self.rect.center = rect.center

    def draw(self, surface: pg.Surface, ctx: DrawContext) -> None:
        self._refresh_cache()
        assert self._cached is not None
        surface.blit(self._cached, self.rect.topleft)
