import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# الهوية الفخمة لنظام Marwan Karroum
st.set_page_config(page_title="VCIS | VesselCore", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #e0e0e0; }
    h1, h2 { color: #2aa198 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚢 VesselCore Intelligence System")
st.write("### CEO Dashboard | Marwan Karroum")

# أسطول السفن الـ 12
ship = st.sidebar.selectbox("Select Vessel", ["NJ MOON", "NJ AIO", "NJ MARS", "YARA J"])

st.header(f"Technical Audit: {ship}")
col1, col2 = st.columns([2, 1])

with col1:
    units = [f"U{i}" for i in range(1, 7)]
    temps = [385, 388, 25, 382, 390, 384] # كشف حرارة الـ 25 درجة
    
    fig = go.Figure(go.Bar(
        x=units, y=temps,
        marker_color=['#2aa198' if t > 150 else '#e74c3c' for t in temps],
        text=[f"{t}°C" for t in temps], textposition='auto'
    ))
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.write("#### 🛡️ Expert Audit Alerts")
    for i, t in enumerate(temps):
        if t < 150:
            st.error(f"UNIT {i+1}: 🛑 FAKE DATA DETECTED.")
    st.info("💡 Tip: Verify turbocharger efficiency via Scavenge Air pressure.")

st.markdown("---")
st.write("📋 **ISM Compliance:** Monitoring active for IMO 2026.")
