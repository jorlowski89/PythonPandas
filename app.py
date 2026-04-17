from __future__ import annotations

import streamlit as st

from src.analysis_service import dataset_overview, global_correlations
from src.data_loader import DataLoadError, load_project_data

st.set_page_config(
    page_title="Bezrobocie a przestępczość w powiatach",
    page_icon="📊",
    layout="wide",
)

try:
    bundle = load_project_data(prefer_api=True)
except DataLoadError as exc:
    st.error(f"Nie udalo sie zaladowac danych z API GUS BDL. Szczegoly: {exc}")
    st.stop()

data = bundle["data"]
metadata = bundle["metadata"]
overview = dataset_overview(data)
correlations = global_correlations(data)

st.title("Analiza zależności między bezrobociem a przestępczością w powiatach Polski")
st.caption("Projekt zaliczeniowy z przedmiotu Analiza danych w Pandas, z warstwą prezentacyjną w Streamlit.")

if metadata["source"] == "api":
    st.success("Aplikacja korzysta aktualnie z danych pobranych z API GUS BDL.")
elif metadata["source"] == "api_cache":
    st.warning(
        "Nie udalo sie odswiezyc danych online, dlatego pokazana jest ostatnia zapisana migawka danych pobranych z API GUS BDL."
    )
else:
    st.warning(
        "Aplikacja korzysta z danych przykladowych. Ten tryb powinien byc potrzebny tylko awaryjnie."
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
st.markdown(
    """
W menu po lewej stronie znajdują się kolejne sekcje projektu:

1. `Dane` - podgląd i filtrowanie zbioru.
2. `Analiza opisowa` - statystyki i zmiany rok do roku.
3. `Korelacje i wykresy` - zależności statystyczne i wykresy.
4. `Powiaty odstające` - jednostki wyłamujące się z trendu.
5. `Wnioski` - podsumowanie hipotez i ograniczeń projektu.
"""
)
