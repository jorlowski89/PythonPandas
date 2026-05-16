from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Bezrobocie a przestępczość w powiatach",
    page_icon="📊",
    layout="wide",
)

pg = st.navigation([
    st.Page("home.py", title="Podstawowe informacje"),
    st.Page("pages/Dane.py", title="Dane"),
    st.Page("pages/Analiza_opisowa.py", title="Analiza opisowa"),
    st.Page("pages/Korelacje_i_wykresy.py", title="Korelacje i wykresy"),
    st.Page("pages/Powiaty_odstajace.py", title="Powiaty odstające"),
    st.Page("pages/Wnioski.py", title="Wnioski"),
])
pg.run()
