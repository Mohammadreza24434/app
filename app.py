import streamlit as st
import requests
from datetime import datetime, timedelta
import hashlib
import plotly.graph_objects as go

# رمز فقط برای تو
OWNER_PASSWORD = "244343696Mzt"

# تولید کد 20 روزه
def create_license():
    expiry = (datetime.now() + timedelta(days=20)).strftime("%Y%m%d")
    raw = "airguard2025" + expiry
    h = hashlib.md5(raw.encode()).hexdigest().upper()[:12]
    return f"AG25-{h[:4]}-{h[4:8]}-{h[8:]}"

# چک کردن کد
def check_license(code):
    try:
        if not code.startswith("AG25-"): return False, "Invalid"
        clean = code[5:].replace("-", "").upper()
        today = datetime.now().date()
        for d in range(0, 26):
            date = today + timedelta(days=d)
            expected = hashlib.md5(("airguard2025" + date.strftime("%Y%m%d")).encode()).hexdigest().upper()[:12]
            if expected == clean and d <= 20:
                return True, f"{20 - d} days left"
        return False, "Expired or invalid"
    except:
        return False, "Error"

# کش هوشمند: فقط وقتی lat+lon دقیقاً یکسان باشه، کش کنه
@st.cache_data(ttl=180, show_spinner=False)  # فقط 3 دقیقه کش
def get_air_data(lat, lon):
    key = f"{lat},{lon}"
    current_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1"
    forecast_url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1"
    
    try:
        current = requests.get(current_url, timeout=8).json()
        forecast = requests.get(forecast_url, timeout=8).json()
        return current, forecast
    except:
        return None, None

# صفحه
st.set_page_config(page_title="AirGuard Pro", page_icon="🌍", layout="centered")

# تم خفن شیشه‌ای
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px;}
    .title {font-size: 4.5rem; text-align: center; font-weight: 900; background: linear-gradient(90deg, #fff, #00f5ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .card {background: rgba(255,255,255,0.15); backdrop-filter: blur(20px); border-radius: 20px; padding: 30px; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 8px 32px rgba(0,0,0,0.3);}
    .license {font-family: 'Courier New'; font-size: 1.8rem; background: #000; color: #0f0; padding: 15px; border-radius: 10px; letter-spacing: 5px;}
    .stButton>button {background: linear-gradient(45deg, #ff6b6b, #feca57); border: none; border-radius: 50px; height: 60px; font-weight: bold; font-size: 1.3rem;}
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
            st.markdown("### 20-Day License - 200,000 IRR")
            code = st.text_input("Enter License Key", type="password", placeholder="AG25-XXXX-XXXX-XXXX")
            if st.button("Activate License", type="primary"):
                ok, msg = check_license(code)
                if ok:
                    st.session_state.valid = True
                    st.success(f"Activated! {msg}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(msg)
            st.markdown("**Purchase:** @YourTelegramID")
            st.markdown("</div>", unsafe_allow_html=True)

    owner = st.text_input("Owner Password", type="password")
    if owner == OWNER_PASSWORD:
        st.success("Welcome Boss!")
        if st.button("Generate New License"):
            st.markdown(f"<div class='license'>{create_license()}</div>", unsafe_allow_html=True)

else:
    st.markdown("<h2 style='color:#fff; text-align:center;'>AirGuard Pro - Premium Active</h2>", unsafe_allow_html=True)
    if st.sidebar.button("Logout"):
        st.session_state.valid = False
        st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        lat = st.text_input("Latitude", value="35.6892", help="e.g. Tehran: 35.6892")
    with col2:
        lon = st.text_input("Longitude", value="51.3890", help="e.g. Tehran: 51.3890")

    if st.button("Get Air Quality Report", type="primary", use_container_width=True):
        # پاک کردن کش برای این مختصات (تا همیشه تازه باشه)
        get_air_data.clear()
        
        with st.spinner("Fetching latest data..."):
            current, forecast = get_air_data(float(lat), float(lon))
            
            if not current or 'list' not in current:
                st.error("Invalid coordinates or no data")
                st.stop()

            c = current['list'][0]['components']

            # محاسبه AQI دقیق‌تر
            pm25_aqi = min((c['pm2_5'] / 12) * 50 + 50, 500) if c['pm2_5'] > 0 else 0
            pm10_aqi = min((c['pm10'] / 54) * 50 + 50, 500) if c['pm10'] > 0 else 0
            no2_aqi = min((c['no2'] / 53) * 100, 500)
            o3_aqi = min((c['o3'] * 1000 / 70) * 100, 500)
            aqi = max(pm25_aqi, pm10_aqi, no2_aqi, o3_aqi, 0)
            aqi = int(aqi)

            levels = ["Good", "Moderate", "Unhealthy for Sensitive", "Unhealthy", "Very Unhealthy", "Hazardous"]
            colors = ["#00e400", "#ffff00", "#ff7e00", "#ff0000", "#8f3f97", "#7e0023"]
            level = levels[min(aqi // 51, 5)]
            color = colors[min(aqi // 51, 5)]

            st.markdown(f"<h2 style='text-align:center; color:{color}; font-size:3.5rem; margin:20px 0;'>{level}<br>AQI {aqi}</h2>", unsafe_allow_html=True)

            # آلاینده‌ها با واحد
            cols = st.columns(6)
            data = [
                ("PM2.5", c['pm2_5'], "µg/m³"),
                ("PM10", c['pm10'], "µg/m³"),
                ("CO", c['co'], "µg/m³"),
                ("NO₂", c['no2'], "µg/m³"),
                ("O₃", round(c['o3']*1000, 1), "ppb"),
                ("SO₂", c['so2'], "µg/m³")
            ]
            for i, (name, val, unit) in enumerate(data):
                with cols[i]:
                    st.metric(name, f"{val:.1f}", delta=unit)

            # نمودار فوق سریع
            times = [datetime.fromtimestamp(f['dt']) for f in forecast['list'][:48]]
            aqis = []
            for f in forecast['list'][:48]:
                comp = f['components']
                aqi_val = max(
                    (comp['pm2_5'] / 12) * 50 + 50,
                    (comp['pm10'] / 54) * 50 + 50,
                    comp['no2'],
                    comp['o3'] * 1000 / 70 * 100
                )
                aqis.append(min(max(int(aqi_val), 0), 500))

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=times, y=aqis, mode='lines+markers', line=dict(color='#ff6b6b', width=4), marker=dict(size=6)))
            fig.update_layout(
                title="48-Hour AQI Forecast",
                template="plotly_dark",
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=60, b=20)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.caption("AirGuard Pro © 2025 - Real-time Global Air Quality Monitor")
