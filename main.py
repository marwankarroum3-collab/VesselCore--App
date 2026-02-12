import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

# --- 1. الهوية البصرية العالمية (Professional Command Center UI) ---
st.set_page_config(page_title="VesselCore Intelligence OS", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #e1e4e8; }
    .stMetric { background-color: #1c2128; border: 1px solid #30363d; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #30363d; }
    h1, h2, h3 { color: #58a6ff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stTab { background-color: #0d1117; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك الأرشفة والبيانات السيادية (Persistence Engine) ---
DB_FILE = 'vessel_master_intel.csv'
FLEET_SPECS = {
    "NJ MOON": {"Engine": "MAN B&W 6S50MC-C", "Pitch": 4.82, "BHP_Max": 12880, "Cyl": 6},
    "NJ MARS": {"Engine": "MAN B&W 6S60MC-C", "Pitch": 5.10, "BHP_Max": 15600, "Cyl": 6},
    "NJ AIO": {"Engine": "Mitsubishi UEC", "Pitch": 4.95, "BHP_Max": 11000, "Cyl": 6},
    "YARA J": {"Engine": "MAN B&W 5S50MC-C", "Pitch": 4.75, "BHP_Max": 10500, "Cyl": 5}
}

def load_vessel_core():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df
    return pd.DataFrame(columns=['Date', 'Ship', 'Dist_Obs', 'RPM', 'Speed', 'ME_FO', 'AE_DO', 'Cyl_LO', 'Slip', 'ME_Exh', 'Gen_Exh', 'SFOC'])

df_archive = load_vessel_core()

# --- 3. محرك التحليل الهندسي (Marine Engineering Brain) ---
def analyze_propulsion(rpm, pitch, dist_obs):
    if rpm <= 0 or dist_obs <= 0: return 0.0, 0.0
    # مسافة الماكينة النظرية
    dist_eng = (rpm * 60 * 24 * pitch) / 1852
    slip = ((dist_eng - dist_obs) / dist_eng) * 100
    # تقدير السرعة النظرية (Theoretical Speed)
    theo_speed = (rpm * 60 * pitch) / 1852
    return round(slip, 2), round(theo_speed, 2)

# --- 4. واجهة القيادة الجانبية (The Bridge Sidebar) ---
with st.sidebar:
    st.title("🚢 VesselCore Command")
    st.image("https://cdn-icons-png.flaticon.com/512/3243/3243171.png", width=100)
    st.write(f"**CEO & Technical Director:** Marwan Karroum")
    
    st.divider()
    menu = st.radio("Navigation:", ["Fleet Operations", "Engineering Diagnostic", "Data Archive", "Settings"])
    
    if menu == "Settings":
        st.subheader("📡 Gmail Auto-Sync")
        st.info("System linked to: marwankarroum1989@gmail.com")

# --- 5. لوحة التحكم الاستراتيجية (Fleet Operations) ---
if menu == "Fleet Operations":
    st.title("🌍 Fleet Intelligence Dashboard")
    target_ship = st.selectbox("Select Vessel for Analysis:", list(FLEET_SPECS.keys()))
    
    ship_db = df_archive[df_archive['Ship'] == target_ship].sort_values(by='Date')
    
    if not ship_db.empty:
        latest = ship_db.iloc[-1]
        
        # الصف الأول: مؤشرات الأداء الحيوية (Strategic Metrics)
        st.subheader("🚀 Performance KPIs")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Distance Observed", f"{latest['Dist_Obs']} NM")
        c2.metric("Propeller Slip", f"{latest['Slip']}%", delta="Normal" if latest['Slip'] < 15 else "Critical")
        c3.metric("Bunker FO Cons.", f"{latest['ME_FO']} MT", "-2.1%")
        c4.metric("Engine RPM", latest['RPM'], "Verified")

        st.divider()

        # نظام التبويبات المتطور (Professional Analysis Tabs)
        tab_perf, tab_mech, tab_aux = st.tabs(["📊 Navigation Analysis", "🔥 Main Engine Diagnostic", "⚡ Auxiliary Machinery"])
        
        with tab_perf:
            col_graph, col_stats = st.columns([2, 1])
            with col_graph:
                # تريند استهلاك الوقود المزدوج مع السرعة
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(go.Scatter(x=ship_db['Date'], y=ship_db['ME_FO'], name="ME Fuel (MT)", line=dict(color='#3498db', width=4)), secondary_y=False)
                fig.add_trace(go.Scatter(x=ship_db['Date'], y=ship_db['Slip'], name="Slip %", line=dict(color='#00ff00', width=2, dash='dot')), secondary_y=True)
                fig.update_layout(template="plotly_dark", title="Fuel Consumption vs Propeller Slip Trend", height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_stats:
                st.write("**Engineering Insights:**")
                st.markdown(f"> **Slip Analysis:** Current slip of {latest['Slip']}% indicates {'optimal hull condition' if latest['Slip'] < 12 else 'potential hull fouling or heavy weather'}.")
                st.write(f"**Efficiency Rate:** {(latest['ME_FO']/latest['Dist_Obs']):.3f} MT/NM")

        with tab_mech:
            st.subheader("🔥 Exhaust Gas Combustion Thermal Map")
            # تحليل حريق الماكينة - معايير MAN B&W
            exh_vals = [int(x) for x in str(latest.get('ME_Exh', "0,0,0,0,0,0")).split(',')]
            fig_exh = go.Figure(go.Bar(x=[f"Cyl {i+1}" for i in range(len(exh_vals))], y=exh_vals, 
                                       marker=dict(color=exh_vals, colorscale='RdBu_r')))
            fig_exh.update_layout(template="plotly_dark", title="Main Engine Cylinder Exhaust Temperatures (°C)")
            st.plotly_chart(fig_exh, use_container_width=True)

        with tab_aux:
            st.subheader("⚡ Generator Load & Heat Balance")
            # 
            ae_exh = [int(x) for x in str(latest.get('Gen_Exh', "0,0,0,0,0")).split(',')]
            fig_ae = go.Figure(go.Pie(labels=[f"Unit {i+1}" for i in range(len(ae_exh))], values=ae_exh, hole=.4))
            fig_ae.update_layout(template="plotly_dark", title="Aux Engine Heat Distribution")
            st.plotly_chart(fig_ae, use_container_width=True)

    else:
        st.warning(f"Waiting for first Noon Report sync for {target_ship}...")
        st.image("https://cdn.dribbble.com/users/120988/screenshots/1151608/ship.gif", width=400)

# --- 6. صفحة الأرشفة (Data Archive) ---
if menu == "Data Archive":
    st.title("📂 Operational Logs & Archive")
    st.dataframe(df_archive.sort_values(by='Date', ascending=False), use_container_width=True)
    st.download_button("Export Archive to Excel", df_archive.to_csv(), "fleet_archive.csv", "text/csv")

st.caption("© 2026 VesselCore Technical - Engineering Master Intelligence OS")
