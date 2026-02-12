import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import imaplib, email, re, os
from datetime import datetime

# --- 1. الهوية الفنية لغرفة التحكم ---
st.set_page_config(page_title="VesselCore Chief Intelligence", layout="wide")
st.markdown("<style>.stMetric {background-color: #0e1117; border: 1px solid #30363d; padding: 20px; border-radius: 10px;}</style>", unsafe_allow_html=True)

DB_FILE = 'vessel_master_v29.csv'
FLEET = {"NJ MOON": 4.82, "NJ MARS": 5.10, "NJ AIO": 4.95, "YARA J": 4.75}

# --- 2. محرك القراءة "الفولاذي" (The Chief's Parser) ---
def robust_extract(keyword, text):
    """مستشعر مرن يبحث عن الرقم الأول بعد الكلمة المفتاحية"""
    try:
        pattern = rf"{keyword}.*?(\d+[\.]?\d*)"
        match = re.search(pattern, text, re.I | re.S)
        return float(match.group(1)) if match else 0.0
    except: return 0.0

def get_body_safe(msg):
    """فك تشفير الإيميل بأمان لمنع انهيار البرنامج"""
    try:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    return payload.decode(errors='ignore') if payload else ""
        payload = msg.get_payload(decode=True)
        return payload.decode(errors='ignore') if payload else ""
    except: return ""

# --- 3. محرك المزامنة والأرشفة ---
with st.sidebar:
    st.title("🚢 Chief's Command")
    pwd = st.text_input("App Password:", type="password")
    if st.button("🚀 مزامنة الأسطول بالكامل"):
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login("marwankarroum3@gmail.com", pwd)
            mail.select("inbox")
            _, msgs = mail.search(None, '(OR SUBJECT "Noon Report" SUBJECT "REPORT")')
            
            records = []
            for num in msgs[0].split()[-10:]:
                _, d = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(d[0][1])
                body = get_body_safe(msg)
                
                for ship in FLEET.keys():
                    if ship in body.upper():
                        data = {
                            "Date": str(datetime.now().date()), "Ship": ship,
                            "Dist": robust_extract(r"Dis|Distance", body),
                            "RPM": robust_extract(r"RPM|R\.P\.M", body),
                            "FO": robust_extract(r"Fuel|FO", body),
                            "Slip": robust_extract(r"Slip", body),
                            "Raw": body[:400] # لحل مشكلة Audit
                        }
                        # استخراج الحرارات (MAN B&W Pattern)
                        exh = re.search(r"(?:TEMP|EXH).*?([\d\s,]{8,})", body, re.I | re.S)
                        data['Exh'] = exh.group(1).strip().replace(" ", ",") if exh else "0,0,0,0,0,0"
                        records.append(data)
            
            if records:
                new_df = pd.DataFrame(records)
                old_df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame()
                pd.concat([old_df, new_df]).drop_duplicates(subset=['Date', 'Ship']).to_csv(DB_FILE, index=False)
                st.success("تم تحديث الأرشيف بنجاح!")
        except Exception as e: st.error(f"عطل في المزامنة: {e}")

# --- 4. لوحة القيادة والتحليل الهندسي ---
st.title("🌐 Fleet Strategic Operations & Diagnostics")
if os.path.exists(DB_FILE):
    df_all = pd.read_csv(DB_FILE).fillna(0)
    target = st.selectbox("اختر السفينة:", df_all['Ship'].unique())
    latest = df_all[df_all['Ship'] == target].iloc[-1]
    
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance", f"{latest['Dist']} NM")
    c2.metric("Propeller Slip", f"{latest['Slip']}%", delta="Normal" if latest['Slip'] < 15 else "High")
    c3.metric("Fuel Cons.", f"{latest['FO']} MT")
    c4.metric("Engine RPM", latest['RPM'])

    st.divider()
    t1, t2 = st.tabs(["🔥 Engine Combustion", "📝 Raw Data Audit"])
    with t1:
        try:
            exh_raw = str(latest.get('Exh', "0,0,0,0,0,0")).replace(',', ' ')
            temps = [int(float(x)) for x in exh_raw.split() if x.strip().replace('.','').isdigit()]
            if temps:
                st.plotly_chart(go.Figure(go.Bar(x=[f"C{i+1}" for i in range(len(temps))], y=temps, marker_color='#3498db', text=temps, textposition='auto')))
        except: st.info("بيانات الحرارة قيد التحديث...")
    with t2:
        st.subheader("تحليل النص المستخرج")
        st.code(latest['Raw'])
else: st.warning("بانتظار سحب التقارير لبناء الأرشيف.")
