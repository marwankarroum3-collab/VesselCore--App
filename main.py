import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import imaplib, email, re, os
from datetime import datetime

# --- 1. واجهة القيادة (UI) ---
st.set_page_config(page_title="VesselCore Absolute Intelligence", layout="wide")
st.markdown("<style>.stMetric {background-color: #111; border: 1px solid #444; padding: 15px; border-radius: 10px;}</style>", unsafe_allow_html=True)

DB_FILE = 'vessel_fleet_final_db.csv'
FLEET = {"NJ MOON": 4.82, "NJ MARS": 5.10, "NJ AIO": 4.95, "YARA J": 4.75}

# --- 2. محرك القراءة "الفولاذي" (The Steel Parser) ---
def ultra_parse(text):
    data = {}
    # تنظيف النص كلياً قبل البحث
    clean_text = re.sub(r'\s+', ' ', text)
    
    # محاولة استخراج القيم بمرونة قصوى (Flexible Regex)
    patterns = {
        "Dist": r"(?:Dis|Distance|Dist).*?(\d+[\.]?\d*)",
        "RPM": r"(?:RPM|R\.P\.M).*?(\d+[\.]?\d*)",
        "Speed": r"(?:Speed|Spd).*?(\d+[\.]?\d*)",
        "FO": r"(?:Fuel oil|FO|Consumption).*?(\d+[\.]?\d*)",
        "Slip": r"(?:Slip).*?([\-\d\.]+)%",
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, clean_text, re.I)
        data[key] = float(match.group(1)) if match else 0.0
    
    # استخراج حرارات العوادم (البحث عن سلسلة أرقام متتالية)
    exh_match = re.search(r"(?:TEMP|EXHT|EXH).*?([\d\s,]{8,})", clean_text, re.I)
    data['Exh'] = exh_match.group(1).strip().replace(" ", ",") if exh_match else "0,0,0,0,0,0"
    
    return data

# --- 3. محرك المزامنة (Gmail Bridge) ---
def sync_emails_v26(app_pass):
    user = "marwankarroum3@gmail.com"
    results = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, app_pass)
        mail.select("inbox")
        _, msgs = mail.search(None, '(OR SUBJECT "Noon Report" SUBJECT "REPORT")')
        
        for num in msgs[0].split()[-10:]:
            _, d = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(d[0][1])
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors='ignore')
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')

            for ship in FLEET.keys():
                if ship in body.upper():
                    parsed = ultra_parse(body)
                    parsed.update({"Ship": ship, "Date": msg['Date']})
                    results.append(parsed)
        return pd.DataFrame(results)
    except Exception as e:
        st.error(f"عطل تقني: {e}")
        return pd.DataFrame()

# --- 4. العرض الفني والتحليلي ---
with st.sidebar:
    st.title("🚢 VesselCore v26")
    pwd = st.text_input("App Password:", type="password")
    if st.button("🚀 مزامنة وتحليل الأسطول"):
        new_df = sync_emails_v26(pwd)
        if not new_df.empty:
            df_old = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame()
            pd.concat([df_old, new_df]).drop_duplicates(subset=['Date', 'Ship']).to_csv(DB_FILE, index=False)
            st.success("تم التحديث!")

st.title("🌐 Operations & Strategic Analysis Dashboard")

if os.path.exists(DB_FILE):
    df_master = pd.read_csv(DB_FILE).fillna(0)
    target = st.selectbox("اختر السفينة للتحليل:", df_master['Ship'].unique())
    latest = df_master[df_master['Ship'] == target].iloc[-1]
    
    # لوحة الـ KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance", f"{latest['Dist']} NM")
    c2.metric("Propeller Slip", f"{latest['Slip']}%", delta="Critical" if latest['Slip'] > 15 else "Normal")
    c3.metric("Fuel Consumption", f"{latest['FO']} MT")
    c4.metric("Average RPM", latest['RPM'])

    st.divider()
    
    # تحليل الحريق (Exhaust Map)
    st.subheader("🔥 Exhaust Thermal Profile (Cyl 1-6)")
    try:
        t_data = str(latest['Exh']).replace(',', ' ').split()
        temps = [int(float(x)) for x in t_data if x.strip().replace('.','').isdigit()]
        if temps:
            st.plotly_chart(go.Figure(go.Bar(x=[f"C{i+1}" for i in range(len(temps))], y=temps, marker_color='#3498db')), use_container_width=True)
    except: st.info("بيانات الحرارة قيد المعالجة...")
    
    st.subheader("📂 التاريخ الفني المؤرشف")
    st.dataframe(df_master[df_master['Ship'] == target].sort_values(by='Date', ascending=False))
else:
    st.warning("بانتظار سحب التقارير لبناء الأرشيف من Marwankarroum3@gmail.com")
