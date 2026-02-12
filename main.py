import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import imaplib, email, re, os
from datetime import datetime

# --- 1. الهوية السيادية والوقاية من الانهيار (UI) ---
st.set_page_config(page_title="VesselCore Intelligence OS", layout="wide")
st.markdown("<style>.stMetric {background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #444;}</style>", unsafe_allow_html=True)

DB_FILE = 'vessel_master_db_v24.csv'
FLEET = {"NJ MOON": 4.82, "NJ MARS": 5.10, "NJ AIO": 4.95, "YARA J": 4.75}

# --- 2. محرك البحث "المُصفح" (Indestructible Parser) ---
def safe_extract(pattern, text, default=0.0):
    """يمنع خطأ Attribute 'group'"""
    try:
        match = re.search(pattern, text, re.I | re.S)
        return float(match.group(1)) if match else default
    except: return default

def safe_decode(msg):
    """يمنع خطأ 'NoneType' object has no attribute 'decode'"""
    try:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    return payload.decode(errors='ignore') if payload else ""
        else:
            payload = msg.get_payload(decode=True)
            return payload.decode(errors='ignore') if payload else ""
    except: return ""
    return ""

# --- 3. محرك المزامنة الذكي (Master Sync) ---
def sync_fleet_v24(app_pass):
    user = "marwankarroum3@gmail.com"
    new_data = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, app_pass)
        mail.select("inbox")
        _, msgs = mail.search(None, '(OR SUBJECT "Noon Report" SUBJECT "REPORT")')
        
        for num in msgs[0].split()[-15:]: # فحص آخر 15 تقرير
            _, d = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(d[0][1])
            body = safe_decode(msg)
            
            for ship in FLEET.keys():
                if ship in body.upper():
                    new_data.append({
                        "Date": str(datetime.now().date()), "Ship": ship,
                        "Dist": safe_extract(r"Dis.*?([\d\.]+)", body),
                        "RPM": safe_extract(r"R.*?P.*?M.*?([\d\.]+)", body),
                        "Speed": safe_extract(r"Speed.*?([\d\.]+)", body),
                        "FO": safe_extract(r"Fuel.*?oil.*?([\d\.]+)", body),
                        "Slip": safe_extract(r"Slip.*?([\-\d\.]+)%", body),
                        "Exh": re.search(r"TEMP\s*([\d\s,]+)", body).group(1).strip() if re.search(r"TEMP", body) else "0,0,0,0,0,0"
                    })
        return pd.DataFrame(new_data)
    except: return pd.DataFrame()

# --- 4. واجهة التحكم والعرض ---
with st.sidebar:
    st.title("🚢 VesselCore v24")
    st.write(f"**CEO:** Marwan Karroum")
    pwd = st.text_input("App Password:", type="password")
    if st.button("🚀 تحديث الأسطول والتحليل الهندسي"):
        df_new = sync_fleet_v24(pwd)
        if not df_new.empty:
            df_old = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame()
            pd.concat([df_old, df_new]).drop_duplicates(subset=['Date', 'Ship']).to_csv(DB_FILE, index=False)
            st.success("تم تحديث الأرشيف بنجاح!")

st.title("🌐 Strategic Fleet Intelligence")
if os.path.exists(DB_FILE):
    df_master = pd.read_csv(DB_FILE).fillna(0)
    target = st.selectbox("اختر السفينة للتشخيص:", df_master['Ship'].unique())
    ship_df = df_master[df_master['Ship'] == target]
    latest = ship_df.iloc[-1]
    
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance", f"{latest['Dist']} NM")
    c2.metric("Propeller Slip", f"{latest['Slip']}%")
    c3.metric("Fuel Consumption", f"{latest['FO']} MT")
    c4.metric("Average RPM", latest['RPM'])

    st.divider()
    
    # تحليل الاحتراق (حل خطأ ValueError)
    st.subheader("🔥 Engine Combustion Map (All Units)")
        try:
        raw_exh = str(latest.get('Exh', "0,0,0,0,0,0")).replace(',', ' ')
        temps = [int(float(x)) for x in raw_exh.split() if x.strip().replace('.','').isdigit()]
        if temps:
            fig = go.Figure(go.Bar(x=[f"C{i+1}" for i in range(len(temps))], y=temps, marker_color='#3498db', text=temps, textposition='auto'))
            fig.update_layout(template="plotly_dark", height=300, yaxis_range=[0, 500])
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("بيانات الحرارة غير مكتملة في هذا التقرير.")
    except: st.error("خطأ فني في عرض درجات الحرارة.")

    st.subheader("📂 التاريخ الفني المؤرشف")
    st.dataframe(ship_df.sort_values(by='Date', ascending=False), use_container_width=True)
else:
    st.info("بانتظار سحب أول تقرير لبناء الأرشيف التاريخي.")
