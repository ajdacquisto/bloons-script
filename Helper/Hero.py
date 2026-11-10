"""Represent heroes and their positions on the selection screen."""

from typing import Tuple, List


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

    def get_coords(self) -> Tuple[int, int]:
        """Return the hero button's screen coordinates."""
        horiz_adjust = 100
        horiz_scaling = 150

        vert_adjust = 200
        vert_scaling = 200

        x = self.col * horiz_scaling + horiz_adjust
        y = self.row * vert_scaling + vert_adjust
        return (x, y)


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
