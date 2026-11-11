"""Store runtime settings, project paths, and image-match thresholds."""

import os
from pathlib import Path

from Helper.Map import Map, map_setup
from Helper.Hero import get_heroes
from Helper.Page import get_pages
from Helper.UICalibration import UI_CLICKS, UI_TARGETS as UI_TARGETS
from Helper.UICalibration import HERO_SELECTED_OFFSET as HERO_SELECTED_OFFSET


PROJECT_DIR = Path(__file__).resolve().parent
HELPER_DIR = PROJECT_DIR / "Helper"
MEDIA_DIR = PROJECT_DIR / "Media"
MATCHES_FILE = HELPER_DIR / "data.txt"
# Compatibility alias; edit the shared calibration rather than this value.
HOME_PLAY_COORDS: tuple[int, int] = UI_CLICKS["home_play"]
LOG_LEVEL = "INFO"
STOP_KEY = "f12"
VISION_POLL_INTERVAL = 0.2
VISION_LOG_INTERVAL = 3.0

# Desktop position of the game display's top-left corner; monitor 2: (-1920, 290).
GAME_SCREEN_ORIGIN: tuple[int, int] = (-1920, 290)


def get_desktop_coords(x: int, y: int) -> tuple[int, int]:
    """Translate game-local coordinates to desktop coordinates."""
    origin_x, origin_y = GAME_SCREEN_ORIGIN
    return x + origin_x, y + origin_y


def set_matches(number_list):
    """Write all image-match thresholds to the data file."""
    new_string = ",".join(str(num) for num in number_list)
    with MATCHES_FILE.open("w") as f:
        f.write(new_string)


def get_matches() -> list[float]:
    """Read the stored image-match thresholds."""
    with MATCHES_FILE.open("r") as f:
        return [float(value) for value in f.read().split(",")]


def set_match(i, j, do_reporting=False):
    """Update one stored match threshold, optionally reporting the change."""
    j = round(j - 0.0001, 4)
    this_list = get_matches()
    if do_reporting:
        print(f"constant.set_match: Updating D[{i}] {this_list[i]} -> {j}")
    this_list[i] = j
    set_matches(this_list)


def get_match(i):
    """Return one stored match threshold."""
    this_list = get_matches()
    return this_list[i]


def init():
    """Initialize runtime settings and load map and page data."""
    # Settings
    # ---

    global MAP_SELECTION_MODE
    MAP_SELECTION_MODE = 1
    # selection mode:
    #   0 - only default map, on repeat
    #   1 - chooses a random map
    #   2 - plays maps in order
    #   3 - does candy search & if none, mode 0
    #   4 - does candy search & if none, mode 2
    #   5 - does candy search & if none, calibrates expansively

    global DEFAULT_MAP
    DEFAULT_MAP = "Muddy Puddles"

    global DEFAULT_MODE
    DEFAULT_MODE = "Deflation"

    global MAP_LOADING_TIME
    MAP_LOADING_TIME = 0

    global POST_WIN_WAIT
    POST_WIN_WAIT = 0

    global MAP_LOADING_TIMEOUT_DEFLATION
    MAP_LOADING_TIMEOUT_DEFLATION = 30

    # Filename stuff
    # ---
    global HERO_DATA
    HERO_DATA = str(HELPER_DIR / "heroes.dat")
    Map.HEROES = get_heroes(HERO_DATA)

    global MAPS  # List[Map]
    MAPS = map_setup(str(HELPER_DIR / "mapLocations.dat"))

    global PAGES
    PAGES = get_pages(str(HELPER_DIR / "pageInfo.dat"))

    global FILE_PREFIX
    FILE_PREFIX = str(MEDIA_DIR) + os.sep

    global BADGE_NAME
    BADGE_NAME = "cakeBadge.png"

    # Miscellaneous stuff
    # ---
    global MIN_MATCHES
    MIN_MATCHES = get_matches()

    global AUTO_START
    AUTO_START = -1
