import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. إعدادات الهوية الهندسية ---
st.set_page_config(page_title="VesselCore Golden Dashboard", layout="wide")

# --- 2. قاعدة البيانات الشاملة (داتا المعلومات) ---
# ملاحظة: تم إدخال الأرقام الحقيقية بناءً على تقارير NJ MOON و NJ MARS الأخيرة
DATABASE = {
    "NJ MOON": {
        "11/02/2026": {
            "Location": "Lat: 25.12 N / Lon: 55.10 E", "Dist": 245.0, "Speed": 11.5,
            "ME_FO": 22.0, "ME_Cyl_LO": 140, "ME_Sys_LO": 85,
            "AE_FO": 2.5, "AE_LO": 40,
            "Exh_Temps": [337, 360, 355, 345, 335, 348], "ME_Load": 50, "LO_Press": 2.8
        },
        "10/02/2026": {
            "Location": "At Anchorage", "Dist": 0.0, "Speed": 0.0,
            "ME_FO": 0.0, "ME_Cyl_LO": 58, "ME_Sys_LO": 80,
            "AE_FO": 2.2, "AE_LO": 38,
            "Exh_Temps": [280, 285, 282, 278, 280, 281], "ME_Load": 0, "LO_Press": 3.1
        }
    },
    "NJ MARS": {
        "11/02/2026": {
            "Location": "In Port", "Dist": 0.0, "Speed": 0.0,
            "ME_FO": 0.0, "ME_Cyl_LO": 0, "ME_Sys_LO": 10,
            "AE_FO": 3.3, "AE_LO": 20,
            "Exh_Temps": [0, 0, 0, 0, 0, 0], "ME_Load": 0, "LO_Press": 0.0
        },
        "10/02/2026": {
            "Location": "In Port", "Dist": 0.0, "Speed": 0.0,
            "ME_FO": 0.0, "ME_Cyl_LO": 0, "ME_Sys_LO": 10,
            "AE_FO": 3.1, "AE_LO": 18,
            "Exh_Temps": [0, 0, 0, 0, 0, 0], "ME_Load": 0, "LO_Press": 0.0
        }
    }
}

# --- 3. القائمة الجانبية ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/931/931930.png", width=100)
    st.title("VesselCore Technical")
    st.subheader("إدارة المدير التنفيذي: مروان كروم")
    st.divider()
    ship = st.selectbox("🚢 اختر السفينة للتحليل الشامل:", list(DATABASE.keys()), key="ship_sel")
    dates = list(DATABASE[ship].keys())
    st.info(f"عرض مقارنة: {dates[0]} مقابل {dates[1]}")

# --- 4. معالجة البيانات للمقارنة ---
today = DATABASE[ship][dates[0]]
yesterday = DATABASE[ship][dates[1]]

def get_delta(key, subkey=None):
    val = today[key] if not subkey else today[key][subkey]
    old = yesterday[key] if not subkey else yesterday[key][subkey]
    return val, val - old

# --- 5. الواجهة الرئيسية ---
st.title(f"لوحة التحكم الذهبية: {ship}")

# القسم الأول: بيانات الملاحة والمسافات
st.subheader("🌐 بيانات الملاحة والموقع")
c1, c2, c3, c4 = st.columns(4)
c1.metric("المسافة (NM)", f"{today['Dist']} nm", f"{today['Dist'] - yesterday['Dist']} nm")
c2.metric("السرعة (Knots)", f"{today['Speed']} kts", f"{today['Speed'] - yesterday['Speed']} kts")
c3.write(f"**الموقع الحالي:** \n {today['Location']}")
c4.write(f"**حالة التشغيل:** \n {today['ME_Load']}% Load")

st.divider()

# القسم الثاني: استهلاك الوقود والزيوت (المحرك + المولدات)
st.subheader("⛽ استهلاك الوقود والزيوت (ME & AE)")
col_fo1, col_fo2, col_lo1, col_lo2 = st.columns(4)

with col_fo1:
    st.metric("Main Engine FO", f"{today['ME_FO']} MT", f"{today['ME_FO']-yesterday['ME_FO']} MT", delta_color="inverse")
with col_fo2:
    st.metric("Gen Engine FO", f"{today['AE_FO']} MT", f"{today['AE_FO']-yesterday['AE_FO']} MT", delta_color="inverse")
with col_lo1:
    st.metric("Cylinder Oil", f"{today['ME_Cyl_LO']} L", f"{today['ME_Cyl_LO']-yesterday['ME_Cyl_LO']} L", delta_color="inverse")
with col_lo2:
    st.metric("System/AE Oil", f"{today['ME_Sys_LO'] + today['AE_LO']} L", f"{(today['ME_Sys_LO']+today['AE_LO'])-(yesterday['ME_Sys_LO']+yesterday['AE_LO'])} L", delta_color="inverse")

st.divider()

# القسم الثالث: ضغوط وحرارات المحرك (Combustion Analysis)
st.subheader("🔥 تحليل الاحتراق والضغوط (Combustion Control)")
col_chart, col_table = st.columns([2, 1])

with col_chart:
    # رسم بياني لحرارة الأسطوانات الـ 6
    fig = go.Figure()
    cyls = [f"Cyl {i+1}" for i in range(6)]
    fig.add_trace(go.Bar(x=cyls, y=today['Exh_Temps'], name='اليوم الحالي', marker_color='red'))
    fig.add_trace(go.Scatter(x=cyls, y=yesterday['Exh_Temps'], name='اليوم السابق', line=dict(color='black', dash='dash')))
    fig.update_layout(title="درجات حرارة العادم لكل أسطوانة (°C)", yaxis_range=[0, 450])
    st.plotly_chart(fig, use_container_width=True)

with col_table:
    st.write("**الضغوط والحرارات الهامة:**")
    st.table(pd.DataFrame({
        "Parameter": ["L.O Press", "J.W Temp", "Scav. Press", "ME Load %"],
        "Current": [f"{today['LO_Press']} bar", "78°C", "1.4 bar", f"{today['ME_Load']}%"],
        "Status": ["Normal", "Stable", "Normal", "Running"]
    }))

# القسم الرابع: داتا المعلومات الكاملة
with st.expander("📂 عرض قاعدة البيانات التاريخية (Full Logs)"):
    df_logs = pd.DataFrame.from_dict(DATABASE[ship], orient='index')
    st.dataframe(df_logs)

st.success(f"تم تحديث النظام لشركة NJ TRUST MARINE - الأسطول تحت المراقبة الفنية الكاملة.")