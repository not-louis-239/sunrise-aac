# module for linting language trees and creating error objects

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


from dataclasses import dataclass

from sunrise.core.constants import ALLOWED_IMAGE_SUFFIXES
from sunrise.core.language_tree import LanguageTree
from sunrise.core.paths import get_image_path
from sunrise.core.problem_severity import Severity
from sunrise.ui.constants import GRID_H, GRID_W


@dataclass(frozen=True)
class Problem:
    severity: Severity
    desc: str
    node_id: str | None = None
    button_label: str | None = None

    def __str__(self) -> str:
        if self.node_id and self.button_label:
            return f"Node '{self.node_id}', Button '{self.button_label}': {self.desc}"
        elif self.node_id:
            return f"Node '{self.node_id}': {self.desc}"
        else:
            return self.desc

    def __hash__(self) -> int:
        return hash((self.severity.value, self.desc, self.node_id, self.button_label))


def lint_language_tree(lt: LanguageTree) -> list[Problem]:
    """
    Lint a LanguageTree object and return a list of `Problem`s if applicable, such as:
     - missing UNIVERSAL node
     - unreachable nodes
     - buttons with no action set (no word, destination or function)
     - buttons with OOB grid positions
     - buttons overlapping with UNIVERSAL or same-node buttons
     - buttons with bad image paths
    """

    problems: list[Problem] = []

    # Check for the UNIVERSAL node
    universal_node = lt.get("UNIVERSAL")
    if not universal_node:
        universal_button_coords: set[tuple[int, int]] = set()
        problems.append(Problem(severity=Severity.ERROR, desc="Missing UNIVERSAL node"))
    else:
        universal_button_coords: set[tuple[int, int]] = {(button.coords[0] % GRID_W, button.coords[1] % GRID_H) for button in universal_node.buttons}  # normalise

    # Check for unreachable nodes
    # Buttons in unreachable nodes won't be considered for further analysis
    reachable_node_ids = lt.get_reachable_node_ids()
    unreachable_node_ids = set(lt.nodes.keys()) - reachable_node_ids
    for node_id in unreachable_node_ids:
        if (node := lt.get(node_id)) is not None:
            for button in node.buttons:
                problems.append(Problem(Severity.WARNING, f"Unreachable node '{node_id}'", node_id=node_id, button_label=button.label))

    # Check for OOB positions and overlaps
    for node_id in reachable_node_ids - {"UNIVERSAL"}:
        node = lt.nodes[node_id]  # not using .get() here so Pyright won't complain, we know that it points to a valid node
        seen_coords = universal_button_coords.copy()

        for button in node.buttons:
            # No function set
            if not button.word and not button.dest and not button.func:
                problems.append(Problem(Severity.WARNING, "No word, destination or function set", node_id=node_id, button_label=button.label))

            # Grid position out of bounds
            x, y = button.coords
            if not (-GRID_W <= x < GRID_W and -GRID_H <= y < GRID_H):
                problems.append(Problem(Severity.ERROR, f"Out-of-bounds coordinates {button.coords}", node_id=node_id, button_label=button.label))

            # Overlaps
            coords_norm = button.coords[0] % GRID_W, button.coords[1] % GRID_H  # normalise
            if coords_norm in seen_coords:
                problems.append(Problem(Severity.ERROR, f"Coordinates {button.coords} is already occupied by another button", node_id=node_id, button_label=button.label))
            seen_coords.add(coords_norm)

            # Bad image paths
            if button.img is not None:
                img_path = get_image_path(button.img)
                if not img_path.exists():
                    problems.append(Problem(Severity.WARNING, f"Image not found: '{button.img}'", node_id=node_id, button_label=button.label))
                elif not img_path.is_file():
                    problems.append(Problem(Severity.WARNING, f"'{button.img}' is not a file", node_id=node_id, button_label=button.label))
                elif img_path and img_path.suffix not in ALLOWED_IMAGE_SUFFIXES:
                    problems.append(Problem(Severity.ERROR, f"Unsupported image format. Please use one of: {', '.join(ALLOWED_IMAGE_SUFFIXES)}", node_id=node_id, button_label=button.label))

    return problems
