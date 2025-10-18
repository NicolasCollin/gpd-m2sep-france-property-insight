import matplotlib.pyplot as plt
import pandas as pd


def exp():
    df = pd.read_csv("data/raw/sample2024.txt", sep="|", header=0)
    print("Aperçu des premières lignes :")
    print(df.head(), "\n")

    print("Info dataframe :")
    print(df.info(), "\n")

    print(f"Dimensions : {df.shape[0]} lignes × {df.shape[1]} colonnes\n")
    print("Colonnes :", list(df.columns), "\n")

    # Valeurs manquantes
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        print("Valeurs manquantes :")
        print(missing, "\n")

    # Sélection des variables
    vars_to_keep = [
        "Valeur fonciere",
        "Code postal",
        "Surface reelle bati",
        "Surface terrain",
        "Nombre pieces principales",
    ]
    df = df[vars_to_keep]

    #  Statistiques descriptives
    print("Statistiques descriptives :")
    print(df.describe(include="all").transpose(), "\n")

    #  Visualisation : histogrammes
    numeric_cols = ["Valeur fonciere", "Surface reelle bati", "Surface terrain", "Nombre pieces principales"]
    df_numeric = df[numeric_cols]

    df_numeric.hist(figsize=(12, 8), bins=30)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    exp()
