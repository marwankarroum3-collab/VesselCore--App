import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import imaplib, email, re, os
from datetime import datetime

# --- 1. إعدادات الهوية الفنية (VesselCore UI) ---
st.set_page_config(page_title="VesselCore Auto-Sync OS", layout="wide")
st.markdown("""<style>.stMetric {background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px;}</style>""", unsafe_allow_html=True)

# --- 2. محرك الربط مع Gmail (Marwankarroum3@gmail.com) ---
def fetch_noon_data(app_pass):
    user = "marwankarroum3@gmail.com"
    data_list = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, app_pass)
        mail.select("inbox")
        # البحث عن إيميلات Noon Report لأسطولك
        _, msgs = mail.search(None, '(SUBJECT "Noon Report")')
        
        for num in msgs[0].split()[-10:]: # قراءة آخر 10 تقارير تلقائياً
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            body = msg.get_payload(decode=True).decode(errors='ignore')
            
            # محرك المسح الذكي (Regex) لاستخراج الأرقام الحقيقية
            ship = re.search(r"M\.V\s+([A-Z\s]+)", body)
            dist = re.search(r"Dis:\s*([\d\.]+)", body)
            rpm = re.search(r"R\.P\.M:\s*([\d\.]+)", body)
            fo = re.search(r"Fuel oil:.*?(\d+)\s*M/T", body, re.S)
            slip = re.search(r"Slip\s*([\-\d\.]+)%", body)
            
            if ship and rpm:
                data_list.append({
                    "Date": msg['Date'],
                    "Ship": ship.group(1).strip(),
                    "Dist": float(dist.group(1)) if dist else 0,
                    "RPM": float(rpm.group(1)) if rpm else 0,
                    "FO_Cons": float(fo.group(1)) if fo else 0,
                    "Slip": float(slip.group(1)) if slip else 0
                })
        return pd.DataFrame(data_list)
    except Exception as e:
        st.error(f"فشل الاتصال: {e}")
        return pd.DataFrame()

# --- 3. واجهة التحكم الجانبية ---
with st.sidebar:
    st.title("🚢 VesselCore OS")
    st.write(f"**Technical Director Control**")
    pwd = st.text_input("App Password (Gmail):", type="password", help="أدخل رمز التطبيق المكون من 16 حرفاً")
    sync_btn = st.button("🔄 تحديث البيانات آلياً")

# --- 4. العرض الاستراتيجي (Strategic Analysis) ---
st.title("🌐 Fleet Live Operations & Intelligence")

if sync_btn and pwd:
    with st.spinner("جاري سحب التقارير من الإيميل وتحديث النظام..."):
        df = fetch_noon_data(pwd)
        if not df.empty:
            st.session_state['fleet_data'] = df
            st.success("تم تحديث بيانات الأسطول بنجاح!")

if 'fleet_data' in st.session_state:
    df = st.session_state['fleet_data']
    target_ship = st.selectbox("اختر السفينة للتحليل:", df['Ship'].unique())
    ship_data = df[df['Ship'] == target_ship]
    latest = ship_data.iloc[-1]

    # عرض KPIs الحقيقية
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance Run", f"{latest['Dist']} NM")
    c2.metric("Propeller Slip", f"{latest['Slip']}%", delta="Normal" if latest['Slip'] < 15 else "Critical")
    c3.metric("FO Consumption", f"{latest['FO_Cons']} MT")
    c4.metric("RPM", latest['RPM'])

    st.divider()
    
    # تريند الأداء
    st.subheader(f"📊 Performance Trend: {target_ship}")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ship_data['Date'], y=ship_data['Slip'], name="Slip %", line=dict(color='#00ff00', width=3)))
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📂 التاريخ المؤرشف (Verified History)")
    st.dataframe(ship_data)
else:
    st.info("بانتظار إدخال App Password والضغط على تحديث لجلب البيانات من إيميل Marwankarroum3@gmail.com")

st.caption("© 2026 VesselCore Technical - Automated Intelligence System")
