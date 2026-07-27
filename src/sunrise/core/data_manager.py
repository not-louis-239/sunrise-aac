# module for handling user `config.json` files

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


import json
from typing import TYPE_CHECKING, TypedDict

from .paths import CONFIG_FILE

if TYPE_CHECKING:
    from sunrise.core.aac import AAC


class Config(TypedDict):
    theme_idx: int
    speak_keyboard_chars: bool


def load_config() -> Config:
    try:
        with open(CONFIG_FILE, "r") as f:
            raw_config = json.load(f)
    except FileNotFoundError:
        print("Warning: Config file not found.")
        raw_config = {}
    except PermissionError:
        print("Warning: Permission denied when trying to read config file.")
        raw_config = {}
    except json.JSONDecodeError:
        print("Warning: Config file is corrupted.")
        raw_config = {}
    except Exception as e:
        print(f"Warning: An unexpected error occurred while loading the config file: {e}")
        raw_config = {}

    # Process the loaded config data
    data: Config = {
        "theme_idx": raw_config.get("theme_idx", 0),  # Default to 0 ("Light") if not found
        "speak_keyboard_chars": raw_config.get("speak_keyboard_chars", True)
    }

    return data

def save_config(aac_inst: AAC) -> None:
    serialised: Config = {
        "theme_idx": aac_inst.config.theme_idx,
        "speak_keyboard_chars": aac_inst.config.speak_keyboard_chars
    }

    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(serialised, f, indent=4)
    except Exception as e:
        print(f"Warning: An unexpected error occurred while saving the config file: {e}")
