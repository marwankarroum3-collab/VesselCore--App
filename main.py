import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import imaplib, email, re, os

# --- 1. الهوية السيادية (VesselCore Master UI) ---
st.set_page_config(page_title="VesselCore Intelligence", layout="wide")
st.markdown("<style>.stMetric {background-color: #111; border: 1px solid #444; padding: 15px; border-radius: 10px;}</style>", unsafe_allow_html=True)

DB_FILE = 'vessel_master_secure_v19.csv'
FLEET = {"NJ MOON": 4.82, "NJ MARS": 5.10, "NJ AIO": 4.95, "YARA J": 4.75}

# --- 2. محرك الأرشفة الصامد (Persistence Engine) ---
def load_vessel_db():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE).fillna(0)
    return pd.DataFrame()

# --- 3. محرك المسح "الحجري" الصامد (Resilient Parser) ---
def get_safe_text(msg):
    try:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode(errors='ignore')
        return msg.get_payload(decode=True).decode(errors='ignore')
    except: return ""

def sync_gmail_secure(app_pass):
    user = "marwankarroum3@gmail.com"
    data_found = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, app_pass)
        mail.select("inbox")
        _, msgs = mail.search(None, '(OR SUBJECT "Noon Report" SUBJECT "REPORT")')
        
        for num in msgs[0].split()[-12:]: # فحص آخر 12 تقرير
            _, d = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(d[0][1])
            body = get_safe_text(msg)
            
            # محرك التعرف المرن (Flexible Extraction)
            for ship in FLEET.keys():
                if ship in body.upper():
                    # استخراج الأرقام بأمان تام
                    res = {
                        "Date": msg['Date'], "Ship": ship,
                        "Dist": float(re.search(r"Dis.*?([\d\.]+)", body).group(1)) if re.search(r"Dis.*?([\d\.]+)", body) else 0.0,
                        "RPM": float(re.search(r"R.*?P.*?M.*?([\d\.]+)", body).group(1)) if re.search(r"R.*?P.*?M.*?([\d\.]+)", body) else 0.0,
                        "FO": float(re.search(r"Fuel.*?oil.*?([\d\.]+)", body).group(1)) if re.search(r"Fuel.*?oil", body) else 0.0,
                        "Slip": float(re.search(r"Slip.*?([\-\d\.]+)%", body).group(1)) if re.search(r"Slip", body) else 0.0,
                        "Exh": re.search(r"TEMP\s*([\d\s,]+)", body).group(1).strip() if re.search(r"TEMP", body) else "0,0,0,0,0,0"
                    }
                    data_found.append(res)
        return pd.DataFrame(data_found)
    except: return pd.DataFrame()

# --- 4. واجهة التحكم والعرض ---
with st.sidebar:
    st.title("🚢 VesselCore v19")
    pwd = st.text_input("App Password:", type="password")
    if st.button("🔄 تحديث الأرشيف (Gmail Sync)"):
        new_df = sync_gmail_secure(pwd)
        if not new_df.empty:
            current_db = load_vessel_db()
            final_db = pd.concat([current_db, new_df]).drop_duplicates(subset=['Date', 'Ship'])
            final_db.to_csv(DB_FILE, index=False)
            st.success("تم تحديث قاعدة البيانات!")

st.title("🌐 Strategic Operations Dashboard")
df = load_vessel_db()

if not df.empty:
    target = st.selectbox("اختر السفينة:", df['Ship'].unique())
    ship_data = df[df['Ship'] == target].sort_values(by='Date')
    latest = ship_data.iloc[-1]
    
    # عرض KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance", f"{latest['Dist']} NM")
    c2.metric("Propeller Slip", f"{latest['Slip']}%", delta="Normal" if latest['Slip'] < 15 else "Critical")
    c3.metric("Fuel Cons.", f"{latest['FO']} MT")
    c4.metric("Engine RPM", latest['RPM'])

    st.divider()
    
    # خريطة الحريق (Combustion)
    st.subheader("🔥 Exhaust Temperatures Profile")
    try:
        t_list = [int(float(x)) for x in str(latest['Exh']).replace(',', ' ').split() if x.strip().isdigit()]
        if t_list:
            st.plotly_chart(go.Figure(go.Bar(x=[f"C{i+1}" for i in range(len(t_list))], y=t_list, marker_color='#3498db')), use_container_width=True)
    except: st.info("بيانات الحرارة قيد التجهيز...")
    
    st.subheader("📂 التاريخ الفني المؤرشف")
    st.dataframe(ship_data, use_container_width=True)
else:
    st.warning("بانتظار سحب أول تقرير من إيميل Marwankarroum3@gmail.com")
