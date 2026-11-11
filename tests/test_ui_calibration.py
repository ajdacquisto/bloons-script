"""Regression tests for calibrated targets and bounded vision polling."""

import unittest
from dataclasses import replace
from unittest.mock import call, patch

from PIL import Image

import Main
import constant as const
from Helper import GUI, ImageGrabTest
from Helper.UICalibration import HERO_GRID_BOTTOM_LAST_ROW_Y, HERO_GRID_COLUMNS_X


class UICalibrationTests(unittest.TestCase):
    """Verify central settings reach detection, clicks, and useful live logs."""

    def test_deflation_loading_uses_configured_timeout(self):
        """Slow Deflation loads use the configured budget and never silently exit."""
        strategy = unittest.mock.Mock()
        strategy.get_game_mode.return_value = "Deflation"
        game_map = unittest.mock.Mock()
        game_map.name = "Bloody Puddles"
        game_map.page_location.x = 100
        game_map.page_location.y = 200
        with (
            patch.object(Main, "select_strategy", return_value=strategy),
            patch.object(GUI, "wait_click"),
            patch.object(Main, "select_hero_smart"),
            patch.object(Main, "select_difficulty_smart"),
            patch.object(Main, "select_gamemode_smart"),
            patch.object(Main, "overwrite_save_smart"),
            patch.object(const, "MAP_LOADING_TIMEOUT_DEFLATION", 30, create=True),
            patch.object(Main, "map_loading_wait",
                         side_effect=TimeoutError("loaded: best=3.1%")) as wait,
            patch.object(Main, "adjust_auto_start_smart") as adjust,
        ):
            with self.assertRaisesRegex(TimeoutError, "loaded: best=3.1%"):
                Main.beat_map(game_map)
        wait.assert_called_once_with(timeout=30, post_load_wait=0.8)
        adjust.assert_not_called()

    def test_loading_wait_clicks_only_after_detection(self):
        """A missing load prompt cannot trigger an OK click."""
        with (
            patch.object(Main, "wait_for_ui", side_effect=TimeoutError("loaded")),
            patch.object(GUI, "wait_click") as click,
        ):
            with self.assertRaises(TimeoutError):
                Main.map_loading_wait(timeout=30)
        click.assert_not_called()
        with (
            patch.object(Main, "wait_for_ui") as wait,
            patch.object(GUI, "wait_click") as click,
            patch.object(GUI, "wait") as sleep,
        ):
            Main.map_loading_wait(timeout=30, post_load_wait=0.8)
        wait.assert_called_once_with("loaded", 30)
        click.assert_called_once_with(0, *const.UI_CLICKS["loaded"])
        sleep.assert_called_once_with(0.8)

    def test_page_tab_moves_cursor_away_before_detection(self):
        """Hovering changes the Expert template; clear hover after each tab click."""
        with (
            patch.object(GUI, "wait_click") as click,
            patch.object(GUI, "center_cursor") as center,
        ):
            operations = unittest.mock.Mock()
            operations.attach_mock(click, "click")
            operations.attach_mock(center, "center")
            GUI.page_button(3)
        self.assertEqual(operations.mock_calls, [
            call.click(0, 1338, 977), call.center(),
        ])

    def test_single_target_uses_central_settings(self):
        """A changed target supplies its filename, center, radius, and threshold."""
        target = replace(const.UI_TARGETS["easy"], coords=(620, 410), radius=3)
        with (
            patch.dict(const.UI_TARGETS, easy=target),
            patch.object(const, "FILE_PREFIX", "templates\\", create=True),
            patch.object(Main, "wait_for_badge", return_value=True) as wait,
        ):
            self.assertTrue(Main.wait_for_ui("easy", 4))
        wait.assert_called_once_with(
                "templates\\selectEasy.png", [(620, 410)], 4, [0.6],
            search_radius=3, label="easy", rounding=1,
        )

    def test_selected_hero_uses_tolerant_color_rounding(self):
        target = replace(const.UI_TARGETS["hero_selected"], coords=(303, 737))
        with (
            patch.dict(const.UI_TARGETS, hero_selected=target),
            patch.object(const, "FILE_PREFIX", "templates\\", create=True),
            patch.object(Main, "wait_for_badge", return_value=True) as wait,
        ):
            self.assertTrue(Main.wait_for_ui("hero_selected", 3))
        wait.assert_called_once_with(
            "templates\\heroSelected.png", [(303, 737)], 3, [0.4],
            search_radius=2, label="hero_selected", rounding=2,
        )

    def test_alternatives_preserve_individual_calibration(self):
        """Each alternative keeps its own threshold and search radius."""
        with (
            patch.object(const, "FILE_PREFIX", "", create=True),
            patch.object(Main, "locate",
                         side_effect=[(False, (1, 2), 0.1), (True, (3, 4), 0.9)]) as locate,
            patch.object(GUI, "exit_key_check"),
        ):
            self.assertEqual(Main.wait_for_ui_any(("home_play", "expert"), 1), 1)
        self.assertEqual(locate.call_args_list, [
            call("homePlay.png", [(960, 945)], 0, [0.8], 0, 1),
            call("expert.png", [(1338, 1047)], 2, [0.8], 0, 1),
        ])

    def test_wait_logs_progress_success_and_sleeps(self):
        """Unsuccessful sweeps sleep, throttle progress, and log the detected score."""
        clock = [0.0]

        def sleep(seconds):
            clock[0] += seconds

        with (
            patch.object(Main.time, "monotonic", side_effect=lambda: clock[0]),
            patch.object(const, "VISION_POLL_INTERVAL", 0.2),
            patch.object(const, "VISION_LOG_INTERVAL", 0.3),
            patch.object(GUI, "wait", side_effect=sleep) as wait,
            patch.object(GUI, "exit_key_check"),
            patch.object(Main, "locate", side_effect=[
                (False, (5, 6), 0.2), (False, (5, 6), 0.4),
                (False, (5, 6), 0.3), (True, (5, 6), 0.95),
            ]),
            self.assertLogs(Main.LOGGER, level="INFO") as logs,
        ):
            self.assertTrue(Main.wait_for_badge(
                "test.png", [(5, 6)], 2, 0.9, label="test",
            ))
        self.assertEqual(wait.call_count, 3)
        progress = [line for line in logs.output if "Still waiting" in line]
        self.assertEqual(len(progress), 1)
        self.assertIn("best=40.0%", progress[0])
        self.assertTrue(any("Detected test" in line and "95.0%" in line
                            for line in logs.output))

    def test_timeout_preserves_best_score_and_coordinates(self):
        """Timeout diagnostics use the best observation, not the last one."""
        clock = [0.0]

        def sleep(seconds):
            clock[0] += seconds

        with (
            patch.object(Main.time, "monotonic", side_effect=lambda: clock[0]),
            patch.object(const, "VISION_POLL_INTERVAL", 0.2),
            patch.object(GUI, "wait", side_effect=sleep),
            patch.object(GUI, "exit_key_check"),
            patch.object(Main, "locate", side_effect=[
                (False, (5, 6), 0.4), (False, (7, 8), 0.8), (False, (9, 10), 0.1),
            ]),
            self.assertLogs(Main.LOGGER, level="WARNING") as logs,
        ):
            with self.assertRaisesRegex(
                TimeoutError, r"test: best=80.0% at \(7, 8\), required>\[0.9\]"
            ):
                Main.wait_for_badge("test.png", [(5, 6)], 0.4, [0.9], label="test")
        self.assertIn("Vision timed out", logs.output[-1])

    def test_capture_errors_and_cancellation_propagate(self):
        """Detection errors are not converted to timeouts or optional absence."""
        for error in (OSError("capture failed"), SystemExit()):
            with (
                self.subTest(error=type(error).__name__),
                patch.object(const, "FILE_PREFIX", "", create=True),
                patch.object(GUI, "exit_key_check"),
                patch.object(Main, "locate", side_effect=error),
            ):
                with self.assertRaises(type(error)):
                    Main.overwrite_save_smart()

    def test_mode_selection_uses_calibrated_wait_and_click(self):
        """Standard and Deflation use the same named configuration across surfaces."""
        for mode in ("Standard", "Deflation"):
            with (
                self.subTest(mode=mode),
                patch.object(Main, "wait_for_ui") as wait,
                patch.object(GUI, "wait_click") as click,
            ):
                Main.select_gamemode_smart(mode)
                wait.assert_called_once_with(mode.lower(), 3)
                click.assert_called_once_with(0, *const.UI_CLICKS[mode.lower()])

    def test_calibrated_assets_tolerate_two_pixel_displacement(self):
        """Actual refreshed assets remain detectable within their configured radius."""
        for name in ("expert", "easy", "standard", "deflation",
                     "auto_start_off", "auto_start_on", "hero_selected"):
            target = const.UI_TARGETS[name]
            coords = target.coords
            if name == "hero_selected":
                coords = (
                    HERO_GRID_COLUMNS_X[0] + const.HERO_SELECTED_OFFSET[0],
                    HERO_GRID_BOTTOM_LAST_ROW_Y + const.HERO_SELECTED_OFFSET[1],
                )
            with self.subTest(name=name):
                with Image.open(const.MEDIA_DIR / target.filename) as image:
                    source = image.convert("RGB")
                x, y = coords
                screen = Image.new("RGB", (1920, 1080), (1, 2, 3))
                screen.paste(source, (x - source.width // 2 + 2,
                                      y - source.height // 2 - 2))
                with patch.object(ImageGrabTest.ImageGrab, "grab", return_value=screen):
                    found, match_coords, score = ImageGrabTest.locate(
                        str(const.MEDIA_DIR / target.filename), [coords],
                        target.radius, [target.threshold], 0, 1,
                    )
                self.assertTrue(found)
                self.assertEqual(match_coords, coords)
                self.assertEqual(score, 1.0)

    def test_auto_start_state_templates_are_distinct(self):
        """Off and on switch crops cannot satisfy each other's calibrated threshold."""
        with (
            Image.open(const.MEDIA_DIR / const.UI_TARGETS["auto_start_off"].filename) as image,
            Image.open(const.MEDIA_DIR / const.UI_TARGETS["auto_start_on"].filename) as image_on,
        ):
            score = ImageGrabTest.compare_images(
                image.convert("RGB"), image_on.convert("RGB"), 0, 1
            )
        self.assertLess(score, const.UI_TARGETS["auto_start_on"].threshold)

    def test_dot_detection_rejects_inactive_indicators(self):
        """Only the filled dot qualifies among the configured page positions."""
        target = const.UI_TARGETS["map_dot"]
        pages = Main.Page.get_pages(str(const.HELPER_DIR / "pageInfo.dat"))
        with Image.open(const.MEDIA_DIR / target.filename) as image:
            source = image.convert("RGB")
        for selected in (0, 8, 16):
            with self.subTest(selected=selected):
                screen = Image.new("RGB", (1920, 1080), (0, 0, 0))
                x, y = pages[selected].dot_coords
                screen.paste(source, (x - source.width // 2, y - source.height // 2))
                with patch.object(ImageGrabTest.ImageGrab, "grab", return_value=screen):
                    found, coords, score = ImageGrabTest.locate(
                        str(const.MEDIA_DIR / target.filename),
                        Main.Page.get_dot_coord_list(pages), target.radius,
                        [target.threshold], 0, 1,
                    )
                self.assertTrue(found)
                self.assertEqual(coords, (x, y))
                self.assertEqual(score, 1.0)


if __name__ == "__main__":
    unittest.main()
