"""Represent map-card locations on the selection screen."""


class Location:
    """Store the name and screen coordinates of a map-card location."""

    def __init__(self, name_val, coordsXY):  # pylint: disable=invalid-name
        self.name = name_val
        self.x = coordsXY[0]
        self.y = coordsXY[1]

    def __eq__(self, p2):
        return self.name == p2.name and self.x == p2.x and self.y == p2.y

    def getName(self):  # pylint: disable=invalid-name
        """Return the location name as text."""
        return str(self.name)

    def getX(self):  # pylint: disable=invalid-name
        """Return the horizontal screen coordinate."""
        return self.x

    def getY(self):  # pylint: disable=invalid-name
        """Return the vertical screen coordinate."""
        return self.y

    def info(self):
        """Return the coordinates and name."""
        return (self.x, self.y, self.name)


def getLoc(locName):  # pylint: disable=invalid-name
    """Find a location by its name, or return None."""
    for location in LOCATIONS:
        if location.name == locName:
            return location


def get_coord_list():
    """Return the coordinates of all known map-card locations."""
    coord_list = []
    for location in LOCATIONS:
        coord_list.append((location.x, location.y))
    return coord_list


def get_loc_from_coords(C):  # pylint: disable=invalid-name
    """Find a location by its coordinates, or return None."""
    x, y = C
    for location in LOCATIONS:
        if location.x == x and location.y == y:
            return location
    return None


def get_loc_num(inp_L):  # pylint: disable=invalid-name
    """Return the index of a named location, or -1 if it is absent."""
    for i, location in enumerate(LOCATIONS):
        if location.getName() == inp_L.getName():
            return i
    return -1


LOCATIONS = [
    Location("Top left", (697, 296)),
    Location("Top middle", (1120, 296)),
    Location("Top right", (1544, 296)),
    Location("Bottom left", (697, 610)),  #
    Location("Bottom middle", (1120, 610)),
    Location("Bottom right", (1544, 610)),
]  #


# Old values:
# Location('Top left', (701,283) ),
# Location('Top middle', (1124,283) ),
# Location('Top right', (1548,283) ),
# Location('Bottom left', (701,597) ),
# Location('Bottom middle', (1124,610) ),
# Location('Bottom right', (1548,597) )]
