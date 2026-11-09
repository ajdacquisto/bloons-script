class Map:
    def __init__(self, name, diff, subpageNum, subpagePos, delayTime, towers):
        self.name = name
        self.difficulty = diff # Beginner, Intermediate, Advanced, Expert
        self.subpage = subpageNum
        self.position = subpagePos
        self.delayTime = delayTime
        self.towers = towers
