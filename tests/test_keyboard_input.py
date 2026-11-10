"""Regression tests for keyboard input validation."""

import unittest
from unittest.mock import patch

from Helper import GUI


class KeyPushTests(unittest.TestCase):
    """Key validation and dispatch do not send unexpected input."""

    def test_invalid_key_raises_value_error_without_sending_input(self):
        """Unsupported keys produce a useful error before sending scan codes."""
        with (
            patch.object(GUI, "exit_key_check"),
            patch.object(GUI, "PressKey") as press,
            patch.object(GUI, "ReleaseKey") as release,
            self.assertRaisesRegex(ValueError, "Invalid character"),
        ):
            GUI.key_push("?")

        press.assert_not_called()
        release.assert_not_called()

    def test_supported_key_sends_scan_code(self):
        """A recognized key still sends its press and release."""
        with (
            patch.object(GUI, "exit_key_check"),
            patch.object(GUI, "PressKey") as press,
            patch.object(GUI, "ReleaseKey") as release,
        ):
            GUI.key_push("q")

        press.assert_called_once_with(0x10)
        release.assert_called_once_with(0x10)

    def test_escape_uses_direct_input(self):
        """Escape retains its separate direct-input path."""
        with (
            patch.object(GUI, "exit_key_check"),
            patch.object(GUI, "PressKey") as press,
            patch.object(GUI, "ReleaseKey") as release,
            patch.object(GUI.pydirectinput, "press") as direct_press,
        ):
            GUI.key_push("esc")

        direct_press.assert_called_once_with("esc")
        press.assert_not_called()
        release.assert_not_called()


if __name__ == "__main__":
    unittest.main()
