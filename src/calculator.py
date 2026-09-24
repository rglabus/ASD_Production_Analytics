import pandas as pd
import numpy as np

def calculate_inventory_summary(
    df: pd.DataFrame, 
    base_plan: int, 
    new_plan: int, 
    safety_days: int, 
    working_days: int = 5
) -> pd.DataFrame:
    """
    Uproszczony silnik wyliczający stan magazynowy, zapotrzebowanie 
    oraz deltę zakupów przy skalowaniu planu produkcyjnego.
    """
    res = df.copy()

    # 1. Wartość obecnego magazynu
    res['Wartosc_Magazynu_PLN'] = res['Aktualny_Stan_Magazyn'] * res['Cena_Jednostkowa_PLN']

    # 2. Zapotrzebowanie na komponenty dla planów tygodniowych
    res['Zapotrzebowanie_Base_Szt'] = res['Ilosc_w_BOM'] * base_plan
    res['Zapotrzebowanie_New_Szt'] = res['Ilosc_w_BOM'] * new_plan

    # 3. Zapas bezpieczeństwa (bufor N dni na podstawie nowego planu)
    daily_demand = res['Zapotrzebowanie_New_Szt'] / working_days
    res['Zapas_Bezpieczenstwa_Szt'] = np.ceil(daily_demand * safety_days)

    # 4. Całkowite zapotrzebowanie operacyjne (Tydzień + Bufor N dni)
    res['Calkowite_Wymaganie_Szt'] = res['Zapotrzebowanie_New_Szt'] + res['Zapas_Bezpieczenstwa_Szt']

    # 5. Brakujące ilości i koszt dokupienia dla Nowego Planu
    res['Brak_Do_Dokupienia_Szt'] = np.maximum(0.0, res['Calkowite_Wymaganie_Szt'] - res['Aktualny_Stan_Magazyn'])
    res['Koszt_Dokupienia_PLN'] = res['Brak_Do_Dokupienia_Szt'] * res['Cena_Jednostkowa_PLN']

    # 6. Wyliczenie delty (o ile zwiększyć zakupy w stosunku do planu bazowego)
    base_daily = res['Zapotrzebowanie_Base_Szt'] / working_days
    base_safety = np.ceil(base_daily * safety_days)
    base_total_req = res['Zapotrzebowanie_Base_Szt'] + base_safety
    base_shortage = np.maximum(0.0, base_total_req - res['Aktualny_Stan_Magazyn'])

    res['Delta_Zakupow_Szt'] = res['Brak_Do_Dokupienia_Szt'] - base_shortage
    res['Delta_Koszt_PLN'] = res['Delta_Zakupow_Szt'] * res['Cena_Jednostkowa_PLN']

    return res