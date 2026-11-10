"""Behavior checks for convention-only refactoring."""

import unittest
from pathlib import Path
from unittest.mock import call, patch

from PIL import Image

import Main
from Helper import GUI, ImageGrabTest, KeyboardInput, Location, Map, Page
from Helper.Hero import Hero
from Helper.Tower import Tower


ROOT = Path(__file__).resolve().parent.parent


class ExistingBehaviorTests(unittest.TestCase):
    """Keep legacy keyword arguments and automation behavior intact."""

    def test_map_and_page_data_load_through_legacy_keywords(self):
        """The existing data files and public keyword names still work."""
        maps = Map.map_setup(dataFilePath=str(ROOT / "Helper" / "mapLocations.dat"))
        pages = Page.get_pages(str(ROOT / "Helper" / "pageInfo.dat"))

        self.assertEqual(len(maps), 11)
        self.assertEqual(len(pages), 13)
        self.assertEqual(maps[0].name, "Dark Dungeons")
        strategies = maps[0].strategy
        if not isinstance(strategies, list):
            self.fail("Expected a list of map strategies")
        self.assertEqual(len(strategies), 2)
        self.assertEqual(Page.get_page_by_info(pageList=pages, diff=3, subpage=1), pages[12])
        self.assertEqual(Page.get_dot_coord_list(pageList=pages)[0], (738, 758))

    def test_legacy_location_and_hero_accessors(self):
        """Legacy constructor keywords and accessors remain available."""
        location = Location.Location(name_val="Example", coordsXY=(4, 5))
        hero = Hero(name="Example", bCoords=(1, 2))
        known = Location.getLoc(locName="Top left")

        self.assertEqual((location.getName(), location.getX(), location.getY()), ("Example", 4, 5))
        self.assertEqual(hero.get_coords(), (400, 400))
        self.assertIs(Location.get_loc_from_coords(C=(697, 296)), known)
        self.assertEqual(Location.get_loc_num(inp_L=known), 0)

    def test_legacy_image_matching_keywords(self):
        """Existing keyword names work through the normal image search path."""
        source = Image.new("RGB", (4, 2), "black")
        screen = Image.new("RGB", (8, 6), "white")
        screen.paste(source, (2, 2))

        with (
            patch.object(ImageGrabTest.Image, "open", return_value=source),
            patch.object(ImageGrabTest.ImageGrab, "grab", return_value=screen),
        ):
            result = ImageGrabTest.locate(
                filename="unused.png",
                coordList=[(4, 3)],
                radius=0,
                thresh_list=[0.99],
                search_mode=0,
                rounding=1,
            )

        self.assertEqual(result, (True, (4, 3), 1.0))
        self.assertEqual(
            ImageGrabTest.compare_images(Im1=source, Im2=source, mode=0, rounding=1), 1
        )
        self.assertEqual(
            ImageGrabTest.optimize_match_ratio(
                source,
                screen,
                (4, 3),
                0,
                0,
                1,
                doReporting=False,
                doFileSave=False,
                saveFileName="unused.png",
            ),
            1,
        )

    def test_legacy_keyboard_keywords_do_not_send_real_input(self):
        """Both legacy key helpers keep their keyword argument."""
        with patch.object(KeyboardInput.ctypes.windll.user32, "SendInput") as send_input:
            KeyboardInput.PressKey(hexKeyCode=0x10)
            KeyboardInput.ReleaseKey(hexKeyCode=0x10)

        self.assertEqual(send_input.call_count, 2)

    def test_gui_legacy_keywords(self):
        """GUI entry points retain their established keyword names."""
        hero = Hero("Example", (1, 2))
        with (
            patch.object(GUI, "wait_click") as wait_click,
            patch.object(GUI, "hero_change_button"),
            patch.object(GUI, "hero_select_button"),
            patch.object(GUI, "back_arrow_button"),
        ):
            GUI.play_button(waitTime=0)
            GUI.select_hero(H=hero)

        self.assertEqual(wait_click.call_args_list, [call(0, 833, 936), call(0.5, 400, 400)])

    def test_map_navigation_wraps_within_difficulty(self):
        """Moving from the last subpage to the first takes one click."""
        current = Page.Page(3, 0, 3, (849, 758))
        target = Page.Page(0, 0, 0, (738, 758))
        with (
            patch.object(Main, "identify_current_page", return_value=current),
            patch.object(GUI, "page_button") as page_button,
        ):
            self.assertIs(Main.navigate(target), target)

        page_button.assert_called_once_with(0)

    def test_tower_upgrade_keys_keep_their_order(self):
        """Upgrades and targeting changes are issued in their original order."""
        tower = Tower("Dart Monkey", (100, 200), [2, 1, 1], 2)
        with (
            patch.object(GUI, "place_tower") as place_tower,
            patch.object(GUI, "select_tower") as select_tower,
            patch.object(GUI, "wait"),
            patch.object(GUI, "key_push") as key_push,
            patch.object(GUI, "deselect") as deselect,
        ):
            Main.do_tower_action(tower)

        place_tower.assert_called_once_with(tower)
        select_tower.assert_called_once_with(tower)
        self.assertEqual(
            key_push.call_args_list,
            [call(","), call(","), call("."), call("/"), call("tab"), call("tab")],
        )
        deselect.assert_called_once_with()
        self.assertEqual(tower.delayTime, 0)


if __name__ == "__main__":
    unittest.main()
