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


from collections import deque
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
    fixed_font_size: int | None = None
    img: str | None           # relative path to image folder from assets/images
    coords: tuple[int, int]   # (x, y) from:
                              #     for x:  [-10..-1] U [0..9]
                              #     for y:  [-6..-1] U [0..5]

    type: str                 # used for button highlighting


@dataclass(kw_only=True)
class Node:
    buttons: list[Button] = field(default_factory=list)


@dataclass
class LanguageTree:
    nodes: dict[str, Node] = field(default_factory=dict)

    def get(self, k: str) -> Node | None:
        return self.nodes.get(k)

    def add_node(self, node_label: str) -> Node:
        """Initialise a new empty node called `node_label` in
        `self`'s nodes dictionary if it doesn't exist, before returning
        the new node, or the pre-existing node if it already exists."""
        if node_label not in self.nodes:
            self.nodes[node_label] = Node()
        return self.nodes[node_label]

    def serialise_to_json(self) -> dict[str, Any]:
        # clean the tree before serialising
        self.gc()

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

    def get_reachable_node_ids(self, start_node_id: str = "HOME") -> set[str]:
        """Returns a set of node IDs for all nodes
        that are reachable from `start_node`."""

        reachable_nodes: set[str] = {"UNIVERSAL"}
        queue = deque([start_node_id])

        while queue:
            current_node = queue.popleft()
            if current_node in reachable_nodes:
                continue
            reachable_nodes.add(current_node)

            node = self.get(current_node)
            if node is None:
                continue

            for button in node.buttons:
                if isinstance(button.dest, str):
                    queue.append(button.dest)

        return reachable_nodes

    def gc(self) -> None:
        """Run garbage collection on the language tree by removing
        any nodes that contain no buttons."""
        empty_nodes = [node_name for node_name, node in self.nodes.items() if not node.buttons]
        for node_name in empty_nodes:
            del self.nodes[node_name]


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
                immutable=button_raw.get("immutable", False),
            )
            node_buttons.append(button)

        node = Node(buttons=node_buttons)
        nodes[node_name] = node

    return LanguageTree(nodes=nodes)


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


if __name__ == "__main__":
    _test()
