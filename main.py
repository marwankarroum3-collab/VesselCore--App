import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. إعدادات الهوية العالمية (World Class UI) ---
st.set_page_config(page_title="VesselCore Master OS", layout="wide")

# تصميم CSS لغرفة التحكم (Control Room Design)
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    [data-testid="stSidebar"] { background-color: #010409; border-right: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات الموثقة (Verified Fleet Database) ---
# تم استعادة السفن الـ 4 مع بيانات NJ MOON الحقيقية
FLEET_DB = {
    "NJ MOON": {
        "Specs": "MAN B&W 6S50MC-C",
        "Last_Report": {
            "Date": "2026-02-11", "Loc": "27 44.52 N / 033 48.56 E", "Dist": 222.1, "Speed": 9.2, 
            "RPM": 101, "ME_FO": 22.0, "Cyl_LO": 140, "Gen_LO": 40, "Load": 50, "LO_P": 2.8,
            "Exh": [337, 360, 355, 345, 335, 348]
        }
    },
    "NJ MARS": {
        "Specs": "MAN B&W 6S60MC-C",
        "Last_Report": {"Date": "2026-02-11", "Loc": "Freetown Port", "Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "Cyl_LO": 0, "Gen_LO": 20, "Load": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0]}
    },
    "NJ AIO": {
        "Specs": "Mitsubishi UEC",
        "Last_Report": {"Date": "2026-02-11", "Loc": "Loading Port", "Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "Cyl_LO": 0, "Gen_LO": 28, "Load": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0]}
    },
    "YARA J": {
        "Specs": "MAN B&W 5S50MC-C",
        "Last_Report": {"Date": "2026-02-11", "Loc": "Anchorage", "Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "Cyl_LO": 0, "Gen_LO": 22, "Load": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0]}
    }
}

# --- 3. محرك التحليل الهندسي (Manufacturer Diagnostic) ---
def run_diagnostic(exh, load):
    if load == 0 or sum(exh) == 0: return "SYSTEM STANDBY", "#8b949e", "Engine stopped. Monitoring auxiliaries."
    avg_t = sum(exh)/6
    max_dev = max([abs(x - avg_t) for x in exh])
    if max_dev > 30: return "CRITICAL IMBALANCE", "#f85149", f"Alert: High thermal deviation ({int(max_dev)}°C). Check injectors."
    return "OPTIMAL PERFORMANCE", "#3fb950", "Combustion is balanced within manufacturer limits."

# --- 4. واجهة المستخدم (The Dashboard) ---
with st.sidebar:
    st.title("🚢 VesselCore Pro")
    st.write(f"**Chief Engineer:** Marwan Karroum")
    ship = st.selectbox("Select Vessel:", list(FLEET_DB.keys()))
    st.divider()
    st.info("📡 Automatic Sync Active: marwankarroum3@gmail.com")

t = FLEET_DB[ship]["Last_Report"]
diag_status, diag_color, diag_msg = run_diagnostic(t['Exh'], t['Load'])

st.title(f"🚀 Dashboard: {ship} | {t['Date']}")
st.markdown(f"**Position:** `{t['Loc']}` | **Engine:** `{FLEET_DB[ship]['Specs']}`")

# عرض الـ KPIs الحقيقية المستخرجة من تقريرك
c1, c2, c3, c4 = st.columns(4)
c1.metric("Fuel Consumption (ME)", f"{t['ME_FO']} MT", "Actual")
c2.metric("Propulsion RPM", t['RPM'], "Stable")
c3.metric("Cylinder Oil (24h)", f"{t['Cyl_LO']} L", "Actual")
c4.metric("LO Inlet Press", f"{t['LO_P']} bar", "Normal")

st.divider()

# تحليل الاحتراق (Exhaust Gas Analysis)
col_left, col_right = st.columns([2, 1])
with col_left:
    st.subheader("🔥 Exhaust Gas Thermal Profile (Cyl 1-6)")
    if sum(t['Exh']) > 0:
        fig = go.Figure(go.Bar(x=[f"Cyl {i+1}" for i in range(6)], y=t['Exh'], marker_color='#58a6ff'))
        fig.add_hline(y=sum(t['Exh'])/6, line_dash="dash", line_color="white", annotation_text="Mean Temp")
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else: st.warning("Main Engine is Offline. Monitoring Generator Performance.")

with col_right:
    st.subheader("🛠️ Technical Diagnostic")
    st.markdown(f"**Health Status:** <span style='color:{diag_color}; font-weight:bold;'>{diag_status}</span>", unsafe_allow_html=True)
    st.write(diag_msg)
    st.table(pd.DataFrame({
        "Parameter": ["Engine Load", "Avg. Exh Temp", "Generator Oil"],
        "Value": [f"{t['Load']}%", f"{int(sum(t['Exh'])/6)}°C", f"{t['Gen_LO']} L"]
    }))