from __future__ import annotations

import streamlit as st

from src.analysis_service import global_correlations, lagged_correlation, yearly_correlations
from src.config import CRIME_COLUMNS, INDICATOR_LABELS
from src.data_loader import DataLoadError, load_project_data
from src.visualization import (
    build_lag_scatter_figure,
    build_scatter_figure,
    build_yearly_correlation_figure,
)

st.title("Korelacje i wykresy")

try:
    bundle = load_project_data(prefer_api=True)
except DataLoadError as exc:
    st.error(f"Nie udalo sie zaladowac danych z API GUS BDL. Szczegoly: {exc}")
    st.stop()

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
    "-" if lagged["pearson_r"] != lagged["pearson_r"] else f"{lagged['pearson_r']:.3f}",
)
metric_3.metric(
    "Spearman rho",
    "-" if lagged["spearman_rho"] != lagged["spearman_rho"] else f"{lagged['spearman_rho']:.3f}",
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
