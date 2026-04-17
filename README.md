# Analiza zależności między bezrobociem a przestępczością w powiatach Polski (2014-2024)

Projekt zaliczeniowy z przedmiotu **Analiza danych w Pandas**. Głównym celem projektu jest sprawdzenie, czy istnieje zależność między **stopą bezrobocia rejestrowanego** a **poziomem przestępczości** w powiatach Polski w latach **2014-2024**.

Warstwa analityczna została przygotowana w Pythonie z użyciem biblioteki **Pandas**, a wyniki są prezentowane w prostej aplikacji **Streamlit**.

## Cel projektu

Projekt odpowiada na pytania:

- czy w powiatach o wyższym bezrobociu obserwujemy wyższy poziom przestępczości,
- czy zależność zmienia się w czasie,
- czy zależność jest silniejsza dla przestępstw przeciwko mieniu,
- czy efekt jest lepiej widoczny po zastosowaniu przesunięcia czasowego o 1 rok.

## Zakres analizy

Analiza obejmuje:

- przygotowanie i czyszczenie danych,
- łączenie danych po roku i powiecie,
- statystyki opisowe,
- korelację Pearsona,
- korelację Spearmana,
- analizę rok do roku,
- analizę z opóźnieniem o 1 rok,
- wykrywanie powiatów odstających od trendu,
- przygotowanie prostych wniosków końcowych.

## Technologie

- Python 3
- Pandas
- NumPy
- Streamlit
- requests
- Plotly
- SciPy
- openpyxl

## Struktura projektu

```text
project/
├── app.py
├── pages/
│   ├── 1_Dane.py
│   ├── 2_Analiza_opisowa.py
│   ├── 3_Korelacje_i_wykresy.py
│   ├── 4_Powiaty_odstajace.py
│   └── 5_Wnioski.py
├── src/
│   ├── __init__.py
│   ├── analysis_service.py
│   ├── config.py
│   ├── data_cleaning.py
│   ├── data_loader.py
│   └── visualization.py
├── data/
│   ├── processed/
│   ├── raw/
│   └── sample/
│       ├── crime_sample.csv
│       └── unemployment_sample.csv
├── assets/
├── README.md
└── requirements.txt
```

## Opis modułów

- `src/config.py` - konfiguracja projektu, ścieżki, zakres lat, ustawienia API BDL.
- `src/data_loader.py` - pobieranie danych z API GUS BDL, zapis surowych danych, fallback do CSV.
- `src/data_cleaning.py` - czyszczenie danych, zmiana nazw kolumn, łączenie danych po powiecie i roku.
- `src/analysis_service.py` - statystyki opisowe, korelacje, analiza dynamiki i powiaty odstające.
- `src/visualization.py` - wykresy Plotly do wykorzystania w aplikacji Streamlit.
- `app.py` i `pages/` - warstwa prezentacyjna w Streamlit.

## Dane i źródło

Podstawowym źródłem danych ma być **GUS BDL API**:

- stopa bezrobocia rejestrowanego,
- przestępstwa stwierdzone przez Policję ogółem na 1000 mieszkańców,
- opcjonalnie przestępstwa przeciwko mieniu na 1000 mieszkańców,
- opcjonalnie przestępstwa przeciwko życiu i zdrowiu na 1000 mieszkańców.

W projekcie znajduje się:

- kod do pobierania danych z API BDL przez `requests`,
- obsługa zapisu surowych danych do `data/raw/`,
- zapis przetworzonej migawki danych pobranych z API do `data/processed/`.

## Wykorzystane serie BDL

W pliku `src/config.py` zostały wpisane identyfikatory serii użytych w projekcie:

- `395392` - stopa bezrobocia rejestrowanego, ogółem, poziom powiatów,
- `398594` - przestępstwa stwierdzone przez Policję ogółem na 1000 mieszkańców,
- `498623` - przestępstwa stwierdzone przez Policję przeciwko mieniu na 1000 mieszkańców,
- `498624` - przestępstwa stwierdzone przez Policję przeciwko życiu i zdrowiu na 1000 mieszkańców.

Projekt działa w trybie **API-first**:

1. przy starcie próbuje pobrać dane bezpośrednio z GUS BDL,
2. zapisuje surowe pliki i scalony zbiór do katalogu `data/`,
3. jeżeli API chwilowo nie odpowiada lub zwróci limit zapytań, aplikacja może użyć ostatniej zapisanej migawki pobranej wcześniej z API.

## Instalacja

1. Utwórz i aktywuj środowisko wirtualne.
2. Zainstaluj zależności:

```bash
pip install -r requirements.txt
```

Opcjonalnie można ustawić własny klucz API BDL, jeśli chcesz zwiększyć limity zapytań:

```bash
set BDL_CLIENT_ID=twoj_klucz_api
```

## Uruchomienie

```bash
streamlit run app.py
```

Po uruchomieniu aplikacja będzie dostępna lokalnie w przeglądarce.

## Jak działa projekt

1. Aplikacja pobiera dane z API GUS BDL.
2. Dane są czyszczone i łączone po `powiat` oraz `rok`.
3. Moduł analityczny oblicza korelacje, statystyki opisowe, dynamikę zmian i outliery.
4. Streamlit prezentuje wyniki w osobnych sekcjach.

## Najważniejsze widoki aplikacji

- **Strona główna** - opis celu, pytań badawczych i źródła danych.
- **Dane** - podgląd rekordów, filtry, liczba obserwacji, liczba powiatów i zakres lat.
- **Analiza opisowa** - średnie, mediany, min, max i odchylenie standardowe.
- **Korelacje i wykresy** - trendy czasowe, scatter plot, korelacje roczne i analiza opóźnienia.
- **Powiaty odstające** - lista powiatów odbiegających od trendu.
- **Wnioski** - podsumowanie wyników, ocena hipotez i ograniczenia projektu.

## Możliwe rozwinięcia

- dodanie ręcznego przycisku odświeżenia danych z API,
- rozszerzenie liczby kategorii przestępstw,
- zapis wyników do Excela,
- dodanie mapy powiatów po przygotowaniu danych przestrzennych.
