# US Market Monitor

Aplikacja Django do wyszukiwania spółek giełdowych, obserwowania wybranych firm i pobierania raportów Word.

## Wymagania

- Python 3.10+
- Połączenie z internetem (dane z Yahoo Finance)

## Instalacja

```bash
pip install -r requirements.txt
python manage.py migrate
```

## Uruchomienie

```bash
python manage.py runserver
```

Aplikacja będzie dostępna pod adresem: http://127.0.0.1:8000/

## Funkcje

- **Wyszukiwarka** — wyszukiwanie spółek po symbolu giełdowym lub nazwie
- **Lista spółek** — alfabetyczny katalog popularnych spółek US pod wyszukiwarką
- **Obserwowane** — wspólna lista obserwowanych spółek z licznikiem w nawigacji
- **Strona spółki** — dane firmy, wykres świecowy (6 miesięcy) i pobieranie raportu
- **Raport Word** — dokument `.docx` z opisem spółki, danymi podstawowymi i wykresem cen

## Struktura projektu

```
US_market_monitor/
├── manage.py
├── requirements.txt
├── config/                     # ustawienia Django
└── companies/                  # główna aplikacja
    ├── models.py               # WatchedCompany
    ├── views.py
    ├── context_processors.py   # licznik obserwowanych
    ├── data/
    │   └── companies_catalog.py
    ├── services/
    │   ├── yfinance_service.py
    │   └── report_service.py
    ├── static/companies/css/
    │   └── theme.css           # ciemny motyw
    └── templates/companies/
```
