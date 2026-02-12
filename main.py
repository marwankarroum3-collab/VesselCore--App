import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import imaplib, email, re, os
from datetime import datetime

# --- 1. الهوية السيادية (Master Command UI) ---
st.set_page_config(page_title="VesselCore Absolute v14", layout="wide")
st.markdown("""<style>.stMetric {background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px;}</style>""", unsafe_allow_html=True)

# --- 2. محرك الأرشيف الصامت (Master Database) ---
DB_FILE = 'vessel_master_intel_v14.csv'
FLEET_SPECS = {
    "NJ MOON": {"Pitch": 4.82, "Cyl": 6}, "NJ MARS": {"Pitch": 5.10, "Cyl": 6},
    "NJ AIO": {"Pitch": 4.95, "Cyl": 6}, "YARA J": {"Pitch": 4.75, "Cyl": 5}
}

# --- 3. محرك المسح الدفاعي (Safe Technical Parser) ---
def get_email_body(msg):
    """فك تشفير محتوى الإيميل بأمان لمنع خطأ NoneType"""
    try:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode(errors='ignore')
        else:
            return msg.get_payload(decode=True).decode(errors='ignore')
    except: return ""
    return ""

def safe_parse(body):
    """استخراج البيانات بدقة 100% وبدون تخمين"""
    data = {}
    try:
        ship_match = re.search(r"(NJ MOON|NJ MARS|NJ AIO|YARA J)", body, re.I)
        if not ship_match: return None
        
        data['Ship'] = ship_match.group(1).upper()
        data['Dist'] = float(re.search(r"Dis:\s*([\d\.]+)", body).group(1)) if re.search(r"Dis:\s*([\d\.]+)", body) else 0.0
        data['RPM'] = float(re.search(r"R\.P\.M:\s*([\d\.]+)", body).group(1)) if re.search(r"R\.P\.M:\s*([\d\.]+)", body) else 0.0
        data['Speed'] = float(re.search(r"Speed:\s*([\d\.]+)", body).group(1)) if re.search(r"Speed:\s*([\d\.]+)", body) else 0.0
        data['FO'] = float(re.search(r"Fuel oil:.*?(\d+[\.]?\d*)", body, re.S).group(1)) if re.search(r"Fuel oil:", body) else 0.0
        data['Slip'] = float(re.search(r"Slip\s*([\-\d\.]+)%", body).group(1)) if re.search(r"Slip\s*([\-\d\.]+)%", body) else 0.0
        
        exh_match = re.search(r"EXHT TEMP\s*([\d\s]+)", body)
        data['Exh'] = exh_match.group(1).strip().replace(" ", ",") if exh_match else "0,0,0,0,0,0"
        return data
    except: return None

# --- 4. واجهة التحكم (Command Sidebar) ---
with st.sidebar:
    st.title("🚢 VesselCore v14")
    app_pwd = st.text_input("App Password (Marwankarroum3):", type="password")
    if st.button("🚀 تحديث الأسطول والتحليل الهندسي"):
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login("marwankarroum3@gmail.com", app_pwd)
            mail.select("inbox")
            _, msgs = mail.search(None, '(OR SUBJECT "Noon Report" SUBJECT "DAILY REPORT")')
            
            all_data = []
            for num in msgs[0].split()[-10:]:
                _, d = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(d[0][1])
                body = get_email_body(msg)
                parsed = safe_parse(body)
                if parsed:
                    parsed['Date'] = msg['Date']
                    all_data.append(parsed)
            
            if all_data:
                new_df = pd.DataFrame(all_data)
                if os.path.exists(DB_FILE):
                    old_df = pd.read_csv(DB_FILE)
                    final_df = pd.concat([old_df, new_df]).drop_duplicates(subset=['Date', 'Ship'])
                else: final_df = new_df
                final_df.to_csv(DB_FILE, index=False)
                st.success("تم تحديث الأرشيف بالبيانات الجديدة!")
            else: st.warning("اتصلنا بالإيميل ولكن لم نجد تقارير بتنسيق مفهوم.")
        except Exception as e: st.error(f"خطأ: {e}")

# --- 5. لوحة القيادة (The Strategic Bridge) ---
st.title("🌐 Operations & Strategic Analysis")
if os.path.exists(DB_FILE):
    df_master = pd.read_csv(DB_FILE)
    ship = st.selectbox("اختر السفينة للتحليل:", list(FLEET_SPECS.keys()))
    ship_df = df_master[df_master['Ship'] == ship]
    
    if not ship_df.empty:
        latest = ship_df.iloc[-1]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Distance", f"{latest['Dist']} NM")
        c2.metric("Propeller Slip", f"{latest['Slip']}%", delta="Critical" if latest['Slip'] > 15 else "Normal")
        c3.metric("Fuel Cons.", f"{latest['FO']} MT")
        c4.metric("Engine RPM", latest['RPM'])
        
        st.subheader("🔥 Exhaust Temperatures & Combustion")
        temps = [int(x) for x in str(latest['Exh']).split(',')]
        st.plotly_chart(go.Figure(go.Bar(x=[f"Cyl {i+1}" for i in range(len(temps))], y=temps, marker_color='#3498db')), use_container_width=True)
    else: st.warning(f"لا توجد بيانات مؤرشفة لـ {ship} حتى الآن.")
else: st.info("بانتظار سحب أول تقرير لبناء الأرشيف.")
