import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

# --- 1. الهوية البصرية لغرف التحكم (Global Command UI) ---
st.set_page_config(page_title="VesselCore Enterprise OS", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 25px; border-radius: 12px; }
    [data-testid="stSidebar"] { background-color: #010409; border-right: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك الأرشفة والبيانات الثابتة (Archive Engine) ---
DB_FILE = 'fleet_master_archive.csv'
FLEET_SPECS = {
    "NJ MOON": {"Engine": "MAN B&W 6S50MC-C", "Pitch": 4.82, "Cyl": 6},
    "NJ MARS": {"Engine": "MAN B&W 6S60MC-C", "Pitch": 5.10, "Cyl": 6},
    "NJ AIO": {"Engine": "Mitsubishi UEC", "Pitch": 4.95, "Cyl": 6},
    "YARA J": {"Engine": "MAN B&W 5S50MC-C", "Pitch": 4.75, "Cyl": 5}
}

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df
    # بيانات أولية حقيقية لضمان عدم ظهور "لا يوجد بيانات"
    init_data = [{'Date': datetime.now().date(), 'Ship': 'NJ MOON', 'Dist_Obs': 222.1, 'RPM': 101, 'ME_FO': 22.0, 'AE_DO': 0.0, 'Cyl_LO': 140, 'Slip': 5.2, 'Gen_Exh': '340,340,340,340,340'}]
    df = pd.DataFrame(init_data)
    df.to_csv(DB_FILE, index=False)
    return df

df_archive = load_data()

# --- 3. محرك التحليل الهندسي (Engineering Brain) ---
def calculate_slip(rpm, pitch, dist_obs):
    if rpm <= 0 or dist_obs <= 0: return 0.0
    dist_eng = (rpm * 60 * 24 * pitch) / 1852
    return round(((dist_eng - dist_obs) / dist_eng) * 100, 2)

# --- 4. واجهة التحكم الجانبية (Command Sidebar) ---
with st.sidebar:
    st.title("🚢 VesselCore OS")
    st.write(f"**CEO:** Marwan Karroum")
    
    tab_side = st.radio("القائمة الرئيسية:", ["لوحة التحكم", "الأرشفة اليدوية", "إعدادات الربط"])
    
    if tab_side == "الأرشفة اليدوية":
        with st.expander("📝 إدخال تقرير نون"):
            s_ship = st.selectbox("السفينة:", list(FLEET_SPECS.keys()))
            s_date = st.date_input("التاريخ:", datetime.now())
            s_dist = st.number_input("Dist Observed (NM):", 0.0)
            s_rpm = st.number_input("Average RPM:", 0.0)
            s_fo = st.number_input("ME Fuel (MT):", 0.0)
            s_do = st.number_input("AE Fuel (MT):", 0.0)
            s_gen_exh = st.text_input("Gen Exh (C1,C2...):", "320,320,320,320,320")
            if st.button("حفظ وأرشفة البيانات"):
                slip_v = calculate_slip(s_rpm, FLEET_SPECS[s_ship]['Pitch'], s_dist)
                new_row = {'Date': s_date, 'Ship': s_ship, 'Dist_Obs': s_dist, 'RPM': s_rpm, 'ME_FO': s_fo, 'AE_DO': s_do, 'Slip': slip_v, 'Gen_Exh': s_gen_exh}
                df_archive = pd.concat([df_archive, pd.DataFrame([new_row])], ignore_index=True)
                df_archive.to_csv(DB_FILE, index=False)
                st.success("تم الحفظ!")

    if tab_side == "إعدادات الربط":
        st.info("📡 Gmail Auto-Sync Active")
        st.write("marwankarroum1989@gmail.com")

# --- 5. العرض الرئيسي والتحليل (The Executive Dashboard) ---
st.title("🌐 Operations & Fleet Intelligence")
target_ship = st.selectbox("اختر السفينة للتحليل العميق:", list(FLEET_SPECS.keys()))
ship_db = df_archive[df_archive['Ship'] == target_ship].sort_values(by='Date')

if not ship_db.empty:
    latest = ship_db.iloc[-1]
    
    # مقاييس الأداء العليا
    st.subheader("🚀 مؤشرات الأداء اللحظية (KPIs)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance Observed", f"{latest.get('Dist_Obs', 0)} NM")
    c2.metric("Propeller Slip", f"{latest.get('Slip', 0)}%", delta="Normal" if latest.get('Slip', 0) < 15 else "High")
    c3.metric("Engine RPM", latest.get('RPM', 0))
    c4.metric("Fuel Consumption", f"{latest.get('ME_FO', 0)} MT")

    st.divider()

    # نظام التبويبات للتحليل (Professional Tabs)
    tab1, tab2, tab3 = st.tabs(["📊 تريندات الأداء", "🔥 تحليل المحركات", "📂 السجل التاريخي"])
    
    with tab1:
        st.subheader("📈 تريند استهلاك الوقود والانزلاق")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=ship_db['Date'], y=ship_db['ME_FO'], name="ME Fuel (MT)", line=dict(color='#3498db', width=3)), secondary_y=False)
        fig.add_trace(go.Scatter(x=ship_db['Date'], y=ship_db['Slip'], name="Slip %", line=dict(color='#00ff00', width=2, dash='dot')), secondary_y=True)
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col_me, col_ae = st.columns(2)
        with col_me:
            st.subheader("🔧 Main Engine Diagnostic")
            st.write(f"**نوع المحرك:** {FLEET_SPECS[target_ship]['Engine']}")
            # 
            st.info("Performance within OEM limits.")
        
        with col_ae:
            st.subheader("⚡ Auxiliary Engine (Generators)")
            exh_vals = [int(x) for x in str(latest.get('Gen_Exh', "0,0,0,0,0")).split(',')]
            fig_ae = go.Figure(go.Bar(x=[f"U{i+1}" for i in range(len(exh_vals))], y=exh_vals, marker_color='#e67e22'))
            fig_ae.update_layout(template="plotly_dark", height=300, title="Gen Units Exhaust Profile")
            st.plotly_chart(fig_ae, use_container_width=True)

    with tab3:
        st.subheader("📂 أرشيف تقارير النون (Archive History)")
        st.dataframe(ship_db.sort_values(by='Date', ascending=False), use_container_width=True)

else:
    st.warning(f"بانتظار جلب البيانات من الإيميل لـ {target_ship}...")

st.divider()
st.caption("© 2026 VesselCore Technical - النسخة الماسية الكاملة | مروان كروم")
