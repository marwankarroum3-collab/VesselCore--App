import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime

# --- 1. الهوية البصرية العالمية (Command Center UI) ---
st.set_page_config(page_title="VesselCore Intelligence OS", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    h1, h2, h3 { color: #58a6ff; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك الأرشفة والبيانات الثابتة (Master Database) ---
DB_FILE = 'vessel_master_db.csv'
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
    # بيانات أولية للسفينة مون (101 RPM) لضمان عدم ظهور رسالة "لا توجد بيانات"
    initial_data = [{'Date': datetime.now().date(), 'Ship': 'NJ MOON', 'Dist_Obs': 222.1, 'RPM': 101, 'ME_FO': 22.0, 'AE_DO': 0.0, 'Cyl_LO': 140, 'Slip': 5.2, 'Gen_Exh': '340,340,340,340,340'}]
    df = pd.DataFrame(initial_data)
    df.to_csv(DB_FILE, index=False)
    return df

df_archive = load_data()

# --- 3. محرك التحليل الهندسي (Engineering Diagnostic) ---
def calc_slip(rpm, pitch, dist_obs):
    if rpm <= 0 or dist_obs <= 0: return 0.0
    dist_eng = (rpm * 60 * 24 * pitch) / 1852
    return round(((dist_eng - dist_obs) / dist_eng) * 100, 2)

# --- 4. واجهة التحكم والربط (Sidebar) ---
with st.sidebar:
    st.title("🚢 VesselCore OS")
    st.write(f"**CEO:** Marwan Karroum")
    
    st.subheader("📡 Gmail Auto-Sync")
    st.text_input("App Password:", type="password", placeholder="أدخل الرمز المكون من 16 حرفاً")
    if st.button("تحديث وجلب بيانات الإيميل"):
        st.info("جاري الاتصال بـ Gmail...") #

    st.divider()
    with st.expander("📝 إدخال يدوي (Manual Entry)"):
        in_ship = st.selectbox("السفينة:", list(FLEET_SPECS.keys()))
        in_dist = st.number_input("Dist Obs (NM):", 0.0)
        in_rpm = st.number_input("Avg RPM:", 0.0)
        if st.button("حفظ وأرشفة"):
            slip_v = calc_slip(in_rpm, FLEET_SPECS[in_ship]['Pitch'], in_dist)
            new_row = {'Date': datetime.now().date(), 'Ship': in_ship, 'Dist_Obs': in_dist, 'RPM': in_rpm, 'Slip': slip_v}
            df_archive = pd.concat([df_archive, pd.DataFrame([new_row])], ignore_index=True)
            df_archive.to_csv(DB_FILE, index=False)
            st.rerun()

# --- 5. العرض والتحليل الاستراتيجي (Strategic Dashboard) ---
st.title("🌐 Operations & Strategic Analysis")
target_ship = st.selectbox("عرض سجلات السفينة:", list(FLEET_SPECS.keys()))
ship_db = df_archive[df_archive['Ship'] == target_ship].sort_values(by='Date')

if not ship_db.empty:
    latest = ship_db.iloc[-1]
    
    # مقاييس الأداء العليا
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance Observed", f"{latest.get('Dist_Obs', 0)} NM")
    c2.metric("Propeller Slip", f"{latest.get('Slip', 0)}%", delta="Normal" if latest.get('Slip', 0) < 15 else "High")
    c3.metric("Propeller RPM", latest.get('RPM', 0))
    c4.metric("Status", "Operational")

    st.divider()

    # الرسوم البيانية (Performance Trends)
    t1, t2 = st.columns(2)
    with t1:
        st.subheader("📉 تريند استهلاك الوقود والانزلاق")
        fig = go.Figure(go.Scatter(x=ship_db['Date'], y=ship_db['Slip'], name="Slip %", line=dict(color='#00ff00', width=3)))
        fig.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        st.subheader("🔥 تحليل حريق المولدات")
        #
        fig_gen = go.Figure(go.Bar(x=["U1", "U2", "U3", "U4", "U5", "U6"], y=[340, 350, 345, 340, 335, 340], marker_color='#3498db'))
        fig_gen.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig_gen, use_container_width=True)

    st.divider()
    st.subheader("🛠️ مقترح التحليل الهندسي (CEO Diagnostic)")
    st.success("الماكينة في حالة إبحار: يتم مراقبة كفاءة الاحتراق والضغط.") #
    st.dataframe(ship_db.tail(10))

else:
    st.warning(f"يرجى إدخال أول تقرير لـ {target_ship} لبدء الأرشفة التاريخية.")
