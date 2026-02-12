import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import imaplib, email, re, os
from datetime import datetime

# --- 1. الهوية السيادية والوقاية من الانهيار (UI) ---
st.set_page_config(page_title="VesselCore Absolute v22", layout="wide")
st.markdown("<style>.stMetric {background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px;}</style>", unsafe_allow_html=True)

DB_FILE = 'vessel_master_db_v22.csv'
FLEET = {"NJ MOON": 4.82, "NJ MARS": 5.10, "NJ AIO": 4.95, "YARA J": 4.75}

# --- 2. محرك البحث الآمن (The Safe Regex Engine) ---
def safe_search(pattern, text, default=0.0):
    """يمنع خطأ 'NoneType' object has no attribute 'group'"""
    match = re.search(pattern, text, re.I | re.S)
    if match:
        try: return float(match.group(1))
        except: return default
    return default

# --- 3. محرك فك التشفير الصامد (Anti-Decode Error) ---
def get_email_content(msg):
    """حل مشكلة الـ NoneType والـ decode"""
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

# --- 4. محرك المزامنة الذكي (Master Sync) ---
def sync_fleet(app_pass):
    user = "marwankarroum3@gmail.com"
    new_records = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, app_pass)
        mail.select("inbox")
        _, msgs = mail.search(None, '(OR SUBJECT "Noon Report" SUBJECT "REPORT")')
        
        for num in msgs[0].split()[-10:]: # آخر 10 تقارير
            _, d = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(d[0][1])
            body = get_email_content(msg)
            
            for ship in FLEET.keys():
                if ship in body.upper():
                    new_records.append({
                        "Date": str(datetime.now().date()), "Ship": ship,
                        "Dist": safe_search(r"Dis.*?([\d\.]+)", body),
                        "RPM": safe_search(r"R.*?P.*?M.*?([\d\.]+)", body),
                        "FO": safe_search(r"Fuel.*?oil.*?([\d\.]+)", body),
                        "Slip": safe_search(r"Slip.*?([\-\d\.]+)%", body),
                        "Exh": re.search(r"TEMP\s*([\d\s,]+)", body).group(1).strip() if re.search(r"TEMP", body) else "0,0,0,0,0,0"
                    })
        return pd.DataFrame(new_records)
    except: return pd.DataFrame()

# --- 5. واجهة التحكم والعرض الفني ---
with st.sidebar:
    st.title("🚢 VesselCore Command")
    st.write(f"**CEO:** Marwan Karroum")
    pwd = st.text_input("App Password:", type="password")
    if st.button("🚀 تحديث الأسطول آلياً"):
        df_new = sync_fleet(pwd)
        if not df_new.empty:
            df_old = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame()
            pd.concat([df_old, df_new]).drop_duplicates(subset=['Date', 'Ship']).to_csv(DB_FILE, index=False)
            st.success("تم التحديث بنجاح!")

st.title("🌐 Operations & Strategic Analysis")
if os.path.exists(DB_FILE):
    df_master = pd.read_csv(DB_FILE).fillna(0)
    target = st.selectbox("اختر السفينة:", df_master['Ship'].unique())
    ship_df = df_master[df_master['Ship'] == target]
    latest = ship_df.iloc[-1]
    
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance", f"{latest['Dist']} NM")
    c2.metric("Propeller Slip", f"{latest['Slip']}%", delta="Critical" if latest['Slip'] > 15 else "Normal")
    c3.metric("Fuel Cons.", f"{latest['FO']} MT")
    c4.metric("RPM", latest['RPM'])

    # الرسم البياني للعوادم (حل خطأ ValueError)
    st.subheader("🔥 Exhaust Thermal Balance")
    try:
        raw_exh = str(latest.get('Exh', "0,0,0,0,0,0")).replace(',', ' ')
        temps = [int(float(x)) for x in raw_exh.split() if x.strip().replace('.','').isdigit()]
        if temps:
            st.plotly_chart(go.Figure(go.Bar(x=[f"C{i+1}" for i in range(len(temps))], y=temps, marker_color='#3498db')), use_container_width=True)
    except: st.info("بيانات الحرارة قيد التحديث.")
    
    st.subheader("📂 السجل التاريخي")
    st.dataframe(ship_df.sort_values(by='Date', ascending=False))
else:
    st.info("بانتظار سحب أول تقرير لبناء الأرشيف.")
