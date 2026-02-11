import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. إعدادات النظام
st.set_page_config(page_title="VesselCore Database Engine", layout="wide")

# 2. إنشاء "داتا المعلومات" (هذا الجزء سيبني تاريخ السفن)
@st.cache_data
def load_vessel_data():
    # هنا نقوم ببناء قاعدة البيانات الحقيقية
    data = [
        # بيانات NJ MOON
        ["NJ MOON", "2026-02-11", "Lat: 27.44N Lon: 33.48E", 222.1, 9.2, 50, 22.0, 0.0, 140, 40, 337, 360, 355, 345, 335, 348],
        ["NJ MOON", "2026-02-10", "At Anchorage", 0.0, 0.0, 0, 0.0, 7.0, 58, 38, 280, 285, 282, 278, 280, 281],
        # بيانات NJ MARS
        ["NJ MARS", "2026-02-11", "In Port", 0.0, 0.0, 0, 0.0, 3.3, 0, 20, 0, 0, 0, 0, 0, 0],
        ["NJ MARS", "2026-02-10", "In Port", 0.0, 0.0, 0, 0.0, 3.1, 0, 18, 0, 0, 0, 0, 0, 0],
    ]
    columns = [
        "Vessel", "Date", "Location", "Dist", "Speed", "Load", 
        "ME_FO", "AE_DO", "Cyl_LO", "Gen_LO", 
        "C1", "C2", "C3", "C4", "C5", "C6"
    ]
    return pd.DataFrame(data, columns=columns)

df_all = load_vessel_data()

# 3. واجهة التحكم (Sidebar)
st.sidebar.title("🚢 VesselCore Database")
st.sidebar.write("**Technical Director:** Marwan Karroum")
selected_vessel = st.sidebar.selectbox("اختر السفينة لمراجعة الداتا:", df_all['Vessel'].unique())

# تصفية البيانات للسفينة المختارة
vessel_df = df_all[df_all['Vessel'] == selected_vessel].sort_values(by="Date", ascending=False)

if len(vessel_df) >= 2:
    today = vessel_df.iloc[0]
    yesterday = vessel_df.iloc[1]
    
    st.title(f"تحليل قاعدة البيانات: {selected_vessel}")
    st.info(f"مقارنة آلية بين تقرير {today['Date']} والتقرير السابق {yesterday['Date']}")

    # 4. عرض المقارنات الشاملة (Deltas)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("المسافة المقطوعة", f"{today['Dist']} NM", f"{round(today['Dist']-yesterday['Dist'],1)} NM")
    col2.metric("استهلاك ME FO", f"{today['ME_FO']} MT", f"{round(today['ME_FO']-yesterday['ME_FO'],1)} MT", delta_color="inverse")
    col3.metric("ديزل المولدات AE DO", f"{today['AE_DO']} MT", f"{round(today['AE_DO']-yesterday['AE_DO'],1)} MT", delta_color="inverse")
    col4.metric("زيت الأسطوانات Cyl LO", f"{today['Cyl_LO']} L", f"{today['Cyl_LO']-yesterday['Cyl_LO']} L", delta_color="inverse")

    st.divider()

    # 5. تحليل حريق المحرك (Combustion Data)
    st.subheader("🔥 مراقبة درجات حرارة الأسطوانات (MAN B&W / Mitsubishi)")
    temps_today = [today['C1'], today['C2'], today['C3'], today['C4'], today['C5'], today['C6']]
    temps_yesterday = [yesterday['C1'], yesterday['C2'], yesterday['C3'], yesterday['C4'], yesterday['C5'], yesterday['C6']]
    
    fig = go.Figure()
    cyl_labels = [f"Cyl {i+1}" for i in range(6)]
    fig.add_trace(go.Bar(x=cyl_labels, y=temps_today, name='Today', marker_color='darkred'))
    fig.add_trace(go.Scatter(x=cyl_labels, y=temps_yesterday, name='Yesterday', line=dict(color='black', dash='dot')))
    fig.update_layout(yaxis_title="Temp °C", barmode='group')
    st.plotly_chart(fig, use_container_width=True)

    # 6. سجل البيانات التاريخي (The Log)
    st.subheader("📋 السجل الفني التاريخي للسفينة")
    st.dataframe(vessel_df, use_container_width=True)
else:
    st.warning("لا توجد بيانات كافية لإجراء المقارنة. يرجى إضافة تقارير Noon إضافية.")

# 7. ميزة إضافة البيانات (تحت التطوير)
with st.expander("➕ إضافة تقرير Noon جديد للقاعدة"):
    st.write("يمكنك قريباً رفع ملف الـ Excel هنا لتحديث قاعدة البيانات تلقائياً.")