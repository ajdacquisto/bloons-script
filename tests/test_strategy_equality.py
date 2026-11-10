"""Regression tests for strategy equality."""

import unittest

from Helper.Action import Action
from Helper.Hero import Hero
from Helper.Strategy import Strategy


class StrategyEqualityTests(unittest.TestCase):
    """Strategies compare their metadata and their complete action lists."""

    def setUp(self):
        self.hero = Hero("Quincy", (0, 0))

    def test_equal_actions_compare_equal(self):
        """Equivalent actions on separate strategies compare equal."""
        first = Strategy(0, "Deflation", self.hero, [Action("WaitSec", 1)])
        second = Strategy(0, "Deflation", self.hero, [Action("WaitSec", 1)])

        self.assertEqual(first, second)

    def test_extra_actions_make_strategies_unequal_in_both_orders(self):
        """A shared action prefix is not sufficient for equality."""
        short = Strategy(0, "Deflation", self.hero, [Action("WaitSec", 1)])
        long = Strategy(
            0, "Deflation", self.hero, [Action("WaitSec", 1), Action("Ability", "1")]
        )

        self.assertNotEqual(short, long)
        self.assertNotEqual(long, short)

    def test_empty_actions_are_not_equal_to_nonempty_actions(self):
        """An empty action list differs from a nonempty one."""
        empty = Strategy(0, "Deflation", self.hero, [])
        nonempty = Strategy(0, "Deflation", self.hero, [Action("WaitSec", 1)])

        self.assertNotEqual(empty, nonempty)

    def test_different_metadata_or_actions_are_unequal(self):
        """Differences other than list length remain significant."""
        baseline = Strategy(0, "Deflation", self.hero, [Action("WaitSec", 1)])
        alternatives = (
            Strategy(1, "Deflation", self.hero, [Action("WaitSec", 1)]),
            Strategy(0, "Standard", self.hero, [Action("WaitSec", 1)]),
            Strategy(0, "Deflation", Hero("Psi", (0, 0)), [Action("WaitSec", 1)]),
            Strategy(0, "Deflation", self.hero, [Action("WaitSec", 2)]),
        )

        for alternative in alternatives:
            with self.subTest(alternative=alternative.get_game_mode()):
                self.assertNotEqual(baseline, alternative)

    def test_unrelated_objects_compare_unequal(self):
        """Comparison with an unrelated type follows Python's equality protocol."""
        strategy = Strategy(0, "Deflation", self.hero, [])

        self.assertNotEqual(strategy, object())


if __name__ == "__main__":
    unittest.main()
