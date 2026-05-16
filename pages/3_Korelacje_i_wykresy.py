from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analysis_service import (
    between_within_decomposition,
    global_correlations,
    lagged_correlation,
    voivodeship_correlations,
    voivodeship_lagged_correlations,
    yearly_correlations,
)
from src.config import CRIME_COLUMNS, INDICATOR_LABELS
from src.data_loader import DataLoadError, load_project_data
from src.help_content import render_page_help
from src.ui_components import render_data_source_sidebar
from src.visualization import (
    build_lag_scatter_figure,
    build_scatter_figure,
    build_voivodeship_correlation_bar_figure,
    build_yearly_correlation_figure,
)

st.title("Korelacje i wykresy")

render_page_help(
    st,
    page_key="korelacje",
    glossary_terms=[
        "pearson_r",
        "pearson_p",
        "spearman_rho",
        "spearman_p",
        "skala_sily_korelacji",
        "liczba_obserwacji",
        "liczba_par",
        "lag",
        "pooled",
        "between",
        "within",
        "paradoks_simpsona",
    ],
)

try:
    bundle = load_project_data()
except DataLoadError as exc:
    st.error(f"Nie udalo sie zaladowac danych. Szczegoly: {exc}")
    st.stop()

render_data_source_sidebar(st, bundle)

data = bundle["data"].copy()

selected_crime_column = st.sidebar.selectbox(
    "Wybierz kategorię przestępczości",
    CRIME_COLUMNS,
    format_func=lambda column: INDICATOR_LABELS[column],
)

available_years = sorted(data["rok"].unique().tolist())
selected_years = st.sidebar.multiselect("Lata", available_years, default=available_years)

filtered = data[data["rok"].isin(selected_years)].copy()
if filtered.empty:
    st.warning("Brak danych dla wybranego zakresu lat.")
    st.stop()

global_corr = global_correlations(filtered)
yearly_corr = yearly_correlations(filtered, crime_column=selected_crime_column)
lagged = lagged_correlation(filtered, crime_column=selected_crime_column)

st.subheader("Korelacje dla całego zbioru")
st.dataframe(
    global_corr.style.format(
        {
            "pearson_r": "{:.3f}",
            "pearson_p": "{:.4f}",
            "spearman_rho": "{:.3f}",
            "spearman_p": "{:.4f}",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

col_left, col_right = st.columns(2)

with col_left:
    st.plotly_chart(
        build_scatter_figure(
            filtered,
            selected_crime_column,
            f"Bezrobocie vs {INDICATOR_LABELS[selected_crime_column]}",
        ),
        use_container_width=True,
    )

with col_right:
    st.plotly_chart(
        build_yearly_correlation_figure(
            yearly_corr,
            "Korelacje w poszczególnych latach",
        ),
        use_container_width=True,
    )

st.subheader("Analiza z opóźnieniem o 1 rok")
metric_1, metric_2, metric_3 = st.columns(3)
metric_1.metric("Liczba par obserwacji", lagged["observations"])
metric_2.metric(
    "Pearson r",
    "-" if pd.isna(lagged["pearson_r"]) else f"{lagged['pearson_r']:.3f}",
)
metric_3.metric(
    "Spearman rho",
    "-" if pd.isna(lagged["spearman_rho"]) else f"{lagged['spearman_rho']:.3f}",
)

if not lagged["lagged_frame"].empty:
    st.plotly_chart(
        build_lag_scatter_figure(
            lagged["lagged_frame"],
            selected_crime_column,
            "Bezrobocie w roku t a przestępczość w roku t+1",
        ),
        use_container_width=True,
    )

st.dataframe(
    yearly_corr.style.format(
        {
            "pearson_r": "{:.3f}",
            "pearson_p": "{:.4f}",
            "spearman_rho": "{:.3f}",
            "spearman_p": "{:.4f}",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.divider()
st.header("Analiza regionalna")
st.caption(
    "Te same korelacje rozbite po wojewodztwach. Pozwala sprawdzic, czy zaleznosc "
    "jest jednolita w skali kraju, czy nieregularna - silna w jednych regionach, slaba w innych."
)

voivodeship_corr = voivodeship_correlations(filtered, crime_column=selected_crime_column)

if voivodeship_corr.empty:
    st.warning("Za malo danych do liczenia korelacji per wojewodztwo.")
else:
    reg_left, reg_right = st.columns([1.1, 1])
    with reg_left:
        st.plotly_chart(
            build_voivodeship_correlation_bar_figure(
                voivodeship_corr,
                "pearson_r",
                f"Korelacja Pearsona per wojewodztwo: bezrobocie vs {INDICATOR_LABELS[selected_crime_column]}",
            ),
            use_container_width=True,
        )
    with reg_right:
        st.dataframe(
            voivodeship_corr.style.format(
                {
                    "pearson_r": "{:.3f}",
                    "pearson_p": "{:.4f}",
                    "spearman_rho": "{:.3f}",
                    "spearman_p": "{:.4f}",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

st.subheader("Dekompozycja: between vs within (test paradoksu Simpsona)")
st.caption(
    "Pooled = surowa korelacja na wszystkich obserwacjach. "
    "Between = na sredniach wojewodzkich (efekt regionalny). "
    "Within = po odjeciu sredniej regionalnej (faktyczna dynamika wewnatrz regionu). "
    "Jesli between >> within, korelacja jest zjawiskiem miedzyregionalnym, a nie efektem zmian wewnatrz regionow."
)

decomposition = between_within_decomposition(filtered, crime_column=selected_crime_column)
if decomposition.empty:
    st.warning("Za malo danych do dekompozycji.")
else:
    st.dataframe(
        decomposition.style.format(
            {
                "pearson_r": "{:.3f}",
                "pearson_p": "{:.4f}",
                "spearman_rho": "{:.3f}",
                "spearman_p": "{:.4f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

st.subheader("Korelacje z opóźnieniem o 1 rok — per województwo")
st.caption(
    "Czy efekt opoznienia (H4) jest jednolity w kraju, czy widoczny tylko w niektorych regionach?"
)

lagged_by_voivodeship = voivodeship_lagged_correlations(
    filtered, crime_column=selected_crime_column
)
if lagged_by_voivodeship.empty:
    st.warning("Za malo danych do liczenia korelacji z opoznieniem per wojewodztwo.")
else:
    lag_left, lag_right = st.columns([1.1, 1])
    with lag_left:
        st.plotly_chart(
            build_voivodeship_correlation_bar_figure(
                lagged_by_voivodeship,
                "pearson_r",
                "Pearson r (bezrobocie t → przestępczość t+1) per województwo",
            ),
            use_container_width=True,
        )
    with lag_right:
        st.dataframe(
            lagged_by_voivodeship.style.format(
                {
                    "pearson_r": "{:.3f}",
                    "pearson_p": "{:.4f}",
                    "spearman_rho": "{:.3f}",
                    "spearman_p": "{:.4f}",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
