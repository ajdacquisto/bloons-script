"""Verify automatic selection never chooses a map without a strategy."""

import unittest
from unittest.mock import DEFAULT, mock_open, patch

import Main
import constant as const
from Helper import GUI, Location, Map, Page


class MapSelectionTests(unittest.TestCase):
    """Keep ordered and reward-based selection on playable maps."""

    def setUp(self):
        self.maps = Map.map_setup(str(const.HELPER_DIR / "mapLocations.dat"))
        self.pages = Page.get_pages(str(const.HELPER_DIR / "pageInfo.dat"))

    def test_default_selection_is_random_without_event_search(self):
        with patch.dict(const.__dict__):
            const.init()
            self.assertEqual(const.MAP_SELECTION_MODE, 1)
            with (
                patch.multiple(GUI, check_input_vars=DEFAULT, wait_click=DEFAULT,
                               play_button=DEFAULT),
                patch.multiple(Main, wait_for_ui=DEFAULT, navigate=DEFAULT),
                patch.object(Main, "find_rewards_map") as search,
                patch.object(Map, "pick_rand", return_value=self.maps[0]) as pick,
                patch.object(Main, "beat_map", side_effect=StopIteration),
                patch("builtins.print"),
                self.assertRaises(StopIteration),
            ):
                Main.main()
            pick.assert_called_once_with(const.MAPS)
            search.assert_not_called()

    def test_random_selection_only_chooses_playable_maps(self):
        playable = [m for m in self.maps if m.strategy]
        for index, expected in enumerate(playable):
            with (
                self.subTest(index=index),
                patch.object(Map, "randint", return_value=index) as choose,
            ):
                self.assertIs(Map.pick_rand(self.maps), expected)
            choose.assert_called_once_with(0, len(playable) - 1)

    def test_ordered_modes_skip_maps_without_strategies(self):
        """The second fallback skips Glacial Trail in modes 2, 4, and 5."""
        for mode in (2, 4, 5):
            with (
                self.subTest(mode=mode),
                patch.multiple(
                    const, init=DEFAULT, MAPS=self.maps, PAGES=self.pages,
                    MAP_SELECTION_MODE=mode, DEFAULT_MAP="Muddy Puddles",
                    DEFAULT_MODE="Deflation", POST_WIN_WAIT=0, MAP_LOADING_TIME=0,
                    FILE_PREFIX="", BADGE_NAME="badge.png", RETURN_HOME_TIMEOUT=60,
                    create=True,
                ),
                patch.multiple(GUI, check_input_vars=DEFAULT, wait_click=DEFAULT,
                               play_button=DEFAULT, wait=DEFAULT),
                patch.multiple(Main, wait_for_ui=DEFAULT, navigate=DEFAULT),
                patch.object(Main, "wait_for_ui_any", return_value=0) as wait_any,
                patch.object(Main, "find_rewards_map", return_value=None),
                patch.object(Main, "beat_map", side_effect=[True, StopIteration]) as beat,
                patch("builtins.print"),
                self.assertRaises(StopIteration),
            ):
                Main.main()

            self.assertEqual(
                [item.args[0].name for item in beat.call_args_list],
                ["Tricky Tracks", "Dark Dungeons"],
            )
            wait_any.assert_called_once_with(("home_play", "collect"), 60)

    def test_ordered_selection_wraps_only_playable_maps(self):
        """Ordered selection preserves playable-map order and wraps safely."""
        playable = [m for m in self.maps if m.strategy]
        self.assertEqual(
            [Map.pick_ordered(self.maps, i) for i in range(len(playable) + 1)],
            playable + playable[:1],
        )
        with self.assertRaisesRegex(ValueError, "No maps have a defined strategy"):
            Map.pick_ordered([], 0)

    def _search_rewards(self, maps, results, thresholds):
        with (
            patch.object(const, "MAPS", maps, create=True),
            patch.object(const, "PAGES", self.pages, create=True),
            patch.object(const, "FILE_PREFIX", "", create=True),
            patch.object(const, "get_matches", return_value=thresholds),
            patch.object(const, "set_match") as set_match,
            patch.object(Main, "navigate", side_effect=lambda page: page),
            patch.object(Main, "wait_for_ui"),
            patch.object(GUI, "wait"),
            patch.object(Main, "locate", side_effect=results) as locate,
        ):
            result = Main.find_rewards_map(3, "unused.png")
        return result, locate.call_args_list, set_match.call_args_list

    def test_reward_search_only_scans_playable_slots_with_matching_thresholds(self):
        """Unsupported and unknown cards cannot win a reward search."""
        locations = Location.get_coord_list()
        thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        result, calls, _ = self._search_rewards(
            self.maps,
            [(False, (0, 0), 0), (False, (0, 0), 0),
             (True, locations[2], 0.95)],
            thresholds,
        )
        if result is None:
            self.fail("Expected a playable reward match")
        self.assertEqual(result.name, "Dark Dungeons")
        self.assertEqual(calls[0].args[1], locations)
        self.assertEqual(calls[1].args[1], [locations[0]])
        self.assertEqual(calls[1].args[3], [thresholds[0]])
        self.assertEqual(calls[2].args[1], [locations[i] for i in (0, 2, 3, 4, 5)])
        self.assertEqual(calls[2].args[3], [thresholds[i] for i in (0, 2, 3, 4, 5)])

    def test_passing_match_uses_its_own_page_not_an_earlier_weak_match(self):
        """A valid match on a later page wins over an earlier below-threshold score."""
        locations = Location.get_coord_list()
        result, _, _ = self._search_rewards(
            self.maps,
            [(False, locations[1], 0.8), (True, locations[0], 0.6)],
            [0.5, 0.9, 0.5, 0.5, 0.5, 0.5],
        )
        if result is None:
            self.fail("Expected a playable reward match")
        self.assertEqual(result.name, "Ouch")

    def test_pages_without_playable_maps_are_skipped(self):
        """A page with no configured strategy is not passed to image matching."""
        ouch = Map.get_map_by_name(self.maps, "Ouch")
        result, calls, _ = self._search_rewards(
            [ouch], [(False, (0, 0), 0)], [0.5] * 6
        )
        self.assertIsNone(result)
        self.assertEqual(len(calls), 1)

    def test_weak_reward_match_keeps_threshold_calibration(self):
        """Existing weak-match calibration still updates the right card threshold."""
        locations = Location.get_coord_list()
        result, _, updates = self._search_rewards(
            self.maps,
            [(False, locations[1], 0.4), (False, (0, 0), 0), (False, (0, 0), 0)],
            [0.5] * 6,
        )
        if result is None:
            self.fail("Expected a playable reward match")
        self.assertEqual(result.name, "Bloody Puddles")
        self.assertEqual(updates[0].args, (1, 0.4))
        self.assertEqual(updates[0].kwargs, {"do_reporting": True})

    def test_single_reward_threshold_is_preserved_and_calibrated(self):
        """A global threshold applies to every eligible card and remains global."""
        locations = Location.get_coord_list()
        result, calls, updates = self._search_rewards(
            self.maps,
            [(False, locations[1], 0.4), (False, (0, 0), 0), (False, (0, 0), 0)],
            [0.5],
        )
        if result is None:
            self.fail("Expected a playable reward match")
        self.assertEqual(result.name, "Bloody Puddles")
        self.assertTrue(all(item.args[3] == [0.5] for item in calls))
        self.assertEqual(updates[0].args, (0, 0.4))
        self.assertEqual(updates[0].kwargs, {"do_reporting": True})

    def test_invalid_reward_threshold_count_fails_explicitly(self):
        """Malformed calibration data cannot silently omit map locations."""
        with self.assertRaisesRegex(ValueError, "Expected 1 or 6 reward thresholds"):
            self._search_rewards(self.maps, [], [0.5, 0.6])

    def test_reward_thresholds_load_as_numbers(self):
        """Stored threshold values remain numeric for per-card comparisons."""
        with patch("pathlib.Path.open", mock_open(read_data="0.1,0.5")):
            self.assertEqual(const.get_matches(), [0.1, 0.5])

    def test_missing_strategy_is_reported_before_any_map_click(self):
        """A bad map choice stops before entering the difficulty screen."""
        glacial = Map.get_map_by_name(self.maps, "Glacial Trail")
        with patch.object(GUI, "wait_click") as click:
            with self.assertRaisesRegex(ValueError, "No strategy defined for Glacial Trail"):
                Main.beat_map(glacial)
        click.assert_not_called()

    def test_unsupported_default_is_rejected_only_when_used_as_fallback(self):
        """Modes 0 and 3 cannot use a default map with no strategy."""
        for mode in (0, 3):
            with self.subTest(mode=mode):
                with self.assertRaisesRegex(ValueError, "Default map.*no strategy"):
                    GUI.check_input_vars(self.maps, [0, 0, "Glacial Trail", mode])
        for mode in (1, 2, 4, 5):
            with self.subTest(mode=mode):
                GUI.check_input_vars(self.maps, [0, 0, "Glacial Trail", mode])


if __name__ == "__main__":
    unittest.main()
