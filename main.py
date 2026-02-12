import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. الهوية البصرية العالمية (Command Center UI) ---
st.set_page_config(page_title="VesselCore Technical Master OS", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    [data-testid="stSidebar"] { background-color: #010409; border-right: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. قاعدة البيانات الحقيقية والمدققة (الأربع سفن - فبراير 2026) ---
# تم إدخال الأرقام الحقيقية (101 RPM، 140 لتر زيت، إلخ)
FLEET_DB = {
    "NJ MOON": {
        "Specs": {"Engine": "MAN B&W 6S50MC-C", "Pitch": 4.82},
        "History": [
            {"Date": "2026-02-12", "Dist_Obs": 230.5, "RPM": 102, "ME_FO": 22.5, "AE_DO": 0.0, "Cyl_LO": 142, "LO_P": 2.8, "Exh": [340, 362, 358, 348, 338, 350], "Gen_Exh": [350, 345, 340, 335, 345]},
            {"Date": "2026-02-11", "Dist_Obs": 222.1, "RPM": 101, "ME_FO": 22.0, "AE_DO": 0.0, "Cyl_LO": 140, "LO_P": 2.8, "Exh": [337, 360, 355, 345, 335, 348], "Gen_Exh": [340, 340, 350, 350, 340]}
        ]
    },
    "NJ MARS": {
        "Specs": {"Engine": "MAN B&W 6S60MC-C", "Pitch": 5.10},
        "History": [{"Date": "2026-02-12", "Dist_Obs": 0, "RPM": 0, "ME_FO": 0, "AE_DO": 3.3, "Cyl_LO": 0, "LO_P": 0, "Exh": [0]*6, "Gen_Exh": [310, 315, 320, 318, 310]}]
    },
    "NJ AIO": {
        "Specs": {"Engine": "Mitsubishi UEC", "Pitch": 4.95},
        "History": [{"Date": "2026-02-12", "Dist_Obs": 0, "RPM": 0, "ME_FO": 1.0, "AE_DO": 1.1, "Cyl_LO": 0, "LO_P": 0, "Exh": [0]*6, "Gen_Exh": [280, 285, 290, 285, 280]}]
    },
    "YARA J": {
        "Specs": {"Engine": "MAN B&W 5S50MC-C", "Pitch": 4.75},
        "History": [{"Date": "2026-02-12", "Dist_Obs": 0, "RPM": 0, "ME_FO": 1.0, "AE_DO": 2.5, "Cyl_LO": 0, "LO_P": 0, "Exh": [0]*5, "Gen_Exh": [320, 325, 330, 325, 320]}]
    }
}

# --- 3. محرك التحليل الهندسي (Analytical Brain) ---
def calculate_slip(rpm, pitch, dist_obs):
    if rpm == 0 or dist_obs == 0: return 0.0
    # مسافة المحرك بالاميال البحرية
    dist_eng = (rpm * 60 * 24 * pitch) / 1852
    slip = ((dist_eng - dist_obs) / dist_eng) * 100
    return round(slip, 2)

# --- 4. واجهة التحكم ---
with st.sidebar:
    st.title("🚢 VesselCore OS")
    st.write(f"**Technical Director:** Marwan Karroum")
    ship = st.selectbox("Select Vessel:", list(FLEET_DB.keys()))
    st.divider()
    st.info("📡 Data: Verified 100% (Feb 2026)")

vessel = FLEET_DB[ship]
latest = vessel['History'][0]
df_hist = pd.DataFrame(vessel['History'])

st.title(f"🚀 Technical Analysis: {ship}")
st.markdown(f"**Engine Specs:** `{vessel['Specs']['Engine']}` | **Status:** `{'Underway' if latest['RPM']>0 else 'At Port/Anchorage'}`")

# --- 5. تحليل الانزلاق والتريند (Slip & Fuel Trends) ---
st.subheader("📊 أداء الملاحة واستهلاك الوقود (Navigation & Fuel Trends)")
col_slip, col_trend = st.columns([1, 2])

with col_slip:
    slip_val = calculate_slip(latest['RPM'], vessel['Specs']['Pitch'], latest['Dist_Obs'])
    st.metric("Engine Slip %", f"{slip_val}%", delta="Normal" if slip_val < 15 else "High", delta_color="inverse")
    st.write(f"**Slip Formula:**")
    st.latex(r"Slip\% = \frac{Dist_{Eng} - Dist_{Obs}}{Dist_{Eng}} \times 100")

with col_trend:
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=df_hist['Date'], y=df_hist['ME_FO'], name="Fuel ME", line=dict(color='#3498db', width=3)))
    fig_trend.add_trace(go.Scatter(x=df_hist['Date'], y=df_hist['AE_DO'], name="Fuel AE", line=dict(color='#e74c3c', width=3)))
    fig_trend.update_layout(template="plotly_dark", height=300, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# --- 6. تحليل المحركات المساعدة (Auxiliary Engine Analysis) ---
st.subheader("⚡ تحليل المحركات المساعدة (Aux Engine Thermal Diagnostic)")
col_gen_stats, col_gen_graph = st.columns([1, 2])

with col_gen_stats:
    avg_gen = sum(latest['Gen_Exh'])/5
    max_dev = max(latest['Gen_Exh']) - min(latest['Gen_Exh'])
    st.write(f"**Gen Exhaust Avg:** {int(avg_gen)}°C")
    st.write(f"**Thermal Deviation:** {max_dev}°C")
    if max_dev > 35: st.error("⚠️ Check Gen Injectors!")
    else: st.success("✅ Aux Engine Balanced")

with col_gen_graph:
    fig_gen = go.Figure(go.Bar(x=[f"Unit {i+1}" for i in range(5)], y=latest['Gen_Exh'], marker_color='#58a6ff'))
    fig_gen.update_layout(template="plotly_dark", height=250, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_gen, use_container_width=True)

# --- 7. الماكينة الرئيسية والضغوط ---
st.divider()
st.subheader("🔧 Main Engine Performance")
c1, c2, c3, c4 = st.columns(4)
c1.metric("RPM", latest['RPM'])
c2.metric("LO Press", f"{latest['LO_P']} bar")
c3.metric("Cyl Oil (24h)", f"{latest['Cyl_LO']} L")
c4.metric("Dist Obs", f"{latest['Dist_Obs']} NM")

st.divider()
st.caption("© 2026 VesselCore Technical - Engineering Master OS")