from pathlib import Path

from PIL import Image
from Helper import ImageGrabTest as IGT
from Helper import Location

media_dir = Path(__file__).resolve().parent / "Media"

def locate(src, scn, coordList, radius, threshold, search_mode, rounding, filenameForSaving):

    src_img = Image.open(src) # Load source image
    screen_img = Image.open(scn) # Take a screenshot

    for C in coordList:
        match_ratio = IGT.optimize_match_ratio(src_img, screen_img, C, radius, search_mode, rounding, True, True, filenameForSaving)

        if match_ratio > threshold:
            return ( True, C, round(100 * match_ratio, 3) )
    return ( False, (0,0), 0 )


print('\nEnter the filepath for a screenshot of map selection screen containing the icon.')
print(f'Ex: {media_dir / "screenshot.png"}')
input_filename = input('Path: ')

print('\nIn the screenshot, what location is the icon in?')
print('Ex: Top right')
input_locname = input('Location: ')

location1 = Location.getLoc(input_locname)
if location1 is None: raise Exception("Bad location name.")
location_coords = ( location1.getX(), location1.getY() )
COORD_LIST = [ location_coords ]

print('\nEnter the filepath for the icon to be saved as.')
print(f'Ex: {media_dir / "newIcon.png"}')
input_savefile = input('Path: ')

arbitrary_image = media_dir / "totemBadgeSmall.png"

matchFound, matchCoords, matchPercent = locate(arbitrary_image, input_filename, COORD_LIST,
                                                       0, 0.07, 0, 1, input_savefile)