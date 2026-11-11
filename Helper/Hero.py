"""Represent heroes and their positions on the selection screen."""

from typing import Tuple, List

from Helper.UICalibration import (
    HERO_GRID_BOTTOM_LAST_ROW_Y,
    HERO_GRID_CLICKABLE_Y,
    HERO_GRID_COLUMNS_X,
    HERO_GRID_ROW_SPACING,
    HERO_GRID_TOP_FIRST_ROW_Y,
)


class Hero:
    """Describe a hero and the row and column of its selection button."""

    def __init__(self, name: str, bCoords: Tuple[int, int]) -> None:  # pylint: disable=invalid-name
        self.name = name
        self.row, self.col = bCoords

    def __eq__(self, h2) -> bool:
        return self.name == h2.name

    def __str__(self) -> str:
        return "Hero: " + str(self.name)

    def get_name(self) -> str:
        """Return the hero's name."""
        return self.name

    def get_card_position(self, last_row: int) -> Tuple[str, Tuple[int, int]]:
        """Return the scroll anchor ("top"/"bottom") and card center for this hero.

        ``last_row`` is the grid's final row, which determines the bottom anchor.
        """
        if not 0 <= self.col < len(HERO_GRID_COLUMNS_X) or not 0 <= self.row <= last_row:
            raise ValueError(f"{self.name}: Slot ({self.row}, {self.col}) is outside the hero grid")
        x = HERO_GRID_COLUMNS_X[self.col]
        low, high = HERO_GRID_CLICKABLE_Y
        top_y = HERO_GRID_TOP_FIRST_ROW_Y + self.row * HERO_GRID_ROW_SPACING
        if low <= top_y <= high:
            return "top", (x, top_y)
        bottom_y = HERO_GRID_BOTTOM_LAST_ROW_Y - (last_row - self.row) * HERO_GRID_ROW_SPACING
        if low <= bottom_y <= high:
            return "bottom", (x, bottom_y)
        raise ValueError(f"{self.name}: Row {self.row} is not reachable from either scroll anchor")


def get_heroes(filename: str) -> List[Hero]:
    """Load named hero slots, reporting invalid records with their line number."""
    heroes = []
    names = set()
    with open(filename, "r") as source:
        for line_number, line in enumerate(source, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                name, row_text, col_text = (field.strip() for field in line.split(","))
                row, col = int(row_text), int(col_text)
                valid_slot = (
                    (row, col) == (-1, -1) if name == "None"
                    else row >= 0 and 0 <= col <= 2
                )
                if not name or name in names or not valid_slot:
                    raise ValueError("Invalid name, duplicate hero, or invalid slot")
            except ValueError as exc:
                raise ValueError(f"{filename}:{line_number}: Invalid hero record") from exc
            heroes.append(Hero(name, (row, col)))
            names.add(name)
    if not heroes:
        raise ValueError(f"{filename}: No heroes defined")
    return heroes
