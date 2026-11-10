"""Represent tower placements, upgrades, and targeting."""


class Tower:
    """Store the input needed for one tower action."""

    HOTKEYS = {
        "Dart Monkey": "q",
        "Boomerang Monkey": "w",
        "Bomb Shooter": "e",
        "Tack Shooter": "r",
        "Ice Monkey": "t",
        "Glue Gunner": "y",
        "Sniper Monkey": "z",
        "Monkey Sub": "x",
        "Monkey Buccaneer": "c",
        "Monkey Ace": "v",
        "Heli Pilot": "b",
        "Mortar Monkey": "n",
        "Dartling Gunner": "m",
        "Wizard Monkey": "a",
        "Super Monkey": "s",
        "Ninja Monkey": "d",
        "Alchemist": "f",
        "Druid": "g",
        "Banana Farm": "h",
        "Engineer Monkey": "l",
        "Spike Factory": "j",
        "Monkey Village": "k",
        "Hero": "u",
        "sell": "bksp",
        "upgrade": "0",
    }

    def __init__(self, name, coords, upgrades, targeting):
        self.name = name
        self.position = coords
        self.upgrades = upgrades
        self.targeting = targeting
        self.hotkey = self.HOTKEYS[self.name]
        self.towers = []
        self.delayTime = 0  # pylint: disable=invalid-name

    def get_hotkey(self):
        """Return the hotkey associated with this tower action."""
        return self.hotkey

    def get_position(self):
        """Return the tower's screen position."""
        return self.position

    def get_upgrades(self):
        """Return the upgrades to apply on each path."""
        return self.upgrades
