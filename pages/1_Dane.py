from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analysis_service import dataset_overview
from src.data_loader import DataLoadError, load_project_data

st.title("Dane")

try:
    bundle = load_project_data(prefer_api=True)
except DataLoadError as exc:
    st.error(f"Nie udalo sie zaladowac danych z API GUS BDL. Szczegoly: {exc}")
    st.stop()

data = bundle["data"].copy()
overview = dataset_overview(data)

available_years = sorted(data["rok"].unique().tolist())
available_powiats = sorted(data["powiat"].unique().tolist())

st.sidebar.header("Filtry danych")
selected_years = st.sidebar.multiselect("Wybierz lata", available_years, default=available_years)
selected_powiats = st.sidebar.multiselect(
    "Wybierz powiaty",
    available_powiats,
    default=available_powiats,
)

filtered = data[
    data["rok"].isin(selected_years) & data["powiat"].isin(selected_powiats)
].copy()

if filtered.empty:
    st.warning("Brak danych dla wybranych filtrów. Zaznacz przynajmniej jeden rok i jeden powiat.")
    st.stop()

metric_1, metric_2, metric_3 = st.columns(3)
metric_1.metric("Obserwacje po filtrowaniu", len(filtered))
metric_2.metric("Powiaty po filtrowaniu", filtered["powiat"].nunique())
metric_3.metric("Lata po filtrowaniu", filtered["rok"].nunique())

st.subheader("Podstawowe informacje o zbiorze")
info_frame = pd.DataFrame(
    [
        {"metryka": "Liczba wszystkich obserwacji", "wartosc": overview["observations"]},
        {"metryka": "Liczba powiatów", "wartosc": overview["powiats"]},
        {
            "metryka": "Zakres lat",
            "wartosc": f"{min(overview['years'])} - {max(overview['years'])}",
        },
        {"metryka": "Źródło danych", "wartosc": bundle["metadata"]["source"].upper()},
    ]
)
st.dataframe(info_frame, use_container_width=True, hide_index=True)

st.subheader("Podgląd rekordów")
st.dataframe(filtered, use_container_width=True, hide_index=True)

st.subheader("Liczba rekordów w poszczególnych latach")
year_counts = (
    filtered.groupby("rok", as_index=False)
    .size()
    .rename(columns={"size": "liczba_rekordow"})
)
st.dataframe(year_counts, use_container_width=True, hide_index=True)

st.subheader("Braki danych")
missing_frame = (
    filtered.isna()
    .sum()
    .reset_index()
    .rename(columns={"index": "kolumna", 0: "liczba_brakow"})
    .sort_values("liczba_brakow", ascending=False)
)
st.dataframe(missing_frame, use_container_width=True, hide_index=True)
