from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

from src.config import CRIME_COLUMNS, DEFAULT_ANALYSIS_CRIME_COLUMN, INDICATOR_LABELS
from src.data_cleaning import keep_complete_rows


def _safe_correlation(series_x: pd.Series, series_y: pd.Series) -> dict[str, float]:
    paired = pd.concat([series_x, series_y], axis=1).dropna()
    if len(paired) < 3:
        return {
            "observations": len(paired),
            "pearson_r": np.nan,
            "pearson_p": np.nan,
            "spearman_rho": np.nan,
            "spearman_p": np.nan,
        }

    pearson_r, pearson_p = pearsonr(paired.iloc[:, 0], paired.iloc[:, 1])
    spearman_rho, spearman_p = spearmanr(paired.iloc[:, 0], paired.iloc[:, 1])
    return {
        "observations": len(paired),
        "pearson_r": float(pearson_r),
        "pearson_p": float(pearson_p),
        "spearman_rho": float(spearman_rho),
        "spearman_p": float(spearman_p),
    }


def dataset_overview(frame: pd.DataFrame) -> dict[str, object]:
    data = frame.copy()
    return {
        "observations": int(len(data)),
        "powiats": int(data["powiat"].nunique()),
        "years": sorted(data["rok"].dropna().unique().tolist()),
        "source_columns": data.columns.tolist(),
        "missing_values": data.isna().sum().sort_values(ascending=False).to_dict(),
    }


def descriptive_statistics(
    frame: pd.DataFrame,
    columns: Iterable[str] | None = None,
) -> pd.DataFrame:
    metrics = list(columns or ["unemployment_rate", *CRIME_COLUMNS])
    stats_rows: list[dict[str, object]] = []
    for column in metrics:
        if column not in frame.columns:
            continue
        series = pd.to_numeric(frame[column], errors="coerce").dropna()
        if series.empty:
            continue
        stats_rows.append(
            {
                "zmienna": INDICATOR_LABELS.get(column, column),
                "liczba_obserwacji": int(series.count()),
                "srednia": float(series.mean()),
                "mediana": float(series.median()),
                "minimum": float(series.min()),
                "maksimum": float(series.max()),
                "odchylenie_std": float(series.std(ddof=1)),
            }
        )
    return pd.DataFrame(stats_rows)


def yearly_average_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.groupby("rok", as_index=False)[
        ["unemployment_rate", *CRIME_COLUMNS]
    ].mean(numeric_only=True)
    return data.sort_values("rok").reset_index(drop=True)


def year_over_year_changes(frame: pd.DataFrame) -> pd.DataFrame:
    yearly = yearly_average_metrics(frame).copy()
    for column in ["unemployment_rate", *CRIME_COLUMNS]:
        yearly[f"{column}_yoy_pct"] = yearly[column].pct_change() * 100
    return yearly


def powiat_year_over_year_changes(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.sort_values(["powiat", "rok"]).copy()
    for column in ["unemployment_rate", *CRIME_COLUMNS]:
        data[f"{column}_yoy_pct"] = data.groupby("powiat")[column].pct_change() * 100
    return data


def global_correlations(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for crime_column in CRIME_COLUMNS:
        if crime_column not in frame.columns:
            continue
        metrics = _safe_correlation(frame["unemployment_rate"], frame[crime_column])
        rows.append(
            {
                "para_zmiennych": f"Bezrobocie vs {INDICATOR_LABELS.get(crime_column, crime_column)}",
                **metrics,
            }
        )
    return pd.DataFrame(rows)


def yearly_correlations(
    frame: pd.DataFrame,
    crime_column: str = DEFAULT_ANALYSIS_CRIME_COLUMN,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for year, subset in frame.groupby("rok"):
        metrics = _safe_correlation(subset["unemployment_rate"], subset[crime_column])
        rows.append({"rok": int(year), **metrics})
    return pd.DataFrame(rows).sort_values("rok").reset_index(drop=True)


def lagged_dataset(
    frame: pd.DataFrame,
    crime_column: str = DEFAULT_ANALYSIS_CRIME_COLUMN,
    lag_years: int = 1,
) -> pd.DataFrame:
    data = frame.sort_values(["powiat", "rok"]).copy()
    data[f"{crime_column}_next_year"] = data.groupby("powiat")[crime_column].shift(
        -lag_years
    )
    result = keep_complete_rows(
        data,
        ["unemployment_rate", f"{crime_column}_next_year"],
    )
    return result.reset_index(drop=True)


def lagged_correlation(
    frame: pd.DataFrame,
    crime_column: str = DEFAULT_ANALYSIS_CRIME_COLUMN,
    lag_years: int = 1,
) -> dict[str, object]:
    lagged = lagged_dataset(frame, crime_column=crime_column, lag_years=lag_years)
    metrics = _safe_correlation(
        lagged["unemployment_rate"], lagged[f"{crime_column}_next_year"]
    )
    metrics["lagged_frame"] = lagged
    return metrics


def detect_outlier_powiats(
    frame: pd.DataFrame,
    crime_column: str = DEFAULT_ANALYSIS_CRIME_COLUMN,
    top_n: int = 8,
) -> pd.DataFrame:
    data = keep_complete_rows(frame, ["unemployment_rate", crime_column]).copy()
    if len(data) < 3:
        return pd.DataFrame()

    slope, intercept = np.polyfit(
        data["unemployment_rate"].to_numpy(),
        data[crime_column].to_numpy(),
        1,
    )
    data["expected_crime"] = intercept + slope * data["unemployment_rate"]
    data["residual"] = data[crime_column] - data["expected_crime"]

    grouped = (
        data.groupby("powiat", as_index=False)
        .agg(
            wojewodztwo=("wojewodztwo", "first"),
            srednie_bezrobocie=("unemployment_rate", "mean"),
            srednia_przestepczosc=(crime_column, "mean"),
            srednia_reszta=("residual", "mean"),
            liczba_obserwacji=("rok", "count"),
        )
        .sort_values("srednia_reszta", key=lambda series: series.abs(), ascending=False)
    )

    residual_std = grouped["srednia_reszta"].std(ddof=0)
    if residual_std and not np.isnan(residual_std):
        grouped["outlier_score"] = grouped["srednia_reszta"].abs() / residual_std
    else:
        grouped["outlier_score"] = 0.0

    grouped["kierunek"] = np.where(
        grouped["srednia_reszta"] >= 0,
        "Powyzej trendu",
        "Ponizej trendu",
    )
    grouped["interpretacja"] = np.where(
        grouped["srednia_reszta"] >= 0,
        "Przestepczosc jest wyzsza, niz sugerowalby poziom bezrobocia.",
        "Przestepczosc jest nizsza, niz sugerowalby poziom bezrobocia.",
    )
    return grouped.head(top_n).reset_index(drop=True)


def correlation_strength_label(value: float) -> str:
    if pd.isna(value):
        return "Brak danych"
    absolute = abs(value)
    if absolute < 0.2:
        return "Bardzo slaba"
    if absolute < 0.4:
        return "Slaba"
    if absolute < 0.6:
        return "Umiarkowana"
    if absolute < 0.8:
        return "Silna"
    return "Bardzo silna"


def generate_conclusions(frame: pd.DataFrame) -> dict[str, object]:
    global_corr = global_correlations(frame)
    yearly_corr = yearly_correlations(frame)
    lagged = lagged_correlation(frame)

    total_row = global_corr[
        global_corr["para_zmiennych"].str.contains("ogolem", case=False, na=False)
    ]
    property_row = global_corr[
        global_corr["para_zmiennych"].str.contains("mieniu", case=False, na=False)
    ]

    current_total_corr = (
        float(total_row["pearson_r"].iloc[0]) if not total_row.empty else np.nan
    )
    property_corr = (
        float(property_row["pearson_r"].iloc[0]) if not property_row.empty else np.nan
    )
    lagged_corr_value = float(lagged["pearson_r"]) if not pd.isna(lagged["pearson_r"]) else np.nan
    yearly_spread = yearly_corr["pearson_r"].max() - yearly_corr["pearson_r"].min()

    findings = [
        (
            "W calym zbiorze zaleznosc miedzy bezrobociem a przestepczoscia ogolem jest "
            f"{correlation_strength_label(current_total_corr).lower()} "
            f"(Pearson r = {current_total_corr:.3f})."
            if not pd.isna(current_total_corr)
            else "Nie udalo sie policzyc stabilnej korelacji dla przestepczosci ogolem."
        ),
        (
            "Korelacje liczone osobno dla kolejnych lat zmieniaja sie, co sugeruje, ze "
            "sila zaleznosci nie jest identyczna w calym badanym okresie."
            if not pd.isna(yearly_spread) and yearly_spread > 0.15
            else "Korelacje roczne sa dosc zblizone, wiec zaleznosc wyglada na względnie stabilna."
        ),
        (
            "Dla przestepstw przeciwko mieniu zaleznosc jest silniejsza niz dla przestepczosci ogolem."
            if not pd.isna(property_corr)
            and not pd.isna(current_total_corr)
            and property_corr > current_total_corr
            else "Dla przestepstw przeciwko mieniu nie widac wyraznie silniejszej zaleznosci niz dla ogolu."
        ),
        (
            "Analiza opoznienia o 1 rok pokazuje silniejsza zaleznosc niz analiza bez opoznienia."
            if not pd.isna(lagged_corr_value)
            and not pd.isna(current_total_corr)
            and lagged_corr_value > current_total_corr
            else "Analiza opoznienia o 1 rok nie wzmacnia zaleznosci w sposob jednoznaczny."
        ),
    ]

    hypotheses = pd.DataFrame(
        [
            {
                "hipoteza": "H1: Wyższe bezrobocie wiąże się z wyższą przestępczością.",
                "ocena": "Wstepnie potwierdzona"
                if not pd.isna(current_total_corr) and current_total_corr > 0
                else "Niepotwierdzona",
                "uzasadnienie": findings[0],
            },
            {
                "hipoteza": "H2: Zależność zmienia się w czasie.",
                "ocena": "Czesciowo potwierdzona"
                if not pd.isna(yearly_spread) and yearly_spread > 0.15
                else "Raczej niepotwierdzona",
                "uzasadnienie": findings[1],
            },
            {
                "hipoteza": "H3: Zależność jest silniejsza dla przestępstw przeciwko mieniu.",
                "ocena": "Potwierdzona"
                if not pd.isna(property_corr)
                and not pd.isna(current_total_corr)
                and property_corr > current_total_corr
                else "Niepotwierdzona",
                "uzasadnienie": findings[2],
            },
            {
                "hipoteza": "H4: Zależność jest lepiej widoczna przy opóźnieniu o 1 rok.",
                "ocena": "Potwierdzona"
                if not pd.isna(lagged_corr_value)
                and not pd.isna(current_total_corr)
                and lagged_corr_value > current_total_corr
                else "Niepotwierdzona",
                "uzasadnienie": findings[3],
            },
        ]
    )

    limitations = [
        "Projekt bada zaleznosc statystyczna, a nie zwiazek przyczynowo-skutkowy.",
        "Dla wersji demonstracyjnej aplikacja moze korzystac z danych przykładowych, jesli identyfikatory BDL nie zostaly uzupelnione.",
        "Na poziom przestepczosci moga wplywac tez inne czynniki, np. urbanizacja, dochody czy struktura demograficzna.",
    ]

    return {
        "findings": findings,
        "hypotheses": hypotheses,
        "limitations": limitations,
    }
