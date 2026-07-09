from .widget import Widget

class ScrollableDisplay(Widget):
    """Creates a display that is vertically scrollable.
    Its height depends on the preferred size of the contents inside of the display."""
    def __init__(self, *, flex: int = 0, gap: int = 0) -> None:
        super().__init__(flex=flex)
        self.gap = gap

    def _vertical_size(self) -> int:
        """Get the preferred vertical size of all child components
        inside `self`, including gaps imposed by `self`, but
        excluding padding."""
        total_raw_height = sum(child.preferred_size()[1] for child in self.children)
        num_gaps = max(0, len(self.children) - 1)
        total_gap_h = self.gap * num_gaps
        return total_raw_height + total_gap_h

    def preferred_size(self) -> tuple[int, int]:
        ...  # TODO: implement
