import streamlit as st
import requests
from datetime import datetime, timedelta
import hashlib
import plotly.graph_objects as go
import pandas as pd

# فقط این رمز رو عوض کن
OWNER_PASSWORD = "244343696Mzt"

# تولید کد 20 روزه
def create_license():
    expiry = datetime.now() + timedelta(days=20)
    raw = "airguard2025" + expiry.strftime("%Y%m%d")
    h = hashlib.md5(raw.encode()).hexdigest().upper()[:12]
    return f"AG25-{h[:4]}-{h[4:8]}-{h[8:]}"

# چک کردن کد
def check_license(code):
    try:
        if not code.startswith("AG25-"): return False, "Invalid format"
        clean = code[5:].replace("-", "").upper()
        if len(clean) != 12: return False, "Invalid code"
        today = datetime.now().date()
        for d in range(0, 26):
            date = today + timedelta(days=d)
            expected = hashlib.md5(("airguard2025" + date.strftime("%Y%m%d")).encode()).hexdigest().upper()[:12]
            if expected == clean:
                days_left = 20 - d
                return True, f"{days_left} days left" if days_left >= 0 else "Expired"
        return False, "Invalid or expired"
    except:
        return False, "Error"

# کش برای سرعت بالا
@st.cache_data(ttl=300)  # هر 5 دقیقه آپدیت
def get_air_data(lat, lon):
    try:
        current = requests.get(f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1", timeout=10).json()
        forecast = requests.get(f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1", timeout=10).json()
        return current, forecast
    except:
        return None, None

# صفحه
st.set_page_config(page_title="AirGuard Pro", page_icon="🌍", layout="centered")

# تم فوق جذاب (مدرن و شیشه‌ای)
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px;}
    .title {font-size: 4.5rem; text-align: center; font-weight: 900; background: linear-gradient(90deg, #fff, #00f5ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .card {background: rgba(255,255,255,0.15); backdrop-filter: blur(20px); border-radius: 20px; padding: 30px; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 8px 32px rgba(0,0,0,0.3);}
    .license {font-family: 'Courier New'; font-size: 1.8rem; background: #000; color: #0f0; padding: 15px; border-radius: 10px; letter-spacing: 5px;}
    .stButton>button {background: linear-gradient(45deg, #ff6b6b, #feca57); border: none; border-radius: 50px; height: 60px; font-weight: bold; font-size: 1.3rem;}
    .metric-label {font-size: 1.1rem !important; color: #ccc !important;}
    .metric-value {font-size: 1.8rem !important; font-weight: bold !important;}
</style>
""", unsafe_allow_html=True)

if 'valid' not in st.session_state:
    st.session_state.valid = False

if not st.session_state.valid:
    st.markdown("<h1 class='title'>AirGuard Pro</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#fff; opacity:0.9;'>Real-time Air Quality + 48h Forecast</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 20-Day License - Only 200,000 IRR")
            code = st.text_input("Enter License Key", type="password", placeholder="AG25-XXXX-XXXX-XXXX")
            
            if st.button("Activate License", type="primary"):
                ok, msg = check_license(code)
                if ok:
                    st.session_state.valid = True
                    st.success(f"License Activated! {msg}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(msg)
            
            st.markdown("**Purchase:** @YourTelegramID")
            st.markdown("</div>", unsafe_allow_html=True)

    owner = st.text_input("Owner Password (only you)", type="password")
    if owner == OWNER_PASSWORD:
        st.success("Welcome Boss!")
        if st.button("Generate New 20-Day License"):
            new_code = create_license()
            st.markdown(f"<div class='license'>{new_code}</div>", unsafe_allow_html=True)
            st.success("New license generated!")

else:
    st.markdown("<h2 style='color:#fff; text-align:center;'>AirGuard Pro - Premium Active</h2>", unsafe_allow_html=True)
    if st.sidebar.button("Logout"):
        st.session_state.valid = False
        st.rerun()

    col1, col2 = st.columns([1,1])
    with col1:
        lat = st.text_input("Latitude", "35.6892", help="Example: Tehran")
    with col2:
        lon = st.text_input("Longitude", "51.3890")

    if st.button("Get Air Quality Report", type="primary", use_container_width=True):
        with st.spinner("Loading real-time data..."):
            current, forecast = get_air_data(lat, lon)
            if not current or not forecast:
                st.error("Invalid location or connection error")
                st.stop()

            c = current['list'][0]['components']
            
            # محاسبه AQI واقعی‌تر
            aqi = max(
                c['pm2_5'] * 2,
                c['pm10'],
                c['no2'] * 2,
                c['o3'] * 1000 / 50,
                c['co'] / 3
            )
            aqi = min(max(int(aqi), 0), 500)
            
            levels = ["Good", "Moderate", "Unhealthy for Sensitive", "Unhealthy", "Very Unhealthy", "Hazardous"]
            colors = ["#00e400", "#ffff00", "#ff7e00", "#ff0000", "#8f3f97", "#7e0023"]
            level = levels[min(aqi // 51, 5)]
            color = colors[min(aqi // 51, 5)]

            st.markdown(f"<h2 style='text-align:center; color:{color}; font-size:3rem;'>{level} - AQI {aqi}</h2>", unsafe_allow_html=True)

            # آلاینده‌ها با واحد
            cols = st.columns(6)
            pollutants = [
                ("PM2.5", c['pm2_5'], "μg/m³"),
                ("PM10", c['pm10'], "μg/m³"),
                ("CO", c['co'], "μg/m³"),
                ("NO₂", c['no2'], "μg/m³"),
                ("O₃", c['o3']*1000, "ppb"),
                ("SO₂", c['so2'], "μg/m³")
            ]
            for i, (name, val, unit) in enumerate(pollutants):
                with cols[i]:
                    st.metric(name, f"{val:.1f}", delta=f"{unit}")

            # نمودار سریع
            df = pd.DataFrame([
                {"Time": datetime.fromtimestamp(f['dt']), "AQI": max(f['components']['pm2_5']*2, f['components']['pm10'])}
                for f in forecast['list'][:48]
            ])
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Time'], y=df['AQI'], mode='lines+markers', line=dict(color='#ff6b6b', width=4)))
            fig.update_layout(
                title="48-Hour AQI Forecast",
                template="plotly_dark",
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.caption("AirGuard Pro © 2025 - Premium Air Quality Monitor")
