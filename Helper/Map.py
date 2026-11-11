"""Load maps and define the strategies used to play them."""

from random import randint
from pathlib import Path
from typing import List

from Helper.Hero import Hero, get_heroes
from Helper.Location import Location, getLoc
from Helper.Action import Action
from Helper.Strategy import Strategy
from Helper.Tower import Tower

class Map:
    """Describe a map's menu location and available strategies."""

    HEROES = get_heroes(str(Path(__file__).with_name("heroes.dat")))

    def __init__(
        self,
        name: str,
        diff: int,
        page: int,
        subpage: int,
        page_location: Location,
        strategy: Strategy = None,
    ) -> None:
        self.name = name  # type: str
        self.difficulty = diff  # type: int
        self.page = page  # type: int
        self.subpage = subpage  # type: int
        self.page_location = page_location  # type: Location
        self.strategy = strategy  # type: Strategy

    def get_name(self) -> str:
        """Return the map name."""
        return self.name

    def get_difficulty(self) -> int:
        """Return the map difficulty category."""
        return self.difficulty

    def get_subpage(self) -> int:
        """Return the map's subpage within its category."""
        return self.subpage

    def get_page(self) -> int:
        """Return the map-selection page number."""
        return self.page

    def get_page_location(self) -> Location:
        """Return the map-card location on its page."""
        return self.page_location

    def get_strategy(self) -> Strategy:
        """Return the stored strategies."""
        return self.strategy

    def get_strategy_from_mode(self, game_diff: int, game_mode: str) -> Strategy:
        """Find a strategy matching a game difficulty and mode."""
        for s in self.strategy:
            if game_diff == s.get_game_difficulty() and game_mode == s.get_game_mode():
                return s
        return None


def map_setup(dataFilePath: str) -> List[Map]:  # pylint: disable=invalid-name
    """Load map locations and attach the corresponding strategies."""
    with open(dataFilePath, "r") as f:
        line = f.readline()
        list_of_maps = []
        while line:
            if line[0] != "#":
                # Ignore final newline character:
                if line[-1] == "\n":
                    line = line[:-1]

                # Create a list from comma separated items
                line_list = line.split(",")

                m_name = line_list[0]
                m_diff = int(line_list[1])
                m_page = int(line_list[2])
                m_subpage = int(line_list[3])
                m_loc_name = line_list[4]
                m_loc_num = int(line_list[5])

                m_location = getLoc(m_loc_name)

                if m_location is None:
                    raise Exception("Location not found.")

                m = Map(m_name, m_diff, m_page, m_subpage, m_location)

                m.strategy = get_strategy(m)

                # Append the list
                list_of_maps.append(m)

            line = f.readline()
    return list_of_maps


def get_map_by_name(map_list: List[Map], map_name: str) -> Map:
    """Find a map by name, or return None."""
    for m in map_list:
        if m.name == map_name:
            return m


def get_playable_maps(map_list: List[Map]) -> List[Map]:
    """Return maps with at least one defined strategy."""
    playable_maps = [m for m in map_list if m.strategy]
    if not playable_maps:
        raise ValueError("No maps have a defined strategy")
    return playable_maps


def pick_rand(map_list: List[Map]) -> Map:
    """Choose a random map with at least one defined strategy."""
    playable_maps = get_playable_maps(map_list)
    n = len(playable_maps)
    a = randint(0, n - 1)
    return playable_maps[a]


def pick_ordered(map_list: List[Map], index: int) -> Map:
    """Choose the map for a loop index, skipping maps without strategies."""
    playable_maps = get_playable_maps(map_list)
    return playable_maps[index % len(playable_maps)]


def get_map_from_location(
    map_list: List[Map], page_num: int, page_location_given: Location
) -> Map:
    """Find the map at a given page and map-card location."""
    for m in map_list:
        if m.page == page_num:
            if m.page_location == page_location_given:
                return m
    raise Exception("Map with given position and pageNum was not found.")


def get_hero(hero_name: str) -> Hero:
    """Find a hero by name."""
    for h in Map.HEROES:
        if h.name == hero_name:
            return h
    raise LookupError("get_hero: Invalid argument. Hero not found.")


def get_strategy(m: Map) -> List[Strategy]:
    """Build the available strategies for the supplied map."""
    if m.name == "Dark Dungeons":
        action_list_defl = [
            Action(
                "Tower",
                [
                    Tower("Monkey Village", [1083, 666], [0, 0, 2], 0),
                    Tower("Monkey Ace", [1076, 480], [2, 0, 3], 0),
                ],
            ),
            Action("Start", 0),
            Action(
                "Tower",
                [
                    Tower("Monkey Ace", [1070, 568], [2, 0, 3], 0),
                    Tower("Alchemist", [962, 514], [4, 0, 1], 0),
                    Tower("Hero", [898, 571], [0, 0, 0], 3),
                    Tower("sell", [1083, 666], [0, 0, 0], 0),
                    Tower("Monkey Village", [1083, 666], [2, 2, 0], 0),
                    Tower("Bomb Shooter", [1420, 333], [0, 3, 1], 3),
                ],
            ),
            Action("WaitSec", 288),
        ]
        action_list_stnd = [
            Action(
                "Tower",
                [
                    Tower("Hero", [656, 517], [0, 0, 0], 3),
                    Tower("Dart Monkey", [243, 907], [0, 0, 0], 0),
                ],
            ),
            Action("WaitRound", [1, True]),  # -> end of 1
            Action("Tower", [Tower("Monkey Sub", [1439, 866], [0, 0, 0], 0)]),
            Action("WaitRound", 4),  # -> end of 5
            Action("Tower", [Tower("Monkey Ace", [1075, 470], [0, 0, 0], 0)]),
            Action("WaitRound", 2),  # -> end of 7
            Action(
                "Tower", [Tower("upgrade", [243, 907], [0, 0, 2], 0)]
            ),  # DM -> LRD,EE
            Action("WaitRound", 3),  # -> end of 10
            Action(
                "Tower",
                [
                    Tower("upgrade", [1075, 470], [1, 0, 0], 0),  # MA -> RF
                    Tower("upgrade", [243, 907], [1, 0, 0], 0),  # DM -> SS
                ],
            ),
            Action("WaitRound", 2),  # -> end of 12
            Action("Tower", [Tower("upgrade", [1439, 866], [0, 0, 1], 0)]),  # MS -> TG
            Action("WaitRound", 1),  # -> end of 13
            Action("Tower", [Tower("upgrade", [1075, 470], [0, 0, 1], 0)]),  # MA -> SD
            Action("WaitRound", 4),  # -> end of 17
            Action("Tower", [Tower("upgrade", [1439, 866], [0, 0, 1], 0)]),  # MS -> ABD
            Action("WaitRound", 1),  # -> end of 18
            Action(
                "Tower", [Tower("upgrade", [243, 907], [2, 0, 0], 0)]
            ),  # DM -> RSS,SOP
            Action("WaitRound", 2),  # -> end of 20
            Action("Tower", [Tower("Druid", [930, 972], [0, 0, 0], 0)]),
            Action("WaitRound", 1),  # -> end of 21
            Action("Tower", [Tower("Druid", [171, 911], [0, 0, 0], 0)]),
            Action("WaitRound", 1),  # -> end of 22
            Action(
                "Tower",
                [
                    Tower("upgrade", [930, 972], [0, 1, 0], 0),  # Dr -> TS
                    Tower("upgrade", [171, 911], [0, 1, 0], 0),  # Dr -> TS
                ],
            ),
            Action("WaitRound", 8),  # -> end of 30
            Action(
                "Tower", [Tower("upgrade", [1075, 470], [0, 0, 2], 0)]
            ),  # MA -> CP,NMT
            Action("WaitRound", 1),  # -> end of 31
            Action(
                "Tower", [Tower("upgrade", [1439, 866], [0, 2, 0], 0)]
            ),  # MS -> BD,HTD
            Action("WaitRound", 1),  # -> end of 32
            Action("Tower", [Tower("Ninja Monkey", [1564, 875], [1, 0, 0], 0)]),  # NM
            Action("WaitRound", 2),  # -> end of 34
            Action(
                "Tower",
                [
                    Tower("upgrade", [1075, 470], [1, 0, 0], 0),  # MA -> LMD
                    Tower("upgrade", [1564, 875], [0, 0, 1], 0),  # NM -> SS
                ],
            ),
            Action("WaitRound", 1),  # -> end of 35
            Action("Tower", [Tower("upgrade", [243, 907], [1, 0, 0], 0)]),  # DM -> J
            Action("WaitRound", 4),  # -> end of 39
            Action("Tower", [Tower("Bomb Shooter", [746, 936], [2, 3, 0], 3)]),
            Action("Start", [1, False]),
        ]
        return [
            Strategy(0, "Deflation", get_hero("Psi"), action_list_defl),
            Strategy(0, "Standard", get_hero("Psi"), action_list_stnd),
        ]
    elif m.name == "Sanctuary":
        action_list = [
            Action(
                "Tower",
                [
                    Tower("Hero", [834, 177], [0, 0, 0], 3),
                    Tower("Boomerang Monkey", [838, 287], [4, 0, 2], 0),
                    Tower("Sniper Monkey", [754, 926], [0, 2, 4], 0),
                    Tower("Alchemist", [753, 1007], [4, 2, 0], 0),
                ],
            ),
            Action("Start", 295),
        ]
        return [Strategy(0, "Deflation", get_hero("Psi"), action_list)]
    elif m.name == "Ravine":
        action_list = [
            Action("Tower", [Tower("Monkey Ace", [258, 826], [2, 0, 3], 0)]),
            Action("Start", 0),
            Action(
                "Tower",
                [
                    Tower("Monkey Ace", [413, 897], [2, 0, 3], 0),
                    Tower("Monkey Village", [273, 928], [2, 2, 0], 0),
                    Tower("Alchemist", [393, 805], [4, 0, 1], 0),
                ],
            ),
            Action("WaitSec", 284),
        ]
        return [Strategy(0, "Deflation", get_hero("None"), action_list)]
    elif m.name == "Flooded Valley":
        action_list = [
            Action("Tower", [Tower("Monkey Sub", [1111, 502], [2, 0, 3], 0)]),
            Action("Start", 0),
            Action(
                "Tower",
                [
                    Tower("Monkey Buccaneer", [1033, 762], [3, 2, 0], 0),
                    Tower("Monkey Buccaneer", [1088, 263], [3, 2, 0], 0),
                    Tower("Hero", [717, 404], [0, 0, 0], 0),
                    Tower("Monkey Sub", [1002, 214], [4, 0, 0], 0),
                    Tower("Monkey Sub", [1011, 834], [4, 0, 0], 0),
                ],
            ),
            Action("WaitSec", 288),
        ]
        return [Strategy(0, "Deflation", get_hero("Etienne"), action_list)]
    elif m.name == "Infernal":
        action_list = [
            Action("Start", 0),
            Action(
                "Tower",
                [
                    Tower("Ninja Monkey", [838, 698], [4, 0, 2], 0),
                    Tower("Ninja Monkey", [838, 386], [4, 0, 2], 0),
                    Tower("Alchemist", [838, 755], [4, 0, 0], 0),
                    Tower("Alchemist", [838, 322], [4, 0, 0], 0),
                ],
            ),
            Action("WaitSec", 314.3),
        ]
        return [Strategy(0, "Deflation", get_hero("None"), action_list)]
    elif m.name == "Bloody Puddles":
        action_list = [
            Action(
                "Tower",
                [
                    Tower("Monkey Village", [979, 459], [0, 0, 2], 0),
                    Tower("Monkey Ace", [1000, 556], [2, 0, 3], 0),
                ],
            ),
            Action("Start", 0),
            Action(
                "Tower",
                [
                    Tower("Monkey Ace", [1047, 359], [2, 0, 3], 0),
                    Tower("Alchemist", [1099, 488], [4, 0, 1], 0),
                    Tower("Sniper Monkey", [936, 340], [2, 0, 2], 0),
                    Tower("sell", [979, 459], [0, 0, 0], 0),
                    Tower("Monkey Village", [979, 459], [2, 2, 0], 0),
                ],
            ),
            Action("WaitSec", 283),
        ]
        return [Strategy(0, "Deflation", get_hero("None"), action_list)]
    elif m.name == "Workshop":
        action_list = [
            Action(
                "Tower",
                [
                    Tower("Monkey Village", [897, 417], [2, 0, 2], 0),
                    Tower("Super Monkey", [1004, 484], [0, 3, 2], 0),
                    Tower("Wizard Monkey", [1015, 400], [0, 3, 2], 0),
                    Tower("Alchemist", [905, 498], [3, 0, 0], 0),
                ],
            ),
            Action("Start", 291),
        ]
        return [Strategy(0, "Deflation", get_hero("None"), action_list)]
    elif m.name == "Quad":
        action_list = [
            Action(
                "Tower",
                [
                    Tower("Monkey Village", [1175, 797], [0, 0, 2], 0),
                    Tower("Monkey Village", [1294, 792], [0, 0, 2], 0),
                    Tower("Monkey Ace", [1112, 892], [2, 0, 3], 0),
                    Tower("Monkey Ace", [1265, 890], [2, 0, 3], 0),
                    Tower("Monkey Ace", [1193, 977], [2, 0, 3], 0),
                    Tower("Alchemist", [1307, 963], [4, 0, 1], 0),
                    Tower("sell", [1175, 797], [0, 0, 0], 0),
                    Tower("Monkey Village", [1175, 797], [0, 2, 0], 0),
                    Tower("sell", [1294, 792], [0, 0, 0], 0),
                    Tower("upgrade", [1175, 797], [2, 0, 0], 0),
                ],
            ),
            Action("Start", 303),
        ]
        return [Strategy(0, "Deflation", get_hero("None"), action_list)]
    elif m.name == "Dark Castle":
        action_list = [
            Action("Tower", [Tower("Monkey Sub", [1084, 433], [2, 0, 4], 0)]),
            Action("Start", 0),
            Action(
                "Tower",
                [
                    Tower("Hero", [532, 480], [0, 0, 0], 0),
                    Tower("Monkey Sub", [1084, 367], [2, 0, 4], 0),
                    Tower("Ninja Monkey", [489, 734], [0, 0, 0], 0),
                    Tower("Ninja Monkey", [466, 343], [0, 0, 0], 0),
                    Tower("Alchemist", [1008, 447], [4, 0, 1], 0),
                ],
            ),
            Action("WaitSec", 302),
        ]
        return [Strategy(0, "Deflation", get_hero("Captain Churchill"), action_list)]
    elif m.name == "Muddy Puddles":
        action_list = [
            Action("Tower", [Tower("Monkey Sub", [729, 596], [2, 0, 4], 0)]),
            Action("Start", 0),
            Action(
                "Tower",
                [
                    Tower("Hero", [783, 208], [0, 0, 0], 0),
                    Tower("Ninja Monkey", [416, 192], [0, 0, 0], 0),
                    Tower("Ninja Monkey", [1104, 189], [0, 0, 0], 0),
                    Tower("Monkey Sub", [641, 647], [2, 0, 4], 0),
                    Tower("Alchemist", [615, 504], [4, 0, 2], 0),
                ],
            ),
            Action("WaitSec", 277),
        ]
        return [Strategy(0, "Deflation", get_hero("Captain Churchill"), action_list)]
    elif m.name == "Ouch":
        action_list = [
            Action(
                "Tower",
                [
                    Tower("Hero", [694, 660], [0, 0, 0], 0),
                    Tower("Monkey Buccaneer", [847, 562], [4, 0, 2], 0),
                    Tower("Alchemist", [665, 464], [4, 0, 2], 0),
                    Tower("Wizard Monkey", [1006, 430], [0, 2, 2], 0),
                    Tower("Ninja Monkey", [851, 767], [2, 0, 2], 0),
                ],
            ),
            Action("Start", 299),
            Action("Ability", "1"),
            Action("WaitSec", 2),
        ]
        return [Strategy(0, "Deflation", get_hero("Captain Churchill"), action_list)]
    elif m.name == "Tricky Tracks":
        action_list = [
            Action(
                "Tower",
                [
                    Tower("Monkey Village", [787, 680], [0, 0, 2], 0),
                    Tower("Monkey Ace", [694, 788], [2, 0, 3], 0),
                ],
            ),
            Action("Start", 0),
            Action(
                "Tower",
                [
                    Tower("Monkey Ace", [920, 621], [2, 0, 3], 0),
                    Tower("Alchemist", [704, 714], [4, 0, 1], 0),
                    Tower("Sniper Monkey", [955, 548], [2, 0, 2], 0),
                    Tower("sell", [787, 680], [0, 0, 0], 0),
                    Tower("Monkey Village", [787, 680], [2, 2, 0], 0),
                ],
            ),
            Action("WaitSec", 283),
        ]
        return [Strategy(0, "Deflation", get_hero("None"), action_list)]
    else:
        return None


# MAPS = [
#         Map('Dark Dungeons', 3,1, Loc.getLoc('Top left'),
#             get_hero('Psi'),
#             [
#                 Action( 'Tower',
#                     [   Tower('Monkey Village', [1083,666], [0,0,2], 0),
#                         Tower('Monkey Ace', [1076,480], [2,0,3], 0)
#                     ]
#                 ),
#                 Action( 'Start', 0 ),
#                 Action( 'Tower',
#                     [   Tower('Monkey Ace', [1070,568], [2,0,3], 0),
#                         Tower('Alchemist', [962,514], [4,0,1], 0),
#                         Tower('Hero', [898,571], [0,0,0], 3),
#                         Tower('sell', [1083,666], [0,0,0], 0),
#                         Tower('Monkey Village', [1083,666], [2,2,0], 0),
#                         Tower('Bomb Shooter', [1420,333], [0,3,1], 3)
#                     ]
#                 ),
#                 Action( 'WaitSec', 288 )
#             ]
#         ),
#         Map('Sanctuary', 3,1, Loc.getLoc('Top middle'),
#             get_hero('Psi'),
#             [
#                 Action( 'Tower',
#                     [   Tower('Hero', [834,177], [0,0,0], 3),
#                         Tower('Boomerang Monkey', [838,287], [4,0,2], 0),
#                         Tower('Sniper Monkey', [754,926], [0,2,4], 0),
#                         Tower('Alchemist', [753,1007], [4,2,0], 0)
#                     ]
#                 ),
#                 Action( 'Start', 295 )
#             ]
#         ),
#         Map('Ravine', 3,1, Loc.getLoc('Top right'),
#             get_hero('None'),
#             [
#                 Action( 'Tower',
#                     [   Tower('Monkey Ace', [258,826], [2,0,3], 0)
#                     ]
#                 ),
#                 Action( 'Start', 0 ),
#                 Action( 'Tower',
#                     [   Tower('Monkey Ace', [413,897], [2,0,3], 0),
#                         Tower('Monkey Village', [273,928], [2,2,0], 0),
#                         Tower('Alchemist', [393,805], [4,0,1], 0)
#                     ]
#                 ),
#                 Action( 'WaitSec', 284 )
#             ]
#         ),
#         Map('Flooded Valley', 3, 1, Loc.getLoc('Bottom left'),
#             get_hero('Etienne'),
#             [
#                 Action( 'Tower',
#                     [   Tower('Monkey Sub', [1111,502], [2,0,3], 0)
#                     ]
#                 ),
#                 Action( 'Start', 0 ),
#                 Action( 'Tower',
#                     [   Tower('Monkey Buccaneer', [1033,762], [3,2,0], 0),
#                         Tower('Monkey Buccaneer', [1088,263], [3,2,0], 0),
#                         Tower('Hero', [717,404], [0,0,0], 0),
#                         Tower('Monkey Sub', [1002,214], [4,0,0], 0),
#                         Tower('Monkey Sub', [1011,834], [4,0,0], 0)
#                     ]
#                 ),
#                 Action( 'WaitSec', 288 )
#             ]
#         ),
#         Map('Infernal', 3,1, Loc.getLoc('Bottom middle'),
#             get_hero('None'),
#             [
#                 Action( 'Start', 0 ),
#                 Action( 'Tower',
#                     [   Tower('Ninja Monkey', [838,698], [4,0,2], 0),
#                         Tower('Ninja Monkey', [838,386], [4,0,2], 0),
#                         Tower('Alchemist', [838,755], [4,0,0], 0),
#                         Tower('Alchemist', [838,322], [4,0,0], 0)
#                     ]
#                 ),
#                 Action( 'WaitSec', 314.3 )
#             ]
#         ),
#         Map('Bloody Puddles', 3,1, Loc.getLoc('Bottom right'),
#             get_hero('None'),
#             [
#                 Action( 'Tower',
#                     [   Tower('Monkey Village', [979,459], [0,0,2], 0),
#                         Tower('Monkey Ace', [1000,556], [2,0,3], 0)
#                     ]
#                 ),
#                 Action( 'Start', 0 ),
#                 Action( 'Tower',
#                     [   Tower('Monkey Ace', [1047,359], [2,0,3], 0),
#                         Tower('Alchemist', [1099,488], [4,0,1], 0),
#                         Tower('Sniper Monkey', [936,340], [2,0,2], 0),
#                         Tower('sell', [979,459], [0,0,0], 0),
#                         Tower('Monkey Village', [979,459], [2,2,0], 0)
#                     ]
#                 ),
#                 Action( 'WaitSec', 283 )
#             ]
#         ),
#         Map('Workshop', 3,2, Loc.getLoc('Top left'),
#             get_hero('None'),
#             [
#                 Action( 'Tower',
#                     [   Tower('Monkey Village', [897,417], [2,0,2], 0),
#                         Tower('Super Monkey', [1004,484], [0,3,2], 0),
#                         Tower('Wizard Monkey', [1015,400], [0,3,2], 0),
#                         Tower('Alchemist', [905,498], [3,0,0], 0)
#                     ]
#                 ),
#                 Action( 'Start', 291 )
#             ]
#         ),
#         Map('Quad', 3,2, Loc.getLoc('Top middle'),
#             get_hero('None'),
#             [
#                 Action( 'Tower',
#                     [   Tower('Monkey Village', [1175,797], [0,0,2], 0),
#                         Tower('Monkey Village', [1294,792], [0,0,2], 0),
#                         Tower('Monkey Ace', [1112,892], [2,0,3], 0),
#                         Tower('Monkey Ace', [1265,890], [2,0,3], 0),
#                         Tower('Monkey Ace', [1193,977], [2,0,3], 0),
#                         Tower('Alchemist', [1307,963], [4,0,1], 0),
#                         Tower('sell', [1175,797], [0,0,0], 0),
#                         Tower('Monkey Village', [1175,797], [0,2,0], 0),
#                         Tower('sell', [1294,792], [0,0,0], 0),
#                         Tower('upgrade', [1175,797], [2,0,0], 0)
#                     ]
#                 ),
#                 Action( 'Start', 303 )
#             ]
#         ),
#         Map('Dark Castle', 3,2, Loc.getLoc('Top right'),
#             get_hero('Captain Churchill'),
#             [
#                 Action( 'Tower',
#                     [   Tower('Monkey Sub', [1084,433], [2,0,4], 0)
#                     ]
#                 ),
#                 Action( 'Start', 0 ),
#                 Action( 'Tower',
#                     [   Tower('Hero', [532,480], [0,0,0], 0),
#                         Tower('Monkey Sub', [1084,367], [2,0,4], 0),
#                         Tower('Ninja Monkey', [489,734], [0,0,0], 0),
#                         Tower('Ninja Monkey', [466,343], [0,0,0], 0),
#                         Tower('Alchemist', [1008,447], [4,0,1], 0)
#                     ]
#                 ),
#                 Action( 'WaitSec', 302 )
#             ]
#         ),
#         Map('Muddy Puddles', 3,2, Loc.getLoc('Bottom left'),
#             get_hero('Captain Churchill'),
#             [
#                 Action( 'Tower',
#                     [   Tower('Monkey Sub', [729,596], [2,0,4], 0)
#                     ]
#                 ),
#                 Action( 'Start', 0 ),
#                 Action( 'Tower',
#                     [   Tower('Hero', [783,208], [0,0,0], 0),
#                         Tower('Ninja Monkey', [416,192], [0,0,0], 0),
#                         Tower('Ninja Monkey', [1104,189], [0,0,0], 0),
#                         Tower('Monkey Sub', [641,647], [2,0,4], 0),
#                         Tower('Alchemist', [615,504], [4,0,2], 0)
#                     ]
#                 ),
#                 Action( 'WaitSec', 277 )
#             ]
#         ),
#         Map('Ouch', 3,2, Loc.getLoc('Bottom middle'),
#             get_hero('Captain Churchill'),
#             [
#                 Action( 'Tower',
#                     [   Tower('Hero', [694,660], [0,0,0], 0),
#                         Tower('Monkey Buccaneer', [847,562], [4,0,2], 0),
#                         Tower('Alchemist', [665,464], [4,0,2], 0),
#                         Tower('Wizard Monkey', [1006,430], [0,2,2], 0),
#                         Tower('Ninja Monkey', [851,767], [2,0,2], 0)
#                     ]
#                 ),
#                 Action( 'Start', 299 ),
#                 Action( 'Ability', '1'),
#                 Action( 'WaitSec', 2)
#             ]
#         )
#     ]
