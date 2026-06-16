# module for loading language tree nodes
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


from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json

from sunrise.ui.constants import ALLOWED_BUTTON_TYPES
from sunrise.core.paths import NODES_FILE
from sunrise.core.terminal_formatting import COL_ERR, COL_WARN, COL_INFO, COL_END

_TYPE_DISPLAY_COL = "\033[93m"
_WORD_DISPLAY_COL = "\033[32m"
_DEST_DISPLAY_COL = "\033[94m"
_FUNC_DISPLAY_COL = "\033[95m"
_END = "\033[0m"

@dataclass(kw_only=True)
class Button:
    # How it acts
    word: str | None
    dest: str | int | None   # target folder OR relative offset
    func: str | None         # function alias for hooking
    immutable: bool = False  # if true, it cannot be deleted or modified, only moved
                             # this is needed to prevent little kids deleting the "Home"
                             # button and bricking the program

    # How it looks
    label: str
    img: str | None          # relative path to image folder from assets/images
    coords: tuple[int, int]  # (x, y) from:
                             #     for x:  [-10..-1] U [0..9]
                             #     for y:  [-6..-1] U [0..5]

    type: str                # used for button highlighting

    def inspect(self, node_label: str) -> str:
        """Return a formatted string for inspecting the Button object."""
        first_line = f"button {COL_INFO}'{self.label}'{COL_END} @ {COL_INFO}{self.coords}{COL_END} in node {COL_INFO}'{node_label}'{COL_END}"

        if self.immutable:
            first_line += f" {COL_WARN}(immutable){COL_END}"

        if self.dest:
            first_line += f' -> {COL_INFO}{self.dest}{COL_END}'
        elif self.word:
            first_line += f' (word: {COL_INFO}{self.word}{COL_END})'
        elif self.func:
            first_line += f' -> {COL_INFO}{self.func}(){COL_END}'
        else:
            first_line += f' {COL_WARN}(no defined functionality){COL_END}'

        lines: list[str] = [first_line]

        if self.img:
            lines.append(f"  - image: {COL_INFO}{self.img}{COL_END}")
        lines.append(f"  - type: {COL_INFO}{self.type}{COL_END}")

        return "\n".join(lines)

@dataclass(kw_only=True)
class Node:
    # TODO: Potential idea: if we made this a dict of {(x, y): Button},
    # then button lookup from coordinates could become O(1) instead
    # of O(W * H), this would be great.

    buttons: list[Button] = field(default_factory=list)

@dataclass
class LanguageTree:
    nodes: dict[str, Node] = field(default_factory=dict)

    def get(self, k: str) -> Node | None:
        return self.nodes.get(k)

    def add_node(self, node_label: str) -> Node:
        """Initialise a new empty node called `node_label` in
        `self`'s nodes dictionary if it doesn't exist, before returning
        the new node, or the node if it already exists."""
        if node_label in self.nodes:
            return self.nodes[node_label]

        new_node = Node()
        self.nodes[node_label] = new_node
        return new_node

    def serialise_to_json(self) -> dict[str, Any]:
        return {
            node_name: {
                "buttons": [
                    {
                        "label": button.label,
                        "word": button.word,
                        "dest": button.dest,
                        "func": button.func,
                        "coords": button.coords,
                        "type": button.type,
                        "img": button.img,
                        "immutable": button.immutable
                    }
                    for button in node.buttons
                ]
            }
            for node_name, node in self.nodes.items()
        }

def save_language_tree(lt: LanguageTree) -> None:
    """Write the language tree to the nodes.json file, preserving
    all JSON properties except "nodes", to which the new language
    tree will be written."""

    with open(NODES_FILE, encoding="utf-8") as f:
        data_raw = json.load(f)

    # mutate the raw data in-place to preserve all properties except "nodes"
    data_raw["nodes"] = lt.serialise_to_json()

    with open(NODES_FILE, "w", encoding="utf-8") as f:
        json.dump(data_raw, f, indent=4, ensure_ascii=False)

def load_language_tree() -> LanguageTree:
    with open(NODES_FILE, encoding="utf-8") as f:
        data_raw = json.load(f)

    nodes_raw: dict[str, Any] = data_raw["nodes"]
    nodes: dict[str, Node] = {}

    for node_name, node_dict in nodes_raw.items():
        buttons_raw_list = node_dict["buttons"]

        node_buttons: list[Button] = []
        for button_raw in buttons_raw_list:
            button = Button(
                label=button_raw["label"],
                word=button_raw.get("word", None),
                dest=button_raw.get("dest", None),
                func=button_raw.get("func", None),
                coords=tuple(button_raw["coords"]),
                type=button_raw["type"],
                img=button_raw.get("img", None),
                immutable=button_raw.get("immutable", False)
            )
            node_buttons.append(button)

        node = Node(buttons=node_buttons)
        nodes[node_name] = node

    return LanguageTree(nodes=nodes)

def _make_error(node_name: str, button: Button, msg: str) -> str:
    return f"{COL_ERR}'{node_name}'{COL_END}:{COL_ERR}'{button.label}'{COL_END}@{COL_ERR}{button.coords}{COL_END}: {msg}"

def lint_language_tree(lt: LanguageTree) -> list[str]:
    """Check the language tree for unreachable nodes:
    - OOB grid positions
    - nodes in a folder that cannot be reached from any folder node
    - nodes with duplicate positions with other nodes in the UNIVERSAL or same node as itself

    Also checks for other issues such as:
    - missing or unreadable image paths
    - undefined function aliases
    - destinations not specified in nodes.json
    """

    errors: list[str] = []

    # Get the coordinates of all buttons in the UNIVERSAL node
    uni_node = lt.get("UNIVERSAL")
    if uni_node is None:
        universal_nodes = set()
        errors.append("missing UNIVERSAL node")
    else:
        universal_nodes = {button.coords for button in uni_node.buttons}

    # Import here to avoid circular import with aac.engine which imports this module
    from sunrise.core.engine import AACEngine

    for node_name, node in lt.nodes.items():
        if node_name != "UNIVERSAL":
            seen_positions: set[tuple[int, int]] = universal_nodes.copy()  # start with UNIVERSAL node positions as seen
        else:
            seen_positions = set()

        for button in node.buttons:
            # Check for OOB grid positions
            x, y = button.coords[0], button.coords[1]
            if not (-10 <= x <= 9) or not (-6 <= y <= 5):
                errors.append(_make_error(node_name, button, f"OOB coordinates: {button.coords}"))

            # Check for duplicate positions
            if button.coords in seen_positions:
                errors.append(_make_error(node_name, button, f"duplicate coordinates: {button.coords}"))
            else:
                seen_positions.add(button.coords)

            # Check for missing or unreadable image paths
            if button.img is not None:
                img_path = Path("assets/images") / button.img
                if not img_path.exists():
                    errors.append(_make_error(node_name, button, f"no such image file: {img_path}"))
                elif not img_path.is_file():
                    errors.append(_make_error(node_name, button, f"not an image file: {img_path}"))

            # Check for undefined function aliases
            if button.func is not None and button.func not in AACEngine.FUNC_REGISTRY:
                errors.append(_make_error(node_name, button, f"function '{button.func}' is not defined in AACEngine.FUNC_REGISTRY"))

            # Check for destinations not specified in nodes.json
            if isinstance(button.dest, str) and button.dest != "HOME" and button.dest not in lt.nodes:
                errors.append(_make_error(node_name, button, f"undefined destination '{button.dest}'"))

            # Check for disallowed/unrecognised button types
            if button.type not in ALLOWED_BUTTON_TYPES:
                errors.append(_make_error(node_name, button, f"unrecognised button type '{button.type}'"))

    return errors

def print_lt(lt: LanguageTree) -> None:
    for node_name, node in lt.nodes.items():
        print(f"[{node_name}]")

        for button in node.buttons:
            line = (
                f"  - {button.label!r} {_TYPE_DISPLAY_COL}[{button.type}]{_END}"
                + (f"{_DEST_DISPLAY_COL} -> {button.dest!r}{_END}," if button.dest else ",")
                + (f"{_WORD_DISPLAY_COL} word: {button.word!r}{_END}," if button.word else "")
                + (f"{_FUNC_DISPLAY_COL} func: {button.func!r}{_END}," if button.func else "")
                + f" coords: {button.coords},"
                + f" img: {button.img!r}"
            )

            print(line)

        print()

def _test():
    lt = load_language_tree()
    print_lt(lt)

    print("Linting...")

    issues = lint_language_tree(lt)
    print()
    if not issues:
        print(f"{COL_INFO}No issues found!{COL_END}")
    else:
        num_issues = len(issues)
        print(f"{COL_ERR}{num_issues}{COL_END} issue{'' if num_issues == 1 else 's'} found:")
        for issue in issues:
            print(f"  - {issue}")

if __name__ == "__main__":
    _test()
