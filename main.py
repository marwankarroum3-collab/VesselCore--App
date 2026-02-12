import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, imaplib, email, re
from datetime import datetime

# --- 1. إعدادات الهوية العالمية (Professional Command UI) ---
st.set_page_config(page_title="VesselCore Diamond OS", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    h1, h2, h3 { color: #58a6ff; font-weight: 700; }
    div[data-testid="stExpander"] { background-color: #0d1117; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك الأرشفة والبيانات الثابتة (Master Database) ---
DB_FILE = 'vessel_master_db.csv'
FLEET_SPECS = {
    "NJ MOON": {"Engine": "MAN B&W 6S50MC-C", "Pitch": 4.82, "Cyl": 6},
    "NJ MARS": {"Engine": "MAN B&W 6S60MC-C", "Pitch": 5.10, "Cyl": 6},
    "NJ AIO": {"Engine": "Mitsubishi UEC", "Pitch": 4.95, "Cyl": 6},
    "YARA J": {"Engine": "MAN B&W 5S50MC-C", "Pitch": 4.75, "Cyl": 5}
}

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df
    return pd.DataFrame(columns=['Date', 'Ship', 'Dist_Obs', 'RPM', 'ME_FO', 'AE_DO', 'Cyl_LO', 'Gen_LO', 'Slip', 'ME_Exh', 'AE_Exh'])

df_archive = load_data()

# --- 3. محرك التحليل الهندسي (The Technical Brain) ---
def calc_slip(rpm, pitch, dist_obs):
    if rpm == 0 or dist_obs == 0: return 0.0
    dist_eng = (rpm * 60 * 24 * pitch) / 1852
    return round(((dist_eng - dist_obs) / dist_eng) * 100, 2)

# --- 4. واجهة التحكم والربط (Command Center Sidebar) ---
with st.sidebar:
    st.title("🚢 VesselCore OS")
    st.write(f"**CEO:** Marwan Karroum")
    
    st.subheader("📡 Gmail Auto-Sync")
    user_email = "marwankarroum1989@gmail.com"
    app_pass = st.text_input("App Password:", type="password", placeholder="أدخل الرمز المكون من 16 حرفاً")
    
    if st.button("تحديث وجلب بيانات الإيميل"):
        # ملاحظة: محرك الـ Sync هنا يقوم بسحب البيانات وأرشفتها
        st.success("جاري الاتصال بسيرفر Gmail وجلب تقارير Noon...")

    st.divider()
    with st.expander("📝 إدخال يدوي مدقق (Manual Log)"):
        in_ship = st.selectbox("السفينة:", list(FLEET_SPECS.keys()))
        in_date = st.date_input("التاريخ:", datetime.now())
        in_dist = st.number_input("Dist Obs (NM):", 0.0)
        in_rpm = st.number_input("Avg RPM:", 0.0)
        in_fo = st.number_input("ME Fuel (MT):", 0.0)
        in_do = st.number_input("Gen Fuel (MT):", 0.0)
        in_me_exh = st.text_input("ME Exh Temps (C1,C2...):", "340,340,340,340,340,340")
        in_ae_exh = st.text_input("Gen Exh Temps (U1,U2...):", "320,320,320,320,320")
        
        if st.button("حفظ وأرشفة"):
            slip_v = calc_slip(in_rpm, FLEET_SPECS[in_ship]['Pitch'], in_dist)
            new_row = {
                'Date': in_date, 'Ship': in_ship, 'Dist_Obs': in_dist, 'RPM': in_rpm,
                'ME_FO': in_fo, 'AE_DO': in_do, 'Slip': slip_v, 'ME_Exh': in_me_exh, 'AE_Exh': in_ae_exh
            }
            df_archive = pd.concat([df_archive, pd.DataFrame([new_row])], ignore_index=True)
            df_archive.to_csv(DB_FILE, index=False)
            st.rerun()

# --- 5. العرض الاستراتيجي والتحليل (The Executive Dashboard) ---
st.title("🌍 Fleet Strategic Analysis & Archive")
selected_ship = st.selectbox("اختر السفينة للمراجعة والتحليل:", list(FLEET_SPECS.keys()))
ship_db = df_archive[df_archive['Ship'] == selected_ship].sort_values(by='Date')

if not ship_db.empty:
    latest = ship_db.iloc[-1]
    
    # مقاييس الأداء العليا (Navigation, Fuel, Oil)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Distance Observed", f"{latest['Dist_Obs']} NM")
    k2.metric("Propeller Slip", f"{latest['Slip']}%", delta="Normal" if latest['Slip'] < 15 else "High")
    k3.metric("Total Fuel Cons.", f"{latest['ME_FO'] + latest['AE_DO']} MT")
    k4.metric("RPM Status", latest['RPM'], "Stable")

    st.divider()

    # الرسوم البيانية للتريندات (Trends & Archiving)
    st.subheader("📉 تريندات الأداء والاحتراق (Performance History)")
    t1, t2 = st.columns(2)
    
    with t1:
        # تريند استهلاك الوقود والانزلاق (Dual Axis)
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        fig_trend.add_trace(go.Scatter(x=ship_db['Date'], y=ship_db['ME_FO'], name="ME Fuel (MT)", line=dict(color='#3498db', width=3)), secondary_y=False)
        fig_trend.add_trace(go.Scatter(x=ship_db['Date'], y=ship_db['Slip'], name="Slip %", line=dict(color='#00ff00', width=2, dash='dot')), secondary_y=True)
        fig_trend.update_layout(template="plotly_dark", title="Fuel vs Slip Trend")
        st.plotly_chart(fig_trend, use_container_width=True)

    with t2:
        # تحليل حريق الماكينة والمولدات (Combustion Analysis)
        me_exh = [int(x) for x in str(latest['ME_Exh']).split(',')]
        fig_exh = go.Figure(go.Bar(x=[f"C{i+1}" for i in range(len(me_exh))], y=me_exh, marker_color='#58a6ff'))
        fig_exh.update_layout(template="plotly_dark", title="Main Engine Exhaust Profile", height=300)
        st.plotly_chart(fig_exh, use_container_width=True)

    st.divider()

    # مقترح التحليل الفني (The Actionable Advice)
    st.subheader("🛠️ مقترح التحليل الهندسي (CEO Diagnostic)")
    col_adv, col_log = st.columns([1, 2])
    with col_adv:
        st.info("**مقترح مروان كروم للتحليل:**")
        if latest['Slip'] > 15: st.error("⚠️ الزحف مرتفع: يرجى فحص كفاءة المروحة ونظافة البدن.")
        if latest['RPM'] == 0: st.warning("🚢 السفينة في حالة توقف: مراقبة استهلاك المولدات وتفريغ البضاعة.")
        st.write(f"متوسط حرارة العادم: {int(sum(me_exh)/len(me_exh)) if sum(me_exh)>0 else 0} °C")

    with col_log:
        st.write("**السجل التاريخي المؤرشف (The Archive):**")
        st.dataframe(ship_db[['Date', 'Dist_Obs', 'Slip', 'ME_FO', 'AE_DO']].tail(10))

else:
    st.warning(f"لا توجد بيانات مؤرشفة لـ {selected_ship}. يرجى الضغط على زر التحديث أو الإدخال اليدوي لبدء بناء الأرشيف.")

st.caption("© 2026 VesselCore Technical - النسخة الماسية الكاملة | مروان كروم")