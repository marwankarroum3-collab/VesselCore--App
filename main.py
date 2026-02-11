import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- إعدادات الصفحة ---
st.set_page_config(page_title="VesselCore Golden System", layout="wide")

# --- قاعدة البيانات المصححة (بناءً على تقرير NJ MOON الأخير) ---
DATABASE = {
    "NJ MOON": {
        "11/02/2026": {
            "Location": "Lat: 27 44.52 N / Lon: 033 48.56 E", "Dist": 222.1, "Speed": 9.2,
            "ME_FO": 22.0, "AE_DO": 0.0, "Cyl_LO": 140, "Gen_LO": 40,
            "Exh_Temps": [337, 360, 355, 345, 335, 348], "ME_Load": 50, "LO_Press": 2.8, "RPM": 101
        },
        "10/02/2026": {
            "Location": "At Anchorage", "Dist": 0.0, "Speed": 0.0,
            "ME_FO": 0.0, "AE_DO": 7.0, "Cyl_LO": 58, "Gen_LO": 38,
            "Exh_Temps": [280, 285, 282, 278, 280, 281], "ME_Load": 0, "LO_Press": 3.1, "RPM": 0
        }
    }
}

# --- القائمة الجانبية ---
with st.sidebar:
    st.title("🚢 VesselCore Technical")
    st.write("**المدير التنفيذي:** مروان كروم")
    ship = st.selectbox("اختر السفينة:", list(DATABASE.keys()))
    dates = list(DATABASE[ship].keys())

today = DATABASE[ship][dates[0]]
yesterday = DATABASE[ship][dates[1]]

# --- الواجهة الرئيسية ---
st.title(f"لوحة المراقبة الشاملة: {ship}")
st.info(f"مقارنة Noon Report ليوم {dates[0]} مع اليوم السابق")

# 1. قسم الملاحة والموقع
st.subheader("🌐 الملاحة والسرعات")
c1, c2, c3 = st.columns(3)
c1.metric("المسافة المقطوعة", f"{today['Dist']} NM", f"{round(today['Dist'] - yesterday['Dist'], 1)} NM")
c2.metric("السرعة المتوسطة", f"{today['Speed']} KTS", f"{round(today['Speed'] - yesterday['Speed'], 1)} KTS")
c3.metric("دوران المحرك RPM", f"{today['RPM']}", f"{today['RPM'] - yesterday['RPM']}")

st.divider()

# 2. استهلاك الوقود والزيوت (تصحيح المولدات)
st.subheader("⛽ استهلاك الوقود والزيوت (ME & Generators)")
f1, f2, l1, l2 = st.columns(4)

with f1:
    st.metric("Main Engine (FO)", f"{today['ME_FO']} MT", f"{round(today['ME_FO']-yesterday['ME_FO'], 1)} MT", delta_color="inverse")
with f2:
    st.metric("Generators (D.O)", f"{today['AE_DO']} MT", f"{round(today['AE_DO']-yesterday['AE_DO'], 1)} MT", delta_color="inverse")
with l1:
    st.metric("Cylinder Oil", f"{today['Cyl_LO']} L", f"{today['Cyl_LO']-yesterday['Cyl_LO']} L", delta_color="inverse")
with l2:
    st.metric("Generator Oil", f"{today['Gen_LO']} L", f"{today['Gen_LO']-yesterday['Gen_LO']} L", delta_color="inverse")

st.divider()

# 3. تحليل حرارة الحريق والضغوط
st.subheader("🔥 درجات حرارة الحريق والاحتراق")
col_chart, col_info = st.columns([2, 1])

with col_chart:
    fig = go.Figure()
    cyls = [f"Cyl {i+1}" for i in range(6)]
    fig.add_trace(go.Bar(x=cyls, y=today['Exh_Temps'], name='اليوم الحالي', marker_color='darkblue'))
    fig.add_trace(go.Scatter(x=cyls, y=[365]*6, name='High Alarm Limit', line=dict(color='red', dash='dot')))
    fig.update_layout(title="Exhaust Gas Temperatures (°C)", yaxis_range=[0, 450])
    st.plotly_chart(fig, use_container_width=True)

with col_info:
    st.write("**الضغوط والحرارات التشغيلية:**")
    st.table(pd.DataFrame({
        "المعلمة الفنية": ["L.O Inlet Press", "ME Load Indicator", "Scav. Air Press"],
        "القيمة الحالية": [f"{today['LO_Press']} bar", f"{today['ME_Load']}%", "1.1 bar"],
        "الحالة": ["Normal", "Stable", "Normal"]
    }))

st.success("تم تحديث البيانات الذهبية بناءً على تقارير الـ Noon الحقيقية.")