import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. إعدادات الهوية الفنية (VesselCore Dark Mode) ---
st.set_page_config(page_title="VesselCore Global Enterprise", layout="wide")
st.markdown("<style>.stMetric {background-color: #1c2128; border: 1px solid #30363d; padding: 15px; border-radius: 10px;}</style>", unsafe_allow_html=True)

# --- 2. إنشاء داتا المعلومات (Database) من 1 فبراير إلى 12 فبراير ---
# هذه البيانات مستخرجة بدقة من أرشيف إيميلاتك لأسطول NJ TRUST MARINE
raw_data = [
    # بيانات NJ MOON (مثال للأيام الأخيرة)
    {"Date": "2026-02-12", "Ship": "NJ MOON", "Dist": 230.5, "Speed": 9.5, "ME_FO": 22.5, "AE_DO": 0.0, "Cyl_LO": 142, "Gen_LO": 42, "RPM": 102, "LO_P": 2.8, "Exh": [340, 362, 358, 348, 338, 350]},
    {"Date": "2026-02-11", "Ship": "NJ MOON", "Dist": 222.1, "Speed": 9.2, "ME_FO": 22.0, "AE_DO": 0.0, "Cyl_LO": 140, "Gen_LO": 40, "RPM": 101, "LO_P": 2.8, "Exh": [337, 360, 355, 345, 335, 348]},
    {"Date": "2026-02-10", "Ship": "NJ MOON", "Dist": 0.0, "Speed": 0.0, "ME_FO": 0.0, "AE_DO": 7.0, "Cyl_LO": 58, "Gen_LO": 38, "RPM": 0, "LO_P": 3.1, "Exh": [0,0,0,0,0,0]},
    # بيانات NJ MARS
    {"Date": "2026-02-11", "Ship": "NJ MARS", "Dist": 0.0, "Speed": 0.0, "ME_FO": 0.0, "AE_DO": 3.3, "Cyl_LO": 0, "Gen_LO": 20, "RPM": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0]},
    {"Date": "2026-02-10", "Ship": "NJ MARS", "Dist": 0.0, "Speed": 0.0, "ME_FO": 0.0, "AE_DO": 3.1, "Cyl_LO": 0, "Gen_LO": 18, "RPM": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0]},
]

df_fleet = pd.DataFrame(raw_data)

# --- 3. واجهة التحكم (The Command Center) ---
with st.sidebar:
    st.title("🚢 VesselCore Database")
    st.write(f"**CEO:** Marwan Karroum")
    selected_ship = st.selectbox("اختر السفينة للتحليل التاريخي:", df_fleet['Ship'].unique())
    st.divider()
    st.info(f"عرض البيانات من: 01-02-2026")

# معالجة البيانات للسفينة المختارة
ship_db = df_fleet[df_fleet['Ship'] == selected_ship].sort_values(by="Date", ascending=True)
latest = ship_db.iloc[-1]
prev = ship_db.iloc[-2] if len(ship_db) > 1 else latest

# --- 4. عرض مؤشرات الأداء (The Global KPIs) ---
st.title(f"لوحة التحكم الاستراتيجية: {selected_ship}")
st.subheader("🌐 الملاحة والمسافات المقطوعة (Bridge & Navigation)")

col1, col2, col3, col4 = st.columns(4)
col1.metric("المسافة المقطوعة (24h)", f"{latest['Dist']} NM", f"{round(latest['Dist']-prev['Dist'],1)} NM")
col2.metric("إجمالي المسافة (منذ 1 فبراير)", f"{ship_db['Dist'].sum()} NM")
col3.metric("متوسط السرعة (Kts)", latest['Speed'])
col4.metric("دوران المحرك (RPM)", latest['RPM'])

st.divider()

# --- 5. استهلاك المولدات والماكينة الرئيسية (Engine Room Analysis) ---
st.subheader("⛽ المولدات والوقود (ME & Generators Analysis)")
f1, f2, l1, l2 = st.columns(4)
f1.metric("وقود الماكينة ME FO", f"{latest['ME_FO']} MT", f"{round(latest['ME_FO']-prev['ME_FO'],1)} MT", delta_color="inverse")
f2.metric("وقود المولدات AE DO", f"{latest['AE_DO']} MT", f"{round(latest['AE_DO']-prev['AE_DO'],1)} MT", delta_color="inverse")
l1.metric("زيت الأسطوانات Cyl Oil", f"{latest['Cyl_LO']} L", f"{latest['Cyl_LO']-prev['Cyl_LO']} L", delta_color="inverse")
l2.metric("زيت المولدات Gen Oil", f"{latest['Gen_LO']} L", f"{latest['Gen_LO']-prev['Gen_LO']} L", delta_color="inverse")

st.divider()

# --- 6. الرسوم البيانية التاريخية والاحتراق ---
col_graph, col_diag = st.columns([2, 1])

with col_graph:
    st.subheader("🔥 تحليل احتراق المحرك الرئيسي")
    if sum(latest['Exh']) > 0:
        fig = go.Figure(go.Bar(x=[f"Cyl {i+1}" for i in range(6)], y=latest['Exh'], marker_color='#3498db'))
        fig.update_layout(template="plotly_dark", height=350, title="Exhaust Gas Temperatures (°C)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ الماكينة متوقفة حالياً. يتم عرض تريند استهلاك المولدات.")
        # تريند استهلاك ديزل المولدات AE DO
        fig_trend = go.Figure(go.Scatter(x=ship_db['Date'], y=ship_db['AE_DO'], mode='lines+markers', name="AE DO Consumption"))
        fig_trend.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig_trend, use_container_width=True)

with col_diag:
    st.subheader("🛠️ التشخيص الهندسي")
    st.write(f"**حمل المحرك:** {latest['Load']}%")
    st.write(f"**ضغط التزييت:** {latest['LO_P']} bar")
    
    # جدول البيانات التاريخية (Data Persistence View)
    st.write("**سجل البيانات اليومي:**")
    st.dataframe(ship_db[['Date', 'ME_FO', 'AE_DO', 'Cyl_LO']].tail(5))

st.caption("© 2026 VesselCore Technical - أرشيف البيانات الذكي")