import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- 1. إعداد قاعدة البيانات (Auto-CSV Database) ---
# هذا الملف هو الذي سيخزن كل بياناتك اليومية
DB_FILE = 'vesselcore_fleet_db.csv'

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # إنشاء هيكل البيانات إذا كان الملف غير موجود
        columns = ['Date', 'Ship', 'Status', 'Loc', 'Dist', 'Speed', 'RPM', 'ME_FO', 'AE_DO', 'Cyl_LO', 'Gen_LO', 'Load', 'LO_P', 'Exh_Avg']
        return pd.DataFrame(columns=columns)

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- 2. إعدادات الواجهة الاحترافية ---
st.set_page_config(page_title="VesselCore Technical OS", layout="wide")
st.markdown("<style>.stMetric {background-color: #1c2128; border: 1px solid #30363d; padding: 15px; border-radius: 10px;}</style>", unsafe_allow_html=True)

df_fleet = load_data()

# --- 3. بوابة إدخال البيانات اليومية (Data Entry Port) ---
with st.sidebar:
    st.title("🚢 إدخال البيانات اليومية")
    with st.form("entry_form"):
        u_date = st.date_input("تاريخ التقرير")
        u_ship = st.selectbox("السفينة", ["NJ MOON", "NJ MARS", "NJ AIO", "YARA J"])
        u_status = st.selectbox("الحالة", ["At Sea", "At Port", "Anchorage"])
        u_loc = st.text_input("الموقع (Lat/Lon)")
        
        col_in1, col_in2 = st.columns(2)
        u_speed = col_in1.number_input("السرعة (Kts)", 0.0)
        u_rpm = col_in2.number_input("الـ RPM", 0)
        
        u_mefo = col_in1.number_input("وقود ME (MT)", 0.0)
        u_aedo = col_in2.number_input("وقود AE (MT)", 0.0)
        
        u_cyl = col_in1.number_input("زيت Cyl (L)", 0)
        u_gen = col_in2.number_input("زيت Gen (L)", 0)
        
        u_load = st.slider("حمل المحرك %", 0, 100)
        u_exh = st.number_input("متوسط حرارة العادم", 0)
        
        submitted = st.form_submit_button("حفظ وإرسال للتحليل")
        
        if submitted:
            new_row = {'Date': str(u_date), 'Ship': u_ship, 'Status': u_status, 'Loc': u_loc, 
                       'Dist': 0.0, 'Speed': u_speed, 'RPM': u_rpm, 'ME_FO': u_mefo, 
                       'AE_DO': u_aedo, 'Cyl_LO': u_cyl, 'Gen_LO': u_gen, 'Load': u_load, 
                       'LO_P': 0.0, 'Exh_Avg': u_exh}
            df_fleet = pd.concat([df_fleet, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df_fleet)
            st.success(f"تم تسجيل بيانات {u_ship} بنجاح!")

# --- 4. العرض والتحليل الهندسي (The Dashboard) ---
st.title("📊 لوحة التحكم والتحليل الفني للأسطول")

if not df_fleet.empty:
    selected_ship = st.selectbox("اختر السفينة للعرض:", df_fleet['Ship'].unique())
    ship_data = df_fleet[df_fleet['Ship'] == selected_ship].sort_values(by='Date')
    
    if not ship_data.empty:
        latest = ship_data.iloc[-1]
        
        # عرض المقاييس الرئيسية
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("آخر سرعة مسجلة", f"{latest['Speed']} Kts")
        m2.metric("استهلاك الوقود ME", f"{latest['ME_FO']} MT")
        m3.metric("استهلاك الديزل AE", f"{latest['AE_DO']} MT")
        m4.metric("زيت الأسطوانات", f"{latest['Cyl_LO']} L")

        st.divider()

        # رسم بياني لتحليل الاتجاه (Trends)
        st.subheader(f"📈 تحليل استهلاك الوقود التاريخي - {selected_ship}")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ship_data['Date'], y=ship_data['ME_FO'], name="وقود ME", line=dict(color='#3498db', width=3)))
        fig.add_trace(go.Scatter(x=ship_data['Date'], y=ship_data['AE_DO'], name="ديزل AE", line=dict(color='#e74c3c', width=3)))
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

        # جدول البيانات التاريخي
        with st.expander("📂 عرض سجل البيانات الكامل"):
            st.write(ship_data)
else:
    st.info("مرحباً بك يا مروان. ابدأ بإدخال بيانات أول تقرير يومي من القائمة الجانبية.")

st.sidebar.divider()
st.sidebar.caption("CEO Access: Marwan Karroum")