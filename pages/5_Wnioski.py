from __future__ import annotations

import streamlit as st

from src.analysis_service import generate_conclusions
from src.data_loader import DataLoadError, load_project_data

st.title("Wnioski")

try:
    bundle = load_project_data(prefer_api=True)
except DataLoadError as exc:
    st.error(f"Nie udalo sie zaladowac danych z API GUS BDL. Szczegoly: {exc}")
    st.stop()

data = bundle["data"].copy()
conclusions = generate_conclusions(data)

st.subheader("Najważniejsze obserwacje")
for conclusion in conclusions["findings"]:
    st.markdown(f"- {conclusion}")

st.subheader("Ocena hipotez badawczych")
st.dataframe(conclusions["hypotheses"], use_container_width=True, hide_index=True)

st.subheader("Ograniczenia projektu")
for limitation in conclusions["limitations"]:
    st.markdown(f"- {limitation}")

st.subheader("Komentarz końcowy")
st.markdown(
    """
W tej wersji projektu centrum całej pracy stanowi analiza danych w Pandas. Streamlit
pełni rolę czytelnej warstwy prezentacyjnej, która pozwala wygodnie pokazać tabele,
wykresy, korelacje i końcowe wnioski podczas prezentacji zaliczeniowej.
"""
)
