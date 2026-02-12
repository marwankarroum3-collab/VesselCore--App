import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

# --- 1. الهوية البصرية (Military Grade Dashboard) ---
st.set_page_config(page_title="VesselCore Intelligence OS", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #e1e4e8; }
    .stMetric { background-color: #1c2128; border: 1px solid #30363d; padding: 20px; border-radius: 8px; }
    h1, h2, h3 { color: #58a6ff; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك الأرشفة والبيانات الثابتة (Persistence Engine) ---
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
    init_data = [{'Date': datetime.now().date(), 'Ship': 'NJ MOON', 'Dist_Obs': 222.1, 'RPM': 101, 'ME_FO': 22.0, 'AE_DO': 0.0, 'Cyl_LO': 140, 'Slip': 5.2, 'Gen_Exh': '340,345,350,342,338'}]
    df = pd.DataFrame(init_data)
    df.to_csv(DB_FILE, index=False)
    return df

df_archive = load_data()

# --- 3. محرك التحليل الهندسي (Marine Engineering Brain) ---
def calc_slip(rpm, pitch, dist_obs):
    if rpm <= 0 or dist_obs <= 0: return 0.0
    dist_eng = (rpm * 60 * 24 * pitch) / 1852
    slip = ((dist_eng - dist_obs) / dist_eng) * 100
    return round(slip, 2)

# --- 4. واجهة التحكم الجانبية (Sidebar Command) ---
with st.sidebar:
    st.title("🚢 VesselCore Command")
    st.write(f"**CEO:** Marwan Karroum")
    
    st.divider()
    menu = st.radio("القائمة:", ["اللوحة الرئيسية", "أرشفة تقرير نون"])
    
    if menu == "أرشفة تقرير نون":
        with st.expander("📝 إدخال البيانات الحقيقية"):
            s_ship = st.selectbox("السفينة:", list(FLEET_SPECS.keys()))
            s_date = st.date_input("التاريخ:", datetime.now())
            s_dist = st.number_input("Dist Observed (NM):", 0.0)
            s_rpm = st.number_input("Average RPM:", 0.0)
            s_fo = st.number_input("ME Fuel (MT):", 0.0)
            s_ae_do = st.number_input("AE Fuel (MT):", 0.0)
            s_cyl = st.number_input("Cyl Oil (L):", 0)
            s_gen_exh = st.text_input("Gen Exh (C1,C2,C3...):", "340,340,340,340,340")
            
            if st.button("حفظ وأرشفة"):
                slip_v = calc_slip(s_rpm, FLEET_SPECS[s_ship]['Pitch'], s_dist)
                new_row = {'Date': s_date, 'Ship': s_ship, 'Dist_Obs': s_dist, 'RPM': s_rpm, 'ME_FO': s_fo, 'AE_DO': s_ae_do, 'Cyl_LO': s_cyl, 'Slip': slip_v, 'Gen_Exh': s_gen_exh}
                df_archive = pd.concat([df_archive, pd.DataFrame([new_row])], ignore_index=True)
                df_archive.to_csv(DB_FILE, index=False)
                st.success("تم الحفظ بنجاح!")

# --- 5. العرض والتحليل الاستراتيجي (Strategic Dashboard) ---
st.title("🌐 Fleet Operations & Strategic Analysis")
target_ship = st.selectbox("اختر السفينة للتحليل العميق:", list(FLEET_SPECS.keys()))
ship_db = df_archive[df_archive['Ship'] == target_ship].sort_values(by='Date')

if not ship_db.empty:
    latest = ship_db.iloc[-1]
    
    # مقاييس الأداء العليا
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance Observed", f"{latest['Dist_Obs']} NM")
    c2.metric("Propeller Slip", f"{latest['Slip']}%", delta="Normal" if latest['Slip'] < 15 else "Critical")
    c3.metric("Bunker Cons (ME)", f"{latest['ME_FO']} MT")
    c4.metric("Engine RPM", latest['RPM'])

    st.divider()

    # نظام التبويبات الفنية
    tab1, tab2, tab3 = st.tabs(["📉 تريندات الأداء", "🔥 تحليل الاحتراق", "📂 الأرشيف الكامل"])
    
    with tab1:
        st.subheader("تحليل كفاءة الملاحة والوقود")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=ship_db['Date'], y=ship_db['ME_FO'], name="Fuel ME (MT)", line=dict(color='#3498db', width=3)), secondary_y=False)
        fig.add_trace(go.Scatter(x=ship_db['Date'], y=ship_db['Slip'], name="Slip %", line=dict(color='#00ff00', width=2, dash='dot')), secondary_y=True)
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Auxiliary Engine Exhaust Analysis")
        
        exh_vals = [int(x) for x in str(latest.get('Gen_Exh', "0,0,0,0,0")).split(',')]
        fig_ae = go.Figure(go.Bar(x=[f"Unit {i+1}" for i in range(len(exh_vals))], y=exh_vals, marker_color='#e67e22'))
        fig_ae.update_layout(template="plotly_dark", height=350, title="Generator Exhaust Profile")
        st.plotly_chart(fig_ae, use_container_width=True)

    with tab3:
        st.subheader("سجل الأرشفة التاريخي")
        st.dataframe(ship_db.sort_values(by='Date', ascending=False), use_container_width=True)

else:
    st.warning(f"بانتظار إدخال أول تقرير لـ {target_ship}.")

st.divider()
st.caption("© 2026 VesselCore Technical - Engineering Master Intelligence | Marwan Karroum")
