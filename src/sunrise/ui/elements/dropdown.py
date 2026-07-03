from typing import TypeVar

import pygame as pg
from pygame import Surface

from sunrise.ui.themes import Theme, ThemeKey

from .widget import Widget


T = TypeVar("T")


class Dropdown(Widget):
    def __init__(
            self, *,
            flex: int = 0,
            options: dict[str, T],  # {label: value}
            font: pg.font.Font,
            inset: int = 0,
            k_bg: ThemeKey = ThemeKey.BG,
            k_fg: ThemeKey = ThemeKey.FG,
            k_border: ThemeKey = ThemeKey.BORDER,
            k_bg_hover_options: ThemeKey = ThemeKey.BG_ACTIVE,
            k_fg_hover_options: ThemeKey = ThemeKey.FG_ACTIVE
        ) -> None:
        super().__init__(flex=flex)
        self.options = options
        self.hovered_idx: int = -1
        self.chosen_idx: int = 0

        self.font = font
        self.inset = inset
        self.k_bg = k_bg
        self.k_fg = k_fg
        self.k_border = k_border
        self.k_bg_hover_options = k_bg_hover_options
        self.k_fg_hover_options = k_fg_hover_options

    def handle_left_click(self, event: pg.event.Event) -> None:
        if self.rect.collidepoint(event.pos):
            self.is_open = not self.is_open
        elif self.is_open:
            self.is_open = False

    def preferred_size(self) -> tuple[int, int]:
        h = self.font.get_height()
        largest_w = max(self.font.size(opt)[0] for opt in self.options)  # get the option with largest lateral size
        return (largest_w + self.inset * 2, h + self.inset * 2)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect

    def draw(self, surface: Surface, current_theme: Theme) -> None:
        # Draw the dropdown button
        bg_color = current_theme[self.k_bg]
        fg_color = current_theme[self.k_fg]
        border_color = current_theme[self.k_border]

        pg.draw.rect(surface, bg_color, self.rect)
        pg.draw.rect(surface, border_color, self.rect, 1)

        # Draw the selected option
        text_surface = self.font.render(list(self.options.keys())[self.chosen_idx], True, fg_color)
        surface.blit(text_surface, (self.rect.left + self.inset, self.rect.top + (self.rect.height - text_surface.get_height()) // 2))

        if self.is_open:
            # Draw the dropdown options
            option_rect = pg.Rect(self.rect.left, self.rect.bottom, self.rect.width, len(self.options) * self.font.get_height())
            pg.draw.rect(surface, bg_color, option_rect)
            pg.draw.rect(surface, border_color, option_rect, 1)

            for i, label in enumerate(self.options):
                text_surface = self.font.render(label, True, current_theme[self.k_fg_hover_options if i == self.hovered_idx else self.k_fg])
                surface.blit(text_surface, (self.rect.left + self.inset, option_rect.top + i * self.font.get_height() + (self.font.get_height() - text_surface.get_height()) // 2))

    def update_hover_state(self, mouse_pos: tuple[int, int]) -> None:
        if self.is_open:
            num_options = len(self.options)
            for i in range(num_options):
                option_rect = pg.Rect(
                    self.rect.left,
                    self.rect.bottom + i * self.font.get_height(),
                    self.rect.width,
                    self.font.get_height()
                )
                if option_rect.collidepoint(mouse_pos):
                    self.hovered_idx = i
                    break
            else:
                self.hovered_idx = -1
