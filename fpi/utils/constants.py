VARS_TO_KEEP = [
    "Valeur fonciere",
    "Code postal",
    "Surface reelle bati",
    "Date mutation",
    "Surface terrain",
    "Nombre pieces principales",
]

NUMERIC_VARS = [
    "building_surface",
    "land_surface",
    "main_rooms",
]


VARS_TO_KEEP_SQL = [
    "Valeur_fonciere",  # = target variable
    "Code_departement",
    "Code_commune",
    "Nombre_de_lots",
    "Code_type_local",
    "Surface_reelle_bati",
    "Nombre_pieces_principales",
    "Surface_terrain",
]

VARS_TO_KEEP_SQL_EN = [
    "property_value",  # Valeur_fonciere = target variable
    "department_code",  # Code_departement
    "municipality_code",  # Code_commune
    "lot_count",  # Nombre_de_lots
    "property_type_code",  # Code_type_local
    "built_area",  # Surface_reelle_bati
    "room_count",  # Nombre_pieces_principales
    "land_area",  # Surface_terrain
]
