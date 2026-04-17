from __future__ import annotations

import streamlit as st

from src.analysis_service import detect_outlier_powiats
from src.config import CRIME_COLUMNS, INDICATOR_LABELS
from src.data_loader import DataLoadError, load_project_data
from src.visualization import build_outlier_bar_figure

st.title("Powiaty odstające")

try:
    bundle = load_project_data(prefer_api=True)
except DataLoadError as exc:
    st.error(f"Nie udalo sie zaladowac danych z API GUS BDL. Szczegoly: {exc}")
    st.stop()

data = bundle["data"].copy()

selected_crime_column = st.sidebar.selectbox(
    "Kategoria przestępczości",
    CRIME_COLUMNS,
    format_func=lambda column: INDICATOR_LABELS[column],
)
top_n = st.sidebar.slider("Liczba powiatów", min_value=3, max_value=10, value=6)

outliers = detect_outlier_powiats(data, crime_column=selected_crime_column, top_n=top_n)

st.markdown(
    """
Powiat odstający to taki, w którym poziom przestępczości jest wyraźnie wyższy lub niższy
od wartości sugerowanej przez ogólny trend zależności między bezrobociem a przestępczością.
"""
)

if outliers.empty:
    st.warning("Brak wystarczających danych do wyznaczenia powiatów odstających.")
else:
    st.plotly_chart(
        build_outlier_bar_figure(
            outliers,
            f"Powiaty odstające dla zmiennej: {INDICATOR_LABELS[selected_crime_column]}",
        ),
        use_container_width=True,
    )

    st.dataframe(
        outliers.style.format(
            {
                "srednie_bezrobocie": "{:.2f}",
                "srednia_przestepczosc": "{:.2f}",
                "srednia_reszta": "{:.2f}",
                "outlier_score": "{:.2f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    selected_powiat = st.selectbox("Sprawdź szczegóły powiatu", outliers["powiat"].tolist())
    detail_frame = data[data["powiat"] == selected_powiat].sort_values("rok")
    st.dataframe(detail_frame, use_container_width=True, hide_index=True)
