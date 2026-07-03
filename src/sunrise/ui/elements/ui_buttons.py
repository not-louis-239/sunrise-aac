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

from sunrise.ui.themes import Theme, ThemeKey
from sunrise.ui.constants import BORDER_WIDTH

from ._img_container import ImageContainer
from .widget import Widget


class _UIButton(Widget):
    def __init__(
            self, *,
            flex: int = 0, text: str = "", font: pg.font.Font, inset: int = 0,
            fixed_size: tuple[int, int] | None = None, img_path: Path | None = None,
            k_fg: ThemeKey = ThemeKey.FG, k_fg_active: ThemeKey = ThemeKey.FG_ACTIVE,
            k_bg: ThemeKey = ThemeKey.BG, k_bg_active: ThemeKey = ThemeKey.BG_ACTIVE,
            k_border: ThemeKey = ThemeKey.BORDER, border_w: int = BORDER_WIDTH
        ) -> None:
        # The k_* prefix identifies ThemeKeys.
        # Hence, they are not to be used directly in place of colours,
        # otherwise Python will throw up.

        super().__init__(flex=flex)
        self.text = text
        self.font = font
        self.inset = inset
        self.fixed_size = fixed_size

        self.k_fg = k_fg
        self.k_bg = k_bg
        self.k_fg_active = k_fg_active
        self.k_bg_active = k_bg_active
        self.k_border = k_border
        self.border_w = border_w

        self.img_container: ImageContainer | None = (
            ImageContainer(img_path=img_path, start_size=self._preferred_icon_size())
            if img_path is not None else None
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
    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def preferred_size(self) -> tuple[int, int]:
        return self.fixed_size if self.fixed_size is not None else self._get_text_size()

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect

    def draw(self, surface: pg.Surface, current_theme: Theme) -> None:
        k_fg = self.k_fg_active if self.active else self.k_fg
        k_bg = self.k_bg_active if self.active else self.k_bg

        # Draw the button's background
        pg.draw.rect(surface, current_theme[k_bg], self.rect)

        # Draw icon
        if self.img_container is not None:
            img_surf = self.img_container.get_tinted_scaled_img(current_theme[k_fg], self.preferred_size())
            surface.blit(img_surf, img_surf.get_rect(center=self.rect.center))

        # Draw border
        pg.draw.rect(surface, current_theme[self.k_border], self.rect, width=self.border_w)

        # Draw text
        text_surface = self.font.render(self.text, True, current_theme[k_fg])
        surface.blit(text_surface, text_surface.get_rect(center=self.rect.center))

class CircularUIButton(_UIButton):
    def __init__(
            self, *,
            r: int = 0, flex: int = 0, text: str = "", font: Font, inset: int = 0,
            fixed_size: tuple[int, int] | None = None, img_path: Path | None = None,
            k_fg: ThemeKey = ThemeKey.FG, k_fg_active: ThemeKey = ThemeKey.FG_ACTIVE,
            k_bg: ThemeKey = ThemeKey.BG, k_bg_active: ThemeKey = ThemeKey.BG_ACTIVE,
            k_border: ThemeKey = ThemeKey.BORDER, border_w: int = BORDER_WIDTH
        ) -> None:
        self.r = r
        super().__init__(
            flex=flex, text=text, font=font, inset=inset, fixed_size=fixed_size, img_path=img_path,
            k_fg=k_fg, k_fg_active=k_fg_active, k_bg=k_bg, k_bg_active=k_bg_active, k_border=k_border, border_w=border_w
        )

    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        dx = mouse_pos[0] - self.rect.centerx
        dy = mouse_pos[1] - self.rect.centery
        return dx ** 2 + dy ** 2 <= self.r ** 2

    def preferred_size(self) -> tuple[int, int]:
        return self.r * 2, self.r * 2

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect

    def draw(self, surface: pg.Surface, current_theme: Theme) -> None:
        k_fg = self.k_fg_active if self.active else self.k_fg
        k_bg = self.k_bg_active if self.active else self.k_bg

        # Draw background
        pg.draw.circle(surface, current_theme[k_bg], self.rect.center, self.r)

        # Draw icon, but bound to the button circle
        if self.img_container is not None:
            img_surf = self.img_container.get_tinted_scaled_img(current_theme[k_fg], self.preferred_size())
            surface.blit(img_surf, img_surf.get_rect(center=self.rect.center))

        # Draw the text
        text_surf = self.font.render(self.text, True, current_theme[k_fg])
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

        # Draw the border if applicable
        if self.border_w > 0:
            pg.draw.circle(surface, current_theme[self.k_border], self.rect.center, self.r, width=self.border_w)
