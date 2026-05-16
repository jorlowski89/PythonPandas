from __future__ import annotations

import streamlit as st

from src.analysis_service import (
    descriptive_statistics,
    descriptive_statistics_by_voivodeship,
    year_over_year_changes,
    yearly_average_metrics,
    yearly_metrics_by_voivodeship,
)
from src.config import CRIME_COLUMNS, INDICATOR_LABELS
from src.data_loader import DataLoadError, load_project_data
from src.help_content import render_page_help
from src.ui_components import render_data_source_sidebar
from src.visualization import (
    build_voivodeship_yearly_lines_figure,
    build_yearly_average_line_figure,
    build_yoy_change_figure,
)

st.title("Analiza opisowa")

render_page_help(
    st,
    page_key="analiza_opisowa",
    glossary_terms=[
        "srednia",
        "mediana",
        "minimum",
        "maksimum",
        "odchylenie_std",
        "liczba_obserwacji",
        "liczba_powiatow",
        "yoy_pct",
        "unemployment_rate",
        "crimes_total_per_1000",
    ],
)

try:
    bundle = load_project_data()
except DataLoadError as exc:
    st.error(f"Nie udało się załadować danych. Szczegóły: {exc}")
    st.stop()

data = bundle["data"].copy()

available_years = sorted(data["rok"].unique().tolist())
selected_years = st.sidebar.multiselect("Zakres lat", available_years, default=available_years)

st.sidebar.markdown("---")
render_data_source_sidebar(st, bundle)

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

st.divider()
st.subheader("Analiza regionalna (per województwo)")
st.caption(
    "Dodatkowe spojrzenie: te same wskaźniki agregowane po województwach. Pozwala zauważyć "
    "regionalne kontrasty, które znikają w średniej krajowej."
)

regional_metric = st.selectbox(
    "Wskaźnik do analizy regionalnej",
    ["unemployment_rate", *CRIME_COLUMNS],
    format_func=lambda column: INDICATOR_LABELS.get(column, column),
)

stats_by_voivodeship = descriptive_statistics_by_voivodeship(
    filtered,
    columns=["unemployment_rate", regional_metric] if regional_metric != "unemployment_rate" else ["unemployment_rate"],
)

if not stats_by_voivodeship.empty:
    display_columns = {
        "wojewodztwo": "Województwo",
        "liczba_powiatow": "Liczba powiatów",
        "liczba_obserwacji": "Liczba obserwacji",
        "unemployment_rate_srednia": "Bezrobocie — średnia",
        "unemployment_rate_mediana": "Bezrobocie — mediana",
        "unemployment_rate_std": "Bezrobocie — std",
    }
    if regional_metric != "unemployment_rate":
        display_columns[f"{regional_metric}_srednia"] = f"{INDICATOR_LABELS[regional_metric]} — średnia"
        display_columns[f"{regional_metric}_mediana"] = f"{INDICATOR_LABELS[regional_metric]} — mediana"
        display_columns[f"{regional_metric}_std"] = f"{INDICATOR_LABELS[regional_metric]} — std"

    available = [col for col in display_columns if col in stats_by_voivodeship.columns]
    renamed = stats_by_voivodeship[available].rename(columns=display_columns)
    numeric_cols = [c for c in renamed.columns if renamed[c].dtype.kind in "fc"]
    st.dataframe(
        renamed.style.format({c: "{:.2f}" for c in numeric_cols}),
        use_container_width=True,
        hide_index=True,
    )

yearly_voivodeship = yearly_metrics_by_voivodeship(filtered)

available_voivodeships = sorted(yearly_voivodeship["wojewodztwo"].unique().tolist())
selected_voivodeships = st.multiselect(
    "Województwa na wykresie",
    available_voivodeships,
    default=available_voivodeships,
    help="Odznacz województwa, żeby zmniejszyć liczbę linii.",
)

if selected_voivodeships:
    filtered_yearly = yearly_voivodeship[
        yearly_voivodeship["wojewodztwo"].isin(selected_voivodeships)
    ]
    st.plotly_chart(
        build_voivodeship_yearly_lines_figure(
            filtered_yearly,
            regional_metric,
            f"{INDICATOR_LABELS[regional_metric]} w czasie — per województwo",
        ),
        use_container_width=True,
    )
else:
    st.info("Wybierz przynajmniej jedno województwo, aby zobaczyć wykres.")
