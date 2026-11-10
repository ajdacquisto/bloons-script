"""Represent pages and controls on the map-selection screen."""

from typing import Tuple, List


class Page:
    """Describe one map-selection page and its navigation coordinates."""

    def __init__(
        self, number: int, diff: int, subpage: int, dot_coords: Tuple[int, int]
    ):
        self.number = number
        self.difficulty = diff
        self.subset_num = subpage
        self.dot_coords = dot_coords
        self.button_coords = get_button_coords(dot_coords)

    def __str__(self) -> str:
        ps = "Page #" + str(self.number)
        ps += ": diff=" + str(self.difficulty)
        ps += ", subP=" + str(self.subset_num)
        ps += ", dotC=(" + str(self.dot_coords[0]) + "," + str(self.dot_coords[1]) + ")"
        return ps

    def __eq__(p1, p2) -> bool:
        return p1.number == p2.number

    def get_number(self) -> int:
        """Return the page number."""
        return self.number

    def get_difficulty(self) -> int:
        """Return the map difficulty represented by this page."""
        return self.difficulty

    def get_subpage(self) -> int:
        """Return the page index within its difficulty."""
        return self.subset_num

    def get_dot_coords(self) -> Tuple[int, int]:
        """Return the page indicator coordinates."""
        return self.dot_coords

    def get_button_coords(self) -> Tuple[int, int]:
        """Return the stored difficulty-button coordinates."""
        return self.button_coords


def get_pages(filename: str) -> List[Page]:
    """Load page definitions from a comma-separated data file."""
    with open(filename, "r") as f:
        line = f.readline()
        list_of_pages = []
        while line:
            if line[0] != "#":
                # Ignore final newline character:
                if line[-1] == "\n":
                    line = line[:-1]

                # Create a list from comma separated items
                line_list = line.split(",")

                p_number = int(line_list[0])
                p_difficulty = int(line_list[1])
                p_subpage = int(line_list[2])
                p_dot_x = int(line_list[3])
                p_dot_y = int(line_list[4])

                p_dot_coords = (p_dot_x, p_dot_y)

                p = Page(p_number, p_difficulty, p_subpage, p_dot_coords)

                # Append the list
                list_of_pages.append(p)

            line = f.readline()
    return list_of_pages


def get_page_by_info(pageList: List[Page], diff: int, subpage: int) -> Page:  # pylint: disable=invalid-name
    """Find a page by difficulty and subpage, or return None."""
    try:
        if diff != int(diff):
            raise TypeError()
    except:
        raise TypeError("Bad getPage input.")

    for p in pageList:
        if p.difficulty == diff and p.subset_num == subpage:
            return p

    print(f"> get_page_by_info(diff={diff}, subpage={subpage}) -> None")

    return None


def get_next_in_diff(p: Page) -> Page:
    """Find the next subpage within the current difficulty."""
    page_count = get_num_subpages(p.difficulty)
    subpage = p.subset_num

    last_subpage = page_count - 1

    if subpage < 0:
        raise RuntimeError("get_next_in_diff: Negative current subpage number")
    if subpage + 1 <= last_subpage:
        new_subpage = subpage + 1
    elif subpage + 1 > last_subpage:
        new_subpage = 0

    return get_page_by_info(p.difficulty, new_subpage)


def get_num_subpages(diff: int) -> int:
    """Return the number of subpages for a map difficulty."""
    if diff == 0:
        return 4
    elif diff == 1:
        return 4
    elif diff == 2:
        return 3
    elif diff == 3:
        return 2
    else:
        raise ValueError("get_num_subpages: Invalid difficulty")


def get_button_coords(diff: int) -> Tuple[int, int]:
    """Return the difficulty tab's screen coordinates."""
    match diff:
        case 0:
            return (582, 977)
        case 1:
            return (834, 977)
        case 2:
            return (1086, 977)
        case 3:
            return (1338, 977)


def get_dot_coord_list(pageList: List[Page]) -> Tuple[int, int]:  # pylint: disable=invalid-name
    """Return the screen coordinates of the supplied page indicators."""
    c_list = []
    for p in pageList:
        c_list.append(p.dot_coords)
    return c_list


# PAGES = [
#     Page(0 ,0    , 0, (738, 758) ),
#     Page(1 ,0    , 1, (775, 758) ),
#     Page(2 ,0    , 2, (812, 758) ),
#     Page(3 ,0    , 3, (849, 758) ),
#     Page(4 ,1, 0, (886, 758) ),
#     Page(5 ,1, 1, (923, 758) ),
#     Page(6 ,1, 2, (960, 758) ),
#     Page(7 ,1, 3, (997, 758) ),
#     Page(8 ,2    , 0, (1034, 758)),
#     Page(9,2     , 1, (1071, 758)),
#     Page(10,2    , 2, (1108, 758)),
#     Page(11,3      , 0, (1145, 758)),
#     Page(12,3      , 1, (1182, 758))
# ]
