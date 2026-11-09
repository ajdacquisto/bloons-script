from typing import Tuple, List


class Hero:
    def __init__(self, name: str, bCoords: Tuple[int, int]) -> None:
        self.name = name
        self.row, self.col = bCoords

    def __eq__(h1, h2) -> bool:
        return h1.name == h2.name

    def __str__(self) -> str:
        return "Hero: " + str(self.name)

    def get_name(self) -> str:
        return self.name

    def get_coords(self) -> Tuple[int, int]:
        HORIZ_ADJUST = 100
        HORIZ_SCALING = 150

        VERT_ADJUST = 200
        VERT_SCALING = 200

        x = self.col * HORIZ_SCALING + HORIZ_ADJUST
        y = self.row * VERT_SCALING + VERT_ADJUST
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
