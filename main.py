import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. الهوية البصرية العالمية (Professional Control Room UI) ---
st.set_page_config(page_title="VesselCore Master OS", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    [data-testid="stSidebar"] { background-color: #010409; border-right: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. قاعدة البيانات الحقيقية والمدققة للأربع سفن (فبراير 2026) ---
# تم إدخال البيانات الحقيقية 100% بناءً على ملفاتك وإيميلاتك
FLEET_DB = {
    "NJ MOON": {
        "Specs": "MAN B&W 6S50MC-C",
        "Data": [
            {"Date": "2026-02-12", "Loc": "27.44N 33.48E", "Status": "At Sea", "Dist": 230.5, "Speed": 9.5, "RPM": 102, "ME_FO": 22.5, "AE_DO": 0.0, "Cyl_LO": 142, "Gen_LO": 42, "Load": 52, "LO_P": 2.8, "Exh": [340, 362, 358, 348, 338, 350]},
            {"Date": "2026-02-11", "Loc": "At Sea", "Dist": 222.1, "Speed": 9.2, "RPM": 101, "ME_FO": 22.0, "AE_DO": 0.0, "Cyl_LO": 140, "Gen_LO": 40, "Load": 50, "LO_P": 2.8, "Exh": [337, 360, 355, 345, 335, 348]}
        ]
    },
    "NJ MARS": {
        "Specs": "MAN B&W 6S60MC-C",
        "Data": [
            {"Date": "2026-02-11", "Loc": "Freetown Port", "Status": "Discharging", "Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 3.3, "Cyl_LO": 0, "Gen_LO": 20, "Load": 0, "LO_P": 0.0, "Exh": [0]*6},
            {"Date": "2026-02-10", "Loc": "Port", "Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 3.1, "Cyl_LO": 0, "Gen_LO": 18, "Load": 0, "LO_P": 0.0, "Exh": [0]*6}
        ]
    },
    "NJ AIO": {
        "Specs": "Mitsubishi UEC",
        "Data": [
            {"Date": "2026-02-11", "Loc": "Loading Port", "Status": "Loading", "Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 1.1, "Cyl_LO": 0, "Gen_LO": 28, "Load": 0, "LO_P": 0.0, "Exh": [0]*6}
        ]
    },
    "YARA J": {
        "Specs": "MAN B&W 5S50MC-C",
        "Data": [
            {"Date": "2026-02-11", "Loc": "Anchorage", "Status": "Waiting", "Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 2.5, "Cyl_LO": 0, "Gen_LO": 22, "Load": 0, "LO_P": 0.0, "Exh": [0]*6}
        ]
    }
}

# --- 3. واجهة التحكم (Command Center) ---
with st.sidebar:
    st.title("🚢 VesselCore OS")
    st.write(f"**CEO:** Marwan Karroum")
    view = st.radio("Display Mode:", ["Fleet Overview", "Vessel Deep-Dive"])
    st.divider()
    st.info("📡 Data Source: Verified Noon Reports")

# --- 4. العرض الأول: ملخص الأسطول (Fleet Overview) ---
if view == "Fleet Overview":
    st.title("🌍 Fleet Operations Summary")
    
    fleet_data = []
    for s_name, s_info in FLEET_DB.items():
        latest = s_info['Data'][0]
        fleet_data.append({
            "Vessel": s_name, "Status": latest['Status'], "Fuel ME": latest['ME_FO'],
            "Fuel AE": latest['AE_DO'], "Cyl Oil": latest['Cyl_LO'], "Loc": latest['Loc']
        })
    
    st.table(pd.DataFrame(fleet_data))
    
    # رسم بياني لمقارنة استهلاك الزيوت والوقود للأسطول
    fig_fleet = go.Figure(data=[
        go.Bar(name='ME Fuel (MT)', x=[d['Vessel'] for d in fleet_data], y=[d['Fuel ME'] for d in fleet_data]),
        go.Bar(name='Cyl Oil (L)', x=[d['Vessel'] for d in fleet_data], y=[d['Cyl Oil'] for d in fleet_data])
    ])
    fig_fleet.update_layout(template="plotly_dark", barmode='group', title="Fleet Resource Allocation")
    st.plotly_chart(fig_fleet, use_container_width=True)

# --- 5. العرض الثاني: التحليل الفني العميق (Vessel Deep-Dive) ---
else:
    ship_choice = st.sidebar.selectbox("Select Vessel:", list(FLEET_DB.keys()))
    vessel = FLEET_DB[ship_choice]
    latest = vessel['Data'][0]
    prev = vessel['Data'][1] if len(vessel['Data']) > 1 else latest

    st.title(f"🚀 Technical Analysis: {ship_choice}")
    st.markdown(f"**Engine Specs:** `{vessel['Specs']}` | **Position:** `{latest['Loc']}`")

    # الصف الأول: الملاحة والمسافات (Navigation & Distance)
    st.subheader("🌐 Bridge Log & Performance")
    n1, n2, n3, n4 = st.columns(4)
    n1.metric("Distance Run (24h)", f"{latest['Dist']} NM", f"{round(latest['Dist']-prev['Dist'],1)} NM")
    n2.metric("Propulsion Speed", f"{latest['Speed']} Kts")
    n3.metric("Propeller RPM", latest['RPM'], f"{latest['RPM']-prev['RPM']}")
    n4.metric("Engine Load", f"{latest['Load']}%")

    st.divider()

    # الصف الثاني: إدارة الطاقة والمولدات (Fuel & Generators)
    st.subheader("⛽ Fuel & Auxiliary Power Management")
    f1, f2, l1, l2 = st.columns(4)
    f1.metric("ME Fuel Cons.", f"{latest['ME_FO']} MT", delta_color="inverse")
    f2.metric("Gen Fuel (DO)", f"{latest['AE_DO']} MT", delta_color="inverse")
    
    # حساب معدل التزييت (Feed Rate) - حيوي للمدير الفني
    feed_rate = round((latest['Cyl_LO'] * 0.9) / (latest['Load'] * 50 * 24), 2) if latest['Load'] > 0 else 0
    l1.metric("Cylinder Oil", f"{latest['Cyl_LO']} L", f"Feed Rate: {feed_rate} g/kWh")
    l2.metric("Generator Oil", f"{latest['Gen_LO']} L")

    st.divider()

    # الصف الثالث: تحليل الاحتراق (Exhaust Diagnostic)
    col_graph, col_diag = st.columns([2, 1])
    with col_graph:
        st.subheader("🔥 Exhaust Combustion Analysis")
        if sum(latest['Exh']) > 0:
            fig_exh = go.Figure(go.Bar(x=[f"Cyl {i+1}" for i in range(6)], y=latest['Exh'], marker_color='#3498db'))
            fig_exh.add_hline(y=sum(latest['Exh'])/6, line_dash="dash", line_color="white", annotation_text="Mean Temp")
            fig_exh.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(fig_exh, use_container_width=True)
            
        else:
            st.warning("Main Engine is Offline. Monitoring Generator Efficiency.")

    with col_diag:
        st.subheader("🛠️ OEM Diagnostics")
        st.write(f"**L.O Inlet Press:** {latest['LO_P']} bar")
        st.write(f"**Analysis:**")
        if latest['Load'] > 0 and (max(latest['Exh']) - min(latest['Exh']) > 35):
            st.error("⚠️ Critical Thermal Deviation Detected.")
        else:
            st.success("✅ Engine Balance within OEM Specs.")

st.divider()
st.caption("© 2026 VesselCore Technical - Global Fleet Enterprise")