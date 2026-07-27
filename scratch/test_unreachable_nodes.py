# this is an algorithm that detects unreachable nodes:
#  - nodes that have no buttons that point to them as a destination
#  - and even if a button points to it as a destination, if the button itself is in an unreachable node,
#    then that button doesn't count as a reference


from dataclasses import dataclass, field
from collections import deque


@dataclass
class MockButton:
    dest: str


@dataclass
class Node:
    buttons: list[MockButton] = field(default_factory=list)


@dataclass
class LanguageTree:
    nodes: dict[str, Node] = field(default_factory=dict)

    def get(self, k: str) -> Node | None:
        return self.nodes.get(k)

    def get_reachable_nodes(self, start_node_id: str = "HOME") -> set[str]:
        """Returns a set of node IDs for all nodes
        that are reachable from `start_node`."""

        reachable_nodes: set[str] = set()
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
                queue.append(button.dest)

        return reachable_nodes

    def get_reference_counts(self, start_node: str = "HOME") -> dict[str, int]:
        """Returns a dictionary of {node_id: reference_count}"""

        reachable_nodes = self.get_reachable_nodes(start_node)
        reference_counts = {node: 0 for node in reachable_nodes}

        for node_id in reachable_nodes:
            node = self.get(node_id)
            if node is None:
                continue

            for button in node.buttons:
                if button.dest in reachable_nodes:
                    reference_counts[button.dest] += 1

        return reference_counts


def main():
    DUMMY_LT = LanguageTree(nodes={
        "HOME": Node(
            buttons=[MockButton(dest="REACHABLE")]
        ),
        "REACHABLE": Node(  # standard reachable node because it has a reference from HOME
            buttons=[]
        ),
        "UNREACHABLE_1": Node(  # unreachable because no valid references point to it
            buttons=[MockButton(dest="UNREACHABLE_2")],
        ),
        "UNREACHABLE_2": Node(   # unreachable because no valid references point to it
           buttons=[MockButton(dest="UNREACHABLE_3")],
        ),
        "UNREACHABLE": Node(  # should be unreachable since no buttons point to it at all
           buttons=[],
        )
    })

    refcounts = DUMMY_LT.get_reference_counts()
    print(refcounts)


if __name__ == "__main__":
    main()
