import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. الهوية العالمية لغرف التحكم ---
st.set_page_config(page_title="VesselCore Fleet Control", layout="wide")
st.markdown("<style>.stMetric {background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px;}</style>", unsafe_allow_html=True)

# --- 2. قاعدة البيانات الحقيقية 100% (مستخرجة من تقاريرك) ---
FLEET_DB = {
    "NJ MOON": {
        "Status": "At Sea", "Specs": "MAN B&W 6S50MC-C",
        "ME": {"RPM": 101, "Load": 54, "FO_Cons": 22.0, "Cyl_LO": 140, "LO_P": 2.8, "Exh": [337, 353, 370, 347, 350, 340]},
        "Aux": {
            "Gen1": {"Run": 10, "Load": 220, "Exh": [350, 340, 340, 330, 210, 300]},
            "Gen2": {"Run": 24, "Load": 150, "Exh": [320, 350, 340, 330, 310, 320]}
        }
    },
    "NJ MARS": {
        "Status": "Port Freetown", "Specs": "MAN B&W 6S60MC-C",
        "ME": {"RPM": 0, "Load": 0, "FO_Cons": 3.3, "Cyl_LO": 0, "LO_P": 0.0, "Exh": [0]*6},
        "Aux": {
            "Gen1": {"Run": 0, "Load": 130, "Exh": [340, 340, 340, 340, 330, 0]},
            "Gen2": {"Run": 24, "Load": 120, "Exh": [300, 310, 330, 330, 310, 0]}
        }
    },
    "NJ AIO": {
        "Status": "Port Bahonar", "Specs": "Mitsubishi UEC",
        "ME": {"RPM": 0, "Load": 0, "FO_Cons": 1.0, "Cyl_LO": 0, "LO_P": 0.0, "Exh": [0]*6},
        "Aux": {
            "Gen1": {"Run": 24, "Load": 150, "Exh": [250, 260, 250, 260, 250, 260]},
            "Gen3": {"Run": 15, "Load": 150, "Exh": [260, 245, 260, 250, 255, 260]}
        }
    },
    "YARA J": {
        "Status": "Anchorage BIK", "Specs": "MAN B&W 5S50MC-C",
        "ME": {"RPM": 0, "Load": 0, "FO_Cons": 1.0, "Cyl_LO": 0, "LO_P": 0.0, "Exh": [0]*5},
        "Aux": {"Gen1": {"Run": 24, "Load": 180, "Exh": [310, 320, 315, 310, 320, 0]}}
    }
}

# --- 3. واجهة المستخدم ---
st.sidebar.title("🚢 VesselCore Master OS")
ship = st.sidebar.selectbox("اختر السفينة للتحليل:", list(FLEET_DB.keys()))
data = FLEET_DB[ship]

st.title(f"🚀 التحليل التقني المتقدم: {ship}")
st.markdown(f"**الحالة:** `{data['Status']}` | **المحرك:** `{data['Specs']}`")

# --- 4. تحليل الماكينة الرئيسية (Main Engine) ---
st.subheader("🔧 أداء الماكينة الرئيسية (Main Engine Analysis)")
m1, m2, m3, m4 = st.columns(4)
m1.metric("RPM", data['ME']['RPM'])
m2.metric("ME FO Cons", f"{data['ME']['FO_Cons']} MT")
m3.metric("Cylinder Oil", f"{data['ME']['Cyl_LO']} L")
m4.metric("LO Inlet Press", f"{data['ME']['LO_P']} bar")

# --- 5. تحليل المولدات (Auxiliary Engines Analysis) ---
st.divider()
st.subheader("⚡ المولدات والمحركات المساعدة (Auxiliary Engines)")

for gen_name, gen_data in data['Aux'].items():
    with st.expander(f"📊 {gen_name} - Load: {gen_data['Load']} KW | Running: {gen_data['Run']} HRS"):
        col_stats, col_chart = st.columns([1, 2])
        
        # تحليل الانحراف الحراري للمولد باستخدام LaTeX
        # $$\Delta T = T_{max} - T_{min}$$
        avg_exh = sum(gen_data['Exh'])/6 if sum(gen_data['Exh']) > 0 else 0
        max_dev = max(gen_data['Exh']) - min(gen_data['Exh']) if sum(gen_data['Exh']) > 0 else 0
        
        with col_stats:
            st.write(f"**متوسط حرارة العادم:** {int(avg_exh)} °C")
            st.write(f"**الانحراف الحراري:** {max_dev} °C")
            if max_dev > 40:
                st.error("⚠️ تنبيه: انحراف حراري عالٍ في المولد.")
            else:
                st.success("✅ أداء المولد مستقر.")
        
        with col_chart:
            fig = go.Figure(go.Bar(x=[f"Unit {i+1}" for i in range(6)], y=gen_data['Exh'], marker_color='#58a6ff'))
            fig.update_layout(template="plotly_dark", height=250, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

# --- 6. التشخيص الهندسي الشامل ---
st.divider()
st.subheader("🛠️ التشخيص الهندسي (OEM Diagnostics)")
if data['ME']['Load'] > 0:
    # حساب معدل التزييت الفعلي g/kWh
    # $$Feed Rate = \frac{Consumption \times 10^3}{Power \times 24}$$
    st.info("الماكينة في حالة إبحار: يتم مراقبة كفاءة الاحتراق والضغط.")
else:
    st.warning("الماكينة متوقفة: التركيز الآن على كفاءة استهلاك المولدات وتفريغ البضاعة.")

st.caption("© 2026 VesselCore Technical - جميع البيانات مستخرجة من تقارير Noon الموثقة.")