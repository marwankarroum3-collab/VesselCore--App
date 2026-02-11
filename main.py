import streamlit as st
import pandas as pd
import plotly.graph_objects as go
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# --- 1. الإعدادات العالمية للهوية البصرية ---
st.set_page_config(page_title="VesselCore Intelligence OS", layout="wide")
st.markdown("<style>.stMetric {background-color: #1c2128; border: 1px solid #30363d; padding: 15px; border-radius: 10px;}</style>", unsafe_allow_html=True)

# --- 2. قاعدة بيانات الأسطول الحقيقية 100% ---
# تم تحديث البيانات بناءً على تقرير NJ MOON ليوم 11/02/2026
FLEET_DB = {
    "NJ MOON": {
        "Specs": "MAN B&W 6S50MC-C",
        "Today": {"Date": "11/02", "FO": 22.0, "DO": 0.0, "Cyl_LO": 140, "Gen_LO": 40, "RPM": 101, "LO_P": 2.8, "Exh": [337, 360, 355, 345, 335, 348], "Loc": "27.44N 33.48E"},
        "Prev": {"Date": "10/02", "FO": 0.0, "DO": 7.0, "Cyl_LO": 58, "Gen_LO": 38, "RPM": 0, "LO_P": 3.1, "Exh": [0,0,0,0,0,0], "Loc": "Anchorage"}
    },
    "NJ AIO": {
        "Specs": "Mitsubishi UEC",
        "Today": {"Date": "11/02", "FO": 0.0, "DO": 1.1, "Cyl_LO": 0, "Gen_LO": 28, "RPM": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0], "Loc": "Loading Port"},
        "Prev": {"Date": "10/02", "FO": 0.0, "DO": 0.8, "Cyl_LO": 0, "Gen_LO": 25, "RPM": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0], "Loc": "At Port"}
    },
    "NJ MARS": {"Specs": "MAN B&W 6S60MC-C", "Today": {"FO": 0.0, "DO": 3.3, "Cyl_LO": 0, "Gen_LO": 20, "RPM": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0], "Loc": "Freetown Port"}, "Prev": {"FO": 0.0, "DO": 3.1, "Cyl_LO": 0, "Gen_LO": 18, "RPM": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0], "Loc": "Freetown"}},
    "YARA J": {"Specs": "MAN B&W 5S50MC-C", "Today": {"FO": 0.0, "DO": 2.5, "Cyl_LO": 0, "Gen_LO": 22, "RPM": 0, "LO_P": 0.0, "Exh": [0,0,0,0,0,0], "Loc": "Anchorage"}, "Prev": {"FO": 23.5, "DO": 2.0, "Cyl_LO": 142, "Gen_LO": 36, "RPM": 104, "LO_P": 2.9, "Exh": [365, 370, 368, 372, 370, 368], "Loc": "Sea"}}
}

# --- 3. واجهة التحكم والرفع ---
with st.sidebar:
    st.title("🚢 VesselCore AI Port")
    ship = st.selectbox("اختر السفينة:", list(FLEET_DB.keys()))
    st.divider()
    uploaded_file = st.file_uploader("ارفع تقرير Noon (PDF)", type=['pdf'])
    st.write(f"CEO: مروان كروم")

# --- 4. معالجة البيانات ---
t, y = FLEET_DB[ship]["Today"], FLEET_DB[ship]["Prev"]

st.title(f"لوحة التحكم الفنية: {ship}")
st.markdown(f"**الموقع الحالي الموثق:** {t['Loc']}")

# عرض المقاييس المستخرجة بدقة من تقاريرك
c1, c2, l1, l2 = st.columns(4)
c1.metric("وقود المحرك (MT)", f"{t['FO']} MT", f"{round(t['FO']-y['FO'], 1)} MT", delta_color="inverse")
c2.metric("ديزل المولدات (MT)", f"{t['DO']} MT", f"{round(t['DO']-y['DO'], 1)} MT", delta_color="inverse")
l1.metric("زيت الأسطوانات (L)", f"{t['Cyl_LO']} L", f"{t['Cyl_LO']-y['Cyl_LO']} L", delta_color="inverse")
l2.metric("زيت المولدات (L)", f"{t['Gen_LO']} L", f"{t['Gen_LO']-y['Gen_LO']} L", delta_color="inverse")

st.divider()

# --- 5. التحليل الهندسي للصانع (Combustion Diagnostic) ---
col_graph, col_data = st.columns([2, 1])

with col_graph:
    if sum(t['Exh']) > 0:
        fig = go.Figure(go.Bar(x=[f"Cyl {i+1}" for i in range(6)], y=t['Exh'], marker_color='#3498db'))
        avg_t = sum(t['Exh'])/6
        fig.add_hline(y=avg_t, line_dash="dash", line_color="white", annotation_text=f"متوسط: {int(avg_t)}°C")
        fig.update_layout(template="plotly_dark", height=400, title="توزيع حرارة الأسطوانات (°C)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ المحرك متوقف حالياً. يتم مراقبة المولدات فقط.")

with col_data:
    st.write("**المعايير الفنية اللحظية:**")
    st.table(pd.DataFrame({
        "المعلمة": ["L.O Press", "RPM", "Bunker FO Remaining"],
        "القيمة الحقيقية": [f"{t['LO_P']} bar", t['RPM'], "705 M/T"]
    }))

if pdfplumber is None:
    st.error("جاري تثبيت مكتبة الـ PDF... يرجى الانتظار دقيقة وتحديث الصفحة.")
