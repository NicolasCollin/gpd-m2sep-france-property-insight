from fpi.data_pipeline.loader import load_all_csv
from fpi.analysis.report import (
    count_missing_values,
    count_type_local,
    detect_outliers,
    analyze_dataset_quality,
)

def report_data () -> None:

   df = load_all_csv("data/raw")

   print("=== Effectifs de NA par colonne ===")
   print(count_missing_values(df))

   print("\n=== Effectifs par type_local ===")
   print(count_type_local(df))

   print("\n=== Outliers par colonne numérique ===")
   print(detect_outliers(df))

   print("\n=== Rapport global ===")
   print(analyze_dataset_quality(df))