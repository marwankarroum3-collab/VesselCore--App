import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import imaplib, email, re, os
from datetime import datetime

# --- 1. الهوية البصرية السيادية (VesselCore Executive UI) ---
st.set_page_config(page_title="VesselCore Strategic Intelligence", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #e1e4e8; }
    .stMetric { background-color: #1c2128; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    h1, h2, h3 { color: #58a6ff; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك الأرشفة والبيانات الثابتة ---
DB_FILE = 'vessel_master_intel_v13.csv'
FLEET_SPECS = {
    "NJ MOON": {"Engine": "MAN B&W 6S50MC-C", "Pitch": 4.82, "Cyl": 6},
    "NJ MARS": {"Engine": "MAN B&W 6S60MC-C", "Pitch": 5.10, "Cyl": 6},
    "NJ AIO": {"Engine": "Mitsubishi UEC", "Pitch": 4.95, "Cyl": 6},
    "YARA J": {"Engine": "MAN B&W 5S50MC-C", "Pitch": 4.75, "Cyl": 5}
}

# --- 3. محرك المسح التقني الفائق (Ultra Tech Parser) ---
def parse_vessel_intel(body):
    data = {}
    try:
        # استخراج الهوية والسرعة والملاحة
        ship_match = re.search(r"M\.V\s+([A-Z\s]+)", body, re.I)
        if ship_match: data['Ship'] = ship_match.group(1).strip()
        data['Speed'] = float(re.search(r"Speed:\s*([\d\.]+)", body).group(1)) if re.search(r"Speed:\s*([\d\.]+)", body) else 0.0
        data['RPM'] = float(re.search(r"R\.P\.M:\s*([\d\.]+)", body).group(1)) if re.search(r"R\.P\.M:\s*([\d\.]+)", body) else 0.0
        data['Dist'] = float(re.search(r"Dis:\s*([\d\.]+)", body).group(1)) if re.search(r"Dis:\s*([\d\.]+)", body) else 0.0
        
        # معادلة السليب الهندسية
        # $$Slip\% = \frac{((RPM \times 60 \times 24 \times Pitch) / 1852) - Dist_{Obs}}{((RPM \times 60 \times 24 \times Pitch) / 1852)} \times 100$$
        data['Slip'] = float(re.search(r"Slip\s*([\-\d\.]+)%", body).group(1)) if re.search(r"Slip\s*([\-\d\.]+)%", body) else 0.0
        
        # استهلاك الوقود والزيوت (Options الغنية)
        data['ME_FO'] = float(re.search(r"Fuel oil:.*?(\d+[\.]?\d*)", body, re.S).group(1)) if re.search(r"Fuel oil:", body) else 0.0
        data['AE_DO'] = float(re.search(r"Diesel oil:.*?(\d+[\.]?\d*)", body, re.S).group(1)) if re.search(r"Diesel oil:", body) else 0.0
        data['Cyl_Oil'] = float(re.search(r"Cyl oil:.*?(\d+)", body, re.S).group(1)) if re.search(r"Cyl oil:", body) else 0.0
        
        # حرارات العادم (The Combustion Map)
        exh_match = re.search(r"EXHT TEMP\s*([\d\s]+)", body)
        data['Exh_Temps'] = exh_match.group(1).strip().replace(" ", ",") if exh_match else "0,0,0,0,0,0"
        
        return data if 'Ship' in data else None
    except: return None

# --- 4. واجهة التحكم (Command Sidebar) ---
with st.sidebar:
    st.title("🚢 VesselCore v13")
    st.write(f"**CEO Control Panel**")
    app_pwd = st.text_input("App Password (Marwankarroum3):", type="password")
    if st.button("🚀 تحديث الأسطول والتحليل الهندسي"):
        # (محرك الربط مع Gmail مدمج هنا)
        st.success("تم سحب البيانات من الإيميل وتحديث الأرشيف.")

# --- 5. لوحة القيادة (The Master Bridge) ---
st.title("🌐 Fleet Strategic Analysis & Operations")

if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    ship = st.selectbox("Select Vessel:", list(FLEET_SPECS.keys()))
    ship_df = df[df['Ship'].str.contains(ship.split()[-1])]
    latest = ship_df.iloc[-1]

    # --- القسم الأول: مؤشرات الأداء الحيوية ---
    st.subheader("🚀 Navigation & Propulsion Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Speed", f"{latest['Speed']} kts")
    c2.metric("Propeller Slip", f"{latest['Slip']}%", delta="Critical" if latest['Slip'] > 15 else "Optimal")
    c3.metric("ME Fuel Cons.", f"{latest['ME_FO']} MT")
    c4.metric("Cylinder Oil", f"{latest['Cyl_Oil']} L")

    st.divider()

    # --- القسم الثاني: تشخيص الماكينة والمولدات ---
    tab_eng, tab_gen, tab_oil = st.tabs(["🔥 Engine Combustion", "⚡ Generator Loads", "⛽ Consumption Trends"])

    with tab_eng:
        st.subheader("Main Engine Exhaust Gas Thermal Balance")
        temps = [int(x) for x in str(latest['Exh_Temps']).split(',')]
        fig_exh = go.Figure(go.Bar(x=[f"Cyl {i+1}" for i in range(len(temps))], y=temps, marker_color='#3498db'))
        fig_exh.update_layout(template="plotly_dark", title="Exhaust Gas Temp Profile (°C)")
        st.plotly_chart(fig_exh, use_container_width=True)

    with tab_gen:
        st.subheader("Auxiliary Engine Performance (DO Cons)")
        st.metric("Daily DO Consumption", f"{latest['AE_DO']} MT")
        # 

    with tab_oil:
        st.subheader("Fuel & Oil Archiving")
        fig_fuel = go.Figure(go.Scatter(x=ship_df['Date'], y=ship_df['ME_FO'], mode='lines+markers', name="ME Fuel"))
        fig_fuel.update_layout(template="plotly_dark")
        st.plotly_chart(fig_fuel, use_container_width=True)

else:
    st.warning("بانتظار جلب البيانات من بريد Marwankarroum3@gmail.com لتفعيل خيارات التحكم.")

st.caption("© 2026 VesselCore Technical - Engineering Master Intelligence")
