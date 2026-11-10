"""Compare screen captures with image templates."""

from pathlib import Path

from PIL import ImageGrab, Image, ImageChops
from numpy import asarray


def image_to_arr(im):
    """Convert a Pillow image to a NumPy array."""
    return asarray(im)


def arr_to_image(ar):
    """Convert a NumPy array to a Pillow image."""
    return Image.fromarray(ar)


def display(im):
    """Display an image using the system image viewer."""
    im.show()


# ..............................................................................
def locate(
    filename,
    coordList,  # pylint: disable=invalid-name
    radius,
    thresh_list,
    search_mode,
    rounding,
    debug_mode=False,
):
    """
    Find the best template match at the supplied screen locations.

    :param filename: (String) source image to locate
    :param coordList: [(x,y),(x,y),...] screen locations to check
    :param radius: (Int) search radius. Default = 0
    :param thresh_list: [0.08, 0.06, ...] How close does match have to be? Default = 0.08
    :param search_mode: (0 or 1) [See ImageGrabTest.compare_images()] Default = 0
    :param rounding: (Int, 1 to 256) [See ImageGrabTest.compare_images()] Default = 1
    :return: Triplet.
        1) (bool) Match found or not.
        2) (x,y) Match coords. From given coordList.
        3) (0<x<1) Match ratio. [See ImageGrabTest.compare_images()]
    """

    if len(thresh_list) != 1 and len(thresh_list) != len(coordList):
        raise Exception("ImageGrabTest.locate: Invalid len(thresh_list)")
    if len(coordList) < 1:
        raise ValueError("ImageGrabTest.locate: Invalid len(coordList)")
    if len(thresh_list) != len(coordList):
        n = len(coordList)
        thresh_list = thresh_list * n

    src_img = Image.open(filename)  # Load source image
    screen_img = ImageGrab.grab()  # Take a screenshot

    best_info = (-1, False, (0, 0), 0)
    # index, meetsReqt, coords, ratio

    for i, (coords, threshold) in enumerate(zip(coordList, thresh_list)):
        match_ratio = optimize_match_ratio(
            src_img, screen_img, coords, radius, search_mode, rounding
        )

        # Define match as 'found' if the matchRatio exceeds the threshold.
        match_found = match_ratio > threshold

        if match_ratio > best_info[3]:
            best_info = (i, match_found, coords, match_ratio)

        if debug_mode:
            match_percent = round(100 * match_ratio, 1)
            if match_percent == 0:
                print(f"~ [{coords[0]} {coords[1]}] No match.")
            elif match_found:
                print(
                    f"~ [{coords[0]} {coords[1]}] {match_percent}% match. "
                    f"Exceeds threshold {threshold}."
                )
            else:
                print(
                    f"~ [{coords[0]} {coords[1]}] {match_percent}% match. "
                    f"Does not exceed threshold {threshold}."
                )

    if best_info[1]:
        return (True, best_info[2], best_info[3])
    return (False, best_info[2], best_info[3])


def to_hex_chain(rgb):
    """Convert an RGB triplet to a six-character hexadecimal string."""
    r = to_hex_special(rgb[0])
    g = to_hex_special(rgb[1])
    b = to_hex_special(rgb[2])
    return r[2:] + g[2:] + b[2:]


def to_hex_special(num):
    """Format one channel as a two-digit hexadecimal value."""
    s = hex(num)
    if num < 16:
        s = s[:2] + "0" + s[2:]
    return s


def optimize_match_ratio(
    src_img,
    screen_img,
    search_coords,
    search_radius,
    search_mode,
    rounding,
    doReporting=False,  # pylint: disable=invalid-name
    doFileSave=False,  # pylint: disable=invalid-name
    saveFileName="",  # pylint: disable=invalid-name
):
    """Return the best match ratio within a radius around the search coordinates."""
    # First, convert both images to the correct format
    src_img = src_img.convert("RGB")
    screen_img = screen_img.convert("RGB")

    width = src_img.width
    height = src_img.height

    if (search_radius < 0) or (search_radius != search_radius // 1):
        raise ValueError("optimize_match_ratio: Invalid search radius.")

    if search_radius > min(screen_img.width // 2, screen_img.height // 2):
        raise ValueError("optimize_match_ratio: Search radius is too large.")

    center_x = search_coords[0]
    center_y = search_coords[1]

    x_left = center_x - width // 2
    y_top = center_y - height // 2

    x_left_first = x_left - search_radius
    x_left_last = x_left + search_radius

    y_top_first = y_top - search_radius
    y_top_last = y_top + search_radius

    total = 0
    max_ratio = 0
    max_coords = (0, 0)
    best_img = None

    predicted_total = (x_left_last - x_left_first + 1) * (y_top_last - y_top_first + 1)

    for x1 in range(x_left_first, x_left_last + 1):
        for y1 in range(y_top_first, y_top_last + 1):
            total += 1
            x2 = x1 + width
            y2 = y1 + height
            screen_img_cropped = screen_img.crop((x1, y1, x2, y2))
            new_ratio = compare_images(
                screen_img_cropped, src_img, search_mode, rounding
            )

            if doReporting:
                print(
                    f"[{round(100 * (total / predicted_total), 1)}% done] "
                    f"at ({round(x1 + width / 2, 0)},{round(y1 + height / 2, 0)}) "
                    f"with {round(100 * new_ratio, 1)}% match; "
                    f"best is ({round(max_coords[0] + width / 2, 0)},"
                    f"{round(max_coords[1] + height / 2, 0)}) "
                    f"with {round(100 * max_ratio, 1)}% match"
                )

            if new_ratio > max_ratio:
                max_ratio = new_ratio
                best_img = screen_img_cropped
                max_coords = (x1, y1)

    if doReporting:
        try:
            display(best_img)  #
            if saveFileName == "":
                saveFileName = (
                    Path(__file__).resolve().parent.parent
                    / "Media"
                    / "reference"
                    / "test.png"
                )
            if doFileSave:
                best_img.save(saveFileName)
        except:
            print("not found.")

    return max_ratio


def compare_images(Im1, Im2, mode, rounding):  # pylint: disable=invalid-name
    """
    compare_images will compare each pixel of the two images, returning a
    decimal in [0,1] where 0 is a 0% match and 1 is a 100% match.

    :param Im1: Image number one
    :param Im2: Image number two
    :param mode: changes how comparison is performed. 0 uses conversion to
        array and rounding. 1 uses image subtraction and black percent.
    :param args: for mode 1, only one argument & it is rounding_factor
    :return: a decimal between 0 and 1, inclusive.  1=100% match. 0=0% match.
    """
    match mode:
        case 0:
            # Use image to array and comparison
            array1 = image_to_arr(Im1)
            array2 = image_to_arr(Im2)
            return get_arr_match_ratio(array1, array2, rounding)
        case 1:
            # Use image difference and black percent
            img_difference = ImageChops.difference(Im1, Im2)
            black_check_mode = 0
            return compute_black_ratio(img_difference, black_check_mode, rounding)
        case _:
            raise ValueError("compare_images: Invalid comparison mode.")


def get_arr_match_ratio(A1, A2, rndg):  # pylint: disable=invalid-name
    """
    get_match_ratio takes two arrays and determines how many matching cells
    they have. A higher rounding value will result in close-but-not-exact
    values counting towards the total. Each cell value in the arrays should be
    a triplet representing an RGB value.

    :param A1: n x m x 3 array
    :param A2: n x m x 3 array
    :param rndg: Integer to divide by. 1=no rounding. 256=fully rounded.
    :return: a decimal between 0 and 1, inclusive. 1=100% match. 0=0% match.
    """
    width = len(A1[0, :])
    height = len(A1[:, 0])
    w2 = len(A2[0, :])
    h2 = len(A2[:, 0])

    if width != w2 or height != h2:
        raise RuntimeError("get_match_ratio: Array sizes don't match.")

    total = 0
    matches = 0
    for a in range(height):
        for b in range(width):
            if compare_triplets(A1[a, b], A2[a, b], rndg):
                matches += 1
            total += 1

    return matches / total


def compare_triplets(t1, t2, rndg):
    """Compare two color triplets after applying the rounding factor."""
    # returns true or false
    if len(t1) != len(t2):
        raise RuntimeError("compare_triplets: Triplet sizes don't match.")

    for first, second in zip(t1, t2):
        if (first // rndg) != (second // rndg):
            return False
    return True


def compute_black_ratio(im, mode, rounding):
    """Return the fraction of pixels considered black."""
    rgb_arr = image_to_arr(im)
    black_count = 0
    total = 0
    for a in range(len(rgb_arr)):
        for b in range(len(rgb_arr[0])):
            if is_black(rgb_arr[a, b], mode, rounding):
                black_count += 1
            total += 1

    return black_count / total


def is_black(rgb, mode, rounding):
    """
    is_black determines whether an RGB triplet represents black or not.

    :param rgb: triplet of integers. Represents red, green, blue values.
    :param mode: Integer uses rounding & individual comparison for mode 0. Use
        hex values and string comparison for mode 1.
    :param args: For mode 1, args[0] is the rounding factor.
    :return: Boolean
    """
    match mode:
        case 0:
            # Compare each value to 0
            for channel in rgb:
                if channel // rounding != 0:
                    return False
            return True
        case 1:
            # Use hexChain
            return to_hex_chain(rgb) == "000000"
        case _:
            raise ValueError("isBlack: Invalid comparison mode.")


# ..............................................................................
