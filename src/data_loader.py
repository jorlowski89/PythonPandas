from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from src.config import (
    API_SNAPSHOT_METADATA_PATH,
    API_SNAPSHOT_PATH,
    API_TIMEOUT_SECONDS,
    BDL_BASE_URL,
    BDL_VARIABLE_IDS,
    CRIME_COLUMNS,
    DEFAULT_POWIAT_LEVEL,
    INDICATOR_LABELS,
    RAW_DATA_DIR,
    SAMPLE_FILES,
    VOIVODESHIP_CODES,
    YEARS,
    api_headers,
    has_minimum_api_configuration,
)
from src.data_cleaning import (
    merge_indicator_frames,
    pivot_bdl_indicator,
    prepare_crime_data,
    prepare_unemployment_data,
)


class DataLoadError(RuntimeError):
    """Wyjatek sygnalizujacy problem z pobieraniem danych."""


def _build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(api_headers())
    return session


def _request_json(endpoint: str, params: list[tuple[str, Any]]) -> dict[str, Any]:
    url = f"{BDL_BASE_URL}/{endpoint.lstrip('/')}"
    session = _build_session()
    response = session.get(url, params=params, timeout=API_TIMEOUT_SECONDS)
    response.encoding = "utf-8"
    if response.status_code == 429:
        raise DataLoadError(
            "API GUS BDL zwrocilo status 429 (limit zapytan). "
            "Sprobuj ponownie pozniej albo ustaw zmienna srodowiskowa BDL_CLIENT_ID."
        )
    response.raise_for_status()
    return response.json()


def infer_wojewodztwo_from_unit_id(unit_id: object) -> str:
    text = str(unit_id or "")
    return VOIVODESHIP_CODES.get(text[:2], "Nieznane")


def search_bdl_variables(query: str, page_size: int = 10) -> pd.DataFrame:
    payload = _request_json(
        "variables",
        [("format", "json"), ("name", query), ("page-size", page_size), ("page", 0)],
    )
    return pd.DataFrame(payload.get("results", []))


def fetch_bdl_variable_data(
    variable_id: str | int,
    years: list[int] | None = None,
    unit_level: int = DEFAULT_POWIAT_LEVEL,
) -> pd.DataFrame:
    selected_years = years or YEARS
    page = 0
    records: list[dict[str, Any]] = []

    while True:
        params: list[tuple[str, Any]] = [
            ("format", "json"),
            ("unit-level", unit_level),
            ("page-size", 100),
            ("page", page),
        ]
        params.extend(("year", year) for year in selected_years)
        payload = _request_json(f"data/by-variable/{variable_id}", params)
        results = payload.get("results", [])

        for unit in results:
            for value_item in unit.get("values", []):
                records.append(
                    {
                        "unit_id": unit.get("id"),
                        "powiat": unit.get("name"),
                        "wojewodztwo": infer_wojewodztwo_from_unit_id(unit.get("id")),
                        "rok": value_item.get("year"),
                        "value": value_item.get("val"),
                    }
                )

        if not payload.get("links", {}).get("next"):
            break
        page += 1

    if not records:
        raise DataLoadError(f"Brak danych dla zmiennej BDL o id={variable_id}.")

    return pd.DataFrame(records)


def save_frame(frame: pd.DataFrame, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(target_path, index=False, encoding="utf-8")


def save_api_metadata(metadata: dict[str, Any]) -> None:
    API_SNAPSHOT_METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    API_SNAPSHOT_METADATA_PATH.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_cached_api_dataset() -> dict[str, Any]:
    if not API_SNAPSHOT_PATH.exists():
        raise DataLoadError("Brak lokalnej migawki danych pobranych z API.")

    data = pd.read_csv(API_SNAPSHOT_PATH)
    metadata: dict[str, Any] = {}
    if API_SNAPSHOT_METADATA_PATH.exists():
        metadata = json.loads(API_SNAPSHOT_METADATA_PATH.read_text(encoding="utf-8"))

    metadata.setdefault("source", "api_cache")
    metadata.setdefault("messages", [])
    metadata["messages"] = list(metadata["messages"])
    metadata["messages"].append(
        "Zaladowano ostatnia zapisana migawke danych pobranych z API GUS BDL."
    )
    metadata["observations"] = int(len(data))
    metadata["powiat_count"] = int(data["powiat"].nunique())
    metadata["year_min"] = int(data["rok"].min())
    metadata["year_max"] = int(data["rok"].max())
    metadata["columns"] = data.columns.tolist()
    return {
        "data": data,
        "metadata": metadata,
        "indicator_labels": INDICATOR_LABELS,
    }


def load_sample_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    unemployment_frame = pd.read_csv(SAMPLE_FILES["unemployment_rate"])
    crime_frame = pd.read_csv(SAMPLE_FILES["crime_metrics"])
    return unemployment_frame, crime_frame


def load_api_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    unemployment_raw = fetch_bdl_variable_data(BDL_VARIABLE_IDS["unemployment_rate"])
    total_crime_raw = fetch_bdl_variable_data(BDL_VARIABLE_IDS["crimes_total_per_1000"])

    save_frame(unemployment_raw, RAW_DATA_DIR / "bdl_unemployment_raw.csv")
    save_frame(total_crime_raw, RAW_DATA_DIR / "bdl_crimes_total_raw.csv")

    unemployment_frame = pivot_bdl_indicator(unemployment_raw, "unemployment_rate")
    crime_frame = pivot_bdl_indicator(total_crime_raw, "crimes_total_per_1000")

    for optional_column in ("property_crimes_per_1000", "violent_crimes_per_1000"):
        variable_id = BDL_VARIABLE_IDS.get(optional_column)
        if not variable_id:
            crime_frame[optional_column] = pd.NA
            continue

        optional_raw = fetch_bdl_variable_data(variable_id)
        save_frame(optional_raw, RAW_DATA_DIR / f"bdl_{optional_column}_raw.csv")
        optional_frame = pivot_bdl_indicator(optional_raw, optional_column)
        crime_frame = crime_frame.merge(
            optional_frame,
            on=["unit_id", "powiat", "wojewodztwo", "rok"],
            how="outer",
        )

    for column in CRIME_COLUMNS:
        if column not in crime_frame.columns:
            crime_frame[column] = pd.NA

    return unemployment_frame, crime_frame


@lru_cache(maxsize=4)
def load_project_data(
    prefer_api: bool = True,
    allow_api_cache: bool = True,
    allow_sample_fallback: bool = False,
) -> dict[str, Any]:
    messages: list[str] = []
    source = "api"

    if prefer_api and has_minimum_api_configuration():
        try:
            unemployment_frame, crime_frame = load_api_frames()
            messages.append(
                "Dane zostaly pobrane z API GUS BDL na poziomie powiatow."
            )
        except (requests.RequestException, DataLoadError, ValueError) as exc:
            if allow_api_cache and API_SNAPSHOT_PATH.exists():
                cached_bundle = load_cached_api_dataset()
                cached_bundle["metadata"]["messages"].insert(
                    0,
                    "Nie udalo sie odswiezyc danych bezposrednio z API GUS BDL. "
                    f"Uzyto zapisanej migawki API. Szczegoly: {exc}",
                )
                return cached_bundle

            if allow_sample_fallback:
                messages.append(
                    "Pobieranie z API GUS BDL nie powiodlo sie. Uzyto danych przykladowych. "
                    f"Szczegoly: {exc}"
                )
                source = "sample"
                unemployment_frame, crime_frame = load_sample_frames()
            else:
                raise DataLoadError(
                    "Nie udalo sie pobrac danych z API GUS BDL i brak lokalnej migawki API. "
                    f"Szczegoly: {exc}"
                ) from exc
    else:
        if allow_api_cache and API_SNAPSHOT_PATH.exists():
            return load_cached_api_dataset()

        if allow_sample_fallback:
            messages.append("Nie mozna skorzystac z API. Uzyto danych przykladowych.")
            source = "sample"
            unemployment_frame, crime_frame = load_sample_frames()
        else:
            raise DataLoadError(
                "Brak poprawnej konfiguracji API GUS BDL i brak lokalnej migawki API."
            )

    unemployment_clean = prepare_unemployment_data(unemployment_frame)
    crime_clean = prepare_crime_data(crime_frame)
    merged = merge_indicator_frames(unemployment_clean, crime_clean)

    save_frame(merged, API_SNAPSHOT_PATH)

    metadata = {
        "source": source,
        "observations": int(len(merged)),
        "powiat_count": int(merged["powiat"].nunique()),
        "year_min": int(merged["rok"].min()),
        "year_max": int(merged["rok"].max()),
        "columns": merged.columns.tolist(),
        "messages": messages,
    }
    save_api_metadata(metadata)

    return {
        "data": merged,
        "metadata": metadata,
        "indicator_labels": INDICATOR_LABELS,
    }
