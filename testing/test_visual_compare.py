"""Known-pixel fixtures for the visual comparison report, without account data."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/compare-ui.py"


class VisualCompareTests(unittest.TestCase):
    def compare(self, reference, candidate, masks=None):
        self.directory = tempfile.TemporaryDirectory(prefix="yapcord-visual-test-")
        self.addCleanup(self.directory.cleanup)
        root = Path(self.directory.name)
        reference.save(root / "reference.png")
        candidate.save(root / "candidate.png")
        command = [sys.executable, str(SCRIPT), str(root / "reference.png"),
                   str(root / "candidate.png"), "--output", str(root / "result")]
        if masks is not None:
            (root / "mask.json").write_text(json.dumps(masks))
            command += ["--mask", str(root / "mask.json")]
        return subprocess.run(command, capture_output=True, text=True), root / "result"

    def test_one_changed_channel_has_the_expected_area_and_error(self):
        reference = Image.new("RGB", (2, 2), "black")
        candidate = reference.copy()
        candidate.putpixel((0, 0), (20, 0, 0))
        result, output = self.compare(reference, candidate)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((output / "report.json").read_text())
        self.assertEqual(report["compared_pixels"], 4)
        self.assertEqual(report["different_pixels"], 1)
        self.assertEqual(report["different_percent"], 25.0)
        self.assertAlmostEqual(report["mean_absolute_error"], 20 / 12, places=5)
        with Image.open(output / "overlay.png") as overlay:
            self.assertEqual(overlay.getpixel((0, 0)), (10, 0, 0))
        self.assertTrue((output / "difference.png").is_file())

    def test_masked_pixels_are_excluded_from_the_denominator(self):
        reference = Image.new("RGB", (2, 2), "black")
        candidate = reference.copy()
        candidate.putpixel((0, 0), (255, 255, 255))
        result, output = self.compare(reference, candidate, [[0, 0, 1, 1]])
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((output / "report.json").read_text())
        self.assertEqual(report["compared_pixels"], 3)
        self.assertEqual(report["masked_pixels"], 1)
        self.assertEqual(report["different_pixels"], 0)
        self.assertEqual(report["mean_absolute_error"], 0)

    def test_mismatched_dimensions_are_rejected_without_resizing(self):
        result, output = self.compare(Image.new("RGB", (2, 2)), Image.new("RGB", (3, 2)))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("dimensions", result.stderr.lower())
        self.assertFalse(output.exists())

    def test_masking_the_entire_image_is_an_error(self):
        result, output = self.compare(Image.new("RGB", (2, 2)), Image.new("RGB", (2, 2)),
                                      [[0, 0, 2, 2]])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unmasked", result.stderr.lower())
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
