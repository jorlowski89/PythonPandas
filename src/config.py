from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
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

SAMPLE_FILES = {
    "unemployment_rate": SAMPLE_DATA_DIR / "unemployment_sample.csv",
    "crime_metrics": SAMPLE_DATA_DIR / "crime_sample.csv",
}

API_SNAPSHOT_PATH = PROCESSED_DATA_DIR / "powiat_analysis_dataset.csv"
API_SNAPSHOT_METADATA_PATH = PROCESSED_DATA_DIR / "powiat_analysis_metadata.json"

INDICATOR_LABELS = {
    "unemployment_rate": "Stopa bezrobocia rejestrowanego (%)",
    "crimes_total_per_1000": "Przestepstwa ogolem na 1000 mieszkancow",
    "property_crimes_per_1000": "Przestepstwa przeciwko mieniu na 1000 mieszkancow",
    "violent_crimes_per_1000": "Przestepstwa przeciwko zyciu i zdrowiu na 1000 mieszkancow",
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
    "02": "Dolnoslaskie",
    "04": "Kujawsko-Pomorskie",
    "06": "Lubelskie",
    "08": "Lubuskie",
    "10": "Lodzkie",
    "12": "Malopolskie",
    "14": "Mazowieckie",
    "16": "Opolskie",
    "18": "Podkarpackie",
    "20": "Podlaskie",
    "22": "Pomorskie",
    "24": "Slaskie",
    "26": "Swietokrzyskie",
    "28": "Warminsko-Mazurskie",
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
