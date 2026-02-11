import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. إعدادات الثبات الفني ---
st.set_page_config(page_title="VesselCore Engineering v3.0", layout="wide")

# --- 2. محرك التحليل الهندسي (Manufacturer Diagnostics) ---
# هذا القسم يقوم مقام "الخبير الفني" للصانع
def run_manufacturer_analysis(ship_data):
    alerts = []
    # تحليل توازن حرارة العادم (Exhaust Thermal Balance)
    avg_temp = sum(ship_data['Exh_Temps']) / 6
    for i, t in enumerate(ship_data['Exh_Temps']):
        if abs(t - avg_temp) > 30: # معيار الصانع المعتاد +/- 30 درجة
            alerts.append(f"⚠️ انحراف حراري في الأسطوانة {i+1}: {t}°C (المتوسط: {int(avg_temp)}°C)")
    
    # تحليل SFOC (استهلاك الوقود النوعي)
    if ship_data['ME_Load'] > 0:
        actual_sfoc = (ship_data['ME_FO'] * 1000) / (ship_data['ME_Load'] * 100) # معادلة تقريبية
        if actual_sfoc > 175: # معيار MAN B&W للتحذير
            alerts.append(f"❌ استهلاك الوقود (SFOC) مرتفع: {int(actual_sfoc)} g/kWh")
            
    return alerts, avg_temp

# --- 3. قاعدة البيانات الذهبية (المستقرة) ---
DATABASE = {
    "NJ MOON": {
        "11/02/2026": {
            "Dist": 222.1, "Speed": 9.2, "ME_FO": 22.0, "AE_DO": 0.0, 
            "Cyl_LO": 140, "Gen_LO": 40, "ME_Load": 50, "LO_Press": 2.8,
            "Exh_Temps": [337, 360, 355, 345, 335, 348]
        },
        "10/02/2026": {
            "Dist": 0.0, "Speed": 0.0, "ME_FO": 0.0, "AE_DO": 7.0, 
            "Cyl_LO": 58, "Gen_LO": 38, "ME_Load": 0, "LO_Press": 3.1,
            "Exh_Temps": [280, 285, 282, 278, 280, 281]
        }
    }
}

# --- 4. واجهة المستخدم (Sidebar) ---
st.sidebar.title("🚢 VesselCore OS")
ship = st.sidebar.selectbox("اختر السفينة:", list(DATABASE.keys()))
today = DATABASE[ship]["11/02/2026"]
yesterday = DATABASE[ship]["10/02/2026"]

# --- 5. العقل المفكر (التحليل الهندسي للصانع) ---
st.title(f"لوحة التحكم الهندسية: {ship}")
eng_alerts, mean_temp = run_manufacturer_analysis(today)

with st.expander("🛠️ تقرير التحليل الفني حسب معايير الصانع", expanded=True):
    if not eng_alerts:
        st.success("✅ جميع مؤشرات المحرك الرئيسي والمولدات ضمن الحدود المسموحة للصانع.")
    else:
        for alert in eng_alerts:
            st.error(alert)
    st.info(f"متوسط حرارة العادم الحالي: {int(mean_temp)}°C")

# --- 6. مقارنة الاستهلاك والضغوط ---
st.divider()
c1, c2, l1, l2 = st.columns(4)
c1.metric("ME Fuel Oil", f"{today['ME_FO']} MT", f"{today['ME_FO']-yesterday['ME_FO']} MT", delta_color="inverse")
c2.metric("AE Diesel Oil", f"{today['AE_DO']} MT", f"{today['AE_DO']-yesterday['AE_DO']} MT", delta_color="inverse")
l1.metric("Cylinder Oil", f"{today['Cyl_LO']} L", f"{today['Cyl_LO']-yesterday['Cyl_LO']} L", delta_color="inverse")
l2.metric("Gen Oil", f"{today['Gen_LO']} L", f"{today['Gen_LO']-yesterday['Gen_LO']} L", delta_color="inverse")

# --- 7. رسم بياني للحريق (Combustion Curve) ---
st.subheader("📊 منحنى توزيع حرارة الأسطوانات")
fig = go.Figure()
cyls = [f"Cyl {i+1}" for i in range(6)]
fig.add_trace(go.Bar(x=cyls, y=today['Exh_Temps'], name='Actual Temp', marker_color='darkblue'))
fig.add_hline(y=mean_temp + 30, line_dash="dash", line_color="red", annotation_text="Upper Limit")
fig.add_hline(y=mean_temp - 30, line_dash="dash", line_color="orange", annotation_text="Lower Limit")
st.plotly_chart(fig, use_container_width=True)