from __future__ import annotations

GLOSSARY: dict[str, str] = {
    # Klucze identyfikujące rekord
    "rok": "Rok obserwacji (2014-2024). Każda para (powiat, rok) to jedna obserwacja.",
    "powiat": "Nazwa powiatu z GUS. Powiaty grodzkie mają prefiks 'Powiat m.'.",
    "wojewodztwo": (
        "Województwo wyliczone z kodu TERYT (pozycje 2-3 unit_id). Pozwala robić "
        "analizę regionalną."
    ),
    "unit_id": "Identyfikator jednostki terytorialnej w API GUS BDL (11 cyfr, format TERYT).",
    # Wskaźniki
    "unemployment_rate": "Stopa bezrobocia rejestrowanego (%) — odsetek zarejestrowanych bezrobotnych.",
    "crimes_total_per_1000": "Liczba przestępstw stwierdzonych przez Policję ogółem na 1000 mieszkańców.",
    "property_crimes_per_1000": "Przestępstwa przeciwko mieniu (kradzieże, włamania) na 1000 mieszkańców.",
    "violent_crimes_per_1000": "Przestępstwa przeciwko życiu i zdrowiu na 1000 mieszkańców.",
    "crime_minus_unemployment": (
        "Pomocnicza różnica: przestępczość − bezrobocie. Wartość dodatnia oznacza, "
        "że przestępczość jest liczbowo wyższa niż stopa bezrobocia (w tych samych jednostkach)."
    ),
    # Statystyki opisowe
    "srednia": "Średnia arytmetyczna wszystkich obserwacji w wybranym wycinku.",
    "mediana": "Wartość środkowa — 50% obserwacji jest mniejszych, 50% większych. Odporna na wartości skrajne.",
    "minimum": "Najmniejsza obserwowana wartość.",
    "maksimum": "Największa obserwowana wartość.",
    "odchylenie_std": (
        "Odchylenie standardowe (ddof=1) — miara rozrzutu wokół średniej. "
        "Im wyższe, tym bardziej zmienne są wartości."
    ),
    "liczba_obserwacji": "Liczba wierszy (par powiat-rok) wziętych do liczenia statystyki.",
    "liczba_powiatow": "Liczba unikalnych powiatów w danym wycinku.",
    "liczba_par": "Liczba par obserwacji (powiat, rok) z poprawnym opóźnieniem t → t+1.",
    # Korelacja
    "pearson_r": (
        "Korelacja Pearsona (−1 do +1). Mierzy siłę LINIOWEJ zależności. "
        "+1 = idealny wzrost wspólny, −1 = idealny spadek, 0 = brak liniowej zależności. "
        "Wrażliwa na wartości skrajne (outliery)."
    ),
    "pearson_p": (
        "Wartość p dla korelacji Pearsona. Im mniejsza, tym mniejsze "
        "prawdopodobieństwo, że obserwowany wynik powstał przypadkiem. "
        "Konwencjonalny próg 'istotne statystycznie' to p < 0.05."
    ),
    "spearman_rho": (
        "Korelacja rangowa Spearmana (−1 do +1). Mierzy zależność MONOTONICZNĄ (nie musi być liniowa) "
        "na rangach. Odporna na outliery. Jeśli rho i r mocno się różnią, zależność nie jest liniowa."
    ),
    "spearman_p": "Wartość p dla korelacji Spearmana, interpretacja jak dla pearson_p.",
    # Siła korelacji — skala
    "skala_sily_korelacji": (
        "Skala interpretacyjna |r|: <0.2 bardzo słaba, 0.2–0.4 słaba, "
        "0.4–0.6 umiarkowana, 0.6–0.8 silna, ≥0.8 bardzo silna."
    ),
    # Dynamika
    "yoy_pct": (
        "Procentowa zmiana rok do roku (year-over-year). Wartość dodatnia = wzrost, "
        "ujemna = spadek wzgl. roku poprzedniego."
    ),
    # Dekompozycja regionalna
    "pooled": (
        "Korelacja na wszystkich obserwacjach (powiat-rok) bez podziału na regiony. "
        "Standardowy wynik 'globalny'."
    ),
    "between": (
        "Korelacja liczona na ŚREDNICH wojewódzkich (16 obserwacji = 16 województw). "
        "Mierzy: 'czy regiony o wyższym średnim bezrobociu mają wyższą średnią przestępczość'."
    ),
    "within": (
        "Korelacja po odjęciu średniej regionalnej od każdej obserwacji. Mierzy faktyczną "
        "dynamikę WEWNĄTRZ regionu — czy w danym regionie wyższe bezrobocie w danym roku "
        "idzie z wyższą przestępczością."
    ),
    "paradoks_simpsona": (
        "Sytuacja, gdy korelacja na zagregowanych grupach (between) ma inny znak niż "
        "korelacja wewnątrz grup (within). Sygnał, że wniosek globalny nie obowiązuje na poziomie "
        "indywidualnym — klasyczny błąd ekologiczny."
    ),
    # Analiza opóźnienia
    "lag": (
        "Opóźnienie czasowe. lag = 1 rok oznacza: bezrobocie w roku t skorelowane z "
        "przestępczością w roku t+1. Test hipotezy, że efekt nie jest natychmiastowy."
    ),
    # Outliery i regresja
    "expected_crime": (
        "Przewidywana wartość przestępczości wg linii trendu (regresja liniowa OLS na "
        "(unemployment_rate, crime))."
    ),
    "residual": "Reszta: faktyczna_przestępczość − expected_crime. Dodatnia = powyżej trendu, ujemna = poniżej.",
    "srednia_reszta": (
        "Średnia reszta dla powiatu (po wszystkich latach). Im większa co do wartości bezwzględnej, "
        "tym mocniej powiat odstaje od trendu."
    ),
    "outlier_score": (
        "|srednia_reszta| / odchylenie standardowe średnich reszt po wszystkich powiatach. "
        "Wartość >2 — powiat wyraźnie odstający, >3 — silnie odstający."
    ),
    "kierunek": (
        "'Powyżej trendu' = przestępczość jest wyższa niż sugeruje trend; "
        "'Poniżej trendu' = niższa niż sugeruje trend."
    ),
    "trend_globalny_vs_regionalny": (
        "Tryb wyznaczania linii trendu: GLOBALNY = jedna linia dla całego kraju "
        "(porównanie wzgl. ogółu); REGIONALNY = osobna linia dla każdego województwa "
        "(porównanie wzgl. własnego regionu, kontrola dla regionalnego poziomu bazowego)."
    ),
}


PAGE_USAGE: dict[str, str] = {
    "home": """
**Cel aplikacji:** sprawdzić, czy w powiatach Polski istnieje związek między stopą bezrobocia
rejestrowanego a przestępczością w latach 2014–2024.

**Sugerowana ścieżka analizy:**

1. **Dane** — obejrzyj surowy zbiór, filtruj po latach i powiatach, sprawdź braki danych.
2. **Analiza opisowa** — poznaj rozkład zmiennych (średnie, rozrzut), dynamikę rok do roku
   i przekrój regionalny.
3. **Korelacje i wykresy** — tu jest serce analizy: korelacje globalne, w czasie, per województwo,
   dekompozycja between/within oraz analiza z opóźnieniem.
4. **Powiaty odstające** — znajdź powiaty, które wyróżniają się na tle trendu (globalnego
   lub regionalnego — dostępny przełącznik).
5. **Wnioski** — automatycznie generowana ocena hipotez badawczych i podsumowanie wniosków,
   w tym wnioski z analizy regionalnej.

**Filtry w panelu bocznym** wpływają tylko na bieżącą stronę — każda strona ma własne filtry.
Domyślnie zaznaczone są wszystkie lata i wszystkie powiaty.

**Wskazówka interpretacyjna:** korelacja nie oznacza przyczynowości. Jeśli widzisz silną
zależność między bezrobociem a przestępczością, może ona wynikać z trzeciego, niewidocznego
czynnika (np. urbanizacji, demografii). Sekcja `between vs within` na stronie Korelacje
pomaga rozpoznać takie przypadki.

**Źródło danych:** GUS BDL (Bank Danych Lokalnych) — API publiczne. Aplikacja próbuje pobrać
dane na żywo, a jeśli się nie uda — korzysta z lokalnej migawki.
""",
    "dane": """
- Filtry `Wybierz lata` / `Wybierz powiaty` w panelu bocznym pozwalają zawęzić widoczny zbiór.
- Metryki na górze pokazują stan po filtrowaniu, a tabela `Podstawowe informacje` — stan całego zbioru.
- Tabela `Braki danych` pokazuje ile obserwacji nie ma wartości w danej kolumnie — duże braki
  oznaczają, że powiat/rok nie raportował danej zmiennej.
- Kolumna `unit_id` to identyfikator TERYT — z drugiej i trzeciej cyfry tego kodu wyliczane
  jest województwo.
""",
    "analiza_opisowa": """
- Statystyki obejmują wszystkie cztery wskaźniki (bezrobocie + 3 kategorie przestępczości).
- Wykresy linii pokazują **średnią po wszystkich powiatach** w danym roku.
- Sekcja `Dynamika rok do roku` pokazuje procentową zmianę średniej krajowej.
- Sekcja `Analiza regionalna` daje:
  - statystyki opisowe per województwo (przełącznik wskaźnika),
  - linie czasowe dla wybranych województw (możesz odznaczyć część, żeby uprościć wykres).
""",
    "korelacje": """
- Wybierz **kategorię przestępczości** w panelu bocznym — wszystkie analizy na stronie
  będą jej dotyczyć.
- `Korelacje dla całego zbioru` to porównanie bezrobocia z trzema kategoriami przestępczości
  jednocześnie (Pearson i Spearman).
- Scatter plot pokazuje wszystkie obserwacje (każda kropka = jeden powiat-rok) z linią trendu.
- `Korelacje w poszczególnych latach` — jak silna była zależność w kolejnych latach.
- `Analiza z opóźnieniem` — czy bezrobocie z roku t przewiduje przestępczość w roku t+1.

**Sekcja regionalna (niżej):**

- `Korelacja per województwo` — 16 osobnych korelacji pokazuje, że efekt nie musi być
  jednolity w kraju.
- `Dekompozycja between vs within` — **ważny test metodologiczny**. Jeśli korelacja
  between (między regionami) jest dużo silniejsza niż within (wewnątrz regionów), to
  zależność może być artefaktem agregacji.
- `Korelacje z opóźnieniem per województwo` — czy efekt opóźnienia jest jednolity czy regionalny.
""",
    "powiaty_odstajace": """
- Wybierz kategorię przestępczości i liczbę powiatów w panelu bocznym.
- **Przełącznik `Trend odniesienia`** to kluczowy parametr:
  - `Globalny` — jedna linia trendu dla całego kraju, residua liczone wzgl. niej.
    Powiat odstaje, jeśli ma nietypową przestępczość na tle bezrobocia w skali kraju.
  - `Regionalny` — osobna linia trendu w każdym województwie. Powiat odstaje, jeśli
    wyróżnia się na tle WŁASNEGO regionu (kontrola dla regionalnego poziomu bazowego).
- Wykres słupkowy pokazuje średnią resztę: długie słupki = duże odchylenie od trendu.
- W tabeli `outlier_score` to znormalizowana miara odstawania — wartości > 2–3 oznaczają
  silny outlier.
- Możesz wybrać konkretny powiat w selectboxie — zobaczysz wszystkie jego obserwacje rok po roku.
""",
    "wnioski": """
- `Najważniejsze obserwacje` i `Ocena hipotez badawczych` to wnioski liczone dynamicznie
  z aktualnie załadowanych danych — jeśli zmienią się dane, zmieni się ocena.
- Cztery hipotezy badawcze (H1–H4) odpowiadają pytaniom z README.
- Sekcja `Wnioski z analizy regionalnej` zawiera **dodatkowe spostrzeżenia** z cięcia
  per województwo:
  - kierunek i siła globalnej korelacji,
  - dekompozycja between/within (test paradoksu Simpsona),
  - heterogeniczność regionalna,
  - porównanie outlierów trendu globalnego i regionalnego.
- Tabele pod sekcją są źródłem liczb dla powyższych wniosków.
""",
}


_DEFAULT_GLOSSARY_TITLE = "Słownik pojęć"
_DEFAULT_USAGE_TITLE = "Jak korzystać z tej strony"


def render_glossary(st_module, terms: list[str] | None = None, expanded: bool = False) -> None:
    """Renderuje rozwijaną sekcję słownika dla podanych pojęć (lub wszystkich)."""
    keys = terms if terms else list(GLOSSARY.keys())
    visible = [(k, GLOSSARY[k]) for k in keys if k in GLOSSARY]
    if not visible:
        return
    with st_module.expander(_DEFAULT_GLOSSARY_TITLE, expanded=expanded):
        for key, description in visible:
            st_module.markdown(f"- **`{key}`** — {description}")


def render_usage(st_module, page_key: str, expanded: bool = False) -> None:
    """Renderuje rozwijaną sekcję 'Jak korzystać z tej strony'."""
    content = PAGE_USAGE.get(page_key)
    if not content:
        return
    with st_module.expander(_DEFAULT_USAGE_TITLE, expanded=expanded):
        st_module.markdown(content)


def render_page_help(
    st_module,
    page_key: str,
    glossary_terms: list[str] | None = None,
    usage_expanded: bool = False,
    glossary_expanded: bool = False,
) -> None:
    render_usage(st_module, page_key, expanded=usage_expanded)
    render_glossary(st_module, terms=glossary_terms, expanded=glossary_expanded)
