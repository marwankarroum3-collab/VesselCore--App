import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. الهوية البصرية السيادية (VesselCore Dark Command UI) ---
st.set_page_config(page_title="VesselCore Master OS", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 25px; border-radius: 12px; }
    [data-testid="stSidebar"] { background-color: #010409; border-right: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك الأرشفة والبيانات الحقيقية (منذ 1 فبراير) ---
# تم استعادة البيانات الحقيقية فقط لضمان الصدق 100%
FLEET_HISTORY = {
    "NJ MOON": {
        "Specs": {"Engine": "MAN B&W 6S50MC-C", "Pitch": 4.82},
        "Logs": [
            {"Date": "2026-02-12", "Dist": 230.5, "RPM": 102, "ME_FO": 22.5, "AE_DO": 0.0, "Cyl_LO": 142, "Gen_LO": 42, "ME_Exh": [340, 362, 358, 348, 338, 350], "AE_Exh": [350, 345, 340, 335, 345]},
            {"Date": "2026-02-11", "Dist": 222.1, "RPM": 101, "ME_FO": 22.0, "AE_DO": 0.0, "Cyl_LO": 140, "Gen_LO": 40, "ME_Exh": [337, 360, 355, 345, 335, 348], "AE_Exh": [340, 340, 350, 350, 340]},
            {"Date": "2026-02-10", "Dist": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 17.2, "Cyl_LO": 58, "Gen_LO": 38, "ME_Exh": [0]*6, "AE_Exh": [300, 310, 320, 320, 320]},
            {"Date": "2026-02-09", "Dist": 215.0, "RPM": 98, "ME_FO": 21.0, "AE_DO": 0.0, "Cyl_LO": 138, "Gen_LO": 39, "ME_Exh": [330, 350, 345, 340, 330, 342], "AE_Exh": [335, 335, 340, 340, 335]}
        ]
    },
    "NJ MARS": {
        "Specs": {"Engine": "MAN B&W 6S60MC-C", "Pitch": 5.10},
        "Logs": [
            {"Date": "2026-02-12", "Dist": 0, "RPM": 0, "ME_FO": 0, "AE_DO": 3.3, "Cyl_LO": 0, "Gen_LO": 20, "ME_Exh": [0]*6, "AE_Exh": [310, 315, 320, 318, 310]}
        ]
    },
    "NJ AIO": {
        "Specs": {"Engine": "Mitsubishi UEC", "Pitch": 4.95},
        "Logs": [
            {"Date": "2026-02-12", "Dist": 0, "RPM": 0, "ME_FO": 1.0, "AE_DO": 1.1, "Cyl_LO": 0, "Gen_LO": 28, "ME_Exh": [0]*6, "AE_Exh": [280, 285, 290, 285, 280]}
        ]
    },
    "YARA J": {
        "Specs": {"Engine": "MAN B&W 5S50MC-C", "Pitch": 4.75},
        "Logs": [
            {"Date": "2026-02-12", "Dist": 0, "RPM": 0, "ME_FO": 1.0, "AE_DO": 2.5, "Cyl_LO": 30, "Gen_LO": 22, "ME_Exh": [0]*5, "AE_Exh": [320, 325, 330, 325, 320]}
        ]
    }
}

# --- 3. محرك التحليل الهندسي (Propulsion & Slip) ---
def calculate_slip(rpm, pitch, dist_obs):
    if rpm == 0 or dist_obs == 0: return 0.0
    dist_eng = (rpm * 60 * 24 * pitch) / 1852
    return round(((dist_eng - dist_obs) / dist_eng) * 100, 2)

# --- 4. واجهة التحكم الجانبية ---
with st.sidebar:
    st.title("🚢 Fleet Intelligence")
    ship = st.selectbox("Select Vessel:", list(FLEET_HISTORY.keys()))
    st.divider()
    st.info(f"Technical Director: Marwan Karroum")
    st.caption("Archive Start: 01 Feb 2026")

v = FLEET_HISTORY[ship]
df = pd.DataFrame(v['Logs']).sort_values(by="Date")
latest = df.iloc[-1]

st.title(f"🚀 Technical Command Center: {ship}")
st.markdown(f"**Engine Specs:** `{v['Specs']['Engine']}` | **Status:** `{'At Sea' if latest['RPM'] > 0 else 'Port/Anchorage'}`")

# --- 5. مصفوفة تريندات الأداء (The Master Trends) ---
# تجميع التريندات: سليب، وقود، وزيوت
st.subheader("📊 Fleet Performance Trends (Feb 2026 Archive)")
col_t1, col_t2 = st.columns(2)

with col_t1:
    # تريند استهلاك الوقود (ME FO vs AE DO)
    fig_fuel = go.Figure()
    fig_fuel.add_trace(go.Scatter(x=df['Date'], y=df['ME_FO'], name="ME Fuel (MT)", line=dict(color='#3498db', width=4)))
    fig_fuel.add_trace(go.Scatter(x=df['Date'], y=df['AE_DO'], name="Gen Fuel (MT)", line=dict(color='#e74c3c', width=4)))
    fig_fuel.update_layout(template="plotly_dark", title="Fuel Consumption Trend", height=300)
    st.plotly_chart(fig_fuel, use_container_width=True)

with col_t2:
    # تريند السليب (Propeller Slip Trend)
    slips = [calculate_slip(r['RPM'], v['Specs']['Pitch'], r['Dist']) for _, r in df.iterrows()]
    fig_slip = go.Figure(go.Scatter(x=df['Date'], y=slips, name="Slip %", line=dict(color='#00ff00', width=4), mode='lines+markers'))
    fig_slip.update_layout(template="plotly_dark", title="Propeller Slip Trend", height=300)
    st.plotly_chart(fig_slip, use_container_width=True)

st.divider()

# --- 6. تحليل الحريق العميق (Combustion Intelligence) ---
st.subheader("🔥 Exhaust Gas Combustion Trends (ME vs Aux)")
col_me, col_ae = st.columns(2)

with col_me:
    # تحليل حريق الماكينة الرئيسية (لأحدث يوم)
    if sum(latest['ME_Exh']) > 0:
        fig_me = go.Figure(go.Bar(x=[f"C{i+1}" for i in range(len(latest['ME_Exh']))], y=latest['ME_Exh'], marker_color='#58a6ff'))
        fig_me.update_layout(template="plotly_dark", title="ME Exhaust Temperatures", height=300)
        st.plotly_chart(fig_me, use_container_width=True)
    else:
        st.warning("Main Engine Stopped (In Port/Anchorage)")

with col_ae:
    # تحليل حريق المولدات (أرشيف المولدات)
    fig_ae = go.Figure(go.Bar(x=[f"U{i+1}" for i in range(len(latest['AE_Exh']))], y=latest['AE_Exh'], marker_color='#e67e22'))
    fig_ae.update_layout(template="plotly_dark", title="Gen Units Exhaust Gas", height=300)
    st.plotly_chart(fig_ae, use_container_width=True)

st.divider()

# --- 7. أرشيف الزيوت والبيانات التاريخية ---
st.subheader("📂 Fleet Archive & Lubrication Logs")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Latest Slip %", f"{calculate_slip(latest['RPM'], v['Specs']['Pitch'], latest['Dist'])}%")
c2.metric("Total Distance (Feb)", f"{df['Dist'].sum()} NM")
c3.metric("Cylinder Oil Rate", f"{latest['Cyl_LO']} L")
c4.metric("Generator Oil", f"{latest['Gen_LO']} L")

with st.expander("📂 عرض السجل التاريخي الكامل لأسطول فبراير"):
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)

st.caption("© 2026 VesselCore Technical - Engineering Master OS | Marwan Karroum")