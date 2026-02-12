import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. إعدادات الهوية العالمية (Global Fleet Standard) ---
st.set_page_config(page_title="VesselCore Technical OS | Marwan Karroum", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
    h1, h2, h3 { color: #58a6ff; font-weight: 700; }
    div[data-testid="stExpander"] { background-color: #0d1117; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات التاريخي (من 1 فبراير إلى 12 فبراير) ---
# تم تنظيم البيانات بناءً على تقارير النون المستخرجة من الإيميلات
@st.cache_data
def load_vessel_database():
    data = [
        # نموذج NJ MOON (MAN B&W 6S50MC-C)
        {"Date": "2026-02-12", "Ship": "NJ MOON", "Dist": 230.5, "Speed": 9.5, "RPM": 102, "ME_FO": 22.5, "AE_DO": 0.0, "Cyl_LO": 142, "Gen_LO": 42, "Load": 52, "LO_P": 2.8, "Exh": [340, 362, 358, 348, 338, 350]},
        {"Date": "2026-02-11", "Ship": "NJ MOON", "Dist": 222.1, "Speed": 9.2, "RPM": 101, "ME_FO": 22.0, "AE_DO": 0.0, "Cyl_LO": 140, "Gen_LO": 40, "Load": 50, "LO_P": 2.8, "Exh": [337, 360, 355, 345, 335, 348]},
        {"Date": "2026-02-10", "Ship": "NJ MOON", "Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 7.0, "Cyl_LO": 58, "Gen_LO": 38, "Load": 0, "LO_P": 3.1, "Exh": [0]*6},
        {"Date": "2026-02-09", "Ship": "NJ MOON", "Dist": 215.0, "Speed": 8.9, "RPM": 98, "ME_FO": 21.2, "AE_DO": 0.0, "Cyl_LO": 138, "Gen_LO": 39, "Load": 48, "LO_P": 2.9, "Exh": [330, 352, 348, 338, 332, 344]},
        # نموذج NJ MARS (MAN B&W 6S60MC-C)
        {"Date": "2026-02-11", "Ship": "NJ MARS", "Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 3.3, "Cyl_LO": 0, "Gen_LO": 20, "Load": 0, "LO_P": 0.0, "Exh": [0]*6},
        {"Date": "2026-02-10", "Ship": "NJ MARS", "Dist": 0.0, "Speed": 0.0, "RPM": 0, "ME_FO": 0.0, "AE_DO": 3.1, "Cyl_LO": 0, "Gen_LO": 18, "Load": 0, "LO_P": 0.0, "Exh": [0]*6},
    ]
    return pd.DataFrame(data)

df_db = load_vessel_database()

# --- 3. واجهة التحكم الذكية (Smart Command Sidebar) ---
with st.sidebar:
    st.title("🚢 VesselCore Technical")
    st.write(f"**Technical Director:** Marwan Karroum")
    ship_selected = st.selectbox("اختر السفينة للتحليل العميق:", df_db['Ship'].unique())
    st.divider()
    st.info("📊 نطاق البيانات: 01-02-2026 إلى اليوم")

# تصفية البيانات المختارة
ship_data = df_db[df_db['Ship'] == ship_selected].sort_values(by="Date")
latest = ship_data.iloc[-1]
prev = ship_data.iloc[-2] if len(ship_data) > 1 else latest

# --- 4. التحليل الاستراتيجي للأداء (Strategic Performance Analysis) ---
st.title(f"🚀 Dashboard: {ship_selected} | Fleet Intelligence")

# القسم الأول: مؤشرات الملاحة والكفاءة
st.subheader("🌐 أداء الملاحة (Propulsion & Navigation)")
m1, m2, m3, m4 = st.columns(4)
m1.metric("المسافة (24h)", f"{latest['Dist']} NM", f"{round(latest['Dist']-prev['Dist'],1)} NM")
m2.metric("إجمالي المسافة (Feb)", f"{ship_data['Dist'].sum()} NM")
m3.metric("متوسط السرعة الشهرية", f"{round(ship_data[ship_data['Speed']>0]['Speed'].mean(),1)} Kts")
m4.metric("دوران المحرك (RPM)", latest['RPM'], f"{latest['RPM']-prev['RPM']}")

st.divider()

# القسم الثاني: إدارة الوقود والزيوت (Bunker & Lubrication Management)
st.subheader("⛽ استهلاك الطاقة والتزييت (Energy & LO Analysis)")
f1, f2, f3, f4 = st.columns(4)

# حساب معدل التزييت الفعلي (Cylinder Oil Feed Rate) - معيار MAN B&W
# SFOC/Feed Rate calculation simulation
feed_rate = round((latest['Cyl_LO'] * 0.9) / (latest['Load'] * 50 * 24), 2) if latest['Load'] > 0 else 0

f1.metric("وقود المحرك ME FO", f"{latest['ME_FO']} MT", delta_color="inverse")
f2.metric("وقود المولدات AE DO", f"{latest['AE_DO']} MT", delta_color="inverse")
f3.metric("زيت الأسطوانات", f"{latest['Cyl_LO']} L", f"Feed Rate: {feed_rate} g/kWh")
f4.metric("زيت المولدات", f"{latest['Gen_LO']} L")

st.divider()

# --- 5. التحليل الهندسي المتقدم (Advanced Mechanical Diagnostics) ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📊 تريند الأداء: الوقود مقابل السرعة (Efficiency Trend)")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=ship_data['Date'], y=ship_data['Speed'], name="السرعة (Kts)", line=dict(color="#00ff00", width=3)), secondary_y=False)
    fig.add_trace(go.Bar(x=ship_data['Date'], y=ship_data['ME_FO'], name="وقود ME", marker_color="rgba(52, 152, 219, 0.4)"), secondary_y=True)
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🛠️ تشخيص المحرك (OEM Check)")
    avg_exh = sum(latest['Exh'])/6 if sum(latest['Exh']) > 0 else 0
    
    # مصفوفة الحالة الفنية
    st.table(pd.DataFrame({
        "المعلمة الفنية": ["Engine Load", "L.O Press", "Avg. Exhaust", "Turbo Status"],
        "القيمة الحالية": [f"{latest['Load']}%", f"{latest['LO_P']} bar", f"{int(avg_exh)} °C", "Normal"]
    }))
    
    # تحليل احتراق الأسطوانات
    if avg_exh > 0:
        fig_exh = go.Figure(go.Bar(x=[f"C1", "C2", "C3", "C4", "C5", "C6"], y=latest['Exh'], marker_color='#3498db'))
        fig_exh.add_hline(y=avg_exh, line_dash="dash", line_color="white")
        fig_exh.update_layout(template="plotly_dark", height=200, margin=dict(l=5, r=5, t=5, b=5))
        st.plotly_chart(fig_exh, use_container_width=True)
    else:
        st.info("الماكينة في حالة انتظار (Port/Anchorage)")

# --- 6. أرشيف البيانات الموثقة (Historical Logs) ---
with st.expander("📂 سجل البيانات التقني الكامل (أرشيف فبراير)"):
    st.dataframe(ship_data.sort_values(by="Date", ascending=False), use_container_width=True)

st.divider()
st.caption("© 2026 VesselCore Technical - Engineering Intelligent Systems | Marwan Karroum")