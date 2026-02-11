import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. إعدادات الصفحة الأساسية ---
st.set_page_config(
    page_title="VesselCore Technical Dashboard",
    page_icon="🚢",
    layout="wide"
)

# --- 2. تعريف البيانات الأساسية (الأجهزة والأسطول) ---
# ملاحظة لمروان: يمكنك لاحقاً ربط هذا الجزء بقاعدة بيانات أو ملف Excel
FLEET_LIST = [
    "Vessel 01 - MAN B&W MC-C", "Vessel 02 - Mitsubishi UEC", 
    "Vessel 03", "Vessel 04", "Vessel 05", "Vessel 06",
    "Vessel 07", "Vessel 08", "Vessel 09", "Vessel 10",
    "Vessel 11", "Vessel 12"
]

# --- 3. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.image("https://via.placeholder.com/150", caption="VesselCore Technical") # استبدلها بلوجو شركتك
    st.title("مدير المكتب الفني")
    st.write(f"المستخدم: مروان كروم")
    
    st.divider()
    
    # حل مشكلة Duplicate ID بإضافة Key فريد لكل عنصر
    selected_ship = st.selectbox(
        "🚢 اختر السفينة للمراجعة:",
        options=FLEET_LIST,
        key="main_ship_selector_v2"
    )
    
    report_date = st.date_input("تاريخ التقرير (Noon Report):", datetime.now(), key="report_date_picker")
    
    st.divider()
    st.info("نظام تحليل أداء المحركات MAN B&W & Mitsubishi")

# --- 4. الواجهة الرئيسية (Main Dashboard) ---
st.header(f"لوحة التحكم الفنية: {selected_ship}")

# توزيع الشاشة إلى أعمدة للبيانات السريعة (KPIs)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("حمل المحرك (Load)", "85%", "2%")
with col2:
    st.metric("استهلاك الوقود (SFOC)", "165 g/kWh", "-1.5%")
with col3:
    st.metric("سرعة السفينة (Speed)", "14.5 knots", "0.2")
with col4:
    st.metric("حالة التزييت (LO)", "Normal", "Stable")

st.divider()

# --- 5. تبويبات التحليل العميقة (Tabs) ---
tab1, tab2, tab3 = st.tabs(["📊 تحليل الأداء", "🔧 المخطط الفني", "📋 تقارير Noon"])

with tab1:
    st.subheader("تحليل استهلاك الوقود النوعي (Actual vs Design)")
    
    # كود الرسم البياني الاحترافي
    fig = go.Figure()
    # بيانات افتراضية للمقارنة
    loads = [25, 50, 75, 85, 100]
    actual_sfoc = [178, 172, 168, 166, 170]
    design_sfoc = [175, 170, 165, 164, 168]
    
    fig.add_trace(go.Scatter(x=loads, y=actual_sfoc, name='Actual (Current)', line=dict(color='#FF4B4B', width=4)))
    fig.add_trace(go.Scatter(x=loads, y=design_sfoc, name='Design (Sea Trial)', line=dict(dash='dash', color='#31333F')))
    
    fig.update_layout(xaxis_title="Engine Load (%)", yaxis_title="SFOC (g/kWh)", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("مراقبة درجات حرارة الأسطوانات")
    # هنا يمكن إضافة رسوم بيانية لدرجات حرارة Exhaust Gas
    st.warning("يرجى رفع ملف البيانات لربط درجات الحرارة الحقيقية.")

with tab3:
    st.subheader("مراجعة بيانات Noon Report الأخيرة")
    # جدول عرض البيانات
    data_df = pd.DataFrame({
        "Parameter": ["RPM", "Pmax Avg", "Pcomp Avg", "Fuel Temp"],
        "Value": [105, "75 bar", "55 bar", "135°C"],
        "Status": ["Normal", "Check", "Normal", "Optimal"]
    })
    st.table(data_df)

# --- 6. قسم الملاحظات الفنية ---
st.divider()
notes = st.text_area("أضف ملاحظاتك الفنية كمدير تقني لهذه السفينة:", key="admin_notes")
if st.button("حفظ التقارير والملاحظات", key="save_button"):
    st.success(f"تم حفظ تحديثات السفينة {selected_ship} بنجاح.")
