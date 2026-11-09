class Tower:
    
    HOTKEYS = {'Dart Monkey': 'q',
           'Boomerang Monkey': 'w',
           'Bomb Shooter': 'e',
           'Tack Shooter': 'r',
           'Ice Monkey': 't',
           'Glue Gunner': 'y',
           'Sniper Monkey': 'z',
           'Monkey Sub': 'x',
           'Monkey Buccaneer': 'c',
           'Monkey Ace': 'v',
           'Heli Pilot': 'b',
           'Mortar Monkey': 'n',
           'Dartling Gunner': 'm',
           'Wizard Monkey': 'a',
           'Super Monkey': 's',
           'Ninja Monkey': 'd',
           'Alchemist': 'f',
           'Druid': 'g',
           'Banana Farm': 'h',
           'Engineer Monkey': 'l',
           'Spike Factory': 'j',
           'Monkey Village': 'k',
           'Hero': 'u',
           'sell': 'bksp',
           'upgrade': '0'}

    towers = []
    
    def __init__(self, name, coords, upgrades, targeting):
        self.name = name
        self.position = coords
        self.upgrades = upgrades
        self.targeting = targeting
        self.hotkey = self.HOTKEYS[self.name]
        self.towers = []
        self.delayTime = 0

    def getHotkey(self):
        return self.hotkey

    def getPosition(self):
        return self.position

    def getUpgrades(self):
        return self.upgrades

