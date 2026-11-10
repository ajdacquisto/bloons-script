"""Run an image-match check against a reference screenshot."""

from pathlib import Path

from PIL import Image

from Helper import ImageGrabTest as IGT


def locate(src, scn, coordList, radius, threshold, search_mode, rounding):  # pylint: disable=invalid-name
    """Find a template at one of the supplied screenshot coordinates."""
    src_img = Image.open(src)  # Load source image
    screen_img = Image.open(scn)  # Load screenshot

    for coords in coordList:
        match_ratio = IGT.optimize_match_ratio(
            src_img, screen_img, coords, radius, search_mode, rounding, True, True
        )

        if match_ratio > threshold:
            return (True, coords, round(100 * match_ratio, 3))
    return (False, (0, 0), 0)


media_dir = Path(__file__).resolve().parent / "Media"
srcIm = media_dir / "roundStopped.png"
scnIm = media_dir / "reference" / "roundStopped.png"
COORD_LIST = [(1832, 1016)]
SEARCH_RADIUS = 5
MATCH_THRESHOLD = 0.07
SEARCH_MODE = 0
ROUNDING = 1
matchFound, matchCoords, matchPercent = locate(  # pylint: disable=invalid-name
    srcIm, scnIm, COORD_LIST, SEARCH_RADIUS, MATCH_THRESHOLD, SEARCH_MODE, ROUNDING
)
print(matchFound)
print(matchCoords)
print(matchPercent)
