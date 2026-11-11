"""Behavior checks for the image-matching utility scripts."""

import io
import runpy
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from PIL import Image

from Helper import ImageGrabTest


ROOT = Path(__file__).resolve().parent.parent


class UtilityScriptTests(unittest.TestCase):
    """Run the standalone utilities without displaying or saving images."""

    def test_image_grab_test_script_reports_match(self):
        """The image test script prints its match result."""
        source = Image.new("RGB", (2, 2))
        screen = Image.new("RGB", (4, 4))
        output = io.StringIO()
        with (
            patch.object(ImageGrabTest.Image, "open", side_effect=[source, screen]),
            patch.object(ImageGrabTest, "optimize_match_ratio", return_value=0.5) as optimize,
            redirect_stdout(output),
        ):
            result = runpy.run_path(str(ROOT / "ImageGrabTestTest.py"), run_name="__main__")

        self.assertTrue(result["matchFound"])
        self.assertEqual(result["matchCoords"], (1832, 1016))
        self.assertEqual(result["matchPercent"], 50.0)
        self.assertEqual(output.getvalue().splitlines(), ["True", "(1832, 1016)", "50.0"])
        optimize.assert_called_once_with(source, screen, (1832, 1016), 5, 0, 1, True, True)

    def test_mouse_coords_script_toggles_with_caps_lock(self):
        """The standalone coordinate script pauses and resumes on Caps Lock."""
        script = runpy.run_path(str(ROOT / "mouse_coords.py"), run_name="mouse_coords_test")
        output = io.StringIO()
        get_position = Mock(return_value=(-1700, 500))
        with (
            patch.dict(
                script["main"].__globals__,
                {
                    "caps_lock_pressed": Mock(
                        side_effect=[False, True, True, False, True, False]
                    ),
                    "get_mouse_position": get_position,
                },
            ),
            patch.object(
                script["time"],
                "sleep",
                side_effect=[None, None, None, None, None, KeyboardInterrupt],
            ),
            redirect_stdout(output),
        ):
            script["main"]()

        self.assertIn("Paused.", output.getvalue())
        self.assertIn("Resumed.", output.getvalue())
        self.assertIn("(-1700, 500)", output.getvalue())
        self.assertIn("Stopped.", output.getvalue())
        self.assertEqual(get_position.call_count, 3)

    def test_set_badge_icon_uses_entered_paths_and_location(self):
        """The badge utility passes the user's inputs to the matcher."""
        source = Image.new("RGB", (2, 2))
        screen = Image.new("RGB", (4, 4))
        with (
            patch("builtins.input", side_effect=["screenshot.png", "Top left", "output.png"]),
            patch.object(ImageGrabTest.Image, "open", side_effect=[source, screen]),
            patch.object(ImageGrabTest, "optimize_match_ratio", return_value=0.5) as optimize,
            redirect_stdout(io.StringIO()),
        ):
            result = runpy.run_path(str(ROOT / "SetBadgeIcon.py"), run_name="__main__")

        self.assertTrue(result["matchFound"])
        self.assertEqual(result["matchCoords"], (697, 296))
        optimize.assert_called_once_with(
            source, screen, (697, 296), 0, 0, 1, True, True, "output.png"
        )


if __name__ == "__main__":
    unittest.main()
