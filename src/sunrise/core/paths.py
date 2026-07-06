# paths module
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

try:
    ROOT_DIR = next(p for p in Path(__file__).resolve().parents if (p / ".git").exists())
except StopIteration:
    raise RuntimeError("Could not find root directory.")

ASSETS_DIR = ROOT_DIR / "assets"

FONTS_DIR = ASSETS_DIR / "fonts"
IMAGES_DIR = ASSETS_DIR / "images"
UI_IMAGES_DIR = IMAGES_DIR / "ui"

LOGS_DIR = ROOT_DIR / "logs"

NODES_FILE = ROOT_DIR / "tree" / "nodes.json"
CONFIG_FILE = ROOT_DIR / "config" / "config.json"


def get_image_path(rel_path: str) -> Path:
    """Get the full path for a relative path that a Button may contain.
    Relative path is relative to assets/images, e.g. './food/apple.png'.
    This doesn't check for if the path is actually valid."""

    clean_rel_path = rel_path[2:] if rel_path.startswith("./") else rel_path
    path = IMAGES_DIR / clean_rel_path
    return path
