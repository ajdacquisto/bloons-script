class Location:
    def __init__(self, name_val, coordsXY):
        self.name = name_val
        self.x = coordsXY[0]
        self.y = coordsXY[1]

    def __eq__(p1, p2):
        # return p1.getName() == p2.getName() and p1.getX() == p2.getX() and p1.getY() == p2.getY()
        return p1.name == p2.name and p1.x == p2.x and p1.y == p2.y

    def getName(self):
        return str(self.name)

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def info(self):
        return (self.x, self.y, self.name)


def getLoc(locName):
    for l in LOCATIONS:
        if l.name == locName:
            return l


def get_coord_list():
    coordList = []
    for L in LOCATIONS:
        coordList.append((L.x, L.y))
    return coordList


def get_loc_from_coords(C):
    x, y = C
    for L in LOCATIONS:
        if L.x == x and L.y == y:
            return L
    return None


def get_loc_num(inp_L):
    for i, L in enumerate(LOCATIONS):
        if L.getName() == inp_L.getName():
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
