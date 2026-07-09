#!/usr/bin/env python3

# entry point for the Sunrise AAC program

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


import sys
from pathlib import Path

import pygame as pg

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from sunrise.ui.constants import WN_W, WN_H
from sunrise.core.constants import FPS
from sunrise.core.aac import AAC
from sunrise.core.load_nodes import save_language_tree
from sunrise.core.error_logger import write_error_log

def main():
    pg.init()

    screen = pg.display.set_mode((WN_W, WN_H))
    pg.display.set_caption("Sunrise AAC")
    clock = pg.time.Clock()
    aac = AAC()

    running = True
    while running:
        keys = pg.key.get_pressed()
        events = pg.event.get()
        dt_s = clock.tick(FPS) / 1_000.0

        for event in events:
            if event.type == pg.QUIT:
                save_language_tree(aac.engine.tree)
                aac.quit()
                running = False

        aac.update(dt_s=dt_s)
        aac.take_input(keys=keys, events=events, dt_s=dt_s)
        aac.draw(screen)
        pg.display.flip()

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        write_error_log(exc)
    except KeyboardInterrupt:
        print("\nExited.")
    finally:
        pg.quit()