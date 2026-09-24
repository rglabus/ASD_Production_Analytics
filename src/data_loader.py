import pandas as pd

def _clean_numeric(series: pd.Series) -> pd.Series:
    """
    Czyszczenie wartości numerycznych z tekstów, walut i przecinków.
    """
    if pd.api.types.is_numeric_dtype(series):
        return series.fillna(0.0).astype(float)
    
    s = series.astype(str).str.strip().str.replace('\xa0', '', regex=False).str.replace(' ', '', regex=False)
    s = s.str.replace(',', '.', regex=False)
    s = s.str.replace(r'[^0-9.-]', '', regex=True)
    return pd.to_numeric(s, errors='coerce').fillna(0.0)

def load_and_prepare_data(filepath: str) -> pd.DataFrame:
    df = pd.read_excel(filepath)
    df.columns = df.columns.astype(str).str.strip()

    # Usunięcie duplikatów kolumn, jeśli plik Excel sam w sobie miał powtórzone nagłówki
    df = df.loc[:, ~df.columns.duplicated()].copy()

    keywords = {
        'Nazwa Komponentu': ['nazwa komponentu', 'nazwa', 'komponent', 'opis', 'artykuł', 'item'],
        'Ilosc_w_BOM': ['ilosc w bom', 'ilość w bom', 'ilosc_w_bom', 'ilosc', 'ilość', 'bom', 'sztuk'],
        'Cena_Jednostkowa_PLN': ['cena jednostkowa', 'cena pln', 'cena', 'price', 'koszt'],
        'Aktualny_Stan_Magazyn': ['aktualny stan', 'stan magazynowy', 'stan magazyn', 'stan', 'stock']
    }

    rename_dict = {}
    used_cols = set()

    for target_col, kws in keywords.items():
        # 1. Najpierw szukamy dokładnego dopasowania
        exact_match = None
        for col in df.columns:
            if col not in used_cols and col.lower() == target_col.lower():
                exact_match = col
                break
        
        if exact_match:
            rename_dict[exact_match] = target_col
            used_cols.add(exact_match)
        else:
            # 2. Jeśli brak dokładnego dopasowania, szukamy po słowach kluczowych
            for col in df.columns:
                if col not in used_cols and any(kw in str(col).lower() for kw in kws):
                    rename_dict[col] = target_col
                    used_cols.add(col)
                    break

    df = df.rename(columns=rename_dict)

    # Bezpieczeństwo: ponowne usunięcie duplikatów kolumn po zmianie nazw
    df = df.loc[:, ~df.columns.duplicated()].copy()

    # Czyszczenie i konwersja kolumn numerycznych
    for col in ['Ilosc_w_BOM', 'Cena_Jednostkowa_PLN', 'Aktualny_Stan_Magazyn']:
        if col in df.columns:
            df[col] = _clean_numeric(df[col])
        else:
            df[col] = 0.0

    if 'Nazwa Komponentu' not in df.columns:
        df['Nazwa Komponentu'] = [f"Komponent {i+1}" for i in range(len(df))]

    return df