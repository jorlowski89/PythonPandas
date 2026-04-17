from __future__ import annotations

import streamlit as st

from src.analysis_service import descriptive_statistics, year_over_year_changes, yearly_average_metrics
from src.data_loader import DataLoadError, load_project_data
from src.visualization import build_yearly_average_line_figure, build_yoy_change_figure

st.title("Analiza opisowa")

try:
    bundle = load_project_data(prefer_api=True)
except DataLoadError as exc:
    st.error(f"Nie udalo sie zaladowac danych z API GUS BDL. Szczegoly: {exc}")
    st.stop()

data = bundle["data"].copy()

available_years = sorted(data["rok"].unique().tolist())
selected_years = st.sidebar.multiselect("Zakres lat", available_years, default=available_years)
filtered = data[data["rok"].isin(selected_years)].copy()

if filtered.empty:
    st.warning("Brak danych dla wybranego zakresu lat.")
    st.stop()

stats_frame = descriptive_statistics(filtered)
yearly_frame = yearly_average_metrics(filtered)
yoy_frame = year_over_year_changes(filtered)

st.subheader("Statystyki opisowe")
st.dataframe(
    stats_frame.style.format(
        {
            "srednia": "{:.2f}",
            "mediana": "{:.2f}",
            "minimum": "{:.2f}",
            "maksimum": "{:.2f}",
            "odchylenie_std": "{:.2f}",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

col_left, col_right = st.columns(2)

with col_left:
    st.plotly_chart(
        build_yearly_average_line_figure(
            yearly_frame,
            "unemployment_rate",
            "Średnia stopa bezrobocia w czasie",
        ),
        use_container_width=True,
    )

with col_right:
    st.plotly_chart(
        build_yearly_average_line_figure(
            yearly_frame,
            "crimes_total_per_1000",
            "Średnia przestępczość ogółem w czasie",
        ),
        use_container_width=True,
    )

st.subheader("Dynamika rok do roku")

yoy_left, yoy_right = st.columns(2)

with yoy_left:
    st.plotly_chart(
        build_yoy_change_figure(
            yoy_frame,
            "unemployment_rate",
            "Zmiana rok do roku: bezrobocie",
        ),
        use_container_width=True,
    )

with yoy_right:
    st.plotly_chart(
        build_yoy_change_figure(
            yoy_frame,
            "crimes_total_per_1000",
            "Zmiana rok do roku: przestępczość ogółem",
        ),
        use_container_width=True,
    )

st.dataframe(
    yoy_frame.style.format(
        {
            "unemployment_rate": "{:.2f}",
            "crimes_total_per_1000": "{:.2f}",
            "property_crimes_per_1000": "{:.2f}",
            "violent_crimes_per_1000": "{:.2f}",
            "unemployment_rate_yoy_pct": "{:.2f}",
            "crimes_total_per_1000_yoy_pct": "{:.2f}",
            "property_crimes_per_1000_yoy_pct": "{:.2f}",
            "violent_crimes_per_1000_yoy_pct": "{:.2f}",
        }
    ),
    use_container_width=True,
    hide_index=True,
)
