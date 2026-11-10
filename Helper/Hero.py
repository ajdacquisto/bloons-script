"""Represent heroes and their positions on the selection screen."""

from typing import Tuple, List


class Hero:
    """Describe a hero and the row and column of its selection button."""

    def __init__(self, name: str, bCoords: Tuple[int, int]) -> None:  # pylint: disable=invalid-name
        self.name = name
        self.row, self.col = bCoords

    def __eq__(h1, h2) -> bool:
        return h1.name == h2.name

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


# def get_heroes(filename: str) -> List[Hero]:
#     with open(filename, "r") as f:
#         line = f.readline()
#         heroes = []
#         while line:
#             if line[0] != "#":
#                 # Ignore final newline character:
#                 if line[-1] == "\n":
#                     line = line[:-1]

#                 # Create a list from comma separated items
#                 line_list = line.split(",")

#                 h_name = line_list[0]
#                 h_row = int(line_list[1])
#                 h_col = int(line_list[2])
#                 h_coords = (h_row, h_col)
#                 h = Hero(h_name, h_coords)
#                 heroes.append(h)

#             line = f.readline()
#     return heroes
