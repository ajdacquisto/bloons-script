"""Verify hero data drives strategy selection instead of stale hard-coded slots."""

import io
import unittest
from unittest.mock import patch

import constant as const
from Helper import Map
from Helper.Hero import Hero, get_heroes


class HeroDataTests(unittest.TestCase):
    """Load current slots and reject broken hero data explicitly."""

    def test_current_hero_slots_and_strategy(self):
        """Etienne uses the middle column, not Sauda's right-hand column."""
        heroes = get_heroes(str(const.HELPER_DIR / "heroes.dat"))
        with patch.object(Map.Map, "HEROES", heroes):
            self.assertEqual(Map.get_hero("Etienne").get_coords(), (250, 800))
            self.assertEqual(Map.get_hero("Sauda").get_coords(), (400, 800))
            self.assertEqual(Map.get_hero("Captain Churchill").get_coords(), (250, 600))
            maps = Map.map_setup(str(const.HELPER_DIR / "mapLocations.dat"))
            flooded = Map.get_map_by_name(maps, "Flooded Valley")
            strategies = flooded.strategy
            if not isinstance(strategies, list):
                self.fail("Expected Flooded Valley strategies")
            self.assertEqual(strategies[0].get_hero().get_coords(), (250, 800))

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


if __name__ == "__main__":
    unittest.main()
