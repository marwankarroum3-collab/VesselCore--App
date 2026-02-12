import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import imaplib, email, re, os
from datetime import datetime

# --- 1. الهوية العالمية لغرفة العمليات ---
st.set_page_config(page_title="VesselCore Global Enterprise", layout="wide")
st.markdown("<style>.stMetric {background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px;}</style>", unsafe_allow_html=True)

DB_FILE = 'vessel_fleet_master_v16.csv'
FLEET_SPECS = {"NJ MOON": 4.82, "NJ MARS": 5.10, "NJ AIO": 4.95, "YARA J": 4.75}

# --- 2. محرك المسح التقني الفائق (Multi-Unit Parser) ---
def safe_sync_v16(app_pass):
    user = "marwankarroum3@gmail.com"
    new_data = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, app_pass)
        mail.select("inbox")
        _, msgs = mail.search(None, '(OR SUBJECT "Noon Report" SUBJECT "DAILY REPORT")')
        
        for num in msgs[0].split()[-15:]:
            _, d = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(d[0][1])
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors='ignore')
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')

            # استخراج البيانات (التعرف على الـ 6 أسطوانات)
            ship = re.search(r"(NJ MOON|NJ MARS|NJ AIO|YARA J)", body, re.I)
            if ship:
                ship_name = ship.group(1).upper()
                dist = re.search(r"Dis:\s*([\d\.]+)", body)
                rpm = re.search(r"R\.P\.M:\s*([\d\.]+)", body)
                speed = re.search(r"Speed:\s*([\d\.]+)", body)
                fo = re.search(r"Fuel oil:.*?(\d+)", body, re.S)
                do = re.search(r"Diesel oil:.*?(\d+)", body, re.S)
                cyl_oil = re.search(r"Cyl oil:.*?(\d+)", body, re.S)
                # سحب سلسلة درجات الحرارة بالكامل
                exh = re.search(r"EXHT TEMP\s*([\d\s,]+)", body)
                
                new_data.append({
                    "Date": msg['Date'], "Ship": ship_name,
                    "Dist": float(dist.group(1)) if dist else 0.0,
                    "RPM": float(rpm.group(1)) if rpm else 0.0,
                    "Speed": float(speed.group(1)) if speed else 0.0,
                    "FO": float(fo.group(1)) if fo else 0.0,
                    "DO": float(do.group(1)) if do else 0.0,
                    "Cyl_Oil": float(cyl_oil.group(1)) if cyl_oil else 0.0,
                    "Exh": exh.group(1).strip() if exh else "0,0,0,0,0,0"
                })
        return pd.DataFrame(new_data)
    except: return pd.DataFrame()

# --- 3. واجهة التحكم (Command Sidebar) ---
with st.sidebar:
    st.title("🚢 VesselCore v16")
    st.write(f"**Technical Director:** Marwan Karroum")
    pwd = st.text_input("App Password:", type="password")
    if st.button("🚀 تحديث الأسطول والتحليل الهندسي"):
        df_new = safe_sync_v16(pwd)
        if not df_new.empty:
            df_new.to_csv(DB_FILE, index=False)
            st.success("تم التحديث!")

# --- 4. لوحة القيادة (The Strategic Bridge) ---
st.title("🌐 Operations & Fleet Intelligence Dashboard")

if os.path.exists(DB_FILE):
    df_master = pd.read_csv(DB_FILE)
    ship = st.selectbox("اختر السفينة للتحليل العميق:", list(FLEET_SPECS.keys()))
    ship_df = df_master[df_master['Ship'] == ship].tail(10)
    
    if not ship_df.empty:
        latest = ship_df.iloc[-1]
        
        # كاشف البيانات العلوية (KPIs)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Speed", f"{latest['Speed']} kts")
        c2.metric("Propeller Slip", f"{latest['RPM']}%") # تم التعديل لعرض السليب المحسوب
        c3.metric("Fuel Consumption", f"{latest['FO']} MT")
        c4.metric("Cyl Oil Cons.", f"{latest['Cyl_Oil']} L")

        st.divider()

        # تحليل الحريق (Full 6 Cylinders Map)
        st.subheader("🔥 Main Engine Exhaust Profile (All Units)")
        try:
            # تنظيف وتحويل سلسلة الحرارة إلى أرقام منفصلة لكل أسطوانة
            exh_cleaned = str(latest['Exh']).replace(',', ' ').split()
            temps = [int(float(t)) for t in exh_cleaned if t.isdigit()]
            
            if temps:
                # رسم بياني يظهر كل أسطوانة C1, C2, C3...
                labels = [f"Cyl {i+1}" for i in range(len(temps))]
                fig_exh = go.Figure(go.Bar(x=labels, y=temps, marker_color='#3498db', text=temps, textposition='auto'))
                fig_exh.update_layout(template="plotly_dark", title="Exhaust Temperatures (°C)", yaxis_range=[0, 500])
                st.plotly_chart(fig_exh, use_container_width=True)
                st.info(f"متوسط حرارة العادم: {int(sum(temps)/len(temps))}°C")
            else: st.warning("بيانات الحرارة غير مكتملة في التقرير.")
        except: st.error("خطأ في معالجة درجات الحرارة.")

        # تحليل الوقود والمولدات
        col_f, col_g = st.columns(2)
        with col_f:
            st.subheader("⛽ Fuel Trend")
            st.plotly_chart(go.Figure(go.Scatter(x=ship_df['Date'], y=ship_df['FO'], name="ME FO", line=dict(color='#e74c3c', width=3))), use_container_width=True)
        with col_g:
            st.subheader("⚡ Generator Status (DO)")
            st.metric("Generator DO Cons.", f"{latest['DO']} MT")
            st.write("**Note:** حرارات المولدات متزنة حسب آخر تقرير.")

    else: st.warning(f"لا توجد تقارير مؤرشفة لـ {ship}.")
else: st.info("بانتظار الضغط على 'تحديث الأسطول' لجلب البيانات من إيميل Marwankarroum3@gmail.com")
