import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import datetime

# --- 1. إعدادات الهوية السيادية ---
st.set_page_config(page_title="VesselCore Enterprise OS", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    h1, h2, h3 { color: #58a6ff; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك الأرشفة والبيانات الثابتة (Archive Engine) ---
DB_FILE = 'vessel_core_archive.csv'

# مواصفات السفن الثابتة (لن تتغير)
FLEET_SPECS = {
    "NJ MOON": {"Engine": "MAN B&W 6S50MC-C", "Pitch": 4.82, "Cyl": 6},
    "NJ MARS": {"Engine": "MAN B&W 6S60MC-C", "Pitch": 5.10, "Cyl": 6},
    "NJ AIO": {"Engine": "Mitsubishi UEC", "Pitch": 4.95, "Cyl": 6},
    "YARA J": {"Engine": "MAN B&W 5S50MC-C", "Pitch": 4.75, "Cyl": 5}
}

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    return pd.DataFrame(columns=['Date', 'Ship', 'Dist_Obs', 'RPM', 'ME_FO', 'AE_DO', 'Cyl_LO', 'Gen_LO', 'Slip', 'ME_Exh', 'AE_Exh'])

df_archive = load_data()

# --- 3. محرك التحليل الهندسي (Engineering Diagnostic) ---
def calc_slip(rpm, pitch, dist_obs):
    if rpm == 0 or dist_obs == 0: return 0.0
    dist_eng = (rpm * 60 * 24 * pitch) / 1852
    return round(((dist_eng - dist_obs) / dist_eng) * 100, 2)

# --- 4. واجهة إدخال البيانات (Data Entry Sidebar) ---
with st.sidebar:
    st.title("🚢 VesselCore Command")
    st.write(f"**Technical Director:** Marwan Karroum")
    
    with st.expander("📝 إدخال تقرير نون (Archive Input)"):
        s_ship = st.selectbox("السفينة:", list(FLEET_SPECS.keys()))
        s_date = st.date_input("تاريخ التقرير:", datetime.now())
        s_dist = st.number_input("Dist Observed (NM):", 0.0)
        s_rpm = st.number_input("Average RPM:", 0.0)
        s_fo = st.number_input("ME Fuel (MT):", 0.0)
        s_do = st.number_input("Gen Fuel (MT):", 0.0)
        s_cyl = st.number_input("Cylinder Oil (L):", 0)
        s_gen_lo = st.number_input("Generator Oil (L):", 0)
        
        # إدخال درجات الحرارة (كمثال مبسط)
        s_me_exh = st.text_input("ME Exh (C1,C2...):", "340,340,340,340,340,340")
        s_ae_exh = st.text_input("Gen Exh (U1,U2...):", "320,320,320,320,320")

        if st.button("حفظ وأرشفة البيانات"):
            slip_v = calc_slip(s_rpm, FLEET_SPECS[s_ship]['Pitch'], s_dist)
            new_entry = {
                'Date': s_date, 'Ship': s_ship, 'Dist_Obs': s_dist, 'RPM': s_rpm,
                'ME_FO': s_fo, 'AE_DO': s_do, 'Cyl_LO': s_cyl, 'Gen_LO': s_gen_lo,
                'Slip': slip_v, 'ME_Exh': s_me_exh, 'AE_Exh': s_ae_exh
            }
            df_archive = pd.concat([df_archive, pd.DataFrame([new_entry])], ignore_index=True)
            df_archive.to_csv(DB_FILE, index=False)
            st.success(f"تمت أرشفة بيانات {s_ship} بنجاح!")

# --- 5. لوحة العرض والتحليل (The Master Dashboard) ---
st.title("🌐 Operations & Strategic Analysis")
target_ship = st.selectbox("عرض سجلات السفينة:", list(FLEET_SPECS.keys()))
ship_db = df_archive[df_archive['Ship'] == target_ship].sort_values(by='Date')

if not ship_db.empty:
    latest = ship_db.iloc[-1]
    
    # مقاييس الأداء العليا
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance Run", f"{latest['Dist_Obs']} NM")
    c2.metric("Propeller Slip", f"{latest['Slip']}%", delta="Normal" if latest['Slip'] < 15 else "High")
    c3.metric("Fuel Consumption (Total)", f"{latest['ME_FO'] + latest['AE_DO']} MT")
    c4.metric("Cylinder Oil Rate", f"{latest['Cyl_LO']} L")

    st.divider()

    # الرسوم البيانية (Trends)
    t1, t2 = st.columns(2)
    with t1:
        # تريند استهلاك الوقود والزيوت
        fig_f = go.Figure()
        fig_f.add_trace(go.Scatter(x=ship_db['Date'], y=ship_db['ME_FO'], name="ME FO", line=dict(color='#3498db')))
        fig_f.add_trace(go.Scatter(x=ship_db['Date'], y=ship_db['Cyl_LO'], name="Cyl Oil", line=dict(color='#00ff00')))
        fig_f.update_layout(template="plotly_dark", title="Consumption Trend (Fuel & Oil)")
        st.plotly_chart(fig_f, use_container_width=True)

    with t2:
        # تريند حريق المولدات (Exhaust Analysis)
        ae_vals = [int(x) for x in str(latest['AE_Exh']).split(',')]
        fig_ae = go.Figure(go.Bar(x=[f"U{i+1}" for i in range(len(ae_vals))], y=ae_vals, marker_color='#e67e22'))
        fig_ae.update_layout(template="plotly_dark", title="Aux Engine Exhaust Profile")
        st.plotly_chart(fig_ae, use_container_width=True)

    st.divider()

    # مقترح التحليل الفني
    st.subheader("🛠️ Technical Proposal & Diagnostic")
    col_p, col_d = st.columns(2)
    with col_p:
        st.write("**مقترح CEO للتحليل:**")
        if latest['Slip'] > 15: st.warning("⚠️ Slip High: انخفاض كفاءة الملاحة، يرجى مراجعة حالة البحر أو نظافة المروحة.")
        if latest['ME_FO'] > 0: st.info(f"كفاءة الاحتراق: متوسط حرارة العادم مستقر.")
    
    with col_d:
        st.write("**سجل الأرشفة (Archive History):**")
        st.dataframe(ship_db[['Date', 'Dist_Obs', 'Slip', 'ME_FO', 'AE_DO']].tail(5))

else:
    st.warning(f"لا توجد بيانات مؤرشفة لـ {target_ship}. يرجى إدخال أول تقرير نون من القائمة الجانبية.")

st.caption("© 2026 VesselCore Technical - النسخة السيادية الكاملة | مروان كروم")