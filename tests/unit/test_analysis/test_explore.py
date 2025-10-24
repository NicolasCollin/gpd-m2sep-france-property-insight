import pandas as pd
import pytest
from fpi.analysis.explore import load_data, preprocess
from fpi.analysis.utils_plot import save_hist, save_lv

class TestLoadData:
    """Tests for load_data function"""
    
    def test_returndf(self):
        """Test that load_data returns a DataFrame"""
        df = load_data("data/raw/sample2024.txt")
        assert isinstance(df, pd.DataFrame)
    
    def test_expcol(self):
        """Test that expected columns exist"""
        df = load_data("data/raw/sample2024.txt")
        assert "Valeur fonciere" in df.columns
    
    def test_ne(self):
        """Test that DataFrame is not empty"""
        df = load_data("data/raw/sample2024.txt")
        assert len(df) > 0


class TestPreprocess:
    """Tests for preprocess function"""
    
    def setup_method(self):
        """Common setup for all tests in this class"""
        self.raw_df = load_data("data/raw/sample2024.txt")
        self.clean_df = preprocess(self.raw_df)
    
    def test_translate(self):
        """Test that column names are translated to English"""
        expected_cols = [
            "land_value", "postal_code", "building_surface", 
            "mutation_date", "land_surface", "main_rooms"
        ]
        assert list(self.clean_df.columns) == expected_cols
    
    def test_shape(self):
        """Test that row count hasn't increased"""
        assert self.clean_df.shape[0] == self.raw_df.shape[0]
    
    def test_misscol(self):
        """Test that no expected columns are missing"""
        expected_cols = [
            "land_value", "postal_code", "building_surface", 
            "mutation_date", "land_surface", "main_rooms"
        ]
        for col in expected_cols:
            assert col in self.clean_df.columns


class TestSaveHist:
    """Tests for save_hist function"""
    
    def setup_method(self):
        """Common setup with test data"""
        self.test_df = pd.DataFrame({
            "building_surface": [50, 100, 70], 
            "land_surface": [200, 500, 300], 
            "main_rooms": [2, 3, 4]
        })
    
    def test_histcreate(self, tmp_path):
        """Test that histogram files are created"""
        save_hist(self.test_df, 
                 ["building_surface", "land_surface", "main_rooms"], 
                 output_dir=tmp_path)
        
        for col in ["building_surface", "land_surface", "main_rooms"]:
            assert (tmp_path / f"{col}_hist.png").exists()
    
    def test_histcol(self, tmp_path):
        """Test with empty columns"""
        empty_df = pd.DataFrame({"test_col": []})
        # Should handle empty DataFrames without errors
        save_hist(empty_df, ["test_col"], output_dir=tmp_path)
        assert (tmp_path / "test_col_hist.png").exists()


class TestIntegration:
    """Integration tests between functions"""
    
    def test_pipeline(self, tmp_path):
        """Test complete pipeline: load -> preprocess -> save_hist"""
        # Load data
        df = load_data("data/raw/sample2024.txt")
        assert isinstance(df, pd.DataFrame)
        
        # Preprocess data
        df_clean = preprocess(df)
        expected_cols = [
            "land_value", "postal_code", "building_surface", 
            "mutation_date", "land_surface", "main_rooms"
        ]
        assert list(df_clean.columns) == expected_cols
        
        # Save histograms (just verify it doesn't crash)
        numeric_cols = ["building_surface", "land_surface", "main_rooms"]
        save_hist(df_clean, numeric_cols, output_dir=tmp_path)
        
        for col in numeric_cols:
            assert (tmp_path / f"{col}_hist.png").exists()