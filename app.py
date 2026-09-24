import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from src.data_loader import load_and_prepare_data
from src.calculator import calculate_inventory_summary

st.set_page_config(page_title="Analiza Zapasów Magazynowych", layout="wide")

st.title("📦 Analiza Zapasów i Zapotrzebowania")

# Ścieżka do wewnętrznego pliku BOM w projekcie
BOM_PATH = "data/BOM.xlsx"  # Jeśli plik leży w głównym katalogu, zmień na: "BOM.xlsx"

# Ładowanie danych z wykorzystaniem cache Streamlit dla optymalizacji
@st.cache_data
def load_data():
    return load_and_prepare_data(BOM_PATH)

df_raw = load_data()

# --- SIDEBAR: PARAMETRY ---
st.sidebar.header("⚙️ Parametry Planu")

plan_tygodniowy = st.sidebar.number_input(
    "Plan tygodniowy (szt. automatów):", 
    min_value=0, 
    value=8,
    help="Zwiększ, jeśli weszły nowe zamówienia"
)

safety_days = st.sidebar.slider(
    "Bufor bezpieczeństwa (dni robocze):", 
    min_value=0, 
    max_value=20, 
    value=3,
    help="Zwiększ, aby zabezpieczyć produkcję na więcej dni"
)

# Przeliczenie danych dla podanego planu i bufora
df_calc = calculate_inventory_summary(
    df=df_raw, 
    base_plan=plan_tygodniowy, 
    new_plan=plan_tygodniowy, 
    safety_days=safety_days
)

# --- SEKCJA 1: METRYKI MAGAZYNOWE I ZAPOTRZEBOWANIA ---
st.subheader("📍 Podsumowanie Magazynu i Braków")
col1, col2, col3, col4 = st.columns(4)

total_qty = int(df_calc['Aktualny_Stan_Magazyn'].sum())
total_val = df_calc['Wartosc_Magazynu_PLN'].sum()
shortage_qty = int(df_calc['Brak_Do_Dokupienia_Szt'].sum())
shortage_val = df_calc['Koszt_Dokupienia_PLN'].sum()

col1.metric("Stan magazynu", f"{total_qty:,} szt.".replace(",", " "))
col2.metric("Wartość magazynu", f"{total_val:,.2f} PLN".replace(",", " "))
col3.metric("Brakujące sztuki", f"{shortage_qty:,} szt.".replace(",", " "))
col4.metric("Koszt dokupienia braków", f"{shortage_val:,.2f} PLN".replace(",", " "))

st.markdown("---")

# --- SEKCJA 1B: DYNAMICZNA RELACJA BRAKÓW DO MAGAZYNU ---
st.subheader("🔄 Relacja Braków do Posiadanego Magazynu")

# 1. Podział zapotrzebowania: Produkcja vs Bufor
prod_demand = int(df_calc['Zapotrzebowanie_New_Szt'].sum())
buffer_demand = int(df_calc['Zapas_Bezpieczenstwa_Szt'].sum())
total_demand = prod_demand + buffer_demand

# 2. Rzetelne pokrycie (uwzględnia użyteczny stan per komponent, odrzucając nadwyżki)
df_calc['Uzyteczny_Zapas'] = np.minimum(df_calc['Aktualny_Stan_Magazyn'], df_calc['Calkowite_Wymaganie_Szt'])
useful_qty = int(df_calc['Uzyteczny_Zapas'].sum())

coverage_ratio = (useful_qty / total_demand * 100) if total_demand > 0 else 100.0
coverage_ratio_clamped = min(100.0, max(0.0, coverage_ratio))

# 3. Wskaźniki relatywne
shortage_ratio_qty = (shortage_qty / total_qty * 100) if total_qty > 0 else 0.0
shortage_ratio_val = (shortage_val / total_val * 100) if total_val > 0 else 0.0
items_to_order = int((df_calc['Brak_Do_Dokupienia_Szt'] > 0).sum())
total_items = len(df_calc)

# 4. Wyliczenie maksymalnego bezpiecznego bufora w dniach roboczych
daily_demand_per_item = (df_calc['Ilosc_w_BOM'] * plan_tygodniowy) / 5
avail_for_buffer = df_calc['Aktualny_Stan_Magazyn'] - df_calc['Zapotrzebowanie_New_Szt']

days_cover = np.where(
    daily_demand_per_item > 0,
    np.floor(avail_for_buffer / daily_demand_per_item),
    999.0
)
max_safe_buffer_days = int(np.maximum(0, np.min(days_cover)))

# Dynamiczny komunikat podsumowujący
if shortage_qty == 0:
    st.success(
        f"✅ **Stan magazynowy w pełni wystarcza** na produkcję **{plan_tygodniowy} szt.** automatów oraz bufor **{safety_days} dni**! "
        f"(Maksymalny bufor bez dokupywania to **{max_safe_buffer_days} dni**)."
    )
else:
    st.warning(
        f"⚠️ Dla planu **{plan_tygodniowy} szt.** i bufora **{safety_days} dni** wymagane jest dokupienie "
        f"**{shortage_qty:,} szt.** komponentów o wartości **{shortage_val:,.2f} PLN**.".replace(",", " ")
    )

r1, r2, r3, r4, r5 = st.columns(5)
r1.metric(
    "Pokrycie zapotrzebowania", 
    f"{coverage_ratio:.1f}%", 
    help="Jaki % całkowitego zapotrzebowania (Plan + Bufor) pokrywa Twój obecny magazyn"
)
r2.metric(
    "Zapotrzebowanie na Plan", 
    f"{prod_demand:,} szt.".replace(",", " "), 
    help=f"Wynika z planu tygodniowego ({plan_tygodniowy} automatów)"
)
r3.metric(
    "Zapotrzebowanie na Bufor", 
    f"{buffer_demand:,} szt.".replace(",", " "), 
    help=f"Wynika z bufora bezpieczeństwa ({safety_days} dni)"
)
r4.metric(
    "Maks. bezpieczny bufor", 
    f"{max_safe_buffer_days} dni", 
    help="Maksymalna liczba dni bufora, dla której żaden komponent nie wygeneruje braku"
)
r5.metric(
    "Pozycje do zamówienia", 
    f"{items_to_order} z {total_items} poz.",
    help="Liczba pozycji z BOM, w których występują braki"
)

# Pasek postępu pokrycia zapotrzebowania
st.caption(f"**Stopień pokrycia całkowitego zapotrzebowania ({useful_qty:,} / {total_demand:,} szt.):** {coverage_ratio:.1f}%".replace(",", " "))
st.progress(int(coverage_ratio_clamped))

# Podsumowanie wzrostu zapasów
c_info1, c_info2 = st.columns(2)
c_info1.info(f"📈 **Potrzebny wzrost ilościowy zapasów:** +{shortage_ratio_qty:.1f}% w stosunku do obecnego magazynu")
c_info2.info(f"💰 **Potrzebny wzrost wartościowy magazynu:** +{shortage_ratio_val:.1f}% w stosunku do obecnej wartości")

st.markdown("---")

# --- SEKCJA 2: WYKRES SŁUPKOWY (OBOK SIEBIE) ---
st.subheader("📈 Stan Magazynowy vs Zapotrzebowanie Tygodniowe vs Zapas Bezpieczeństwa")

plot_data = []
for _, row in df_calc.iterrows():
    komponent = row['Nazwa Komponentu']
    plot_data.append({'Komponent': komponent, 'Kategoria': '1. Stan Magazynowy', 'Ilość [szt.]': row['Aktualny_Stan_Magazyn']})
    plot_data.append({'Komponent': komponent, 'Kategoria': '2. Zapotrzebowanie Tygodniowe', 'Ilość [szt.]': row['Zapotrzebowanie_New_Szt']})
    plot_data.append({'Komponent': komponent, 'Kategoria': '3. Zapas Bezpieczeństwa', 'Ilość [szt.]': row['Zapas_Bezpieczenstwa_Szt']})

df_plot = pd.DataFrame(plot_data)

fig = px.bar(
    df_plot,
    x='Komponent',
    y='Ilość [szt.]',
    color='Kategoria',
    barmode='group',
    color_discrete_sequence=['#2ecc71', '#3498db', '#e67e22']
)

fig.update_layout(xaxis_tickangle=-45, height=500, legend_title_text='', margin=dict(l=20, r=20, t=30, b=20))
st.plotly_chart(fig, use_container_width=True)

# --- SEKCJA 3: TABELA SZCZEGÓŁOWA ---
with st.expander("📄 Zobacz tabelę szczegółową z wyliczeniami"):
    display_cols = [
        'Nazwa Komponentu', 'Ilosc_w_BOM', 'Cena_Jednostkowa_PLN', 
        'Aktualny_Stan_Magazyn', 'Wartosc_Magazynu_PLN',
        'Zapotrzebowanie_New_Szt', 'Zapas_Bezpieczenstwa_Szt',
        'Brak_Do_Dokupienia_Szt', 'Koszt_Dokupienia_PLN'
    ]
    
    unique_cols = list(dict.fromkeys(display_cols))
    df_display = df_calc.loc[:, ~df_calc.columns.duplicated()]
    available_cols = [col for col in unique_cols if col in df_display.columns]
    
    st.dataframe(df_display[available_cols], use_container_width=True)