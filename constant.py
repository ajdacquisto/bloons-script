"""Store runtime settings, project paths, and image-match thresholds."""

import os
from pathlib import Path

from Helper.Map import map_setup
from Helper.Page import get_pages


PROJECT_DIR = Path(__file__).resolve().parent
HELPER_DIR = PROJECT_DIR / "Helper"
MEDIA_DIR = PROJECT_DIR / "Media"
MATCHES_FILE = HELPER_DIR / "data.txt"


def set_matches(number_list):
    """Write all image-match thresholds to the data file."""
    new_string = ",".join(str(num) for num in number_list)
    with MATCHES_FILE.open("w") as f:
        f.write(new_string)


def get_matches():
    """Read the stored image-match thresholds."""
    with MATCHES_FILE.open("r") as f:
        contents = f.read()
        contents = contents.split(",")
        for i, s in enumerate(contents):
            contents[i] = float(s)
    return contents


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
    DEFAULT_MAP = "Dark Dungeons"

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
    global MAPS  # List[Map]
    MAPS = map_setup(str(HELPER_DIR / "mapLocations.dat"))

    global PAGES
    PAGES = get_pages(str(HELPER_DIR / "pageInfo.dat"))

    global HERO_DATA
    HERO_DATA = str(HELPER_DIR / "heroes.dat")

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
