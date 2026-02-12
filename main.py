import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import imaplib, email, re, os
from datetime import datetime

# --- 1. إعدادات الاستقرار المطلق ---
st.set_page_config(page_title="VesselCore Intelligence", layout="wide")
st.markdown("<style>.stMetric {background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px;}</style>", unsafe_allow_html=True)

DB_FILE = 'fleet_vessel_master_db.csv'
FLEET_SPECS = {"NJ MOON": 4.82, "NJ MARS": 5.10, "NJ AIO": 4.95, "YARA J": 4.75}

def load_vessel_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE).fillna(0)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

# --- 2. محرك المسح المصفح (Safe Gmail Sync) ---
def parse_safe_body(msg):
    """حل مشكلة الـ NoneType والـ decode"""
    try:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload: return payload.decode(errors='ignore')
        else:
            payload = msg.get_payload(decode=True)
            if payload: return payload.decode(errors='ignore')
    except: return ""
    return ""

def sync_fleet_emails(app_pass):
    user = "marwankarroum3@gmail.com"
    new_records = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, app_pass)
        mail.select("inbox")
        _, msgs = mail.search(None, '(OR SUBJECT "Noon Report" SUBJECT "DAILY REPORT")')
        
        for num in msgs[0].split()[-10:]:
            _, d = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(d[0][1])
            body = parse_safe_body(msg)
            
            # محرك استخراج البيانات الذكي
            ship = re.search(r"(NJ MOON|NJ MARS|NJ AIO|YARA J)", body, re.I)
            if ship:
                ship_name = ship.group(1).upper()
                dist = re.search(r"Dis:\s*([\d\.]+)", body)
                rpm = re.search(r"R\.P\.M:\s*([\d\.]+)", body)
                fo = re.search(r"Fuel oil:.*?(\d+)", body, re.S)
                slip = re.search(r"Slip\s*([\-\d\.]+)%", body)
                exh = re.search(r"EXHT TEMP\s*([\d\s,]+)", body)
                
                new_records.append({
                    "Date": str(datetime.now().date()), "Ship": ship_name,
                    "Dist": float(dist.group(1)) if dist else 0.0,
                    "RPM": float(rpm.group(1)) if rpm else 0.0,
                    "FO": float(fo.group(1)) if fo else 0.0,
                    "Slip": float(slip.group(1)) if slip else 0.0,
                    "Exh": exh.group(1).strip().replace(" ", ",") if exh else "0,0,0,0,0,0"
                })
        return pd.DataFrame(new_records)
    except: return pd.DataFrame()

# --- 3. واجهة القيادة (Sidebar) ---
with st.sidebar:
    st.title("🚢 VesselCore Command")
    st.write(f"**Technical Director:** Marwan Karroum")
    pwd = st.text_input("App Password:", type="password")
    if st.button("🚀 تحديث الأرشيف آلياً"):
        with st.spinner("جاري جلب التقارير..."):
            df_new = sync_fleet_emails(pwd)
            if not df_new.empty:
                df_old = load_vessel_data()
                final_db = pd.concat([df_old, df_new]).drop_duplicates(subset=['Date', 'Ship'], keep='last')
                final_db.to_csv(DB_FILE, index=False)
                st.success("تم تحديث الأرشيف بنجاح!")
            else: st.warning("لم يتم العثور على بيانات جديدة في الإيميل.")

# --- 4. التحليل الهندسي (Master Dashboard) ---
st.title("🌐 Operations & Strategic Analysis")
df_master = load_vessel_data()

if not df_master.empty:
    ship_list = df_master['Ship'].unique()
    target_ship = st.selectbox("اختر السفينة للتحليل:", ship_list)
    ship_df = df_master[df_master['Ship'] == target_ship].sort_values(by='Date')
    latest = ship_df.iloc[-1]
    
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance", f"{latest['Dist']} NM")
    c2.metric("Propeller Slip", f"{latest['Slip']}%")
    c3.metric("Fuel Cons.", f"{latest['FO']} MT")
    c4.metric("RPM", latest['RPM'])

    st.divider()

    # حل مشكلة ValueError في درجات الحرارة
    st.subheader("🔥 Exhaust Temperatures & Combustion")
    try:
        exh_str = str(latest.get('Exh', "0,0,0,0,0,0"))
        # تنظيف النص وتحويله لقائمة أرقام بأمان
        raw_temps = re.split(r'[,\s]+', exh_str)
        temps = []
        for x in raw_temps:
            try:
                if x.strip(): temps.append(int(float(x)))
            except: continue
        
        if temps:
            fig = go.Figure(go.Bar(x=[f"C{i+1}" for i in range(len(temps))], y=temps, marker_color='#3498db'))
            fig.update_layout(template="plotly_dark", height=300)
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("بيانات الحرارة غير مكتملة في التقرير.")
    except: st.error("خطأ في قراءة بيانات الحرارة.")

    st.subheader("⛽ Fuel Consumption Trend")
    fig_f = go.Figure(go.Scatter(x=ship_df['Date'], y=ship_df['FO'], name="ME FO", line=dict(color='#e74c3c', width=3)))
    fig_f.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig_f, use_container_width=True)
else:
    st.warning("بانتظار سحب أول تقرير لبناء الأرشيف من إيميل Marwankarroum3@gmail.com")
