"""Tests for the heterogeneous payloads carried by actions."""

import unittest

from Helper.Action import Action
from Helper.Tower import Tower


class ActionPayloadTests(unittest.TestCase):
    """Action payloads retain the value supplied by the strategy."""

    def test_payload_is_returned_unchanged(self):
        """Scalar, text, and list payloads retain their original identity."""
        payloads = (1, 1.5, "1", [1, True], [Tower("Dart Monkey", (1, 2), [0, 0, 0], 0)])

        for payload in payloads:
            with self.subTest(payload=payload):
                self.assertIs(Action("example", payload).get_info(), payload)


if __name__ == "__main__":
    unittest.main()
