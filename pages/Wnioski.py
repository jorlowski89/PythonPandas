from __future__ import annotations

import streamlit as st

from src.analysis_service import generate_conclusions, generate_regional_conclusions
from src.data_loader import DataLoadError, load_project_data
from src.help_content import render_page_help
from src.ui_components import render_data_source_sidebar

st.title("Wnioski")

render_page_help(
    st,
    page_key="wnioski",
    glossary_terms=[
        "pearson_r",
        "spearman_rho",
        "pooled",
        "between",
        "within",
        "paradoks_simpsona",
        "srednia_reszta",
        "outlier_score",
        "trend_globalny_vs_regionalny",
        "skala_sily_korelacji",
    ],
)

try:
    bundle = load_project_data()
except DataLoadError as exc:
    st.error(f"Nie udało się załadować danych. Szczegóły: {exc}")
    st.stop()

render_data_source_sidebar(st, bundle)

data = bundle["data"].copy()
conclusions = generate_conclusions(data)

st.subheader("Najważniejsze obserwacje")
for conclusion in conclusions["findings"]:
    st.markdown(f"- {conclusion}")

st.subheader("Ocena hipotez badawczych")
st.dataframe(conclusions["hypotheses"], use_container_width=True, hide_index=True)

st.divider()
st.header("Wnioski z analizy regionalnej (per województwo)")
st.caption(
    "Te wnioski powstają z rozbicia danych na 16 województw i są policzone dynamicznie "
    "z aktualnie załadowanego zbioru."
)

regional = generate_regional_conclusions(data)

st.subheader("Główne obserwacje regionalne")
for finding in regional["findings"]:
    st.markdown(f"- {finding}")

if not regional["decomposition"].empty:
    st.subheader("Dekompozycja korelacji: between vs within")
    st.markdown(
        "Test paradoksu Simpsona / ekologicznego: jeśli korelacja **between** "
        "(między średnimi wojewódzkimi) jest wyraźnie większa niż **within** "
        "(po odjęciu średniej regionalnej), to obserwowana zależność jest głównie "
        "międzyregionalna, a nie wynika ze zmian wewnątrz regionów."
    )
    st.dataframe(
        regional["decomposition"].style.format(
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

if not regional["voivodeship_correlations"].empty:
    st.subheader("Korelacje per województwo")
    st.dataframe(
        regional["voivodeship_correlations"]
        .head(16)
        .style.format(
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

if not regional["outliers_global"].empty and not regional["outliers_regional"].empty:
    st.subheader("Outliery: trend globalny vs regionalny")
    out_left, out_right = st.columns(2)
    with out_left:
        st.caption("Top 5 względem trendu globalnego")
        st.dataframe(
            regional["outliers_global"][
                ["powiat", "wojewodztwo", "srednia_reszta", "outlier_score"]
            ].style.format(
                {"srednia_reszta": "{:.2f}", "outlier_score": "{:.2f}"}
            ),
            use_container_width=True,
            hide_index=True,
        )
    with out_right:
        st.caption("Top 5 względem trendu regionalnego (per województwo)")
        st.dataframe(
            regional["outliers_regional"][
                ["powiat", "wojewodztwo", "srednia_reszta", "outlier_score"]
            ].style.format(
                {"srednia_reszta": "{:.2f}", "outlier_score": "{:.2f}"}
            ),
            use_container_width=True,
            hide_index=True,
        )

st.divider()
st.subheader("Ograniczenia projektu")
for limitation in conclusions["limitations"]:
    st.markdown(f"- {limitation}")

st.markdown(
    "- Analiza regionalna zakłada, że województwo jest sensownym poziomem agregacji. "
    "Bardziej szczegółowe efekty (np. miasto na prawach powiatu vs powiat ziemski) "
    "mogą wymagać osobnego cięcia."
)

st.subheader("Komentarz końcowy")
st.markdown(
    """
W tej wersji projektu centrum całej pracy stanowi analiza danych w Pandas. Streamlit
pełni rolę czytelnej warstwy prezentacyjnej, która pozwala wygodnie pokazać tabele,
wykresy, korelacje i końcowe wnioski podczas prezentacji zaliczeniowej.
"""
)
