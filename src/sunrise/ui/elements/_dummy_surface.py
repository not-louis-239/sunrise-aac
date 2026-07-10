from pygame import Surface

# This exists to avoid awkward `Surface | None` typing that
# causes type checkers to complain incessantly!!
DUMMY_SURFACE = Surface((1, 1))
