from __future__ import annotations

GLOSSARY: dict[str, str] = {
    # Klucze identyfikujace rekord
    "rok": "Rok obserwacji (2014-2024). Kazda para (powiat, rok) to jedna obserwacja.",
    "powiat": "Nazwa powiatu z GUS. Powiaty grodzkie maja prefiks 'Powiat m.'.",
    "wojewodztwo": (
        "Wojewodztwo wyliczone z kodu TERYT (pozycje 2-3 unit_id). Pozwala robic "
        "analize regionalna."
    ),
    "unit_id": "Identyfikator jednostki terytorialnej w API GUS BDL (11 cyfr, format TERYT).",
    # Wskazniki
    "unemployment_rate": "Stopa bezrobocia rejestrowanego (%) - odsetek zarejestrowanych bezrobotnych.",
    "crimes_total_per_1000": "Liczba przestepstw stwierdzonych przez Policje ogolem na 1000 mieszkancow.",
    "property_crimes_per_1000": "Przestepstwa przeciwko mieniu (kradzieze, wlamania) na 1000 mieszkancow.",
    "violent_crimes_per_1000": "Przestepstwa przeciwko zyciu i zdrowiu na 1000 mieszkancow.",
    "crime_minus_unemployment": (
        "Pomocnicza roznica: przestepczosc - bezrobocie. Wartosc dodatnia oznacza, "
        "ze przestepczosc jest liczbowo wyzsza niz stopa bezrobocia (w tych samych jednostkach)."
    ),
    # Statystyki opisowe
    "srednia": "Srednia arytmetyczna wszystkich obserwacji w wybranym wycinku.",
    "mediana": "Wartosc srodkowa - 50% obserwacji jest mniejszych, 50% wiekszych. Odporna na wartosci skrajne.",
    "minimum": "Najmniejsza obserwowana wartosc.",
    "maksimum": "Najwieksza obserwowana wartosc.",
    "odchylenie_std": (
        "Odchylenie standardowe (ddof=1) - miara rozrzutu wokol sredniej. "
        "Im wyzsze, tym bardziej zmienne sa wartosci."
    ),
    "liczba_obserwacji": "Liczba wierszy (par powiat-rok) wziętych do liczenia statystyki.",
    "liczba_powiatow": "Liczba unikalnych powiatow w danym wycinku.",
    "liczba_par": "Liczba par obserwacji (powiat, rok) z poprawnym opoznieniem t -> t+1.",
    # Korelacja
    "pearson_r": (
        "Korelacja Pearsona (-1 do +1). Mierzy siłe LINIOWEJ zaleznosci. "
        "+1 = idealny wzrost wspolny, -1 = idealny spadek, 0 = brak liniowej zaleznosci. "
        "Wrazliwa na wartosci skrajne (outliery)."
    ),
    "pearson_p": (
        "Wartosc p dla korelacji Pearsona. Im mniejsza, tym mniejsze "
        "prawdopodobienstwo, ze obserwowany wynik powstal przypadkiem. "
        "Konwencjonalny prog 'istotne statystycznie' to p < 0.05."
    ),
    "spearman_rho": (
        "Korelacja rangowa Spearmana (-1 do +1). Mierzy zaleznosc MONOTONICZNA (nie musi byc liniowa) "
        "na rangach. Odporna na outliery. Jesli rho i r mocno sie roznia, zaleznosc nie jest liniowa."
    ),
    "spearman_p": "Wartosc p dla korelacji Spearmana, interpretacja jak dla pearson_p.",
    # Sila korelacji - skala
    "skala_sily_korelacji": (
        "Skala interpretacyjna |r|: <0.2 bardzo slaba, 0.2-0.4 slaba, "
        "0.4-0.6 umiarkowana, 0.6-0.8 silna, >=0.8 bardzo silna."
    ),
    # Dynamika
    "yoy_pct": (
        "Procentowa zmiana rok do roku (year-over-year). Wartosc dodatnia = wzrost, "
        "ujemna = spadek wzgl. roku poprzedniego."
    ),
    # Dekompozycja regionalna
    "pooled": (
        "Korelacja na wszystkich obserwacjach (powiat-rok) bez podzialu na regiony. "
        "Standardowy wynik 'globalny'."
    ),
    "between": (
        "Korelacja liczona na SREDNICH wojewodzkich (16 obserwacji = 16 wojewodztw). "
        "Mierzy: 'czy regiony o wyzszym sredniem bezrobociu maja wyzsza srednia przestepczosc'."
    ),
    "within": (
        "Korelacja po odjeciu sredniej regionalnej od kazdej obserwacji. Mierzy faktyczna "
        "dynamike WEWNATRZ regionu - czy w danym regionie wyzsze bezrobocie w danym roku "
        "idzie z wyzsza przestepczoscia."
    ),
    "paradoks_simpsona": (
        "Sytuacja, gdy korelacja na zagregowanych grupach (between) ma inny znak niz "
        "korelacja wewnatrz grup (within). Sygnal, ze wniosek globalny nie obowiazuje na poziomie "
        "indywidualnym - klasyczny blad ekologiczny."
    ),
    # Analiza opoznienia
    "lag": (
        "Opoznienie czasowe. lag = 1 rok oznacza: bezrobocie w roku t skorelowane z "
        "przestepczoscia w roku t+1. Test hipotezy, ze efekt nie jest natychmiastowy."
    ),
    # Outliery i regresja
    "expected_crime": (
        "Przewidywana wartosc przestepczosci wg linii trendu (regresja liniowa OLS na "
        "(unemployment_rate, crime))."
    ),
    "residual": "Reszta: faktyczna_przestepczosc - expected_crime. Dodatnia = powyzej trendu, ujemna = ponizej.",
    "srednia_reszta": (
        "Srednia reszta dla powiatu (po wszystkich latach). Im wieksza co do wartosci bezwzglednej, "
        "tym mocniej powiat odstaje od trendu."
    ),
    "outlier_score": (
        "|srednia_reszta| / odchylenie standardowe srednich reszt po wszystkich powiatach. "
        "Wartosc >2 - powiat wyraznie odstajacy, >3 - silnie odstajacy."
    ),
    "kierunek": (
        "'Powyzej trendu' = przestepczosc jest wyzsza niz sugeruje trend; "
        "'Ponizej trendu' = nizsza niz sugeruje trend."
    ),
    "trend_globalny_vs_regionalny": (
        "Tryb wyznaczania linii trendu: GLOBALNY = jedna linia dla calego kraju "
        "(porownanie wzgl. ogolu); REGIONALNY = osobna linia dla kazdego wojewodztwa "
        "(porownanie wzgl. wlasnego regionu, kontrola dla regionalnego poziomu bazowego)."
    ),
}


PAGE_USAGE: dict[str, str] = {
    "home": """
**Cel aplikacji:** sprawdzic, czy w powiatach Polski istnieje zwiazek miedzy stopa bezrobocia
rejestrowanego a przestepczoscia w latach 2014-2024.

**Sugerowana sciezka analizy:**

1. **Dane** - obejrzyj surowy zbior, filtruj po latach i powiatach, sprawdz braki danych.
2. **Analiza opisowa** - poznaj rozklad zmiennych (srednie, rozrzut), dynamike rok do roku
   i przekroj regionalny.
3. **Korelacje i wykresy** - tu jest serce analizy: korelacje globalne, w czasie, per wojewodztwo,
   dekompozycja between/within oraz analiza z opoznieniem.
4. **Powiaty odstajace** - znajdz powiaty, ktore wyrozniaja sie na tle trendu (globalnego
   lub regionalnego - dostepny przelacznik).
5. **Wnioski** - automatycznie generowana ocena hipotez badawczych i podsumowanie wnioskow,
   w tym wnioski z analizy regionalnej.

**Filtry w panelu bocznym** wplywaja tylko na biezaca strone - kazda strona ma wlasne filtry.
Domyslnie zaznaczone sa wszystkie lata i wszystkie powiaty.

**Wskazowka interpretacyjna:** korelacja nie oznacza przyczynowosci. Jesli widzisz silna
zaleznosc miedzy bezrobociem a przestepczoscia, moze ona wynikac z trzeciego, niewidocznego
czynnika (np. urbanizacji, demografii). Sekcja `between vs within` na stronie Korelacje
pomaga rozpoznac takie przypadki.

**Zrodlo danych:** GUS BDL (Bank Danych Lokalnych) - API publiczne. Aplikacja probuje pobrac
dane na zywo, a jesli sie nie uda - korzysta z lokalnej migawki.
""",
    "dane": """
- Filtry `Wybierz lata` / `Wybierz powiaty` w panelu bocznym pozwalaja zawezic widoczny zbior.
- Metryki na gorze pokazuja stan po filtrowaniu, a tabela `Podstawowe informacje` - stan calego zbioru.
- Tabela `Braki danych` pokazuje ile obserwacji nie ma wartosci w danej kolumnie - duze braki
  oznaczaja, ze powiat/rok nie raportowal danej zmiennej.
- Kolumna `unit_id` to identyfikator TERYT - z drugiej i trzeciej cyfry tego kodu wyliczane
  jest wojewodztwo.
""",
    "analiza_opisowa": """
- Statystyki obejmuja wszystkie cztery wskazniki (bezrobocie + 3 kategorie przestepczosci).
- Wykresy linii pokazuja **srednia po wszystkich powiatach** w danym roku.
- Sekcja `Dynamika rok do roku` pokazuje procentowa zmiane sredniej krajowej.
- Sekcja `Analiza regionalna` daje:
  - statystyki opisowe per wojewodztwo (przelacznik wskaznika),
  - linie czasowe dla wybranych wojewodztw (mozesz odznaczyc czesc, zeby uproscic wykres).
""",
    "korelacje": """
- Wybierz **kategorie przestepczosci** w panelu bocznym - wszystkie analizy na stronie
  beda jej dotyczyc.
- `Korelacje dla calego zbioru` to porownanie bezrobocia z trzema kategoriami przestepczosci
  jednoczesnie (Pearson i Spearman).
- Scatter plot pokazuje wszystkie obserwacje (kazda kropka = jeden powiat-rok) z linia trendu.
- `Korelacje w poszczegolnych latach` - jak silna byla zaleznosc w kolejnych latach.
- `Analiza z opoznieniem` - czy bezrobocie z roku t przewiduje przestepczosc w roku t+1.

**Sekcja regionalna (nizej):**

- `Korelacja per wojewodztwo` - 16 osobnych korelacji pokazuje, ze efekt nie musi byc
  jednolity w kraju.
- `Dekompozycja between vs within` - **wazny test metodologiczny**. Jesli korelacja
  between (miedzy regionami) jest duzo silniejsza niz within (wewnatrz regionow), to
  zaleznosc moze byc artefaktem agregacji.
- `Korelacje z opoznieniem per wojewodztwo` - czy efekt opoznienia jest jednolity czy regionalny.
""",
    "powiaty_odstajace": """
- Wybierz kategorie przestepczosci i liczbe powiatow w panelu bocznym.
- **Przelacznik `Trend odniesienia`** to kluczowy parametr:
  - `Globalny` - jedna linia trendu dla calego kraju, residua liczone wzgl. niej.
    Powiat odstaje, jesli ma nietypowa przestepczosc na tle bezrobocia w skali kraju.
  - `Regionalny` - osobna linia trendu w kazdym wojewodztwie. Powiat odstaje, jesli
    wyrozniaja sie na tle WLASNEGO regionu (kontrola dla regionalnego poziomu bazowego).
- Wykres slupkowy pokazuje srednia reszte: dlugie slupki = duze odchylenie od trendu.
- W tabeli `outlier_score` to znormalizowana miara odstawania - wartosci > 2-3 oznaczaja
  silny outlier.
- Mozesz wybrac konkretny powiat w selectboxie - zobaczysz wszystkie jego obserwacje rok po roku.
""",
    "wnioski": """
- `Najwazniejsze obserwacje` i `Ocena hipotez badawczych` to wnioski liczone dynamicznie
  z aktualnie zaladowanych danych - jesli zmienia sie dane, zmieni sie ocena.
- Cztery hipotezy badawcze (H1-H4) odpowiadaja pytaniom z README.
- Sekcja `Wnioski z analizy regionalnej` zawiera **dodatkowe spostrzezenia** z ciecia
  per wojewodztwo:
  - kierunek i sila globalnej korelacji,
  - dekompozycja between/within (test paradoksu Simpsona),
  - heterogenicznosc regionalna,
  - porownanie outlierow trendu globalnego i regionalnego.
- Tabele pod sekcja sa zrodlem liczb dla powyzszych wnioskow.
""",
}


_DEFAULT_GLOSSARY_TITLE = "Slownik pojec"
_DEFAULT_USAGE_TITLE = "Jak korzystac z tej strony"


def render_glossary(st_module, terms: list[str] | None = None, expanded: bool = False) -> None:
    """Renderuje rozwijana sekcje slownika dla podanych pojec (lub wszystkich)."""
    keys = terms if terms else list(GLOSSARY.keys())
    visible = [(k, GLOSSARY[k]) for k in keys if k in GLOSSARY]
    if not visible:
        return
    with st_module.expander(_DEFAULT_GLOSSARY_TITLE, expanded=expanded):
        for key, description in visible:
            st_module.markdown(f"- **`{key}`** — {description}")


def render_usage(st_module, page_key: str, expanded: bool = False) -> None:
    """Renderuje rozwijana sekcje 'Jak korzystac z tej strony'."""
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
    """Skrot: 'Jak korzystac' + 'Slownik' w dwoch expanderach pod tytulem strony."""
    render_usage(st_module, page_key, expanded=usage_expanded)
    render_glossary(st_module, terms=glossary_terms, expanded=glossary_expanded)
