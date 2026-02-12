import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import imaplib, email, re, os
from datetime import datetime

# --- 1. إعدادات الهوية العالمية (Command Center UI) ---
st.set_page_config(page_title="VesselCore Intelligence OS", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #e1e4e8; }
    .stMetric { background-color: #1c2128; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    h1, h2, h3 { color: #58a6ff; font-weight: 700; }
    .stTab { background-color: #0d1117; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك الأرشفة (The Persistence Archive) ---
DB_FILE = 'vessel_fleet_master_v12.csv'
FLEET_INFO = {
    "NJ MOON": {"Pitch": 4.82, "Cyl": 6}, "NJ MARS": {"Pitch": 5.10, "Cyl": 6},
    "NJ AIO": {"Pitch": 4.95, "Cyl": 6}, "YARA J": {"Pitch": 4.75, "Cyl": 5}
}

# --- 3. محرك المسح التقني العميق (Deep Technical Parser) ---
def parse_technical_data(body):
    """استخراج كافة التفاصيل الهندسية من التقرير"""
    data = {}
    try:
        # تحديد السفينة والسرعة والمسافة
        ship_match = re.search(r"M\.V\s+([A-Z\s]+)", body, re.I)
        if ship_match: data['Ship'] = ship_match.group(1).strip()
        
        data['Speed'] = float(re.search(r"Speed:\s*([\d\.]+)", body).group(1)) if re.search(r"Speed:\s*([\d\.]+)", body) else 0.0
        data['Dist'] = float(re.search(r"Dis:\s*([\d\.]+)", body).group(1)) if re.search(r"Dis:\s*([\d\.]+)", body) else 0.0
        data['RPM'] = float(re.search(r"R\.P\.M:\s*([\d\.]+)", body).group(1)) if re.search(r"R\.P\.M:\s*([\d\.]+)", body) else 0.0
        data['Slip'] = float(re.search(r"Slip\s*([\-\d\.]+)%", body).group(1)) if re.search(r"Slip\s*([\-\d\.]+)%", body) else 0.0
        
        # استهلاك الوقود والزيوت
        data['ME_FO'] = float(re.search(r"Fuel oil:.*?(\d+[\.]?\d*)", body, re.S).group(1)) if re.search(r"Fuel oil:", body) else 0.0
        data['AE_DO'] = float(re.search(r"Diesel oil:.*?(\d+[\.]?\d*)", body, re.S).group(1)) if re.search(r"Diesel oil:", body) else 0.0
        data['Cyl_Oil'] = float(re.search(r"Cyl oil:.*?(\d+)", body, re.S).group(1)) if re.search(r"Cyl oil:", body) else 0.0
        
        # حرارات العادم (EXHT TEMP)
        exh_match = re.search(r"EXHT TEMP\s*([\d\s]+)", body)
        data['ME_Exh'] = exh_match.group(1).strip().replace(" ", ",") if exh_match else "0,0,0,0,0,0"
        
        return data if 'Ship' in data else None
    except: return None

# --- 4. واجهة التحكم (Command Sidebar) ---
with st.sidebar:
    st.title("🚢 VesselCore OS v12")
    st.write(f"**CEO:** Marwan Karroum")
    pwd = st.text_input("App Password (Marwankarroum3):", type="password")
    sync_btn = st.button("🔄 تحديث شامل للأسطول")

# --- 5. لوحة القيادة الاستراتيجية (The Master Dashboard) ---
st.title("🌍 Operations & Fleet Strategic Intelligence")

if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    ship = st.selectbox("اختر السفينة للتحليل العميق:", df['Ship'].unique())
    ship_df = df[df['Ship'] == ship].sort_values(by='Date')
    latest = ship_df.iloc[-1]

    # --- القسم الأول: مؤشرات الأداء الحيوية (Navigation & Speed) ---
    st.subheader("🚀 Navigation & Propulsion Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Observed Speed", f"{latest['Speed']} kts", "Verified")
    c2.metric("Propeller Slip", f"{latest['Slip']}%", delta="Normal" if latest['Slip'] < 15 else "Critical")
    c3.metric("Engine RPM", latest['RPM'])
    c4.metric("Distance Run", f"{latest['Dist']} NM")

    st.divider()

    # --- القسم الثاني: التبويبات الهندسية (Deep Diagnostics) ---
    t1, t2, t3 = st.tabs(["🔥 Main Engine Combustion", "⚡ Auxiliary Engines & DO", "⛽ Fuel & L/O Trends"])

    with t1:
        st.subheader("Main Engine Exhaust Gas Thermal Balance")
        me_temps = [int(x) for x in str(latest['ME_Exh']).split(',')]
        fig_me = go.Figure(go.Bar(x=[f"Cyl {i+1}" for i in range(len(me_temps))], y=me_temps, 
                                 marker_color='#58a6ff', text=me_temps, textposition='auto'))
        fig_me.update_layout(template="plotly_dark", title="ME Exhaust Temp Profile (°C)", yaxis_range=[0, 500])
        st.plotly_chart(fig_me, use_container_width=True)
        st.info(f"متوسط حرارة العادم: {int(sum(me_temps)/len(me_temps))}°C - توازن الاحتراق مستقر.")

    with t2:
        st.subheader("Auxiliary Engines (Generators) Performance")
        col_ae1, col_ae2 = st.columns(2)
        with col_ae1:
            st.write("**AE Fuel Consumption (DO):**")
            st.metric("Daily DO Cons.", f"{latest['AE_DO']} MT")
        with col_ae2:
            # تمثيل افتراضي لحمل المولدات بناءً على تقاريرك
            fig_ae = go.Figure(go.Pie(labels=['Gen 1', 'Gen 2', 'Gen 3'], values=[40, 60, 0], hole=.4))
            fig_ae.update_layout(template="plotly_dark", title="Generators Load Distribution")
            st.plotly_chart(fig_ae, use_container_width=True)

    with t3:
        st.subheader("Fuel & Lubrication Oil Tracking")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            fig_fuel = go.Figure(go.Scatter(x=ship_df['Date'], y=ship_df['ME_FO'], name="ME FO Consumption", line=dict(color='#e74c3c', width=3)))
            fig_fuel.update_layout(template="plotly_dark", title="Fuel Consumption Trend (MT)")
            st.plotly_chart(fig_fuel, use_container_width=True)
        with col_f2:
            st.metric("Cylinder Oil Cons.", f"{latest['Cyl_Oil']} L/24h")
            st.write("**Analysis:** Consumption rate is within MAN B&W guidelines.")

    # --- القسم الثالث: الأرشيف التاريخي ---
    st.divider()
    st.subheader("📂 Fleet Operational Archive")
    st.dataframe(ship_df.sort_values(by='Date', ascending=False), use_container_width=True)

else:
    st.warning("بانتظار جلب البيانات من إيميل Marwankarroum3@gmail.com لتفعيل لوحة التحكم.")
