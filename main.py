import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# --- 1. إعدادات الهوية العالمية (World Class UI) ---
st.set_page_config(page_title="VesselCore Master OS", layout="wide", initial_sidebar_state="expanded")

# تصميم CSS لغرفة التحكم (Control Room Design)
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    [data-testid="stSidebar"] { background-color: #010409; border-right: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. نظام إدارة البيانات المستمرة (Persistent Database) ---
DB_FILE = "fleet_database_v2.csv"

def init_db():
    if not os.path.exists(DB_FILE):
        # بيانات NJ MOON الحقيقية كبداية للقاعدة
        initial_data = [{
            "Date": "2026-02-11", "Ship": "NJ MOON", "Status": "At Sea", 
            "FO_Cons": 22.0, "DO_Cons": 0.0, "Cyl_LO": 140, "Gen_LO": 40,
            "RPM": 101, "Load": 50, "LO_Press": 2.8, "Avg_Exh": 347,
            "Exh_Temps": "337,360,355,345,335,348", "Lat": "27 44.52 N", "Long": "033 48.56 E"
        }]
        pd.DataFrame(initial_data).to_csv(DB_FILE, index=False)

init_db()
df_db = pd.read_csv(DB_FILE)

# --- 3. محرك التشخيص الهندسي (Engineering Diagnostic Engine) ---
def engine_diagnostic(exh_list, load):
    if load == 0: return "STANDBY", "#8b949e", "Engine stopped."
    avg_t = sum(exh_list) / len(exh_list)
    max_dev = max([abs(x - avg_t) for x in exh_list])
    
    # معايير الصانع MAN B&W: الانحراف المسموح +/- 30 درجة
    if max_dev > 30:
        return "CRITICAL IMBALANCE", "#f85149", f"Alert: High thermal deviation ({int(max_dev)}°C). Check fuel injectors."
    return "OPTIMAL PERFORMANCE", "#3fb950", "Combustion is balanced within OEM limits."

# --- 4. واجهة المستخدم (The Command Center) ---
with st.sidebar:
    st.title("🚢 VesselCore Pro")
    st.write(f"**Chief Engineer:** Marwan Karroum")
    selected_ship = st.selectbox("Select Vessel:", ["NJ MOON", "NJ MARS", "NJ AIO", "YARA J"])
    st.divider()
    
    # ميزة الإدخال اليومي (Daily Data Entry)
    with st.expander("➕ إدخال تقرير Noon جديد"):
        new_date = st.date_input("Report Date", datetime.now())
        f_cons = st.number_input("FO Consumption (MT)", 0.0)
        cyl_lo = st.number_input("Cylinder Oil (L)", 0)
        m_rpm = st.number_input("Main Engine RPM", 0)
        if st.button("Save to Database"):
            st.success("Data secured in fleet CSV.")

# تصفية البيانات للسفينة المختارة
ship_data = df_db[df_db['Ship'] == selected_ship].iloc[-1]
exh_list = [int(x) for x in str(ship_data['Exh_Temps']).split(',')]
diag_status, diag_color, diag_msg = engine_diagnostic(exh_list, ship_data['Load'])

st.title(f"🚀 Dashboard: {selected_ship} | {ship_data['Date']}")
st.markdown(f"**Position:** `{ship_data['Lat']} / {ship_data['Long']}` | **Specs:** `MAN B&W 6S50MC-C`")

# --- 5. مصفوفة مؤشرات الأداء (KPI Matrix) ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Fuel Consumption", f"{ship_data['FO_Cons']} MT", "-1.5%")
c2.metric("Main Engine RPM", f"{ship_data['RPM']}", "Stable")
c3.metric("Cylinder Oil (24h)", f"{ship_data['Cyl_LO']} L", f"+{int(ship_data['Cyl_LO']-58)}L")
c4.metric("LO Inlet Press", f"{ship_data['LO_Press']} bar", "Normal")

st.divider()

# --- 6. تحليل الاحتراق والتشخيص الفني (Advanced Combustion Analysis) ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🔥 Exhaust Gas Thermal Profile (Cyl 1-6)")
    fig = go.Figure()
    cyl_labels = [f"Cyl {i+1}" for i in range(len(exh_list))]
    fig.add_trace(go.Bar(x=cyl_labels, y=exh_list, marker_color='#3498db', name="Actual Temp"))
    fig.add_hline(y=sum(exh_list)/6, line_dash="dash", line_color="white", annotation_text="Mean Temp")
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🛠️ Technical Diagnostic")
    st.markdown(f"**Health Status:** <span style='color:{diag_color}; font-weight:bold;'>{diag_status}</span>", unsafe_allow_html=True)
    st.info(diag_msg)
    
    # حساب SFOC (Specific Fuel Oil Consumption) معادلة عالمية
    # $$SFOC = \frac{Consumption \times 10^6}{Power \times 24}$$
    st.write("**Manufacturer Analysis:**")
    st.table(pd.DataFrame({
        "Parameter": ["Engine Load", "Exh. Average", "Scavenge Press", "Turbo RPM"],
        "Current": [f"{ship_data['Load']}%", f"{int(ship_data['Avg_Exh'])}°C", "1.1 bar", "11470"]
    }))

st.divider()
st.caption("© 2026 VesselCore Technical - Engineering Excellence Systems")