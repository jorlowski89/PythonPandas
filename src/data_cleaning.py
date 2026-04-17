from __future__ import annotations

from typing import Iterable

import pandas as pd

from src.config import CRIME_COLUMNS


def normalize_powiat_name(value: object) -> str:
    text = str(value or "").strip()
    return " ".join(text.split())


def prepare_unemployment_data(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    rename_map = {
        "year": "rok",
        "powiat_name": "powiat",
        "county": "powiat",
        "value": "unemployment_rate",
    }
    data = data.rename(columns=rename_map)
    required_columns = ["unit_id", "powiat", "wojewodztwo", "rok", "unemployment_rate"]
    data = data[required_columns].copy()
    data["powiat"] = data["powiat"].map(normalize_powiat_name)
    data["wojewodztwo"] = data["wojewodztwo"].fillna("Nieznane").map(normalize_powiat_name)
    data["rok"] = pd.to_numeric(data["rok"], errors="coerce").astype("Int64")
    data["unemployment_rate"] = pd.to_numeric(
        data["unemployment_rate"], errors="coerce"
    )
    data = data.dropna(subset=["rok", "powiat"]).copy()
    data["rok"] = data["rok"].astype(int)
    return data.sort_values(["powiat", "rok"]).reset_index(drop=True)


def prepare_crime_data(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    rename_map = {
        "year": "rok",
        "powiat_name": "powiat",
        "county": "powiat",
    }
    data = data.rename(columns=rename_map)
    for column in CRIME_COLUMNS:
        if column not in data.columns:
            data[column] = pd.NA

    required_columns = ["unit_id", "powiat", "wojewodztwo", "rok", *CRIME_COLUMNS]
    data = data[required_columns].copy()
    data["powiat"] = data["powiat"].map(normalize_powiat_name)
    data["wojewodztwo"] = data["wojewodztwo"].fillna("Nieznane").map(normalize_powiat_name)
    data["rok"] = pd.to_numeric(data["rok"], errors="coerce").astype("Int64")

    for column in CRIME_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=["rok", "powiat"]).copy()
    data["rok"] = data["rok"].astype(int)
    return data.sort_values(["powiat", "rok"]).reset_index(drop=True)


def pivot_bdl_indicator(frame: pd.DataFrame, value_column: str) -> pd.DataFrame:
    data = frame.copy()
    data["powiat"] = data["powiat"].map(normalize_powiat_name)
    data["wojewodztwo"] = data["wojewodztwo"].fillna("Nieznane").map(normalize_powiat_name)
    data["rok"] = pd.to_numeric(data["rok"], errors="coerce").astype("Int64")
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    data = data.dropna(subset=["rok", "powiat"]).copy()
    data["rok"] = data["rok"].astype(int)
    data = data.rename(columns={"value": value_column})
    return data[["unit_id", "powiat", "wojewodztwo", "rok", value_column]].copy()


def merge_indicator_frames(
    unemployment_frame: pd.DataFrame,
    crime_frame: pd.DataFrame,
) -> pd.DataFrame:
    merged = unemployment_frame.merge(
        crime_frame,
        on=["unit_id", "powiat", "wojewodztwo", "rok"],
        how="outer",
    )
    merged = merged.sort_values(["powiat", "rok"]).reset_index(drop=True)

    for column in ["unemployment_rate", *CRIME_COLUMNS]:
        if column not in merged.columns:
            merged[column] = pd.NA
        merged[column] = pd.to_numeric(merged[column], errors="coerce")

    merged["crime_minus_unemployment"] = (
        merged["crimes_total_per_1000"] - merged["unemployment_rate"]
    )
    return merged


def keep_complete_rows(
    frame: pd.DataFrame,
    required_columns: Iterable[str],
) -> pd.DataFrame:
    data = frame.copy()
    return data.dropna(subset=list(required_columns)).reset_index(drop=True)
