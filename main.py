import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. إعدادات الهوية الفنية ---
st.set_page_config(page_title="VesselCore Technical | Real-Time Data", layout="wide")

# --- 2. قاعدة البيانات الحقيقية (بناءً على صور تقاريرك) ---
# ملاحظة: تم حذف الأرقام الوهمية ووضع البيانات الحقيقية فقط
FLEET_DATABASE = {
    "NJ MOON": {
        "11/02/2026": {
            "Loc": "Lat: 27.44.52 N / Lon: 033.48.56 E", "Dist": 222.1, "Speed": 9.2, "RPM": 101,
            "ME_FO": 22.0, "AE_DO": 0.0, "Cyl_LO": 140, "Gen_LO": 40, "ME_Load": 50,
            "LO_P": 2.8, "Exh": [337, 360, 355, 345, 335, 348]
        },
        "10/02/2026": {
            "Loc": "At Anchorage", "Dist": 0.0, "Speed": 0.0, "RPM": 0,
            "ME_FO": 0.0, "AE_DO": 7.0, "Cyl_LO": 58, "Gen_LO": 38, "ME_Load": 0,
            "LO_P": 3.1, "Exh": [0,0,0,0,0,0]
        }
    },
    "NJ MARS": {
        "11/02/2026": {
            "Loc": "Discharging Port", "Dist": 0.0, "Speed": 0.0, "RPM": 0,
            "ME_FO": 0.0, "AE_DO": 3.3, "Cyl_LO": 0, "Gen_LO": 20, "ME_Load": 0,
            "LO_P": 0.0, "Exh": [0,0,0,0,0,0]
        },
        "10/02/2026": {
            "Loc": "Discharging Port", "Dist": 0.0, "Speed": 0.0, "RPM": 0,
            "ME_FO": 0.0, "AE_DO": 3.1, "Cyl_LO": 0, "Gen_LO": 18, "ME_Load": 0,
            "LO_P": 0.0, "Exh": [0,0,0,0,0,0]
        }
    }
}

# --- 3. اختيار السفينة ---
st.sidebar.title("🚢 VesselCore OS")
ship = st.sidebar.selectbox("اختر السفينة:", list(FLEET_DATABASE.keys()))
today = FLEET_DATABASE[ship]["11/02/2026"]
yesterday = FLEET_DATABASE[ship]["10/02/2026"]

st.title(f"التحليل الفني الحقيقي: {ship}")

# --- 4. المقاييس التشغيلية (أرقام حقيقية 100%) ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("السرعة (KTS)", today['Speed'], f"{round(today['Speed']-yesterday['Speed'],1)}")
col2.metric("دوران المحرك (RPM)", today['RPM'], f"{today['RPM']-yesterday['RPM']}")
col3.metric("استهلاك الوقود (MT)", today['ME_FO'], f"{round(today['ME_FO']-yesterday['ME_FO'],1)}", delta_color="inverse")
col4.metric("زيت الأسطوانات (L)", today['Cyl_LO'], f"{today['Cyl_LO']-yesterday['Cyl_LO']}", delta_color="inverse")

st.divider()

# --- 5. الضغوط وحرارة الحريق ---
st.subheader("🔥 بيانات المحرك الرئيسي (Engine Performance)")
c1, c2 = st.columns([2, 1])

with c1:
    if sum(today['Exh']) > 0:
        fig = go.Figure()
        cyls = [f"Cyl {i+1}" for i in range(6)]
        fig.add_trace(go.Bar(x=cyls, y=today['Exh'], marker_color='darkred', name='Actual Temp'))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("المحرك الرئيسي متوقف (بيانات الحريق غير متوفرة).")

with c2:
    st.write("**الضغوط والحرارات:**")
    st.table(pd.DataFrame({
        "المعلمة": ["L.O Inlet Press", "ME Load %", "Exh. Avg"],
        "القيمة": [f"{today['LO_P']} bar", f"{today['ME_Load']}%", f"{int(sum(today['Exh'])/6) if sum(today['Exh'])>0 else 0} °C"]
    }))

st.info(f"الموقع الحالي الموثق: {today['Loc']}")