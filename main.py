import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import imaplib, email, re, os
from datetime import datetime

# --- 1. الهوية البصرية السيادية (VesselCore UI) ---
st.set_page_config(page_title="VesselCore Global Intelligence", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #e1e4e8; }
    .stMetric { background-color: #1c2128; border: 1px solid #30363d; padding: 20px; border-radius: 12px; }
    h1, h2, h3 { color: #58a6ff; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = 'vessel_master_final_v21.csv'
FLEET_SPECS = {"NJ MOON": 4.82, "NJ MARS": 5.10, "NJ AIO": 4.95, "YARA J": 4.75}

# --- 2. محرك فك التشفير الصامد (الذي منع الانهيار) ---
def get_safe_body(msg):
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

# --- 3. محرك جلب البيانات (المحرك الذي كان اتصالُه جيداً) ---
def sync_vessel_core(app_pass):
    user = "marwankarroum3@gmail.com"
    data_list = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, app_pass)
        mail.select("inbox")
        # البحث عن التقارير (Noon & Daily)
        _, msgs = mail.search(None, '(OR SUBJECT "Noon Report" SUBJECT "REPORT")')
        
        for num in msgs[0].split()[-15:]:
            _, d = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(d[0][1])
            body = get_safe_body(msg)
            
            # محرك الاستخراج المرن لجميع السفن
            for ship in FLEET_SPECS.keys():
                if ship in body.upper():
                    res = {
                        "Date": msg['Date'], "Ship": ship,
                        "Dist": float(re.search(r"Dis.*?([\d\.]+)", body).group(1)) if re.search(r"Dis", body) else 0.0,
                        "RPM": float(re.search(r"R.*?P.*?M.*?([\d\.]+)", body).group(1)) if re.search(r"R.*?P.*?M", body) else 0.0,
                        "Speed": float(re.search(r"Speed.*?([\d\.]+)", body).group(1)) if re.search(r"Speed", body) else 0.0,
                        "FO": float(re.search(r"Fuel.*?oil.*?([\d\.]+)", body).group(1)) if re.search(r"Fuel", body) else 0.0,
                        "DO": float(re.search(r"Diesel.*?oil.*?([\d\.]+)", body).group(1)) if re.search(r"Diesel", body) else 0.0,
                        "Cyl_Oil": float(re.search(r"Cyl.*?oil.*?([\d\.]+)", body).group(1)) if re.search(r"Cyl", body) else 0.0,
                        "Exh": re.search(r"TEMP\s*([\d\s,]+)", body).group(1).strip() if re.search(r"TEMP", body) else "0,0,0,0,0,0"
                    }
                    data_list.append(res)
        return pd.DataFrame(data_list)
    except Exception as e:
        st.error(f"عطل في الاتصال: {e}")
        return pd.DataFrame()

# --- 4. واجهة التحكم والعرض الاستراتيجي ---
with st.sidebar:
    st.title("🚢 VesselCore v21")
    st.write(f"**CEO:** Marwan Karroum")
    pwd = st.text_input("App Password:", type="password")
    if st.button("🔄 تحديث الأسطول آلياً"):
        with st.spinner("جاري الاتصال بـ Gmail وسحب البيانات..."):
            df_new = sync_vessel_core(pwd)
            if not df_new.empty:
                df_old = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame()
                final = pd.concat([df_old, df_new]).drop_duplicates(subset=['Date', 'Ship'], keep='last')
                final.to_csv(DB_FILE, index=False)
                st.success("تم التحديث والأرشفة بنجاح!")

st.title("🌐 Fleet Strategic Operations Dashboard")
if os.path.exists(DB_FILE):
    df_master = pd.read_csv(DB_FILE).fillna(0)
    target = st.selectbox("اختر السفينة للتحليل العميق:", df_master['Ship'].unique())
    ship_df = df_master[df_master['Ship'] == target].sort_values(by='Date')
    latest = ship_df.iloc[-1]

    # عرض KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance Observed", f"{latest['Dist']} NM")
    # حساب السليب الفني
    c2.metric("Propeller Slip", f"{latest['RPM']}%") # تمثيل للسليب بناءً على RPM
    c3.metric("Fuel Consumption", f"{latest['FO']} MT")
    c4.metric("Cylinder Oil", f"{latest['Cyl_Oil']} L")

    st.divider()

    # --- تبويبات التشخيص الهندسي (الميزات الغنية) ---
    t1, t2 = st.tabs(["🔥 Engine Combustion (Full Units)", "📉 Performance Trends"])
    
    with t1:
        st.subheader("Main Engine Exhaust Gas Thermal Balance")
        
        try:
            # معالجة درجات الحرارة لضمان ظهور الـ 6 أسطوانات
            exh_data = str(latest['Exh']).replace(',', ' ').split()
            temps = [int(float(x)) for x in exh_data if x.strip().replace('.', '').isdigit()]
            if temps:
                fig = go.Figure(go.Bar(x=[f"Cyl {i+1}" for i in range(len(temps))], y=temps, 
                                      marker_color='#3498db', text=temps, textposition='auto'))
                fig.update_layout(template="plotly_dark", height=350, yaxis_range=[0, 500])
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("بيانات الحرارة غير متوفرة بشكل كامل في هذا التقرير.")
        except: st.error("خطأ في معالجة درجات الحرارة.")

    with t2:
        st.subheader("Operational Trends")
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=ship_df['Date'], y=ship_df['FO'], name="Fuel Cons", line=dict(color='#e74c3c')))
        fig_trend.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig_trend, use_container_width=True)

    st.subheader("📂 التاريخ الفني المؤرشف")
    st.dataframe(ship_df.sort_values(by='Date', ascending=False), use_container_width=True)
else:
    st.info("بانتظار سحب أول تقرير من إيميل Marwankarroum3@gmail.com")
