from fpi.analysis import convert_value_for_display


class TestConvertValueForDisplay:
    """
    Additional unit tests for convert_value_for_display.

    These tests complement doctests by covering:
    - threshold boundaries (999 vs. 1000, 999_999 vs. 1_000_000)
    - negative values around thresholds
    - rounding behaviour consistency
    - decimal inputs
    - extremely large inputs
    """

    def test_below_smallest_threshold(self) -> None:
        """Values below 1000 should be formatted without suffix."""
        assert convert_value_for_display(999) == "999,0"
        assert convert_value_for_display(-999) == "-999,0"

    def test_at_thousand_threshold(self) -> None:
        """1000 and equivalents should correctly use K suffix."""
        assert convert_value_for_display(1000) == "1,0 K"
        assert convert_value_for_display(-1000) == "-1,0 K"

    def test_just_below_million_threshold(self) -> None:
        """999_999 should round to '1000,0 K' (important rounding case)."""
        assert convert_value_for_display(999_999) == "1000,0 K"
        assert convert_value_for_display(-999_999) == "-1000,0 K"

    def test_at_million_threshold(self) -> None:
        """1_000_000 must use M suffix."""
        assert convert_value_for_display(1_000_000) == "1,0 M"
        assert convert_value_for_display(-1_000_000) == "-1,0 M"

    def test_at_billion_threshold(self) -> None:
        """1_000_000_000 must use Md suffix."""
        assert convert_value_for_display(1_000_000_000) == "1,0 Md"

    def test_decimal_value_formatting(self) -> None:
        """Ensure decimal floats are scaled and formatted correctly."""
        assert convert_value_for_display(1530.75) == "1,5 K"

    def test_rounding_behavior(self) -> None:
        """0.05 should round to '0,1' with European decimal comma."""
        assert convert_value_for_display(0.05) == "0,1"

    def test_zero_value(self) -> None:
        """Zero formatting is stable."""
        assert convert_value_for_display(0) == "0,0"

    def test_extreme_value_large(self) -> None:
        """Large values must still be formatted correctly."""
        assert convert_value_for_display(123_456_789_500_000_000) == "123456789,5 Md"
