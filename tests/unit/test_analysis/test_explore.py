import shutil
import unittest
from pathlib import Path
from typing import List

from fpi.analysis.explore import display_trend, load_data
from fpi.utils.constants import VARS_TO_KEEP


class TestLoadData:
    """Tests for load_data function on a cleaned csv"""

    def setup_method(self):
        """Common setup for all tests in this class"""
        self.clean_df = load_data("data/cleaned/cleaned2024")
        # self.clean_df = preprocess(self.raw_df)

    def test_translate(self):
        """Test that column names are translated to English"""
        expected_cols: List[str] = VARS_TO_KEEP
        assert list(self.clean_df.columns) == expected_cols

    def test_misscol(self):
        """Test that no expected columns are missing"""
        expected_cols: List[str] = VARS_TO_KEEP
        for col in expected_cols:
            assert col in self.clean_df.columns


class TestExploreModule(unittest.TestCase):
    def setUp(self):
        """creates a temporary folder which stocks the test files."""
        self.temp_dir = Path("tests/temp_plots")
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """deletes all the PNG files created by the tests"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_display_trend(self):
        """Verify if display_trend creates graphs"""
        display_trend("data/cleaned", dept_filter="75", output_dir=self.temp_dir)
        display_trend("data/cleaned", dept_filter="92", output_dir=self.temp_dir)

        png_files = list(self.temp_dir.glob("*.png"))
        self.assertGreater(len(png_files), 0, "No PNG file generated.")
