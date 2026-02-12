import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import imaplib, email, re, os
from datetime import datetime

# --- 1. الهوية السيادية (UI) ---
st.set_page_config(page_title="VesselCore Intelligence", layout="wide")
st.markdown("<style>.stMetric {background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px;}</style>", unsafe_allow_html=True)

DB_FILE = 'vessel_master_data_v23.csv'
FLEET = {"NJ MOON": 4.82, "NJ MARS": 5.10, "NJ AIO": 4.95, "YARA J": 4.75}

# --- 2. محرك التطهير والقراءة العميق (Deep Vision Parser) ---
def clean_and_parse(text, ship_name):
    data = {"Ship": ship_name, "Date": str(datetime.now().date())}
    # تنظيف النص من الرموز الغريبة والمساحات الزائدة
    clean_text = re.sub(r'\s+', ' ', text)
    
    # مستشعرات مرنة جداً (Flexible Sensors)
    patterns = {
        "Dist": r"(?:Dis|Distance|Dist).*?(\d+[\.]?\d*)",
        "RPM": r"(?:R\.P\.M|RPM).*?(\d+[\.]?\d*)",
        "Speed": r"(?:Speed|Spd).*?(\d+[\.]?\d*)",
        "FO": r"(?:Fuel oil|FO|Consumption).*?(\d+[\.]?\d*)",
        "Slip": r"(?:Slip).*?([\-\d\.]+)%",
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, clean_text, re.I)
        data[key] = float(match.group(1)) if match else 0.0
    
    # استخراج حرارات العادم (Cyl 1-6)
    exh_match = re.search(r"(?:TEMP|EXHT).*?([\d\s,]{10,})", clean_text, re.I)
    data['Exh'] = exh_match.group(1).strip().replace(" ", ",") if exh_match else "0,0,0,0,0,0"
    
    return data

# --- 3. محرك الاتصال بـ Gmail ---
def sync_emails(app_pass):
    user = "marwankarroum3@gmail.com"
    records = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, app_pass)
        mail.select("inbox")
        _, msgs = mail.search(None, '(OR SUBJECT "Noon Report" SUBJECT "REPORT")')
        
        for num in msgs[0].split()[-10:]: # آخر 10 إيميلات
            _, d = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(d[0][1])
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors='ignore')
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')

            for s_name in FLEET.keys():
                if s_name in body.upper():
                    parsed = clean_and_parse(body, s_name)
                    if parsed: records.append(parsed)
        return pd.DataFrame(records)
    except Exception as e:
        st.error(f"فشل في الاتصال أو القراءة: {e}")
        return pd.DataFrame()

# --- 4. واجهة التحكم ---
with st.sidebar:
    st.title("🚢 VesselCore v23")
    pwd = st.text_input("App Password:", type="password")
    if st.button("🚀 تحديث وتحليل البيانات"):
        new_df = sync_emails(pwd)
        if not new_df.empty:
            if os.path.exists(DB_FILE):
                old_df = pd.read_csv(DB_FILE)
                new_df = pd.concat([old_df, new_df]).drop_duplicates(subset=['Date', 'Ship'], keep='last')
            new_df.to_csv(DB_FILE, index=False)
            st.success("تمت القراءة والأرشفة بنجاح!")

# --- 5. العرض والتحليل الهندسي ---
st.title("🌐 Fleet Strategic Analysis & Operations")
if os.path.exists(DB_FILE):
    df_master = pd.read_csv(DB_FILE).fillna(0)
    ship = st.selectbox("اختر السفينة للتحليل:", df_master['Ship'].unique())
    latest = df_master[df_master['Ship'] == ship].iloc[-1]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance", f"{latest['Dist']} NM")
    c2.metric("Propeller Slip", f"{latest['Slip']}%", delta="High" if latest['Slip'] > 15 else "Normal")
    c3.metric("Fuel Cons.", f"{latest['FO']} MT")
    c4.metric("Engine RPM", latest['RPM'])

    st.divider()
    
    # تحليل الاحتراق (Exhaust Map)
    st.subheader("🔥 Exhaust Thermal Balance (Cyl 1-6)")
    try:
        t_str = str(latest.get('Exh', "0,0,0,0,0,0")).replace(',', ' ')
        temps = [int(float(x)) for x in t_str.split() if x.strip().replace('.','').isdigit()]
        if temps:
            st.plotly_chart(go.Figure(go.Bar(x=[f"C{i+1}" for i in range(len(temps))], y=temps, marker_color='#3498db')), use_container_width=True)
    except: st.info("بيانات الحرارة قيد التحديث.")
else:
    st.warning("بانتظار سحب التقارير لبناء قاعدة البيانات.")
