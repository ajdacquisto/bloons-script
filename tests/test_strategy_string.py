"""Regression tests for strategy string formatting."""

import unittest

from Helper.Action import Action
from Helper.Hero import Hero
from Helper.Strategy import Strategy


class StrategyStringTests(unittest.TestCase):
    """A strategy can be displayed regardless of its action count."""

    def test_empty_actions(self):
        """An empty action list is formatted as empty parentheses."""
        strategy = Strategy(0, "Deflation", Hero("Quincy", (0, 0)), [])

        self.assertEqual(
            str(strategy), "S[diff=0,mode=Deflation,hero=Hero: Quincy,actions=()]"
        )

    def test_multiple_actions(self):
        """Multiple actions are separated without a trailing comma."""
        strategy = Strategy(
            0,
            "Deflation",
            Hero("Quincy", (0, 0)),
            [Action("WaitSec", 1), Action("Ability", "1")],
        )

        self.assertEqual(
            str(strategy),
            "S[diff=0,mode=Deflation,hero=Hero: Quincy,"
            "actions=(WaitSec: 1,Ability: 1)]",
        )


if __name__ == "__main__":
    unittest.main()
