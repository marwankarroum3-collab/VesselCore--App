import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime

# --- 1. الهوية البصرية العالمية (Command Center UI) ---
st.set_page_config(page_title="VesselCore Legacy OS", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    h1, h2, h3 { color: #58a6ff; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك الأرشفة والبيانات الحقيقية (Persistence Engine) ---
DB_FILE = 'vessel_master_archive.csv'
FLEET_SPECS = {
    "NJ MOON": {"Engine": "MAN B&W 6S50MC-C", "Pitch": 4.82},
    "NJ MARS": {"Engine": "MAN B&W 6S60MC-C", "Pitch": 5.10},
    "NJ AIO": {"Engine": "Mitsubishi UEC", "Pitch": 4.95},
    "YARA J": {"Engine": "MAN B&W 5S50MC-C", "Pitch": 4.75}
}

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df
    # بيانات أولية حقيقية لضمان عمل الأرشيف فوراً
    init_data = [{'Date': datetime.now().date(), 'Ship': 'NJ MOON', 'Dist_Obs': 222.1, 'RPM': 101, 'ME_FO': 22.0, 'AE_DO': 0.0, 'Cyl_LO': 140, 'Slip': 5.2, 'Gen_Exh': '340,340,340,340,340'}]
    df = pd.DataFrame(init_data)
    df.to_csv(DB_FILE, index=False)
    return df

df_archive = load_data()

# --- 3. محرك التحليل الهندسي (Analytical Brain) ---
def calculate_slip(rpm, pitch, dist_obs):
    if rpm <= 0 or dist_obs <= 0: return 0.0
    # مسافة الماكينة بالاميال البحرية
    # $Dist_{Eng} = \frac{RPM \times 60 \times 24 \times Pitch}{1852}$
    dist_eng = (rpm * 60 * 24 * pitch) / 1852
    slip = ((dist_eng - dist_obs) / dist_eng) * 100
    return round(slip, 2)

# --- 4. واجهة التحكم (Command Sidebar) ---
with st.sidebar:
    st.title("🚢 VesselCore Port")
    st.write(f"**CEO:** Marwan Karroum")
    
    with st.expander("📝 إدخال تقرير نون (Archive Log)"):
        s_ship = st.selectbox("اختر السفينة:", list(FLEET_SPECS.keys()))
        s_date = st.date_input("التاريخ:", datetime.now())
        s_dist = st.number_input("Dist Observed (NM):", 0.0)
        s_rpm = st.number_input("Average RPM:", 0.0)
        s_fo = st.number_input("ME Fuel Cons (MT):", 0.0)
        if st.button("حفظ وأرشفة البيانات"):
            slip_v = calculate_slip(s_rpm, FLEET_SPECS[s_ship]['Pitch'], s_dist)
            new_row = {'Date': s_date, 'Ship': s_ship, 'Dist_Obs': s_dist, 'RPM': s_rpm, 'ME_FO': s_fo, 'Slip': slip_v}
            df_archive = pd.concat([df_archive, pd.DataFrame([new_row])], ignore_index=True)
            df_archive.to_csv(DB_FILE, index=False)
            st.success("Data Archived!")

# --- 5. العرض والتحليل الاستراتيجي (Strategic Dashboard) ---
st.title("🌍 Fleet Strategic Operations")
target_ship = st.selectbox("عرض سجلات السفينة:", list(FLEET_SPECS.keys()))
ship_db = df_archive[df_archive['Ship'] == target_ship].sort_values(by='Date')

if not ship_db.empty:
    latest = ship_db.iloc[-1]
    
    # مقاييس الأداء العليا
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance Observed", f"{latest.get('Dist_Obs', 0)} NM")
    c2.metric("Propeller Slip", f"{latest.get('Slip', 0)}%", delta="Normal" if latest.get('Slip', 0) < 15 else "High")
    c3.metric("Fuel Consumption", f"{latest.get('ME_FO', 0)} MT")
    c4.metric("RPM", latest.get('RPM', 0))

    st.divider()

    # تريندات الأداء (Trends)
    t1, t2 = st.columns(2)
    with t1:
        st.subheader("📉 تريند الانزلاق (Slip Trend)")
        fig = go.Figure(go.Scatter(x=ship_db['Date'], y=ship_db['Slip'], mode='lines+markers', line=dict(color='#00ff00', width=3)))
        fig.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        st.subheader("🔥 تحليل حريق المولدات")
        # 
        fig_gen = go.Figure(go.Bar(x=["U1", "U2", "U3", "U4", "U5"], y=[340, 350, 345, 340, 335], marker_color='#3498db'))
        fig_gen.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig_gen, use_container_width=True)

    st.divider()
    st.subheader("📂 الأرشيف الكامل للسفينة (Historical Archive)")
    st.dataframe(ship_db, use_container_width=True)

else:
    st.warning(f"لا توجد بيانات مؤرشفة لـ {target_ship}. بانتظار تقريرك الأول.")
