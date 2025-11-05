from typing import List

from fpi.analysis.explore import load_data
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
