from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ASSETS_DIR = BASE_DIR / "assets"

YEARS = list(range(2014, 2025))
DEFAULT_POWIAT_LEVEL = 5
API_TIMEOUT_SECONDS = 30
BDL_BASE_URL = "https://bdl.stat.gov.pl/api/v1"
BDL_CLIENT_ID = os.getenv("BDL_CLIENT_ID", "")

BDL_VARIABLE_IDS = {
    "unemployment_rate": 395392,
    "crimes_total_per_1000": 398594,
    "property_crimes_per_1000": 498623,
    "violent_crimes_per_1000": 498624,
}

API_SNAPSHOT_PATH = PROCESSED_DATA_DIR / "powiat_analysis_dataset.csv"
API_SNAPSHOT_METADATA_PATH = PROCESSED_DATA_DIR / "powiat_analysis_metadata.json"

INDICATOR_LABELS = {
    "unemployment_rate": "Stopa bezrobocia rejestrowanego (%)",
    "crimes_total_per_1000": "Przestępstwa ogółem na 1000 mieszkańców",
    "property_crimes_per_1000": "Przestępstwa przeciwko mieniu na 1000 mieszkańców",
    "violent_crimes_per_1000": "Przestępstwa przeciwko życiu i zdrowiu na 1000 mieszkańców",
}

CRIME_COLUMNS = [
    "crimes_total_per_1000",
    "property_crimes_per_1000",
    "violent_crimes_per_1000",
]

DEFAULT_ANALYSIS_CRIME_COLUMN = "crimes_total_per_1000"

PLOTLY_TEMPLATE = "plotly_white"
COLOR_SEQUENCE = ["#0f766e", "#2563eb", "#dc2626", "#ca8a04", "#7c3aed"]

VOIVODESHIP_CODES = {
    "02": "Dolnośląskie",
    "04": "Kujawsko-Pomorskie",
    "06": "Lubelskie",
    "08": "Lubuskie",
    "10": "Łódzkie",
    "12": "Małopolskie",
    "14": "Mazowieckie",
    "16": "Opolskie",
    "18": "Podkarpackie",
    "20": "Podlaskie",
    "22": "Pomorskie",
    "24": "Śląskie",
    "26": "Świętokrzyskie",
    "28": "Warmińsko-Mazurskie",
    "30": "Wielkopolskie",
    "32": "Zachodniopomorskie",
}


def api_headers() -> dict[str, str]:
    headers: dict[str, str] = {"Accept": "application/json"}
    if BDL_CLIENT_ID:
        headers["X-ClientId"] = BDL_CLIENT_ID
    return headers


def has_minimum_api_configuration() -> bool:
    return all(
        BDL_VARIABLE_IDS.get(required_key)
        for required_key in ("unemployment_rate", "crimes_total_per_1000")
    )
