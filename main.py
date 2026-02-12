import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import imaplib, email, re, os
from datetime import datetime

# --- 1. الهوية البصرية العالمية (Professional UI) ---
st.set_page_config(page_title="VesselCore Intelligence OS", layout="wide")
st.markdown("""<style>.stMetric {background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px;}</style>""", unsafe_allow_html=True)

# --- 2. محرك الأرشفة والبيانات الثابتة ---
DB_FILE = 'vessel_fleet_archive.csv'
FLEET_SPECS = {
    "NJ MOON": {"Pitch": 4.82}, "NJ MARS": {"Pitch": 5.10},
    "NJ AIO": {"Pitch": 4.95}, "YARA J": {"Pitch": 4.75}
}

# --- 3. محرك المسح الذكي المتطور (Fixed Parser) ---
def parse_body(msg):
    """حل مشكلة الـ NoneType وفك تشفير الإيميلات بكفاءة"""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                return payload.decode(errors='ignore') if payload else ""
    else:
        payload = msg.get_payload(decode=True)
        return payload.decode(errors='ignore') if payload else ""
    return ""

def fetch_data(app_pass):
    user = "marwankarroum3@gmail.com"
    data_list = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, app_pass)
        mail.select("inbox")
        _, msgs = mail.search(None, '(SUBJECT "Noon Report")')
        
        for num in msgs[0].split()[-10:]:
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            body = parse_body(msg)
            
            # استخراج البيانات بالمعادلات الحقيقية
            ship_match = re.search(r"M\.V\s+([A-Z\s]+)", body)
            dist_match = re.search(r"Dis:\s*([\d\.]+)", body)
            rpm_match = re.search(r"R\.P\.M:\s*([\d\.]+)", body)
            fo_match = re.search(r"Fuel oil:.*?(\d+)\s*M/T", body, re.S)
            slip_match = re.search(r"Slip\s*([\-\d\.]+)%", body)
            
            if ship_match and rpm_match:
                data_list.append({
                    "Date": msg['Date'], "Ship": ship_match.group(1).strip(),
                    "Dist": float(dist_match.group(1)) if dist_match else 0,
                    "RPM": float(rpm_match.group(1)) if rpm_match else 0,
                    "FO": float(fo_match.group(1)) if fo_match else 0,
                    "Slip": float(slip_match.group(1)) if slip_match else 0
                })
        return pd.DataFrame(data_list)
    except Exception as e:
        st.error(f"فشل الاتصال: {e}")
        return pd.DataFrame()

# --- 4. واجهة التحكم والعرض ---
with st.sidebar:
    st.title("🚢 VesselCore OS")
    st.write(f"**CEO:** Marwan Karroum")
    pwd = st.text_input("App Password (Marwankarroum3):", type="password")
    if st.button("🚀 تحديث الأسطول آلياً"):
        df = fetch_data(pwd)
        if not df.empty:
            df.to_csv(DB_FILE, index=False)
            st.session_state['data'] = df
            st.success("تم التحديث!")

st.title("🌐 Fleet Strategic Analysis & Operations")
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    target = st.selectbox("اختر السفينة:", df['Ship'].unique())
    ship_df = df[df['Ship'] == target]
    latest = ship_df.iloc[-1]

    # عرض KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Distance", f"{latest['Dist']} NM")
    c2.metric("Propeller Slip", f"{latest['Slip']}%")
    c3.metric("Fuel Cons.", f"{latest['FO']} MT")
    
    st.subheader(f"📊 تريند الأداء التاريخي لـ {target}")
    fig = go.Figure(go.Scatter(x=ship_df['Date'], y=ship_df['Slip'], name="Slip %", line=dict(color='#00ff00', width=3)))
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("بانتظار الضغط على 'تحديث الأسطول' لبناء قاعدة البيانات من إيميل Marwankarroum3@gmail.com")
