import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. إعدادات الهوية الفنية ---
st.set_page_config(page_title="VesselCore Fleet Dashboard", layout="wide")

# --- 2. قاعدة البيانات الاحترافية للأربع سفن ---
# البيانات مستخرجة بدقة من تقارير Noon الأخيرة
FLEET_DATABASE = {
    "NJ MOON": {
        "11/02/2026": {"Dist": 222.1, "Speed": 9.2, "RPM": 101, "ME_FO": 22.0, "AE_DO": 0.0, "Cyl_LO": 140, "Gen_LO": 40, "ME_Load": 50, "LO_P": 2.8, "Exh": [337, 360, 355, 345, 335, 348], "Loc": "Lat: 27.44N Lon: 33.48E"},
        "10/02/2026": {"Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 7.0, "Cyl_LO": 58, "Gen_LO": 38, "ME_Load": 0, "LO_P": 3.1, "Exh": [280, 285, 282, 278, 280, 281], "Loc": "At Anchorage"}
    },
    "NJ MARS": {
        "11/02/2026": {"Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 3.3, "Cyl_LO": 0, "Gen_LO": 20, "ME_Load": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0], "Loc": "Discharging - Port"},
        "10/02/2026": {"Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 3.1, "Cyl_LO": 0, "Gen_LO": 18, "ME_Load": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0], "Loc": "Discharging - Port"}
    },
    "NJ AIO": {
        "11/02/2026": {"Dist": 180.5, "Speed": 10.1, "RPM": 95, "ME_FO": 18.5, "AE_DO": 1.5, "Cyl_LO": 110, "Gen_LO": 30, "ME_Load": 65, "LO_P": 3.5, "Exh": [320, 325, 318, 330, 322, 328], "Loc": "In Transit"},
        "10/02/2026": {"Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 0.7, "Cyl_LO": 0, "Gen_LO": 30, "ME_Load": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0], "Loc": "Loading Operations"}
    },
    "YARA J": {
        "11/02/2026": {"Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 2.8, "Cyl_LO": 0, "Gen_LO": 25, "ME_Load": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0], "Loc": "At Anchorage"},
        "10/02/2026": {"Dist": 150.0, "Speed": 11.0, "RPM": 105, "ME_FO": 24.2, "AE_DO": 2.1, "Cyl_LO": 145, "Gen_LO": 35, "ME_Load": 78, "LO_P": 2.9, "Exh": [370, 375, 372, 380, 378, 375], "Loc": "In Transit"}
    }
}

# --- 3. اختيار السفينة من القائمة ---
st.sidebar.title("🚢 VesselCore Fleet OS")
ship = st.sidebar.selectbox("اختر السفينة للتحليل:", list(FLEET_DATABASE.keys()))
today = FLEET_DATABASE[ship]["11/02/2026"]
yesterday = FLEET_DATABASE[ship]["10/02/2026"]

st.title(f"التحليل التقني الشامل للسفينة: {ship}")

# --- 4. عرض المقاييس الأساسية (Navigation & Consumption) ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("المسافة (NM)", today['Dist'], f"{round(today['Dist']-yesterday['Dist'],1)}")
m2.metric("استهلاك ME FO", f"{today['ME_FO']} MT", f"{round(today['ME_FO']-yesterday['ME_FO'],1)}", delta_color="inverse")
m3.metric("استهلاك AE DO", f"{today['AE_DO']} MT", f"{round(today['AE_DO']-yesterday['AE_DO'],1)}", delta_color="inverse")
m4.metric("زيت الأسطوانات", f"{today['Cyl_LO']} L", f"{today['Cyl_LO']-yesterday['Cyl_LO']}", delta_color="inverse")

st.divider()

# --- 5. الضغوط والحرارات الهندسية ---
st.subheader("🔧 الضغوط والحرارات وحالة التشغيل")
p1, p2, p3, p4 = st.columns(4)
p1.metric("L.O Press (bar)", today['LO_P'], f"{round(today['LO_P']-yesterday['LO_P'],1)}")
p2.metric("Engine Load (%)", f"{today['ME_Load']}%", f"{today['ME_Load']-yesterday['ME_Load']}%")
p3.metric("Engine RPM", today['RPM'], f"{today['RPM']-yesterday['RPM']}")
p4.info(f"الموقع الحالي:\n{today['Loc']}")

st.divider()

# --- 6. تحليل الاحتراق (Exhaust Gas Monitoring) ---
st.subheader("🔥 تحليل توزيع حرارة الأسطوانات")
avg_t = sum(today['Exh']) / 6 if sum(today['Exh']) > 0 else 0

col_chart, col_diag = st.columns([2, 1])

with col_chart:
    if sum(today['Exh']) > 0:
        fig = go.Figure()
        cyls = [f"Cyl {i+1}" for i in range(6)]
        fig.add_trace(go.Bar(x=cyls, y=today['Exh'], marker_color='darkblue', name='Current'))
        fig.add_hline(y=avg_t + 30, line_dash="dash", line_color="red", annotation_text="+30 Dev")
        fig.add_hline(y=avg_t - 30, line_dash="dash", line_color="orange", annotation_text="-30 Dev")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("المحرك الرئيسي متوقف حالياً (In Port/Anchorage).")

with col_diag:
    st.write("**التشخيص الهندسي (Manufacturer Analysis):**")
    if avg_t > 0:
        dev = max(today['Exh']) - min(today['Exh'])
        if dev > 40:
            st.error(f"⚠️ يوجد انحراف حراري ({dev}°C). يجب فحص حقن الوقود.")
        else:
            st.success("✅ توزيع الأحمال متوازن ضمن معايير الصانع.")
        st.info(f"متوسط حرارة العادم: {int(avg_t)}°C")
    else:
        st.write("لا يوجد بيانات احتراق نشطة حالياً.")

# سجل البيانات التاريخي
with st.expander("📂 عرض سجل البيانات التاريخي الكامل"):
    st.dataframe(pd.DataFrame(FLEET_DATABASE[ship]).T)