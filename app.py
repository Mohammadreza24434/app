import streamlit as st
import requests
from datetime import datetime, timedelta
import hashlib
import plotly.graph_objects as go

# رمز فقط برای تو
OWNER_PASSWORD = "244343696Mzt"

# تولید لایسنس 20 روزه
def create_license():
    expiry = (datetime.now() + timedelta(days=20)).strftime("%Y%m%d")
    raw = "airguard2025" + expiry
    h = hashlib.md5(raw.encode()).hexdigest().upper()[:12]
    return f"AG25-{h[:4]}-{h[4:8]}-{h[8:]}"

# چک کردن لایسنس
def check_license(code):
    try:
        if not code.startswith("AG25-"): return False, "Invalid format"
        clean = code[5:].replace("-", "").upper()
        today = datetime.now().date()
        for d in range(0, 26):
            date = today + timedelta(days=d)
            expected = hashlib.md5(("airguard2025" + date.strftime("%Y%m%d")).encode()).hexdigest().upper()[:12]
            if expected == clean and d <= 20:
                return True, f"{20 - d} days remaining"
        return False, "Expired or invalid"
    except:
        return False, "Error"

# دریافت داده با هندل خطا و کش هوشمند
@st.cache_data(ttl=300, show_spinner=False)
def fetch_air_quality(lat, lon):
    try:
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1"
        forecast_url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1"
        
        current = requests.get(url, timeout=10).json()
        forecast = requests.get(forecast_url, timeout=10).json()
        
        if 'list' not in current or 'list' not in forecast:
            return None, None
        return current, forecast
    except:
        return None, None

# صفحه
st.set_page_config(page_title="AirGuard Pro", page_icon="🌍", layout="centered")

# تم حرفه‌ای و شیشه‌ای
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); min-height: 100vh; padding: 20px;}
    .title {font-size: 4.5rem; text-align: center; font-weight: 900; background: linear-gradient(90deg, #fff, #00f5ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .card {background: rgba(255,255,255,0.15); backdrop-filter: blur(20px); border-radius: 20px; padding: 30px; border: 1px solid rgba(255,255,255,0.2);}
    .license {font-family: 'Courier New'; font-size: 1.8rem; background: #000; color: #0f0; padding: 15px; border-radius: 10px; letter-spacing: 5px;}
    .stButton>button {background: linear-gradient(45deg, #ff6b6b, #feca57); border: none; border-radius: 50px; height: 60px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

if 'valid' not in st.session_state:
    st.session_state.valid = False

if not st.session_state.valid:
    st.markdown("<h1 class='title'>AirGuard Pro</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#fff;'>Real-time Air Quality Index + 48h Forecast</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### Premium 20-Day License - 200,000 IRR")
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
            st.markdown("**Contact:** @YourTelegramID")
            st.markdown("</div>", unsafe_allow_html=True)

    owner = st.text_input("Owner Access", type="password")
    if owner == OWNER_PASSWORD:
        st.success("Welcome Boss!")
        if st.button("Generate New License"):
            st.markdown(f"<div class='license'>{create_license()}</div>", unsafe_allow_html=True)

else:
    st.markdown("<h2 style='color:#fff; text-align:center;'>AirGuard Pro - Live Air Quality</h2>", unsafe_allow_html=True)
    if st.sidebar.button("Logout"):
        st.session_state.valid = False
        st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        lat = st.text_input("Latitude", value="35.6892", help="Example: Tehran → 35.6892")
    with col2:
        lon = st.text_input("Longitude", value="51.3890", help="Example: Tehran → 51.3890")

    if st.button("Get Live Report", type="primary", use_container_width=True):
        with st.spinner("Fetching real-time data..."):
            current, forecast = fetch_air_quality(lat, lon)
            
            if not current or not forecast:
                st.error("Invalid coordinates or no data available for this location.")
                st.stop()

            c = current['list'][0]['components']

            # محاسبه AQI دقیق بر اساس استاندارد EPA (US AQI)
            def calculate_aqi(concentration, breakpoints):
                for (low, high, aqi_low, aqi_high) in breakpoints:
                    if low <= concentration <= high:
                        return ((aqi_high - aqi_low) / (high - low)) * (concentration - low) + aqi_low
                return 0

            # Breakpoints استاندارد EPA
            pm25_bp = [(0, 12, 0, 50), (12.1, 35.4, 51, 100), (35.5, 55.4, 101, 150), (55.5, 150.4, 151, 200), (150.5, 250.4, 201, 300), (250.5, 500, 301, 500)]
            pm10_bp = [(0, 54, 0, 50), (55, 154, 51, 100), (155, 254, 101, 150), (255, 354, 151, 200), (355, 424, 201, 300), (425, 604, 301, 500)]
            o3_bp = [(0, 54, 0, 50), (55, 70, 51, 100), (71, 85, 101, 150), (86, 105, 151, 200), (106, 200, 201, 300)]
            no2_bp = [(0, 53, 0, 50), (54, 100, 51, 100), (101, 360, 101, 150), (361, 649, 151, 200), (650, 1249, 201, 300), (1250, 2049, 301, 500)]
            
            pm25_aqi = calculate_aqi(c['pm2_5'], pm25_bp)
            pm10_aqi = calculate_aqi(c['pm10'], pm10_bp)
            o3_aqi = calculate_aqi(c['o3'] * 1000, o3_bp)  # ppb
            no2_aqi = calculate_aqi(c['no2'], no2_bp)

            aqi = max(pm25_aqi, pm10_aqi, o3_aqi, no2_aqi, 0)
            aqi = int(round(aqi))

            levels = ["Good", "Moderate", "Unhealthy for Sensitive Groups", "Unhealthy", "Very Unhealthy", "Hazardous"]
            colors = ["#00e400", "#ffff00", "#ff7e00", "#ff0000", "#8f3f97", "#7e0023"]
            level = levels[min(aqi // 51, 5)]
            color = colors[min(aqi // 51, 5)]

            st.markdown(f"<h1 style='text-align:center; color:{color}; font-size:4rem; margin:30px 0;'>{level}</h1>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align:center; color:#fff; font-size:2.5rem;'>AQI {aqi}</h2>", unsafe_allow_html=True)

            # آلاینده‌ها با واحد درست
            cols = st.columns(6)
            data = [
                ("PM2.5", f"{c['pm2_5']:.1f}", "µg/m³"),
                ("PM10", f"{c['pm10']:.1f}", "µg/m³"),
                ("CO", f"{c['co']:.0f}", "µg/m³"),
                ("NO₂", f"{c['no2']:.1f}", "µg/m³"),
                ("O₃", f"{c['o3']*1000:.1f}", "ppb"),
                ("SO₂", f"{c['so2']:.1f}", "µg/m³")
            ]
            for i, (name, val, unit) in enumerate(data):
                with cols[i]:
                    st.metric(name, val, delta=unit)

            # نمودار پیش‌بینی واقعی
            forecast_list = forecast['list'][:48]
            times = [datetime.fromtimestamp(item['dt']) for item in forecast_list]
            forecast_aqi = []
            for item in forecast_list:
                comp = item['components']
                aqi_val = max(
                    calculate_aqi(comp['pm2_5'], pm25_bp),
                    calculate_aqi(comp['pm10'], pm10_bp),
                    calculate_aqi(comp['o3'] * 1000, o3_bp),
                    calculate_aqi(comp['no2'], no2_bp)
                )
                forecast_aqi.append(int(round(aqi_val)))

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=times, y=forecast_aqi, mode='lines+markers', line=dict(color='#ff4757', width=4), marker=dict(size=6)))
            fig.update_layout(
                title="48-Hour AQI Forecast",
                template="plotly_dark",
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Time",
                yaxis_title="AQI"
            )
            st.plotly_chart(fig, use_container_width=True)

st.caption("AirGuard Pro © 2025 - Powered by OpenWeatherMap | Real-time Global AQI")
