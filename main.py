import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import imaplib, email, re, os
from datetime import datetime

# --- 1. الهوية الفنية والهيكل (CEO UI) ---
st.set_page_config(page_title="VesselCore Intelligence v27", layout="wide")
st.markdown("<style>.stMetric {background-color: #0e1117; border: 1px solid #30363d; padding: 20px; border-radius: 10px;}</style>", unsafe_allow_html=True)

DB_FILE = 'fleet_master_v27.csv'
FLEET = {"NJ MOON": 4.82, "NJ MARS": 5.10, "NJ AIO": 4.95, "YARA J": 4.75}

# --- 2. محرك القراءة العبقري (Smart Precision Parser) ---
def smart_extract(text):
    """محرك استخراج البيانات مع تنظيف آلي للنص"""
    clean = re.sub(r'\s+', ' ', text)
    extracted = {}
    
    patterns = {
        "Dist": r"(?:Dis|Distance|Dist).*?(\d+[\.]?\d*)",
        "RPM": r"(?:RPM|R\.P\.M).*?(\d+[\.]?\d*)",
        "FO": r"(?:Fuel oil|FO|M/E FO).*?(\d+[\.]?\d*)",
        "Slip": r"(?:Slip).*?([\-\d\.]+)%",
        "Speed": r"(?:Speed|Spd).*?(\d+[\.]?\d*)"
    }
    
    for key, p in patterns.items():
        match = re.search(p, clean, re.I)
        extracted[key] = float(match.group(1)) if match else 0.0
    
    # استخراج حرارات العادم (البحث عن نمط MAN B&W الحراري)
    exh_match = re.search(r"(?:TEMP|EXH).*?([\d\s,]{8,})", clean, re.I)
    extracted['Exh'] = exh_match.group(1).strip().replace(" ", ",") if exh_match else "0,0,0,0,0,0"
    
    return extracted

# --- 3. محرك المزامنة (The Bridge) ---
def fetch_fleet_data(app_pass):
    user = "marwankarroum3@gmail.com"
    final_records = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, app_pass)
        mail.select("inbox")
        _, msgs = mail.search(None, '(OR SUBJECT "Noon Report" SUBJECT "REPORT")')
        
        for num in msgs[0].split()[-12:]: # فحص آخر 12 تقرير
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors='ignore')
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')

            for s_name in FLEET.keys():
                if s_name in body.upper():
                    parsed = smart_extract(body)
                    parsed.update({"Ship": s_name, "Date": msg['Date'], "Raw": body[:200] + "..."})
                    final_records.append(parsed)
        return pd.DataFrame(final_records)
    except Exception as e:
        st.error(f"فشل الاتصال: {e}")
        return pd.DataFrame()

# --- 4. واجهة التحكم (Command Center) ---
with st.sidebar:
    st.title("🚢 VesselCore v27")
    st.write("**CEO: Marwan Karroum**")
    pwd = st.text_input("App Password:", type="password")
    if st.button("🔄 مزامنة الأسطول بالكامل"):
        df_new = fetch_fleet_data(pwd)
        if not df_new.empty:
            df_old = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame()
            pd.concat([df_old, df_new]).drop_duplicates(subset=['Date', 'Ship']).to_csv(DB_FILE, index=False)
            st.success("تم التحديث!")

st.title("🌐 Strategic Fleet Operations Dashboard")
if os.path.exists(DB_FILE):
    df_all = pd.read_csv(DB_FILE).fillna(0)
    ship = st.selectbox("اختر السفينة للتحليل الفني:", df_all['Ship'].unique())
    ship_data = df_all[df_all['Ship'] == ship].sort_values(by='Date')
    latest = ship_data.iloc[-1]
    
    # عرض الـ KPIs الأساسية
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance", f"{latest['Dist']} NM")
    c2.metric("Propeller Slip", f"{latest['Slip']}%", delta="Normal" if latest['Slip'] < 15 else "Critical")
    c3.metric("FO Consumption", f"{latest['FO']} MT")
    c4.metric("Average RPM", latest['RPM'])

    st.divider()

    # تبويبات التحليل الهندسي العميق
    t1, t2, t3 = st.tabs(["🔥 Engine Health", "📈 Operational Trends", "📝 Raw Data Audit"])
    
    with t1:
        st.subheader("Exhaust Gas Thermal Profile")
        
        try:
            t_list = [int(float(x)) for x in str(latest['Exh']).replace(',', ' ').split() if x.strip().isdigit()]
            if t_list:
                fig = go.Figure(go.Bar(x=[f"Cyl {i+1}" for i in range(len(t_list))], y=t_list, marker_color='#3498db', text=t_list, textposition='auto'))
                fig.update_layout(template="plotly_dark", height=350, yaxis_range=[0, 500])
                st.plotly_chart(fig, use_container_width=True)
        except: st.info("بيانات الحرارة قيد المعالجة...")

    with t2:
        st.subheader("Fuel & Speed Trend Analysis")
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=ship_data['Date'], y=ship_data['FO'], name="Fuel Cons (MT)", line=dict(color='#e74c3c')))
        fig_trend.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig_trend, use_container_width=True)

    with t3:
        st.subheader("Email Parsing Verification")
        st.info("هذا الجزء يظهر لك ما رآه البرنامج داخل الإيميل للتأكد من دقة النقل.")
        st.write(f"**آخر نص تم سحبه:** {latest['Raw']}")

else:
    st.warning("بانتظار سحب التقارير لبناء أرشيف الأسطول.")
