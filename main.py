import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import imaplib, email, re, os
from datetime import datetime

# --- 1. الهوية السيادية والوقاية من الانهيار ---
st.set_page_config(page_title="VesselCore Intelligence OS", layout="wide")
st.markdown("<style>.stMetric {background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px;}</style>", unsafe_allow_html=True)

DB_FILE = 'vessel_fleet_archive_final.csv'
FLEET_SPECS = {"NJ MOON": 4.82, "NJ MARS": 5.10, "NJ AIO": 4.95, "YARA J": 4.75}

# بيانات حقيقية محملة مسبقاً (لتجنب لوحة التحكم الفارغة)
def get_initial_df():
    data = [
        {"Date": "2026-02-12", "Ship": "NJ MOON", "Dist": 233.7, "RPM": 102.0, "FO": 21.0, "Slip": 19.29, "Exh": "350,360,370,355,365,360"},
        {"Date": "2026-02-11", "Ship": "NJ MARS", "Dist": 0.0, "RPM": 0.0, "FO": 0.0, "Slip": 0.0, "Exh": "0,0,0,0,0,0"},
        {"Date": "2026-02-11", "Ship": "NJ AIO", "Dist": 0.0, "RPM": 0.0, "FO": 0.0, "Slip": 0.0, "Exh": "0,0,0,0,0,0"}
    ]
    return pd.DataFrame(data)

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        return df.fillna(0)
    return get_initial_df()

# --- 2. محرك المسح الدفاعي (Safe Gmail Sync) ---
def safe_sync(app_pass):
    user = "marwankarroum3@gmail.com"
    new_data = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, app_pass)
        mail.select("inbox")
        _, msgs = mail.search(None, '(OR SUBJECT "Noon Report" SUBJECT "DAILY REPORT")')
        
        for num in msgs[0].split()[-10:]:
            _, d = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(d[0][1])
            # حل مشكلة الـ decode
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        body = payload.decode(errors='ignore') if payload else ""
            else:
                payload = msg.get_payload(decode=True)
                body = payload.decode(errors='ignore') if payload else ""

            # استخراج البيانات (الماسح الذكي)
            ship = re.search(r"(NJ MOON|NJ MARS|NJ AIO|YARA J)", body, re.I)
            if ship:
                ship_name = ship.group(1).upper()
                dist = re.search(r"Dis:\s*([\d\.]+)", body)
                rpm = re.search(r"R\.P\.M:\s*([\d\.]+)", body)
                fo = re.search(r"Fuel oil:.*?(\d+)", body, re.S)
                slip = re.search(r"Slip\s*([\-\d\.]+)%", body)
                exh = re.search(r"EXHT TEMP\s*([\d\s,]+)", body)
                
                new_data.append({
                    "Date": str(datetime.now().date()), "Ship": ship_name,
                    "Dist": float(dist.group(1)) if dist else 0.0,
                    "RPM": float(rpm.group(1)) if rpm else 0.0,
                    "FO": float(fo.group(1)) if fo else 0.0,
                    "Slip": float(slip.group(1)) if slip else 0.0,
                    "Exh": exh.group(1).strip().replace(" ", ",") if exh else "0,0,0,0,0,0"
                })
        return pd.DataFrame(new_data)
    except: return pd.DataFrame()

# --- 3. واجهة التحكم (Command Center) ---
with st.sidebar:
    st.title("🚢 VesselCore Command")
    st.write(f"**CEO:** Marwan Karroum")
    pwd = st.text_input("App Password:", type="password")
    if st.button("🚀 تحديث الأسطول آلياً"):
        df_new = safe_sync(pwd)
        if not df_new.empty:
            df_old = load_data()
            final = pd.concat([df_old, df_new]).drop_duplicates(subset=['Date', 'Ship'], keep='last')
            final.to_csv(DB_FILE, index=False)
            st.success("تم التحديث بنجاح!")
        else: st.warning("لم نجد بيانات جديدة، تم استخدام الأرشيف الحالي.")

# --- 4. العرض والتحليل (The Master Dashboard) ---
st.title("🌐 Fleet Strategic Analysis")
df_master = load_data()
ship = st.selectbox("اختر السفينة للتحليل:", list(FLEET_SPECS.keys()))
ship_df = df_master[df_master['Ship'] == ship]

if not ship_df.empty:
    latest = ship_df.iloc[-1]
    
    # مقاييس الأداء (KPIs)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance", f"{latest['Dist']} NM")
    c2.metric("Propeller Slip", f"{latest['Slip']}%", delta="Critical" if latest['Slip'] > 15 else "Normal")
    c3.metric("Fuel Consumption", f"{latest['FO']} MT")
    c4.metric("Engine RPM", latest['RPM'])

    st.divider()
    
    # حل مشكلة الـ ValueError في درجات الحرارة
    st.subheader("🔥 Exhaust Temperatures & Combustion")
    try:
        exh_str = str(latest['Exh']).replace(' ', ',')
        temps = [int(float(x)) for x in re.split(r'[,\s]+', exh_str) if x]
        if temps:
            st.plotly_chart(go.Figure(go.Bar(x=[f"C1" for i in range(len(temps))], y=temps, marker_color='#3498db')), use_container_width=True)
        else: st.info("بيانات الحرارة غير متوفرة لهذا التقرير.")
    except: st.info("بيانات الحرارة قيد المعالجة.")
    
    st.subheader("📂 التاريخ المؤرشف (Verified History)")
    st.dataframe(ship_df.sort_values(by='Date', ascending=False))
else:
    st.warning(f"لا توجد بيانات مؤرشفة لـ {ship} بعد.")
