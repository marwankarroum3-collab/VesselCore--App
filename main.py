import streamlit as st
import pandas as pd
import imaplib, email, re, os

# --- 1. واجهة CEO المستقرة ---
st.set_page_config(page_title="VesselCore BlackBox", layout="wide")
st.markdown("<style>.stMetric {background-color: #0e1117; border: 1px solid #30363d; padding: 20px; border-radius: 10px;}</style>", unsafe_allow_html=True)

DB_FILE = 'fleet_final_master.csv'
FLEET = {"NJ MOON": 4.82, "NJ MARS": 5.10, "NJ AIO": 4.95, "YARA J": 4.75}

# --- 2. محرك القراءة "المرن" (Resilient Parser) ---
def extract_numbers(text):
    res = {}
    # البحث عن الأرقام بجانب الكلمات المفتاحية مهما كان التنسيق
    res['Dist'] = re.search(r"(?:Dis|Dist|Distance).*?(\d+[\.]?\d*)", text, re.I)
    res['RPM'] = re.search(r"(?:RPM|R\.P\.M).*?(\d+[\.]?\d*)", text, re.I)
    res['FO'] = re.search(r"(?:Fuel|FO|Cons).*?(\d+[\.]?\d*)", text, re.I)
    res['Slip'] = re.search(r"(?:Slip).*?([\-\d\.]+)%", text, re.I)
    
    return {k: float(v.group(1)) if v else 0.0 for k, v in res.items()}

# --- 3. محرك الاتصال والأرشفة ---
with st.sidebar:
    st.title("🚢 VesselCore v28")
    pwd = st.text_input("App Password:", type="password")
    if st.button("🔄 سحب البيانات الآن"):
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login("marwankarroum3@gmail.com", pwd)
            mail.select("inbox")
            _, msgs = mail.search(None, '(OR SUBJECT "Noon Report" SUBJECT "REPORT")')
            
            new_data = []
            for num in msgs[0].split()[-5:]: # آخر 5 إيميلات فقط للسرعة
                _, d = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(d[0][1])
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode(errors='ignore')
                else:
                    body = msg.get_payload(decode=True).decode(errors='ignore')
                
                for s in FLEET.keys():
                    if s in body.upper():
                        parsed = extract_numbers(body)
                        parsed.update({"Ship": s, "Date": msg['Date'], "Raw": body[:300]})
                        new_data.append(parsed)
            
            if new_data:
                df = pd.DataFrame(new_data)
                df.to_csv(DB_FILE, index=False)
                st.success("تم تحديث قاعدة البيانات!")
        except Exception as e:
            st.error(f"عطل فني: {e}")

# --- 4. لوحة التحليل الهندسي ---
st.title("🌐 Fleet Operations Dashboard")
if os.path.exists(DB_FILE):
    df_all = pd.read_csv(DB_FILE).fillna(0)
    ship = st.selectbox("اختر السفينة:", df_all['Ship'].unique())
    latest = df_all[df_all['Ship'] == ship].iloc[-1]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Distance", f"{latest['Dist']} NM")
    # حساب السليب الفني:
    # $$Slip\% = \frac{Dist_{Eng} - Dist_{Obs}}{Dist_{Eng}} \times 100$$
    c2.metric("Propeller Slip", f"{latest['Slip']}%")
    c3.metric("Fuel Cons.", f"{latest['FO']} MT")
    c4.metric("Engine RPM", latest['RPM'])

    st.divider()
    st.subheader("📝 معاينة البيانات الخام (للتحقق)")
    st.text_area("آخر نص قرأه البرنامج من الإيميل:", value=latest['Raw'], height=150)
else:
    st.info("بانتظار سحب التقارير لبناء الأرشيف.")


