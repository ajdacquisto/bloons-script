"""Behavior checks for convention-only refactoring."""

import unittest
from pathlib import Path
from unittest.mock import call, patch

from PIL import Image

import Main
from Helper import GUI, ImageGrabTest, KeyboardInput, Location, Map, Page
from Helper.Action import Action
from Helper.Hero import Hero
from Helper.Tower import Tower


ROOT = Path(__file__).resolve().parent.parent


class ExistingBehaviorTests(unittest.TestCase):
    """Keep legacy keyword arguments and automation behavior intact."""

    def test_model_equality_rules(self):
        """Action, hero, location, and page comparisons keep their existing rules."""
        self.assertEqual(Action("WaitSec", 1), Action("WaitSec", 1))
        self.assertNotEqual(Action("WaitSec", 1), Action("WaitSec", 2))
        self.assertEqual(Hero("Quincy", (0, 0)), Hero("Quincy", (1, 1)))
        self.assertNotEqual(Hero("Quincy", (0, 0)), Hero("Psi", (0, 0)))
        self.assertEqual(Location.Location("A", (1, 2)), Location.Location("A", (1, 2)))
        self.assertNotEqual(Location.Location("A", (1, 2)), Location.Location("A", (2, 1)))
        self.assertEqual(Page.Page(1, 0, 0, (0, 0)), Page.Page(1, 3, 1, (1, 1)))
        self.assertNotEqual(Page.Page(1, 0, 0, (0, 0)), Page.Page(2, 0, 0, (0, 0)))

    def test_map_and_page_data_load_through_legacy_keywords(self):
        """The existing data files and public keyword names still work."""
        maps = Map.map_setup(dataFilePath=str(ROOT / "Helper" / "mapLocations.dat"))
        pages = Page.get_pages(str(ROOT / "Helper" / "pageInfo.dat"))

        self.assertEqual(len(maps), 13)
        self.assertEqual(len(pages), 17)
        self.assertEqual(maps[0].name, "Tricky Tracks")
        strategies = Map.get_map_by_name(maps, "Dark Dungeons").strategy
        if not isinstance(strategies, list):
            self.fail("Expected a list of map strategies")
        self.assertEqual(len(strategies), 2)
        self.assertEqual(Page.get_page_by_info(pageList=pages, diff=3, subpage=1), pages[15])
        self.assertEqual(Page.get_dot_coord_list(pageList=pages)[0], (664, 758))
        for m in maps:
            page = pages[m.page]
            self.assertEqual((page.difficulty, page.subset_num), (m.difficulty, m.subpage))

    def test_home_screen_wait_preserves_cancellation(self):
        """Stopping at startup is not misreported as a detection timeout."""
        with (
            patch.object(Main.const, "init"),
            patch.object(Main.const, "MAPS", [], create=True),
            patch.object(Main.const, "POST_WIN_WAIT", 0, create=True),
            patch.object(Main.const, "MAP_LOADING_TIME", 0, create=True),
            patch.object(Main.const, "DEFAULT_MAP", "Tricky Tracks", create=True),
            patch.object(Main.const, "DEFAULT_MODE", "Deflation", create=True),
            patch.object(Main.const, "MAP_SELECTION_MODE", 0, create=True),
            patch.object(Main.const, "FILE_PREFIX", "", create=True),
            patch.object(GUI, "check_input_vars"),
            patch.object(GUI, "wait_click"),
            patch.object(Main, "wait_for_badge", side_effect=SystemExit),
        ):
            with self.assertRaises(SystemExit):
                Main.main()

    def test_subpage_counts_follow_loaded_data(self):
        """Counts follow the data, including future pages above subpage three."""
        pages = Page.get_pages(str(ROOT / "Helper" / "pageInfo.dat"))
        self.assertEqual([Page.get_num_subpages(pages, diff) for diff in range(4)],
                         [5, 5, 4, 3])
        pages.append(Page.Page(17, 0, 5, (0, 0)))
        self.assertEqual(Page.get_num_subpages(pages, 0), 6)
        for page_list, diff in ((pages, -1), (pages, 4), ([], 0)):
            with self.subTest(diff=diff, count=len(page_list)):
                with self.assertRaises(ValueError):
                    Page.get_num_subpages(page_list, diff)

    def test_next_subpage_advances_and_wraps(self):
        """Every difficulty cycles through all of its configured pages."""
        pages = Page.get_pages(str(ROOT / "Helper" / "pageInfo.dat"))
        for diff in range(4):
            section = [p for p in pages if p.difficulty == diff]
            for index, current in enumerate(section):
                with self.subTest(diff=diff, subpage=index):
                    self.assertIs(Page.get_next_in_diff(pages, current),
                                  section[(index + 1) % len(section)])
        with self.assertRaisesRegex(RuntimeError, "Invalid current subpage"):
            Page.get_next_in_diff(pages, Page.Page(99, 0, -1, (0, 0)))

    def test_random_maps_require_strategies(self):
        """Every random index selects a map with a nonempty strategy list."""
        maps = Map.map_setup(str(ROOT / "Helper" / "mapLocations.dat"))
        playable = [m for m in maps if m.strategy]
        self.assertEqual(len(playable), 12)
        for index, expected in enumerate(playable):
            with self.subTest(index=index):
                with patch.object(Map, "randint", return_value=index) as randint:
                    self.assertIs(Map.pick_rand(maps), expected)
                randint.assert_called_once_with(0, len(playable) - 1)

        unsupported = [m for m in maps if not m.strategy]
        for candidates in ([], unsupported):
            with self.subTest(count=len(candidates)):
                with self.assertRaisesRegex(ValueError, "No maps have a defined strategy"):
                    Map.pick_rand(candidates)
        with patch.object(unsupported[0], "strategy", []):
            with self.assertRaisesRegex(ValueError, "No maps have a defined strategy"):
                Map.pick_rand([unsupported[0]])

    def test_tricky_tracks_coordinates_are_monitor_relative(self):
        """Recorded desktop positions are translated from the capture monitor."""
        maps = Map.map_setup(str(ROOT / "Helper" / "mapLocations.dat"))
        tricky_tracks = Map.get_map_by_name(maps, "Tricky Tracks")
        strategies = tricky_tracks.strategy
        if not isinstance(strategies, list):
            self.fail("Expected Tricky Tracks strategies")
        self.assertEqual(len(strategies), 1)
        strategy = strategies[0]
        self.assertEqual(strategy.get_game_mode(), "Deflation")
        recorded_positions = [
            (-1133, 970), (-1226, 1078), (-1000, 911), (-1216, 1004),
            (-965, 838), (-1133, 970), (-1133, 970),
        ]
        towers = [
            tower for action in strategy.get_actions()
            if action.get_name() == "Tower" for tower in action.get_info()
        ]
        self.assertEqual(
            [tower.get_position() for tower in towers],
            [[x + 1920, y - 290] for x, y in recorded_positions],
        )

    def test_workshop_stacks_discounts_before_selling_second_village(self):
        """Preserve the translated coordinates and exact purchase/sell order."""
        maps = Map.map_setup(str(ROOT / "Helper" / "mapLocations.dat"))
        workshop = Map.get_map_by_name(maps, "Workshop")
        strategies = workshop.strategy
        if not isinstance(strategies, list):
            self.fail("Expected Workshop strategies")
        self.assertEqual(len(strategies), 1)
        strategy = strategies[0]
        self.assertEqual(strategy.get_game_mode(), "Deflation")
        actions = strategy.get_actions()
        self.assertEqual([action.get_name() for action in actions], ["Tower", "Start"])
        self.assertEqual(
            [(tower.name, tower.get_position(), tower.get_upgrades(), tower.targeting)
             for tower in actions[0].get_info()],
            [
                ("Monkey Village", [894, 418], [0, 0, 2], 0),
                ("Monkey Village", [777, 454], [0, 0, 2], 0),
                ("Super Monkey", [1003, 485], [0, 3, 1], 0),
                ("Wizard Monkey", [1004, 397], [0, 3, 0], 0),
                ("Alchemist", [902, 497], [3, 0, 1], 0),
                ("upgrade", [894, 418], [0, 1, 0], 0),
                ("sell", [777, 454], [0, 0, 0], 0),
                ("upgrade", [894, 418], [0, 1, 0], 0),
            ],
        )
        self.assertEqual(actions[1].get_info(), 291)

    def test_ouch_uses_the_validated_alchemist_setup(self):
        """Keep all five tower positions and the calibrated upgrade order."""
        maps = Map.map_setup(str(ROOT / "Helper" / "mapLocations.dat"))
        ouch = Map.get_map_by_name(maps, "Ouch")
        strategies = ouch.strategy
        if not isinstance(strategies, list):
            self.fail("Expected Ouch strategies")
        self.assertEqual(len(strategies), 1)
        strategy = strategies[0]
        self.assertEqual(strategy.get_game_mode(), "Deflation")
        self.assertEqual(strategy.get_hero().get_name(), "Captain Churchill")
        actions = strategy.get_actions()
        self.assertEqual(
            [action.get_name() for action in actions],
            ["Tower", "Start", "Ability", "WaitSec"],
        )
        self.assertEqual(
            [(tower.name, tower.get_position(), tower.get_upgrades(), tower.targeting)
             for tower in actions[0].get_info()],
            [
                ("Hero", [694, 660], [0, 0, 0], 0),
                ("Monkey Buccaneer", [847, 562], [4, 0, 2], 0),
                ("Alchemist", [764, 778], [3, 0, 2], 0),
                ("Wizard Monkey", [1006, 430], [0, 2, 2], 0),
                ("Ninja Monkey", [851, 767], [2, 0, 2], 0),
            ],
        )
        self.assertEqual([action.get_info() for action in actions[1:]], [299, "1", 2])

    def test_reward_search_visits_all_expert_subpages(self):
        """A search without a match scans and cycles through all expert pages."""
        pages = Page.get_pages(str(ROOT / "Helper" / "pageInfo.dat"))
        maps = Map.map_setup(str(ROOT / "Helper" / "mapLocations.dat"))
        with (
            patch.object(Main.const, "PAGES", pages, create=True),
            patch.object(Main.const, "MAPS", maps, create=True),
            patch.object(Main.const, "FILE_PREFIX", "", create=True),
            patch.object(Main.const, "get_matches", return_value=[0.5] * 6),
            patch.object(Main, "navigate", side_effect=lambda page: page) as navigate,
            patch.object(Main, "wait_for_badge"),
            patch.object(GUI, "wait"),
            patch.object(Main, "locate", return_value=(False, (0, 0), 0)) as locate,
        ):
            self.assertIsNone(Main.find_rewards_map(3, "unused.png"))
        self.assertEqual(locate.call_count, 3)
        self.assertEqual([args.args[0].number for args in navigate.call_args_list],
                         [15, 16, 14, 15])

    def test_legacy_location_and_hero_accessors(self):
        """Legacy constructor keywords and accessors remain available."""
        location = Location.Location(name_val="Example", coordsXY=(4, 5))
        hero = Hero(name="Example", bCoords=(1, 2))
        known = Location.getLoc(locName="Top left")

        self.assertEqual((location.getName(), location.getX(), location.getY()), ("Example", 4, 5))
        self.assertEqual(hero.get_card_position(last_row=5), ("top", (405, 414)))
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
        with patch.object(GUI, "wait_click") as wait_click:
            GUI.play_button(waitTime=0)

        self.assertEqual(wait_click.call_args_list, [call(0, 960, 945)])

    def test_validate_map_settings(self):
        """Valid settings pass while invalid waits are rejected."""
        maps = Map.map_setup(dataFilePath=str(ROOT / "Helper" / "mapLocations.dat"))
        GUI.check_input_vars(maps, [0, 0, "Dark Dungeons", 1])

        with self.assertRaisesRegex(ValueError, "Post-Win Wait"):
            GUI.check_input_vars(maps, [-1, 0, "Dark Dungeons", 1])

    def test_identify_current_page(self):
        """The page indicator is matched against the configured coordinates."""
        pages = Page.get_pages(str(ROOT / "Helper" / "pageInfo.dat"))
        with (
            patch.object(Main.const, "PAGES", pages, create=True),
            patch.object(Main.const, "FILE_PREFIX", "", create=True),
            patch.object(Main, "locate", return_value=(True, pages[11].dot_coords, 1)) as locate,
        ):
            self.assertIs(Main.identify_current_page(), pages[11])

        locate.assert_called_once_with(
            "mapDot.png", Page.get_dot_coord_list(pages), 1, [0.85], 0, 1
        )

    def test_wait_for_badge_uses_legacy_coordinate_keyword(self):
        """Badge alternatives retain their order and the legacy keyword."""
        results = [(False, (0, 0), 0), (True, (3, 4), 1)]
        with (
            patch.object(GUI, "exit_key_check"),
            patch.object(Main, "locate", side_effect=results) as locate,
        ):
            result = Main.wait_for_badge_2(
                filenames=["first", "second"],
                coordMx=[[(1, 2)], [(3, 4)]],
                timeout=1,
                match_threshold=[0.5],
            )

        self.assertEqual(result, 1)
        self.assertEqual(
            locate.call_args_list,
            [
                call("first", [(1, 2)], 0, [0.5], 0, 1),
                call("second", [(3, 4)], 0, [0.5], 0, 1),
            ],
        )

    def test_auto_start_state_toggles(self):
        """The cached auto-start state still alternates between off and on."""
        with patch.object(Main.const, "AUTO_START", 0, create=True):
            Main.toggle_auto_start()
            self.assertEqual(Main.const.AUTO_START, 1)
            Main.toggle_auto_start()
            self.assertEqual(Main.const.AUTO_START, 0)

    def test_auto_start_templates_distinguish_both_states(self):
        """Current switch templates detect ON and OFF without confusing them."""
        for state, name in ((0, "auto_start_off"), (1, "auto_start_on")):
            with self.subTest(state=state):
                target = Main.const.UI_TARGETS[name]
                with Image.open(ROOT / "Media" / target.filename) as template:
                    screen = Image.new("RGB", (1920, 1080))
                    x = target.coords[0] - template.width // 2
                    y = target.coords[1] - template.height // 2
                    screen.paste(template, (x, y))
                with (
                    patch.object(Main.const, "FILE_PREFIX", str(ROOT / "Media") + "\\",
                                 create=True),
                    patch.object(ImageGrabTest.ImageGrab, "grab", return_value=screen),
                ):
                    self.assertEqual(Main.check_auto_start(), state)

    def test_auto_start_check_preserves_cancellation(self):
        """Stop-key cancellation propagates through auto-start detection."""
        with (
            patch.object(Main.const, "FILE_PREFIX", "", create=True),
            patch.object(Main, "wait_for_badge_2", side_effect=SystemExit),
        ):
            with self.assertRaises(SystemExit):
                Main.check_auto_start()

    def test_auto_start_adjustment_opens_and_closes_pause(self):
        """Deflation needs ON; Standard needs OFF; only mismatched states toggle."""
        for mode, target in (("Deflation", 1), ("Standard", 0)):
            for current in (0, 1):
                with (
                    self.subTest(mode=mode, current=current),
                    patch.object(Main.const, "AUTO_START", -1, create=True),
                    patch.object(Main, "check_auto_start", return_value=current),
                    patch.object(GUI, "key_push") as key_push,
                    patch.object(GUI, "auto_start_toggle_switch") as toggle,
                ):
                    Main.adjust_auto_start_smart(mode)
                    self.assertEqual(Main.const.AUTO_START, target)
                    self.assertEqual(key_push.call_args_list, [call("esc"), call("esc")])
                    self.assertEqual(toggle.call_count, int(current != target))

    def test_map_navigation_wraps_within_difficulty(self):
        """Moving from the last subpage to the first takes one click."""
        pages = Page.get_pages(str(ROOT / "Helper" / "pageInfo.dat"))
        for diff in range(4):
            section = [p for p in pages if p.difficulty == diff]
            with (
                self.subTest(diff=diff),
                patch.object(Main.const, "PAGES", pages, create=True),
                patch.object(Main, "identify_current_page", return_value=section[-1]),
                patch.object(GUI, "page_button") as page_button,
            ):
                self.assertIs(Main.navigate(section[0]), section[0])
                page_button.assert_called_once_with(diff)

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
