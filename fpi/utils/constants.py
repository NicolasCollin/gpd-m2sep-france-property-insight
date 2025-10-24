VARS_TO_KEEP = [
    "property_value",
    "postal_code",
    "department_code",
    "town_code",
    "property_type_code",
    "building_area",
    "main_rooms",
    "land_area",
]

VARS_TO_KEEP_FR = [
    "Valeur fonciere",
    "Code postal",
    "Surface reelle bati",
    "Date mutation",
    "Surface terrain",
    "Nombre pieces principales",
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

NUMERIC_VARS = [
    "building_area",
    "land_area",
    "main_rooms",
]
