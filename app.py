from __future__ import annotations

import streamlit as st

from src.analysis_service import dataset_overview, global_correlations
from src.data_loader import DataLoadError, load_project_data
from src.help_content import render_glossary, render_usage
from src.ui_components import render_data_source_sidebar

st.set_page_config(
    page_title="Bezrobocie a przestępczość w powiatach",
    page_icon="📊",
    layout="wide",
)

try:
    bundle = load_project_data()
except DataLoadError as exc:
    st.error(f"Nie udalo sie zaladowac danych. Szczegoly: {exc}")
    st.stop()

render_data_source_sidebar(st, bundle)

data = bundle["data"]
metadata = bundle["metadata"]
overview = dataset_overview(data)
correlations = global_correlations(data)

st.title("Analiza zależności między bezrobociem a przestępczością w powiatach Polski")
st.caption("Projekt zaliczeniowy z przedmiotu Analiza danych w Pandas, z warstwą prezentacyjną w Streamlit.")

fetched_at = metadata.get("fetched_at")
if metadata["source"] == "api":
    st.success(
        f"Dane wlasnie pobrane z API GUS BDL ({fetched_at})."
        if fetched_at
        else "Dane pobrane z API GUS BDL."
    )
elif metadata["source"] == "csv":
    st.info(
        f"Dane zaladowane z lokalnego CSV (pobrane z API: {fetched_at}). "
        "Aby pobrac swieze dane, uzyj przycisku w panelu bocznym."
        if fetched_at
        else "Dane zaladowane z lokalnego CSV. Aby pobrac swieze dane, uzyj przycisku w panelu bocznym."
    )
else:
    st.warning(
        f"Aplikacja korzysta z trybu: {metadata['source']}."
    )

for message in metadata["messages"]:
    st.info(message)

st.markdown(
    """
Projekt bada, czy w powiatach Polski w latach 2014-2024 istnieje związek między
stopą bezrobocia rejestrowanego a poziomem przestępczości. Główna część pracy
została wykonana w bibliotece Pandas: pobieranie danych, czyszczenie, łączenie,
liczenie korelacji, analiza zmian w czasie i wykrywanie powiatów odstających.
"""
)

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Liczba obserwacji", overview["observations"])
metric_2.metric("Liczba powiatów", overview["powiats"])
metric_3.metric("Zakres lat", f"{metadata['year_min']} - {metadata['year_max']}")
metric_4.metric("Źródło", metadata["source"].upper())

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Cel i hipotezy")
    st.markdown(
        """
Najważniejsze pytania badawcze:

- czy wyższe bezrobocie wiąże się z wyższą przestępczością,
- czy siła zależności zmienia się w czasie,
- czy silniej widać ją dla przestępstw przeciwko mieniu,
- czy zależność jest wyraźniejsza przy przesunięciu o 1 rok.
"""
    )

with right:
    st.subheader("Szybki podgląd korelacji")
    st.dataframe(
        correlations.style.format(
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

st.subheader("Jak korzystać z aplikacji")
render_usage(st, "home", expanded=True)

st.subheader("Mapa zakładek")

map_left, map_right = st.columns(2)

with map_left:
    st.markdown(
        """
**1. Dane**
Podglad surowego zbioru, filtry po latach i powiatach, liczba brakow danych
w poszczegolnych kolumnach.

**2. Analiza opisowa**
Statystyki opisowe (srednia, mediana, std), srednie krajowe w czasie,
dynamika rok do roku oraz **analiza regionalna** (statystyki i linie czasowe per wojewodztwo).

**3. Korelacje i wykresy**
Korelacje Pearsona i Spearmana w calym zbiorze i rok po roku, scatter plot z linia trendu,
analiza z opoznieniem 1 rok. Sekcja regionalna: **korelacje per wojewodztwo**,
**dekompozycja between/within** (test paradoksu Simpsona) i **lag per region**.
"""
    )

with map_right:
    st.markdown(
        """
**4. Powiaty odstające**
Ranking powiatow odbiegajacych od trendu zaleznosci bezrobocie/przestepczosc.
Przelacznik **trend globalny vs regionalny** pozwala porownac odchylenia
wzgl. calego kraju lub wzgl. wlasnego wojewodztwa.

**5. Wnioski**
Automatycznie generowana ocena czterech hipotez badawczych H1-H4 + dodatkowa sekcja
**Wnioski z analizy regionalnej** (paradoks ekologiczny, heterogenicznosc, outliery).

**Filtry** w panelu bocznym dzialaja niezaleznie na kazdej stronie - domyslnie
zaznaczone sa wszystkie lata i powiaty.
"""
    )

st.subheader("Słownik kluczowych pojęć")
st.caption(
    "Sklasyfikowane wszystkie nazwy kolumn i parametry uzyte w tabelach i wnioskach. "
    "Rozwin sekcje aby zobaczyc objasnienia."
)
render_glossary(st, expanded=False)
