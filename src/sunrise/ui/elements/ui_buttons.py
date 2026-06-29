# module for UI buttons
# these thingos are different from the other Button class as
# they are for UI menus, the other ones are for the AAC buttons

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


from abc import abstractmethod
from pathlib import Path

import pygame as pg
from pygame.font import Font

from sunrise.ui.elements.widget import DrawContext

from ._img_container import ImageContainer
from .widget import Widget


class _UIButton(Widget):
    def __init__(
            self, *, flex: int = 0, text: str, font: pg.font.Font, inset: int = 0,
            fixed_size: tuple[int, int] | None = None, icon_path: Path | None = None
        ) -> None:
        super().__init__(flex=flex)
        self.text = text
        self.font = font
        self.inset = inset
        self.fixed_size = fixed_size

        self.img_container: ImageContainer | None = (
            ImageContainer(img_path=icon_path, start_size=self._preferred_icon_size())
            if icon_path is not None else None
        )

    def _preferred_icon_size(self) -> tuple[int, int]:
        return self.fixed_size or self.preferred_size()

    def _get_text_size(self) -> tuple[int, int]:
        text_size = self.font.size(self.text)
        return text_size[0] + self.inset * 2, text_size[1] + self.inset * 2

    @abstractmethod
    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        raise NotImplementedError

class RectangularUIButton(_UIButton):
    def __init__(
            self, *, text: str, font: Font, inset: int,
            fixed_size: tuple[int, int] | None = None, icon_path: Path | None = None
        ) -> None:
        super().__init__(text=text, font=font, inset=inset, fixed_size=fixed_size, icon_path=icon_path)

    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def preferred_size(self) -> tuple[int, int]:
        return self.fixed_size if self.fixed_size is not None else self._get_text_size()

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect

    def draw(self, surface: pg.Surface, ctx: DrawContext) -> None:
        fg = ctx.fg if self.active else ctx.disabled_fg

        # Draw the button's background
        bg_colour = ctx.active_bg if self.active else ctx.bg
        pg.draw.rect(surface, bg_colour, self.rect)

        # Draw icon
        if self.img_container is not None:
            img_surf = self.img_container.get_tinted_scaled_img(fg[:3], self.preferred_size())
            surface.blit(img_surf, img_surf.get_rect(center=self.rect.center))

        # Draw border
        pg.draw.rect(surface, ctx.border, self.rect, width=ctx.border_w)

        # Draw text
        text_surface = ctx.font.render(self.text, True, fg)
        surface.blit(text_surface, text_surface.get_rect(center=self.rect.center))

class CircularUIButton(_UIButton):
    def __init__(
            self, *, r: int = 0, flex: int = 0, text: str, font: Font, inset: int = 0,
            fixed_size: tuple[int, int] | None = None, img_path: Path | None = None
        ) -> None:
        super().__init__(flex=flex, text=text, font=font, inset=inset, fixed_size=fixed_size, icon_path=img_path)
        self.r = r

    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        return mouse_pos[0] ** 2 + mouse_pos[1] ** 2 <= self.r ** 2

    def preferred_size(self) -> tuple[int, int]:
        return self.r * 2, self.r * 2

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect

    def draw(self, surface: pg.Surface, ctx: DrawContext) -> None:
        fg = ctx.fg if self.active else ctx.disabled_fg

        # Draw background
        pg.draw.circle(surface, ctx.active_bg if self.active else ctx.bg, self.rect.center, self.r)

        # Draw icon, but bound to the button circle
        if self.img_container is not None:
            img_surf = self.img_container.get_tinted_scaled_img(fg[:3], self.preferred_size())
            surface.blit(img_surf, img_surf.get_rect(center=self.rect.center))

        # Draw the text
        text_surf = self.font.render(self.text, True, fg)
        surface.blit(surface, text_surf.get_rect(center=self.rect.center))

        # Draw the border if applicable
        if ctx.border_w > 0:
            pg.draw.circle(surface, ctx.border, self.rect.center, self.r, width=ctx.border_w)
