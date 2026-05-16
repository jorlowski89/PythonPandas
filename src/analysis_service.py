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


def descriptive_statistics_by_voivodeship(
    frame: pd.DataFrame,
    columns: Iterable[str] | None = None,
) -> pd.DataFrame:
    metrics = list(columns or ["unemployment_rate", DEFAULT_ANALYSIS_CRIME_COLUMN])
    rows: list[dict[str, object]] = []
    for voivodeship, subset in frame.groupby("wojewodztwo"):
        row: dict[str, object] = {
            "wojewodztwo": voivodeship,
            "liczba_powiatow": int(subset["powiat"].nunique()),
            "liczba_obserwacji": int(len(subset)),
        }
        for column in metrics:
            if column not in subset.columns:
                continue
            series = pd.to_numeric(subset[column], errors="coerce").dropna()
            if series.empty:
                row[f"{column}_srednia"] = np.nan
                row[f"{column}_mediana"] = np.nan
                row[f"{column}_std"] = np.nan
                continue
            row[f"{column}_srednia"] = float(series.mean())
            row[f"{column}_mediana"] = float(series.median())
            row[f"{column}_std"] = float(series.std(ddof=1)) if len(series) > 1 else 0.0
        rows.append(row)
    result = pd.DataFrame(rows)
    if not result.empty:
        result = result.sort_values("wojewodztwo").reset_index(drop=True)
    return result


def yearly_metrics_by_voivodeship(frame: pd.DataFrame) -> pd.DataFrame:
    data = (
        frame.groupby(["wojewodztwo", "rok"], as_index=False)[
            ["unemployment_rate", *CRIME_COLUMNS]
        ]
        .mean(numeric_only=True)
    )
    return data.sort_values(["wojewodztwo", "rok"]).reset_index(drop=True)


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


def voivodeship_correlations(
    frame: pd.DataFrame,
    crime_column: str = DEFAULT_ANALYSIS_CRIME_COLUMN,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for voivodeship, subset in frame.groupby("wojewodztwo"):
        metrics = _safe_correlation(subset["unemployment_rate"], subset[crime_column])
        rows.append(
            {
                "wojewodztwo": voivodeship,
                "liczba_powiatow": int(subset["powiat"].nunique()),
                **metrics,
            }
        )
    return (
        pd.DataFrame(rows)
        .sort_values("pearson_r", ascending=False, na_position="last")
        .reset_index(drop=True)
    )


def between_within_decomposition(
    frame: pd.DataFrame,
    crime_column: str = DEFAULT_ANALYSIS_CRIME_COLUMN,
) -> pd.DataFrame:
    data = keep_complete_rows(frame, ["unemployment_rate", crime_column, "wojewodztwo"]).copy()
    if data.empty:
        return pd.DataFrame()

    pooled = _safe_correlation(data["unemployment_rate"], data[crime_column])

    voivodeship_means = data.groupby("wojewodztwo", as_index=False)[
        ["unemployment_rate", crime_column]
    ].mean()
    between = _safe_correlation(
        voivodeship_means["unemployment_rate"], voivodeship_means[crime_column]
    )

    data["unemployment_within"] = data["unemployment_rate"] - data.groupby("wojewodztwo")[
        "unemployment_rate"
    ].transform("mean")
    data["crime_within"] = data[crime_column] - data.groupby("wojewodztwo")[
        crime_column
    ].transform("mean")
    within = _safe_correlation(data["unemployment_within"], data["crime_within"])

    rows = [
        {
            "poziom": "Pooled (wszystkie obserwacje)",
            "interpretacja": "Korelacja liczona na surowych danych, bez kontroli regionu.",
            **pooled,
        },
        {
            "poziom": "Between (miedzy wojewodztwami)",
            "interpretacja": "Czy regiony o wyzszym sredniem bezrobociu maja tez wyzsza srednia przestepczosc.",
            **between,
        },
        {
            "poziom": "Within (wewnatrz wojewodztw)",
            "interpretacja": "Czy w obrebie jednego regionu wyzsze bezrobocie idzie z wyzsza przestepczoscia (po odjeciu sredniej regionalnej).",
            **within,
        },
    ]
    return pd.DataFrame(rows)


def voivodeship_lagged_correlations(
    frame: pd.DataFrame,
    crime_column: str = DEFAULT_ANALYSIS_CRIME_COLUMN,
    lag_years: int = 1,
) -> pd.DataFrame:
    lagged = lagged_dataset(frame, crime_column=crime_column, lag_years=lag_years)
    if lagged.empty:
        return pd.DataFrame()

    next_year_column = f"{crime_column}_next_year"
    rows: list[dict[str, object]] = []
    for voivodeship, subset in lagged.groupby("wojewodztwo"):
        metrics = _safe_correlation(subset["unemployment_rate"], subset[next_year_column])
        rows.append(
            {
                "wojewodztwo": voivodeship,
                "liczba_par": int(metrics["observations"]),
                **{k: v for k, v in metrics.items() if k != "observations"},
            }
        )
    return (
        pd.DataFrame(rows)
        .sort_values("pearson_r", ascending=False, na_position="last")
        .reset_index(drop=True)
    )


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


def _fit_residuals(group: pd.DataFrame, crime_column: str) -> pd.DataFrame:
    block = group.copy()
    if len(block) < 3 or block["unemployment_rate"].nunique() < 2:
        block["expected_crime"] = block[crime_column].mean()
    else:
        slope, intercept = np.polyfit(
            block["unemployment_rate"].to_numpy(),
            block[crime_column].to_numpy(),
            1,
        )
        block["expected_crime"] = intercept + slope * block["unemployment_rate"]
    block["residual"] = block[crime_column] - block["expected_crime"]
    return block


def detect_outlier_powiats(
    frame: pd.DataFrame,
    crime_column: str = DEFAULT_ANALYSIS_CRIME_COLUMN,
    top_n: int = 8,
    group_by: str | None = None,
) -> pd.DataFrame:
    data = keep_complete_rows(frame, ["unemployment_rate", crime_column]).copy()
    if len(data) < 3:
        return pd.DataFrame()

    if group_by and group_by in data.columns:
        blocks = [
            _fit_residuals(block, crime_column)
            for _, block in data.groupby(group_by, sort=False)
        ]
        data = pd.concat(blocks, ignore_index=True)
    else:
        data = _fit_residuals(data, crime_column)

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


def generate_regional_conclusions(
    frame: pd.DataFrame,
    crime_column: str = DEFAULT_ANALYSIS_CRIME_COLUMN,
) -> dict[str, object]:
    voivodeship_corr = voivodeship_correlations(frame, crime_column=crime_column)
    decomposition = between_within_decomposition(frame, crime_column=crime_column)
    outliers_global = detect_outlier_powiats(
        frame, crime_column=crime_column, top_n=5, group_by=None
    )
    outliers_regional = detect_outlier_powiats(
        frame, crime_column=crime_column, top_n=5, group_by="wojewodztwo"
    )

    findings: list[str] = []

    # 1. Global correlation — direction & strength
    pooled_r = np.nan
    if not decomposition.empty:
        pooled_row = decomposition[decomposition["poziom"].str.startswith("Pooled")]
        if not pooled_row.empty:
            pooled_r = float(pooled_row["pearson_r"].iloc[0])

    if not pd.isna(pooled_r):
        direction = "ujemny" if pooled_r < 0 else "dodatni"
        interpretation = (
            "wyzsze bezrobocie wiaze sie z NIZSZA przestepczoscia"
            if pooled_r < 0
            else "wyzsze bezrobocie wiaze sie z WYZSZA przestepczoscia"
        )
        findings.append(
            f"Globalna korelacja Pearsona = {pooled_r:.3f} (kierunek {direction}, sila "
            f"{correlation_strength_label(pooled_r).lower()}). Oznacza to, ze w danych "
            f"powiatowych z lat objetych analiza {interpretation} - co {'przeczy' if pooled_r < 0 else 'potwierdza'} "
            "intuicyjnej hipotezie H1."
        )

    # 2. Between vs within — Simpson's paradox check
    between_r = np.nan
    within_r = np.nan
    if not decomposition.empty:
        between_row = decomposition[decomposition["poziom"].str.startswith("Between")]
        within_row = decomposition[decomposition["poziom"].str.startswith("Within")]
        if not between_row.empty:
            between_r = float(between_row["pearson_r"].iloc[0])
        if not within_row.empty:
            within_r = float(within_row["pearson_r"].iloc[0])

    if not pd.isna(between_r) and not pd.isna(within_r):
        ratio_msg = ""
        if within_r != 0:
            ratio = abs(between_r) / max(abs(within_r), 1e-9)
            if ratio >= 1.5:
                ratio_msg = (
                    f" Efekt jest okolo {ratio:.1f}x silniejszy miedzy regionami niz wewnatrz nich, "
                    "co jest sygnalem paradoksu ekologicznego: agregacja powiatowa miesza efekty "
                    "regionalne z indywidualnymi."
                )
            elif ratio <= 0.7:
                ratio_msg = (
                    " Efekt wewnatrz regionow jest silniejszy niz miedzy nimi - faktyczna dynamika "
                    "rozgrywa sie wewnatrz regionow, niezaleznie od ich sredniego poziomu."
                )
        sign_flip = (between_r * within_r < 0)
        flip_msg = (
            " UWAGA: znak korelacji between i within sa przeciwne - klasyczny przypadek paradoksu Simpsona, "
            "gdzie wniosek globalny nie obowiazuje na zadnym poziomie pojedynczym."
            if sign_flip
            else ""
        )
        findings.append(
            f"Dekompozycja korelacji: between (miedzy wojewodztwami) = {between_r:.3f}, "
            f"within (wewnatrz wojewodztw) = {within_r:.3f}.{ratio_msg}{flip_msg}"
        )

    # 3. Regional heterogeneity
    if not voivodeship_corr.empty and voivodeship_corr["pearson_r"].notna().any():
        valid = voivodeship_corr.dropna(subset=["pearson_r"])
        top = valid.iloc[0]
        bottom = valid.iloc[-1]
        spread = float(top["pearson_r"]) - float(bottom["pearson_r"])
        sign_flips = (
            (valid["pearson_r"] > 0).any() and (valid["pearson_r"] < 0).any()
        )
        flip_note = (
            " Co najmniej jedno wojewodztwo lamie kierunek korelacji - zaleznosc nie jest jednorodna w kraju."
            if sign_flips
            else ""
        )
        findings.append(
            f"Heterogenicznosc regionalna jest duza: r waha sie od {float(top['pearson_r']):+.3f} "
            f"({top['wojewodztwo']}) do {float(bottom['pearson_r']):+.3f} ({bottom['wojewodztwo']}); "
            f"rozpietosc = {spread:.3f}.{flip_note}"
        )

    # 4. Outlier overlap (global vs regional trend)
    if not outliers_global.empty and not outliers_regional.empty:
        global_set = set(outliers_global["powiat"].tolist())
        regional_set = set(outliers_regional["powiat"].tolist())
        overlap = global_set & regional_set
        only_global = global_set - regional_set
        only_regional = regional_set - global_set
        findings.append(
            f"Wsrod top-5 outlierow: {len(overlap)} powiatow jest wyjatkowych zarowno wzgl. trendu globalnego, "
            f"jak i regionalnego ({', '.join(sorted(overlap)) or 'brak'}). "
            f"Tylko globalnie wyrozniaja sie: {', '.join(sorted(only_global)) or 'brak'}. "
            f"Tylko regionalnie wyrozniaja sie: {', '.join(sorted(only_regional)) or 'brak'}. "
            "Roznice pokazuja, ktore powiaty sa nietypowe na tle kraju, a ktore na tle wlasnego regionu."
        )

    return {
        "findings": findings,
        "decomposition": decomposition,
        "voivodeship_correlations": voivodeship_corr,
        "outliers_global": outliers_global,
        "outliers_regional": outliers_regional,
    }
