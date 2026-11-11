"""Verify hero data drives strategy selection instead of stale hard-coded slots."""

import io
import unittest
from unittest.mock import call, patch

from PIL import Image

import Main
import constant as const
from Helper import GUI, Map
from Helper.Hero import Hero, get_heroes
from Helper.UICalibration import HERO_GRID_SCROLL_NOTCHES


class HeroDataTests(unittest.TestCase):
    """Load current slots and reject broken hero data explicitly."""

    def test_current_hero_slots_and_strategy(self):
        """Etienne uses the middle column, not Sauda's; Psi needs the bottom anchor."""
        heroes = get_heroes(str(const.HELPER_DIR / "heroes.dat"))
        last_row = max(h.row for h in heroes)
        with patch.object(Map.Map, "HEROES", heroes):
            def position(name):
                return Map.get_hero(name).get_card_position(last_row)
            self.assertEqual(position("Etienne"), ("top", (254, 798)))
            self.assertEqual(position("Sauda"), ("top", (405, 798)))
            self.assertEqual(position("Captain Churchill"), ("top", (254, 606)))
            self.assertEqual(position("Rosalia"), ("bottom", (103, 713)))
            self.assertEqual(position("Psi"), ("bottom", (103, 905)))
            self.assertEqual(position("Corvus"), ("bottom", (405, 905)))
            maps = Map.map_setup(str(const.HELPER_DIR / "mapLocations.dat"))
            flooded = Map.get_map_by_name(maps, "Flooded Valley")
            strategies = flooded.strategy
            if not isinstance(strategies, list):
                self.fail("Expected Flooded Valley strategies")
            self.assertEqual(strategies[0].get_hero().get_card_position(last_row),
                             ("top", (254, 798)))

    def test_unreachable_card_positions_fail(self):
        """Slots outside the grid or beyond both anchors raise instead of misclicking."""
        with self.assertRaisesRegex(ValueError, "outside the hero grid"):
            Hero("Late", (6, 0)).get_card_position(5)
        with self.assertRaisesRegex(ValueError, "not reachable"):
            Hero("Middle", (5, 0)).get_card_position(12)

    def test_parser_handles_comments_blanks_and_whitespace(self):
        """The data loader accepts readable files and the no-hero sentinel."""
        with patch("builtins.open", return_value=io.StringIO(
            "# Name, Row, Col\n\n Etienne, 3, 1 \nNone,-1,-1\n"
        )):
            heroes = get_heroes("example.dat")
        self.assertEqual([(h.name, h.row, h.col) for h in heroes],
                         [("Etienne", 3, 1), ("None", -1, -1)])

    def test_invalid_records_report_filename_and_line(self):
        """Malformed, duplicate, or out-of-range data cannot silently select a hero."""
        for record in ("Etienne,3", "Etienne,x,1", "Etienne,3,3",
                       "Etienne,-1,1", "None,0,0", "Etienne,3,1\nEtienne,3,2"):
            with self.subTest(record=record):
                with patch("builtins.open", return_value=io.StringIO(record)):
                    with self.assertRaisesRegex(ValueError, "example.dat:[12]:"):
                        get_heroes("example.dat")
        with patch("builtins.open", return_value=io.StringIO("# empty\n")):
            with self.assertRaisesRegex(ValueError, "No heroes defined"):
                get_heroes("example.dat")

    def test_init_reloads_heroes_before_building_maps(self):
        """Startup refreshes the data before strategies capture hero objects."""
        updated = [Hero("Etienne", (2, 0))]

        def build_maps(_filename):
            self.assertIs(Map.Map.HEROES, updated)
            return []

        with (
            patch.object(Map.Map, "HEROES", []),
            patch.object(const, "get_heroes", return_value=updated) as load,
            patch.object(const, "map_setup", side_effect=build_maps),
            patch.object(const, "get_pages", return_value=[]),
            patch.object(const, "get_matches", return_value=[]),
            patch.dict(const.__dict__),
        ):
            const.init()
            load.assert_called_once_with(str(const.HELPER_DIR / "heroes.dat"))


class HeroSelectionTests(unittest.TestCase):
    """Scroll to the card's anchor and confirm the checkmark without real input."""

    def test_scroll_sends_full_notches_after_hover(self):
        """Hover registration precedes every wheel notch, then the grid must settle."""
        for anchor, step in (("top", 1), ("bottom", -1)):
            with (
                patch.object(GUI.pg, "moveTo"),
                patch.object(GUI, "nudge_mouse") as nudge,
                patch.object(GUI, "scroll_wheel") as wheel,
                patch.object(GUI, "wait_for_still") as still,
                patch.object(GUI, "wait"),
                patch.object(GUI.time, "sleep"),
            ):
                GUI.scroll_hero_grid(anchor)
            nudge.assert_called_once()
            self.assertEqual(wheel.call_args_list, [call(step)] * HERO_GRID_SCROLL_NOTCHES)
            still.assert_called_once()
        with self.assertRaises(ValueError):
            GUI.scroll_hero_grid("middle")

    def test_wait_for_still_times_out_on_motion(self):
        """A grid that never settles fails instead of clicking a moving card."""
        frames = iter([Image.new("L", (40, 40), shade) for shade in range(0, 250, 10)])
        with (
            patch.object(GUI, "grab_game_screen", side_effect=lambda: next(frames)),
            patch.object(GUI.time, "sleep"),
            patch.object(GUI, "exit_key_check"),
            patch.object(GUI.time, "monotonic", side_effect=[0, 0.1, 0.2, 5]),
        ):
            with self.assertRaises(TimeoutError):
                GUI.wait_for_still((0, 0, 10, 10), timeout=1)

    def _select(self, name, wait_results):
        heroes = get_heroes(str(const.HELPER_DIR / "heroes.dat"))
        with (
            patch.object(Map.Map, "HEROES", heroes),
            patch.object(GUI, "hero_change_button") as change,
            patch.object(GUI, "wait"),
            patch.object(GUI, "pick_hero_card") as pick,
            patch.object(GUI, "back_arrow_button") as back,
            patch.object(Main, "wait_for_ui", side_effect=wait_results) as wait,
        ):
            try:
                Main.select_hero_smart(Map.get_hero(name))
            finally:
                self.calls = (change, pick, back, wait)

    def test_psi_scrolls_to_bottom_and_verifies_checkmark(self):
        """Psi is clicked from the bottom anchor and confirmed at its card's check."""
        self._select("Psi", [True])
        change, pick, back, wait = self.calls
        change.assert_called_once()
        pick.assert_called_once_with("bottom", (103, 905))
        wait.assert_called_once_with("hero_selected", 3, coords=[(152, 844)])
        back.assert_called_once()

    def test_unconfirmed_selection_retries_then_fails(self):
        """A missing checkmark retries once and then stops before leaving the screen."""
        self._select("Etienne", [TimeoutError("miss"), True])
        _, pick, back, _ = self.calls
        self.assertEqual(pick.call_count, 2)
        back.assert_called_once()
        with self.assertRaisesRegex(RuntimeError, "Could not confirm Etienne"):
            self._select("Etienne", [TimeoutError("miss")] * 2)
        _, _, back, _ = self.calls
        back.assert_not_called()

    def test_no_hero_skips_hero_screen(self):
        """Strategies without a hero never open the hero screen."""
        with patch.object(GUI, "hero_change_button") as change:
            Main.select_hero_smart(Hero("None", (-1, -1)))
        change.assert_not_called()


if __name__ == "__main__":
    unittest.main()
