import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="VesselCore Fleet Management", layout="wide")

# --- 2. قاعدة البيانات الحقيقية والمصححة (الأربع سفن) ---
FLEET_DATABASE = {
    "NJ MOON": {
        "11/02/2026": {
            "Loc": "Lat: 27.44.52 N / Lon: 033.48.56 E", "Dist": 222.1, "Speed": 9.2, "RPM": 101,
            "ME_FO": 22.0, "AE_DO": 0.0, "Cyl_LO": 140, "Gen_LO": 40, "ME_Load": 50,
            "LO_P": 2.8, "Exh": [337, 360, 355, 345, 335, 348], "Status": "At Sea"
        },
        "10/02/2026": {"Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 7.0, "Cyl_LO": 58, "Gen_LO": 38, "ME_Load": 0, "LO_P": 3.1, "Exh": [0,0,0,0,0,0], "Status": "Anchorage"}
    },
    "NJ MARS": {
        "11/02/2026": {
            "Loc": "Discharging Port", "Dist": 0.0, "Speed": 0.0, "RPM": 0,
            "ME_FO": 0.0, "AE_DO": 3.3, "Cyl_LO": 0, "Gen_LO": 20, "ME_Load": 0,
            "LO_P": 0.0, "Exh": [0,0,0,0,0,0], "Status": "Port Operations"
        },
        "10/02/2026": {"Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 3.1, "Cyl_LO": 0, "Gen_LO": 18, "ME_Load": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0], "Status": "Port Operations"}
    },
    "NJ AIO": {
        "11/02/2026": {
            "Loc": "At Port - Loading", "Dist": 0.0, "Speed": 0.0, "RPM": 0,
            "ME_FO": 0.0, "AE_DO": 1.1, "Cyl_LO": 0, "Gen_LO": 28, "ME_Load": 0,
            "LO_P": 0.0, "Exh": [0,0,0,0,0,0], "Status": "Loading"
        },
        "10/02/2026": {"Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 0.8, "Cyl_LO": 0, "Gen_LO": 25, "ME_Load": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0], "Status": "Loading"}
    },
    "YARA J": {
        "11/02/2026": {
            "Loc": "At Anchorage", "Dist": 0.0, "Speed": 0.0, "RPM": 0,
            "ME_FO": 0.0, "AE_DO": 2.5, "Cyl_LO": 0, "Gen_LO": 22, "ME_Load": 0,
            "LO_P": 0.0, "Exh": [0,0,0,0,0,0], "Status": "Anchorage"
        },
        "10/02/2026": {"Dist": 155.0, "Speed": 11.2, "RPM": 104, "ME_FO": 23.5, "AE_DO": 2.0, "Cyl_LO": 142, "Gen_LO": 36, "ME_Load": 75, "LO_P": 2.9, "Exh": [365, 370, 368, 372, 370, 368], "Status": "At Sea"}
    }
}

# --- 3. واجهة التحكم ---
st.sidebar.title("🚢 Fleet Control Center")
ship = st.sidebar.selectbox("اختر السفينة:", list(FLEET_DATABASE.keys()))
today = FLEET_DATABASE[ship]["11/02/2026"]
yesterday = FLEET_DATABASE[ship]["10/02/2026"]

st.title(f"التحليل الفني: {ship}")
st.subheader(f"الحالة الحالية: {today['Status']}")

# --- 4. المقاييس ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("المسافة (NM)", today['Dist'], f"{round(today['Dist']-yesterday['Dist'],1)}")
c2.metric("دوران المحرك (RPM)", today['RPM'], f"{today['RPM']-yesterday['RPM']}")
c3.metric("وقود المولدات AE DO", f"{today['AE_DO']} MT", f"{round(today['AE_DO']-yesterday['AE_DO'],1)}", delta_color="inverse")
c4.metric("زيت المولدات Gen LO", f"{today['Gen_LO']} L", f"{today['Gen_LO']-yesterday['Gen_LO']}", delta_color="inverse")

st.divider()

# --- 5. تحليل الأداء ---
col_graph, col_data = st.columns([2, 1])

with col_graph:
    if today['ME_Load'] > 0:
        fig = go.Figure()
        cyls = [f"Cyl {i+1}" for i in range(6)]
        fig.add_trace(go.Bar(x=cyls, y=today['Exh'], marker_color='darkred'))
        fig.update_layout(title="درجات حرارة احتراق الأسطوانات (°C)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("⚠️ المحرك الرئيسي متوقف (ME Stopped) - السفينة في الميناء أو المخطاف.")
        # عرض استهلاك المولدات كبديل
        st.write("**استهلاك المولدات خلال 24 ساعة الماضية:**")
        fig_ae = go.Figure(data=[go.Pie(labels=['AE Fuel', 'AE Oil'], values=[today['AE_DO']*100, today['Gen_LO']])])
        st.plotly_chart(fig_ae)

with col_data:
    st.write("**بيانات التشغيل:**")
    st.table(pd.DataFrame({
        "Parameter": ["L.O Press", "ME Load %", "Location"],
        "Value": [f"{today['LO_P']} bar", f"{today['ME_Load']}%", today['Loc']]
    }))