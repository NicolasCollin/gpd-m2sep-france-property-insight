import pandas as pd
import numpy as np
from pathlib import Path
from tabulate import tabulate

def statdes(df: pd.DataFrame, output_dir: str = "docs/stats") -> pd.DataFrame:
    """
    Compute and save descriptive statistics with improved display.
    
    :param df: Input DataFrame
    :param output_dir: Folder where results will be saved
    :return: Summary DataFrame with descriptive statistics
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print("\n" + "="*80)
    print("COMPREHENSIVE DESCRIPTIVE STATISTICS")
    print("="*80)
    
    # Basic dataset info
    print(f" Dataset Shape: {df.shape[0]:,} rows × {df.shape[1]:,} columns")
    print(f" Data Types:")
    for dtype, count in df.dtypes.value_counts().items():
        print(f"   • {dtype}: {count} columns")
    
    # Missing values overview
    missing_total = df.isnull().sum().sum()
    missing_pct = (missing_total / (df.shape[0] * df.shape[1]) * 100)
    print(f" Missing Values: {missing_total:,} ({missing_pct:.1f}% of total data)")

    # Select only numeric columns for detailed stats
    numeric_df = df.select_dtypes(include=[np.number])
    
    if not numeric_df.empty:
        # Descriptive statistics with better formatting
        stats = numeric_df.describe(percentiles=[.25, .5, .75]).T
        stats['count'] = stats['count'].astype(int)
        stats['missing'] = len(df) - stats['count']
        stats['missing_pct'] = (stats['missing'] / len(df) * 100).round(1)
        
        # Rename columns for clarity
        stats = stats.rename(columns={
            'count': 'Count',
            'mean': 'Mean', 
            'std': 'Std',
            'min': 'Min',
            '25%': 'Q1',
            '50%': 'Median',
            '75%': 'Q3', 
            'max': 'Max',
            'missing': 'Missing',
            'missing_pct': 'Missing%'
        })
        
        # Format numeric values
        for col in ['Mean', 'Std', 'Min', 'Q1', 'Median', 'Q3', 'Max']:
            stats[col] = stats[col].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "NaN")
        
        stats['Count'] = stats['Count'].apply(lambda x: f"{x:,}")
        stats['Missing'] = stats['Missing'].apply(lambda x: f"{x:,}")
        stats['Missing%'] = stats['Missing%'].apply(lambda x: f"{x}%")
        
        print("\n" + "─" * 80)
        print(" NUMERIC VARIABLES SUMMARY")
        print("─" * 80)
        print(tabulate(stats, headers='keys', tablefmt='grid', stralign='right'))
        
        # Additional insights
        print("\n KEY INSIGHTS:")
        print("─" * 50)
        for col in numeric_df.columns:
            col_data = numeric_df[col].dropna()
            if len(col_data) > 0:
                cv = (col_data.std() / col_data.mean() * 100) if col_data.mean() != 0 else 0
                print(f"• {col:20}: {len(col_data):>6,} values | CV: {cv:>6.1f}% | Range: {col_data.min():>10,.1f} - {col_data.max():>10,.1f}")

        # Correlation matrix
        print("\n" + "─" * 80)
        print(" CORRELATION MATRIX")
        print("─" * 80)
        
        corr_matrix = numeric_df.corr(method='pearson')
        
        # Create a styled correlation matrix
        styled_corr = corr_matrix.copy()
        
        # Format values for display
        for col in styled_corr.columns:
            styled_corr[col] = styled_corr[col].apply(
                lambda x: 
                "1.000" if x == 1 else
                "—" if pd.isna(x) else
                f"{x:.3f}" if abs(x) >= 0.01 else
                f"{x:.1e}" if x != 0 else "0.000"
            )
        
        print(tabulate(styled_corr, headers='keys', tablefmt='grid', stralign='center'))
        
        # Highlight strong correlations
        print("\n STRONG CORRELATIONS (|r| > 0.5):")
        print("─" * 50)
        
        strong_corrs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.5 and not pd.isna(corr_val):
                    strong_corrs.append((
                        corr_matrix.columns[i],
                        corr_matrix.columns[j], 
                        corr_val
                    ))
        
        if strong_corrs:
            for var1, var2, corr in sorted(strong_corrs, key=lambda x: abs(x[2]), reverse=True):
                direction = "positive" if corr > 0 else "negative"
                strength = "strong" if abs(corr) > 0.7 else "moderate"
                print(f"• {var1} ↔ {var2}: {corr:.3f} ({strength} {direction})")
        else:
            print("No strong correlations found (|r| > 0.5)")

        # Save results to CSV (keeping original functionality)
        stats.to_csv(f"{output_dir}/descriptive_stats.csv", index=True)
        corr_matrix.to_csv(f"{output_dir}/correlation_matrix.csv", index=True)
        print(f"\n Stats saved in: {output_dir}/")
        
        return stats
        
    else:
        print("No numeric columns found for detailed analysis.")
        return pd.DataFrame()