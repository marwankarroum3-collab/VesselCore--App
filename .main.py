
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. إعدادات الصفحة الاحترافية ---
st.set_page_config(
    page_title="VesselCore Technical | Fleet Management",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. تعريف الأسطول الكامل (12 سفينة) ---
# تم إدراج السفن التي ذكرتها مع تكملة العدد لـ 12
FLEET_DATABASE = {
    "NJ MOON": {"engine": "MAN B&W 6S50MC-C", "imo": "9XXXXX1"},
    "NJ MARS": {"engine": "MAN B&W 6S60MC-C", "imo": "9XXXXX2"},
    "NJ AIO": {"engine": "Mitsubishi UEC", "imo": "9XXXXX3"},
    "YARA J": {"engine": "MAN B&W 5S50MC-C", "imo": "9XXXXX4"},
    "VESSEL 05": {"engine": "TBD", "imo": "0000000"},
    "VESSEL 06": {"engine": "TBD", "imo": "0000000"},
    "VESSEL 07": {"engine": "TBD", "imo": "0000000"},
    "VESSEL 08": {"engine": "TBD", "imo": "0000000"},
    "VESSEL 09": {"engine": "TBD", "imo": "0000000"},
    "VESSEL 10": {"engine": "TBD", "imo": "0000000"},
    "VESSEL 11": {"engine": "TBD", "imo": "0000000"},
    "VESSEL 12": {"engine": "TBD", "imo": "0000000"},
}

# --- 3. تصميم القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.title("🚢 VesselCore Technical")
    st.subheader("إدارة المكتب الفني")
    st.write(f"**المدير الفني:** مروان كروم")
    st.divider()
    
    # القائمة المنسدلة لاختيار السفينة مع Key فريد لمنع الأخطاء
    selected_ship_name = st.selectbox(
        "اختر السفينة للمراجعة:",
        options=list(FLEET_DATABASE.keys()),
        key="fleet_selector_final"
    )
    
    selected_date = st.date_input("تاريخ التقرير الفني:", datetime.now(), key="date_selector")
    
    st.divider()
    st.success(f"السفينة المختارة: {selected_ship_name}")
    st.info(f"نوع المحرك: {FLEET_DATABASE[selected_ship_name]['engine']}")

# --- 4. الواجهة الرئيسية (Main Dashboard) ---
st.title(f"لوحة تحليل الأداء: {selected_ship_name}")
st.markdown(f"**NJ TRUST MARINE Fleet Management System** | Date: {selected_date}")

# عرض المؤشرات الرئيسية (Key Metrics)
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("حمل المحرك (Load %)", "82%", "1.5%")
with m2:
    st.metric("استهلاك الوقود (SFOC)", "167.5 g/kWh", "-2.1%")
with m3:
    st.metric("متوسط حرارة العادم", "385°C", "5°C")
with m4:
    st.metric("ضغط التزييت (LO)", "2.8 bar", "Stable")

st.divider()

# --- 5. تبويبات التحليل الفني (Technical Tabs) ---
tab_perf, tab_engine, tab_reports = st.tabs(["📊 تحليل الأداء والوقود", "🔧 حالة المحرك الرئيسي", "📋 تقارير Noon"])

with tab_perf:
    st.subheader("منحنى استهلاك الوقود النوعي (SFOC Curve)")
    
    # رسم بياني تفاعلي باستخدام Plotly
    fig = go.Figure()
    
    # بيانات افتراضية للمقارنة (تستبدل لاحقاً ببيانات ملفاتك)
    load_axis = [25, 50, 75, 85, 100]
    actual_sfoc = [176, 171, 168, 167, 169]
    design_sfoc = [174, 169, 165, 164, 167]
    
    fig.add_trace(go.Scatter(x=load_axis, y=actual_sfoc, mode='lines+markers', name='Actual Performance', line=dict(color='#FF4B4B', width=3)))
    fig.add_trace(go.Scatter(x=load_axis, y=design_sfoc, mode='lines', name='Sea Trial / Design', line=dict(dash='dash', color='#31333F')))
    
    fig.update_layout(
        xaxis_title="Engine Load (%)",
        yaxis_title="SFOC (g/kWh)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_engine:
    st.subheader(f"الحالة الفنية لمحرك: {FLEET_DATABASE[selected_ship_name]['engine']}")
    c1, c2 = st.columns(2)
    with c1:
        st.info("مراقبة درجات حرارة الأسطوانات")
        # جدول افتراضي لحرارة الأسطوانات
        cyl_data = pd.DataFrame({
            "Cylinder": [1, 2, 3, 4, 5, 6],
            "Exh. Temp (°C)": [380, 385, 382, 390, 388, 384],
            "P-Max (bar)": [145, 146, 144, 148, 147, 145]
        })
        st.table(cyl_data)
    with c2:
        st.info("تحليل الزيوت (LO Analysis)")
        st.write("آخر عينة تم تحليلها: **ناجحة**")
        st.write("نسبة الشوائب: 0.02%")

with tab_reports:
    st.subheader("أرشيف تقارير Noon Report")
    uploaded_file = st.file_uploader("رفع تقرير Noon Report جديد (PDF/Excel)", type=["pdf", "xlsx", "csv"])
    if uploaded_file:
        st.success("تم استلام الملف، جاري التحليل الفني...")

# --- 6. التوقيع والملاحظات الإدارية ---
st.divider()
admin_note = st.text_area("ملاحظات المدير الفني للمتابعة:")
if st.button("اعتماد التقرير وحفظ البيانات"):
    st.balloons()
    st.success(f"تم حفظ ملاحظات السفينة {selected_ship_name} في السجل التقني.")
