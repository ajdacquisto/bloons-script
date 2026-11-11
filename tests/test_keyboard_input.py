"""Regression tests for keyboard input validation."""

import unittest
from unittest.mock import Mock, call, patch

from Helper import GUI


class StopKeyTests(unittest.TestCase):
    """The configured stop key cancels input without using Caps Lock."""

    def test_f12_stops_and_logs_the_reason(self):
        with (
            patch.object(GUI.const, "STOP_KEY", "f12"),
            patch.object(GUI.keyboard, "is_pressed", return_value=True) as pressed,
            self.assertLogs(GUI.LOGGER, level="INFO") as logs,
            self.assertRaises(SystemExit),
        ):
            GUI.exit_key_check()
        pressed.assert_called_once_with("f12")
        self.assertIn("Stop requested via F12", logs.output[0])

    def test_caps_lock_does_not_stop_input(self):
        with (
            patch.object(GUI.const, "STOP_KEY", "f12"),
            patch.object(GUI.keyboard, "is_pressed",
                         side_effect=lambda key: key.lower() == "capslock") as pressed,
        ):
            GUI.exit_key_check()
        self.assertEqual(pressed.call_args_list, [call("f12"), call("Up")])

    def test_stop_key_is_configurable(self):
        with (
            patch.object(GUI.const, "STOP_KEY", "f8"),
            patch.object(GUI.keyboard, "is_pressed", return_value=True) as pressed,
            self.assertRaises(SystemExit),
        ):
            GUI.exit_key_check()
        pressed.assert_called_once_with("f8")

    def test_stop_prevents_zero_delay_click(self):
        with (
            patch.object(GUI.keyboard, "is_pressed", return_value=True),
            patch.object(GUI.pg, "click") as click,
            self.assertRaises(SystemExit),
        ):
            GUI.wait_click(0, 100, 200)
        click.assert_not_called()

    def test_wait_checks_for_stop_between_intervals(self):
        with (
            patch.object(GUI, "exit_key_check",
                         side_effect=[None, None, SystemExit]) as check,
            patch.object(GUI.time, "sleep") as sleep,
            self.assertRaises(SystemExit),
        ):
            GUI.wait(1)
        self.assertEqual(check.call_count, 3)
        sleep.assert_called_once_with(0.1)


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
            patch.object(GUI, "wait"),
            patch.object(GUI, "PressKey") as press,
            patch.object(GUI, "ReleaseKey") as release,
        ):
            GUI.key_push("q")

        press.assert_called_once_with(0x10)
        release.assert_called_once_with(0x10)

    def test_key_is_held_for_a_game_frame_before_release(self):
        """A scan-code press lasts long enough for the game to register it."""
        events = Mock()
        with (
            patch.object(GUI, "exit_key_check"),
            patch.object(GUI, "PressKey", events.press),
            patch.object(GUI, "wait", events.wait),
            patch.object(GUI, "ReleaseKey", events.release),
        ):
            GUI.key_push("u")

        self.assertEqual(events.mock_calls, [
            call.press(0x16),
            call.wait(0.1),
            call.release(0x16),
        ])

    def test_cancel_during_key_hold_still_releases_the_key(self):
        """A stop request while a key is held cannot leave it stuck down."""
        with (
            patch.object(GUI, "exit_key_check"),
            patch.object(GUI, "PressKey"),
            patch.object(GUI, "wait", side_effect=SystemExit),
            patch.object(GUI, "ReleaseKey") as release,
            self.assertRaises(SystemExit),
        ):
            GUI.key_push("u")

        release.assert_called_once_with(0x16)

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
