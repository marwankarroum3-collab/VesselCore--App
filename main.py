import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. الهوية البصرية العالمية (Professional Dark Theme) ---
st.set_page_config(page_title="VesselCore Technical OS", layout="wide", initial_sidebar_state="expanded")

# تصميم الواجهة بأسلوب غرف التحكم الحديثة
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    [data-testid="stSidebar"] { background-color: #010409; border-right: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات الموثقة (Verified Fleet Database) ---
# تم إدخال بياناتك الحقيقية 100% المستخرجة من التقارير
FLEET_DB = {
    "NJ MOON": {
        "Specs": "MAN B&W 6S50MC-C",
        "Data": {
            "Today": {"Date": "11/02", "Loc": "27.44N 33.48E", "Status": "Underway", "Dist": 222.1, "Speed": 9.2, "RPM": 101, "ME_FO": 22.0, "AE_DO": 0.0, "Cyl_LO": 140, "Gen_LO": 40, "Load": 50, "LO_P": 2.8, "Exh": [337, 360, 355, 345, 335, 348]},
            "Prev": {"Date": "10/02", "Loc": "Anchorage", "Status": "Anchorage", "Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 7.0, "Cyl_LO": 58, "Gen_LO": 38, "Load": 0, "LO_P": 3.1, "Exh": [0,0,0,0,0,0]}
        }
    },
    "NJ AIO": {
        "Specs": "Mitsubishi UEC",
        "Data": {
            "Today": {"Date": "11/02", "Loc": "At Port", "Status": "Loading", "Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 1.1, "Cyl_LO": 0, "Gen_LO": 28, "Load": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0]},
            "Prev": {"Date": "10/02", "Loc": "At Port", "Status": "Loading", "Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 0.8, "Cyl_LO": 0, "Gen_LO": 25, "Load": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0]}
        }
    },
    "NJ MARS": {"Specs": "MAN B&W", "Data": {"Today": {"Date": "11/02", "Loc": "Freetown", "Status": "Discharging", "Dist": 0, "Speed": 0, "RPM": 0, "ME_FO": 0, "AE_DO": 3.3, "Cyl_LO": 0, "Gen_LO": 20, "Load": 0, "LO_P": 0, "Exh": [0,0,0,0,0,0]}, "Prev": {"Date": "10/02", "Loc": "Freetown", "Status": "Discharging", "Dist": 0, "Speed": 0, "RPM": 0, "ME_FO": 0, "AE_DO": 3.1, "Cyl_LO": 0, "Gen_LO": 18, "Load": 0, "LO_P": 0, "Exh": [0,0,0,0,0,0]}}},
    "YARA J": {"Specs": "MAN B&W", "Data": {"Today": {"Date": "11/02", "Loc": "Anchorage", "Status": "Waiting", "Dist": 0, "Speed": 0, "RPM": 0, "ME_FO": 0, "AE_DO": 2.5, "Cyl_LO": 0, "Gen_LO": 22, "Load": 0, "LO_P": 0, "Exh": [0,0,0,0,0,0]}, "Prev": {"Date": "10/02", "Loc": "Sea", "Status": "Underway", "Dist": 155, "Speed": 11.2, "RPM": 104, "ME_FO": 23.5, "AE_DO": 2.1, "Cyl_LO": 142, "Gen_LO": 36, "Load": 75, "LO_P": 2.9, "Exh": [365, 370, 368, 372, 370, 368]}}}
}

# --- 3. محرك التحليل الهندسي للصانع (The Diagnostic Brain) ---
def analyze_performance(exh, load):
    if load == 0 or sum(exh) == 0:
        return "SYSTEM STANDBY", "#8b949e", "Engine stopped. Monitoring Auxiliaries."
    avg_t = sum(exh)/6
    max_dev = max([abs(x - avg_t) for x in exh])
    if max_dev > 30:
        return "CRITICAL IMBALANCE", "#f85149", f"Alert: High thermal deviation ({int(max_dev)}°C). Check injectors."
    return "OPTIMAL PERFORMANCE", "#3fb950", "Combustion is balanced within OEM limits."

# --- 4. واجهة المستخدم (The Dashboard) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/931/931930.png", width=80)
    st.title("VesselCore Pro")
    ship_choice = st.selectbox("Select Vessel:", list(FLEET_DB.keys()))
    st.divider()
    st.write(f"**Technical Director:** Marwan Karroum")
    st.info("Engineering Intelligence v4.0")

vessel = FLEET_DB[ship_choice]
t, y = vessel["Data"]["Today"], vessel["Data"]["Prev"]
diag_status, diag_color, diag_msg = analyze_performance(t['Exh'], t['Load'])

st.title(f"🚀 Operations Dashboard: {ship_choice}")
st.markdown(f"**Status:** `{t['Status']}` | **Position:** `{t['Loc']}` | **Engine:** `{vessel['Specs']}`")

# --- 5. لوحة المؤشرات الاستراتيجية (The KPIs) ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("ME Fuel Consumption", f"{t['ME_FO']} MT", f"{round(t['ME_FO']-y['ME_FO'], 1)} MT", delta_color="inverse")
c2.metric("AE Diesel (Gen)", f"{t['AE_DO']} MT", f"{round(t['AE_DO']-y['AE_DO'], 1)} MT", delta_color="inverse")
c3.metric("Cylinder Oil Rate", f"{t['Cyl_LO']} L", f"{t['Cyl_LO']-y['Cyl_LO']} L", delta_color="inverse")
c4.metric("Generator Oil", f"{t['Gen_LO']} L", f"{t['Gen_LO']-y['Gen_LO']} L", delta_color="inverse")

st.divider()

# --- 6. الرسوم البيانية والتحليل الفني العميق ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🔥 Exhaust Gas Thermal Profile (Cyl 1-6)")
    if sum(t['Exh']) > 0:
        fig = go.Figure()
        cyl_labels = [f"Cyl {i+1}" for i in range(6)]
        fig.add_trace(go.Bar(x=cyl_labels, y=t['Exh'], marker_color='#58a6ff', name="Current Temp"))
        avg_temp = sum(t['Exh'])/6
        fig.add_hline(y=avg_temp, line_dash="dash", line_color="white", annotation_text=f"Mean: {int(avg_temp)}°C")
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"Main Engine is {t['Status']}. No combustion data available.")
        # عرض رسم بياني دائري لاستهلاك المولدات كبديل
        fig_pie = go.Figure(data=[go.Pie(labels=['AE Fuel', 'Gen Oil'], values=[t['AE_DO']*10, t['Gen_LO']], hole=.3)])
        fig_pie.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig_pie)

with col_right:
    st.subheader("🛠️ Technical Diagnostics")
    st.markdown(f"**Health Status:** <span style='color:{diag_color}; font-weight:bold;'>{diag_status}</span>", unsafe_allow_html=True)
    st.write(diag_msg)
    
    st.divider()
    st.write("**Real-Time Parameters:**")
    params = pd.DataFrame({
        "Parameter": ["Main RPM", "L.O Inlet Press", "Engine Load", "Avg. Exh Temp"],
        "Current": [t['RPM'], f"{t['LO_P']} bar", f"{t['Load']}%", f"{int(sum(t['Exh'])/6)}°C"]
    })
    st.table(params)

# --- 7. قسم قاعدة البيانات التاريخية (Data Persistence) ---
with st.expander("📂 Fleet Technical Logs (Database View)"):
    st.write(pd.DataFrame(vessel["Data"]).T)

st.divider()
st.caption("© 2026 VesselCore Technical - Engineering Excellence Systems")