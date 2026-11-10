"""Regression tests for image matching."""

import unittest

import numpy as np
from PIL import Image

from Helper.ImageGrabTest import get_arr_match_ratio, optimize_match_ratio


class ImageMatchingTests(unittest.TestCase):
    """Verify pixel comparisons for square and rectangular templates."""

    def test_rectangular_arrays_compare_every_pixel(self):
        """A mismatch counts once in both landscape and portrait arrays."""
        for shape in ((2, 4, 3), (4, 2, 3)):
            with self.subTest(shape=shape):
                original = np.zeros(shape, dtype=np.uint8)
                changed = original.copy()
                changed[0, 0] = (4, 8, 12)

                self.assertEqual(get_arr_match_ratio(original, changed, 1), 7 / 8)

    def test_square_arrays_preserve_rounding_behavior(self):
        """Rounding still groups close channel values as before."""
        original = np.array(
            [[[8, 12, 16], [0, 0, 0]], [[20, 40, 60], [64, 128, 192]]],
            dtype=np.uint8,
        )
        changed = original.copy()
        changed[0, 0] = (9, 13, 17)
        changed[1, 1] = (0, 0, 0)

        self.assertEqual(get_arr_match_ratio(original, changed, 1), 0.5)
        self.assertEqual(get_arr_match_ratio(original, changed, 4), 0.75)

    def test_mismatched_array_sizes_are_rejected(self):
        """Different image dimensions cannot be compared."""
        first = np.zeros((2, 4, 3), dtype=np.uint8)
        second = np.zeros((4, 2, 3), dtype=np.uint8)

        with self.assertRaisesRegex(RuntimeError, "Array sizes don't match"):
            get_arr_match_ratio(first, second, 1)

    def test_rectangular_template_can_be_found_on_screen(self):
        """The normal search path accepts a non-square source image."""
        source = Image.new("RGB", (4, 2), "black")
        screen = Image.new("RGB", (8, 6), "white")
        screen.paste(source, (2, 2))

        self.assertEqual(optimize_match_ratio(source, screen, (4, 3), 0, 0, 1), 1)


if __name__ == "__main__":
    unittest.main()
