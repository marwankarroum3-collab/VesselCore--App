import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. إعدادات الهوية الفنية للوحة التحكم
st.set_page_config(page_title="VesselCore Technical", layout="wide")

# 2. تعريف أسطول NJ TRUST MARINE الحقيقي
# ملاحظة: تم ضبط أنواع المحركات بناءً على خبرتك الفنية
fleet_data = {
    "NJ MOON": {"engine": "MAN B&W 6S50MC-C", "load": 85, "sfoc": 165},
    "NJ MARS": {"engine": "MAN B&W 6S60MC-C", "load": 82, "sfoc": 168},
    "NJ AIO": {"engine": "Mitsubishi UEC", "load": 80, "sfoc": 170},
    "YARA J": {"engine": "MAN B&W 5S50MC-C", "load": 84, "sfoc": 166}
}

# 3. القائمة الجانبية (Sidebar)
with st.sidebar:
    st.header("🚢 VesselCore Technical")
    st.write("**المدير التقني:** مروان كروم")
    st.divider()
    
    # اختيار السفينة من القائمة الحقيقية
    selected_ship = st.selectbox(
        "اختر السفينة للمراجعة:", 
        options=list(fleet_data.keys()), 
        key="vessel_selector_final"
    )
    
    st.info(f"المحرك الرئيسي: {fleet_data[selected_ship]['engine']}")

# 4. لوحة التحكم الرئيسية (Dashboard)
st.title(f"تحليل الأداء الفني: {selected_ship}")

# عرض المؤشرات الفنية الرئيسية (KPIs)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("حمل المحرك (Load %)", f"{fleet_data[selected_ship]['load']}%", "Stable")
with col2:
    st.metric("استهلاك الوقود (SFOC)", f"{fleet_data[selected_ship]['sfoc']} g/kWh", "-1.2%")
with col3:
    st.metric("درجة حرارة العادم (AVG)", "385°C", "Normal")

st.divider()

# 5. الرسم البياني لأداء المحرك (SFOC Curve)
st.subheader("مقارنة الأداء الفني (Actual vs Design)")

# إنشاء رسم بياني احترافي
fig = go.Figure()
load_axis = [25, 50, 75, 85, 100]
actual_sfoc = [175, 170, 168, 165, 169] # أرقام افتراضية للمعاينة
design_sfoc = [173, 168, 165, 163, 166] # قيم تجارب الرصيف

fig.add_trace(go.Scatter(x=load_axis, y=actual_sfoc, name='Actual SFOC', line=dict(color='red', width=3)))
fig.add_trace(go.Scatter(x=load_axis, y=design_sfoc, name='Design SFOC', line=dict(dash='dash', color='gray')))

fig.update_layout(
    xaxis_title="Engine Load (%)",
    yaxis_title="SFOC (g/kWh)",
    template="plotly_white",
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)

st.success(f"تم تحديث بيانات {selected_ship} بنجاح.")
