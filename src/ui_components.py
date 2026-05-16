from __future__ import annotations

from typing import Any

from src.data_loader import DataLoadError, load_project_data

SOURCE_LABELS: dict[str, str] = {
    "api": "API GUS BDL (świeże)",
    "csv": "Lokalny CSV",
    "sample": "Dane przykładowe",
}


def render_data_source_sidebar(st_module, bundle: dict[str, Any]) -> None:
    """Renderuje w sidebarze sekcję 'Źródło danych' z przyciskiem 'Pobierz z API'.

    Po kliknięciu czyścimy lru_cache, wymuszamy fresh fetch (zapis CSV jako efekt
    uboczny) i robimy rerun. Spójne dla wszystkich pages bez session_state.
    """
    metadata = bundle["metadata"]
    sidebar = st_module.sidebar
    sidebar.subheader("Źródło danych")

    source_key = metadata.get("source", "?")
    sidebar.caption(f"Tryb: **{SOURCE_LABELS.get(source_key, source_key)}**")

    fetched_at = metadata.get("fetched_at")
    if fetched_at:
        sidebar.caption(f"Ostatnie pobranie z API: {fetched_at}")
    else:
        sidebar.caption("Ostatnie pobranie z API: nieznane")

    if sidebar.button("Pobierz świeże dane z API", use_container_width=True):
        with sidebar.status("Pobieranie z GUS BDL..."):
            try:
                load_project_data.cache_clear()
                load_project_data(force_api=True)
            except DataLoadError as exc:
                sidebar.error(f"Nie udało się pobrać: {exc}")
                return
        st_module.rerun()
