import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. إعدادات الهوية الفنية للمشروع ---
st.set_page_config(
    page_title="VesselCore Technical | NJ TRUST MARINE",
    page_icon="🚢",
    layout="wide"
)

# --- 2. تعريف الأسطول الحقيقي لشركة NJ TRUST MARINE ---
# ملاحظة: تم إدراج السفن الـ 4 الأساسية مع خانات لبقية الـ 12 سفينة
FLEET_LIST = [
    "NJ MOON", 
    "NJ MARS", 
    "NJ AIO", 
    "YARA J",
    "VESSEL 05", "VESSEL 06", "VESSEL 07", "VESSEL 08",
    "VESSEL 09", "VESSEL 10", "VESSEL 11", "VESSEL 12"
]

# --- 3. تصميم القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.title("🚢 VesselCore Technical")
    st.subheader("إدارة المكتب الفني")
    st.write(f"**المدير الفني:** مروان كروم")
    st.divider()
    
    # حل مشكلة Duplicate ID نهائياً باستخدام Key فريد
    selected_ship = st.selectbox(
        "اختر السفينة للمراجعة:",
        options=FLEET_LIST,
        key="vessel_selector_final_v1"
    )
    
    report_date = st.date_input("تاريخ التقرير (Noon Report):", datetime.now(), key="date_picker_final")
    
    st.divider()
    st.info("نظام تحليل أداء المحركات MAN B&W & Mitsubishi")

# --- 4. الواجهة الرئيسية (Main Dashboard) ---
st.header(f"لوحة التحليل الفني: {selected_ship}")

# عرض المؤشرات الفنية (KPIs)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("حمل المحرك (Load %)", "85%", "2%")
with col2:
    st.metric("استهلاك الوقود (SFOC)", "165 g/kWh", "-1.5%")
with col3:
    st.metric("سرعة السفينة (Speed)", "14.5 knots", "0.2")
with col4:
    st.metric("حالة التزييت (LO)", "Normal", "Stable")

st.divider()

# --- 5. الرسم البياني لأداء المحرك ---
st.subheader(f"منحنى أداء المحرك للسفينة: {selected_ship}")
fig = go.Figure()

# بيانات افتراضية للمعاينة (سيتم ربطها ببياناتك الحقيقية لاحقاً)
loads = [25, 50, 75, 85, 100]
actual_sfoc = [178, 172, 168, 166, 170]
design_sfoc = [175, 170, 165, 164, 168]

fig.add_trace(go.Scatter(x=loads, y=actual_sfoc, name='Actual Performance', line=dict(color='#FF4B4B', width=3)))
fig.add_trace(go.Scatter(x=loads, y=design_sfoc, name='Design (Sea Trial)', line=dict(dash='dash', color='#31333F')))

fig.update_layout(xaxis_title="Engine Load (%)", yaxis_title="SFOC (g/kWh)", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.success(f"تم تحميل بيانات {selected_ship} بنجاح.")