# 📦 ASD Production & Inventory Analytics

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://TWOJ-LINK-DO-APLIKACJI.streamlit.app)

Lekki, chmurowy pulpit analityczny stworzony w bibliotece **Streamlit**, przeznaczony do monitorowania zapasów magazynowych, wyliczania bezpiecznych buforów produkcyjnych oraz błyskawicznego identyfikowania wąskich gardeł w oparciu o czasy dostaw (Lead Time).

Aplikacja jest zoptymalizowana pod kątem prostej, jednowidokowej obsługi (bez zbędnych paneli administracyjnych) i automatycznie przelicza zapotrzebowanie po zmianie planu produkcyjnego.

---

## 🌍 Dostęp do Aplikacji (Live Demo)

Aplikacja jest dostępna publicznie pod adresem: 
**👉 [Uruchom ASD Inventory Analytics](https://asdappuctionanalytics-gm6kfeoqvsnjnsoqzc4u4v.streamlit.app/)**

> **⚠️ Ważna informacja (Tryb Uśpienia):**
> Aplikacja jest hostowana na bezpłatnej platformie Streamlit Community Cloud. Jeśli nikt nie korzystał z niej przez kilka dni, serwer przechodzi w stan oszczędzania energii. Jeśli po wejściu w link zobaczysz ekran z ikoną śpiącej twarzy ("Zzzz") i komunikatem o uśpieniu z powodu braku aktywności[cite: 7], po prostu kliknij niebieski przycisk **"Yes, get this app back up!"**[cite: 7]. Aplikacja uruchomi się ponownie w ciągu 1-2 minut.

---

## 🚀 Główne Funkcje

* **📊 Podsumowanie Magazynu i Braków:** Automatyczne wyliczanie całkowitej wartości magazynu, liczby brakujących elementów oraz szacowanego kosztu dokupienia komponentów.
* **🚨 Analiza Wąskich Gardeł (Komponenty Krytyczne):** Dynamiczne generowanie listy pozycji wymagających natychmiastowego zamówienia, sklasyfikowanych i posortowanych według najdłuższego czasu dostawy (**Lead Time**).
* **⏱️ Kalkulator Bezpiecznego Bufora:** Precyzyjne wyznaczanie maksymalnej liczby dni roboczych, na które wystarczy obecny zapas bez generowania braków na poszczególnych komponentach.
* **📈 Interaktywna Wizualizacja (Plotly):** Wykres słupkowy porównujący stan magazynowy, zapotrzebowanie planowane oraz zapas bezpieczeństwa dla każdego komponentu.
* **⚡ Automatyczny CI/CD:** Pełna integracja z GitHub i Streamlit Cloud — każda zmiana w kodzie natychmiast odświeża aplikację w chmurze.

---

## 🛠️ Architektura i Wymagania

### Struktura Projektu

```text
ASD_Inventory_Analytics/
├── app.py                   # Główny interfejs użytkownika Streamlit
├── requirements.txt         # Zależności bibliotek Pythona
├── .gitignore               # Pliki wykluczone z kontroli wersji
├── data/
│   └── BOM.xlsx             # Centralny plik danych (BOM i stany magazynowe)
└── src/
    ├── calculator.py        # Logika biznesowa i matematyczna wyliczeń
    ├── config.py            # Konfiguracja parametrów i ścieżek
    └── data_loader.py       # Standaryzacja i czyszczenie danych wejściowych