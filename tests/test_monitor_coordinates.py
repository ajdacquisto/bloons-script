"""Verify game-local input and capture coordinates on multiple displays."""

import unittest
from unittest.mock import call, patch

from PIL import Image

import constant as const
from Helper import GUI, ImageGrabTest
from Helper.Tower import Tower


class MonitorCoordinateTests(unittest.TestCase):
    """Keep strategies monitor-relative and translate only at desktop boundaries."""

    def test_mouse_input_uses_display_origin(self):
        """Menu clicks, tower operations, and cursor centering share one offset."""
        for origin in ((0, 0), (-1920, 290), (1920, -1080)):
            with (
                self.subTest(origin=origin),
                patch.object(const, "GAME_SCREEN_ORIGIN", origin),
                patch.object(GUI, "wait"),
                patch.object(GUI, "key_push") as key_push,
                patch.object(GUI.pg, "click") as click,
                patch.object(GUI.pg, "moveTo") as move_to,
            ):
                tower = Tower("Monkey Ace", [694, 788], [2, 0, 3], 0)
                GUI.wait_click(0, 1900, 0)
                GUI.play_button(0)
                GUI.center_cursor()
                GUI.place_tower(tower)
                GUI.select_tower(tower)
                GUI.sell_tower(tower)

                x, y = origin
                click.assert_has_calls([
                    call(x + 1900, y),
                    call(x + 960, y + 945),
                    call(x + 694, y + 788),
                    call(x + 694, y + 788),
                    call(x + 694, y + 788),
                ])
                self.assertEqual(click.call_count, 5)
                self.assertEqual(move_to.call_args_list, [
                    call(x + 960, y + 540),
                    call(x + 694, y + 788, duration=0.1),
                ])
                self.assertEqual(key_push.call_args_list, [call("v"), call("bksp")])
                self.assertEqual(tower.get_position(), [694, 788])

    def test_live_matching_captures_selected_display(self):
        """The capture bbox is desktop-relative, but match coordinates stay local."""
        source = Image.new("RGB", (4, 2), "black")
        screen = Image.new("RGB", (1920, 1080), "white")
        screen.paste(source, (692, 787))
        for origin in ((0, 0), (-1920, 290), (1920, -1080)):
            with (
                self.subTest(origin=origin),
                patch.object(const, "GAME_SCREEN_ORIGIN", origin),
                patch.object(ImageGrabTest.Image, "open", return_value=source),
                patch.object(ImageGrabTest.ImageGrab, "grab", return_value=screen) as grab,
            ):
                result = ImageGrabTest.locate(
                    "unused.png", [(694, 788)], 0, [0.99], 0, 1
                )
                self.assertEqual(result, (True, (694, 788), 1.0))
                x, y = origin
                grab.assert_called_once_with(
                    bbox=(x, y, x + 1920, y + 1080), all_screens=True
                )

    def test_capture_errors_are_not_hidden(self):
        """A failed screen capture propagates instead of looking like no match."""
        with (
            patch.object(ImageGrabTest.Image, "open"),
            patch.object(ImageGrabTest.ImageGrab, "grab", side_effect=OSError("capture")),
        ):
            with self.assertRaisesRegex(OSError, "capture"):
                ImageGrabTest.locate("unused.png", [(960, 540)], 0, [0.5], 0, 1)


if __name__ == "__main__":
    unittest.main()
