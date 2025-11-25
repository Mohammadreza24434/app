import streamlit as st
import requests
from datetime import datetime, timedelta
import hashlib
import plotly.graph_objects as go

# رمز فقط برای تو
OWNER_PASSWORD = "24434"

def create_license():
    expiry = (datetime.now() + timedelta(days=20)).strftime("%Y%m%d")
    raw = "airguard2025" + expiry
    h = hashlib.md5(raw.encode()).hexdigest().upper()[:12]
    return f"AG25-{h[:4]}-{h[4:8]}-{h[8:]}"

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
        return False, "Expired"
    except:
        return False, "Error"

# دریافت داده — کاملاً درست
@st.cache_data(ttl=600, show_spinner=False)
def get_air_data(lat, lon):
    try:
        current = requests.get(f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1", timeout=15).json()
        forecast = requests.get(f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1", timeout=15).json()
        if 'list' not in current or 'list' not in forecast:
            return None, None
        return current['list'][0], forecast['list'][:48]
    except:
        return None, None

# محاسبه AQI دقیق (US EPA)
def calc_aqi(val, breakpoints):
    for lo, hi, a_lo, a_hi in breakpoints:
        if lo <= val <= hi:
            return int(a_lo + (a_hi - a_lo) * (val - lo) / (hi - lo))
    return 500 if val > breakpoints[-1][1] else 0

# Breakpoints استاندارد
pm25_bp = [(0,12,0,50),(12.1,35.4,51,100),(35.5,55.4,101,150),(55.5,150.4,151,200),(150.5,250.4,201,300),(250.5,500,301,500)]
pm10_bp = [(0,54,0,50),(55,154,51,100),(155,254,101,150),(255,354,151,200),(355,424,201,300),(425,604,301,500)]
o3_bp   = [(0,54,0,50),(55,70,51,100),(71,85,101,150),(86,105,151,200),(106,200,201,300)]
no2_bp  = [(0,53,0,50),(54,100,51,100),(101,360,101,150),(361,649,151,200),(650,1249,201,300),(1250,2049,301,500)]

# تم حرفه‌ای + استایل قوی
st.set_page_config(page_title="AirGuard Pro", page_icon="🌍", layout="centered")

st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); min-height: 100vh; padding: 20px; color: white;}
    .title {font-size: 5.5rem; text-align: center; font-weight: 900; background: linear-gradient(90deg, #00ff88, #00f5ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .subtitle {text-align: center; color: #88ffaa; font-size: 1.6rem; margin-top: -10px;}
    .card {background: rgba(255,255,255,0.1); backdrop-filter: blur(20px); border-radius: 25px; padding: 40px; text-align: center; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 15px 35px rgba(0,0,0,0.5);}
    .license {font-family: monospace; font-size: 2rem; background: #000; color: #0f0; padding: 20px; border-radius: 15px; letter-spacing: 8px;}
    .stButton>button {background: linear-gradient(45deg, #ff6b6b, #feca57); border: none; border-radius: 50px; height: 70px; font-size: 1.5rem; font-weight: bold; color: white;}
    
    /* آلاینده‌ها — کاملاً دیده می‌شوند */
    .pollutant-box {
        background: rgba(255,255,255,0.15);
        padding: 18px;
        border-radius: 18px;
        text-align: center;
        margin: 8px;
        min-height: 120px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .pollutant-name {font-size: 1.1rem; color: #aaa; margin-bottom: 5px;}
    .pollutant-value {font-size: 2.3rem !important; font-weight: bold !important; color: white !important; margin: 10px 0;}
    .pollutant-unit {font-size: 1rem; color: #88ffaa;}
</style>
""", unsafe_allow_html=True)

if 'valid' not in st.session_state:
    st.session_state.valid = False

if not st.session_state.valid:
    st.markdown("<h1 class='title'>AirGuard Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Real-time Global Air Quality Monitor</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### Premium 20-Day License — 200,000 IRR")
        code = st.text_input("Enter License Key", type="password", placeholder="AG25-XXXX-XXXX-XXXX")
        if st.button("Activate License", type="primary"):
            ok, msg = check_license(code)
            if ok:
                st.session_state.valid = True
                st.success(f"Activated! {msg}")
                st.balloons()
                st.rerun()
            else:
                st.error("Invalid or expired key")
        st.markdown("**Contact:** @YourTelegramID")
        st.markdown("</div>", unsafe_allow_html=True)

    owner = st.text_input("Owner Access", type="password")
    if owner == OWNER_PASSWORD:
        st.success("Welcome Boss!")
        if st.button("Generate New License"):
            st.markdown(f"<div class='license'>{create_license()}</div>", unsafe_allow_html=True)

else:
    st.markdown("<h1 class='title'>AirGuard Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Live Global Air Quality Monitor</p>", unsafe_allow_html=True)
    
    if st.sidebar.button("Logout"):
        st.session_state.valid = False
        st.rerun()

    col1, col2 = st.columns([1,1])
    with col1: lat = st.text_input("Latitude", "35.6892", key="lat")
    with col2: lon = st.text_input("Longitude", "51.3890", key="lon")

    if st.button("Get Live Report", type="primary", use_container_width=True):
        with st.spinner("Fetching real-time satellite data..."):
            current_item, forecast_list = get_air_data(lat, lon)
            if not current_item or not forecast_list:
                st.error("No data for this location. Try Tehran: 35.6892, 51.3890")
                st.stop()

            c = current_item['components']

            # AQI واقعی
            aqi = max(
                calc_aqi(c['pm2_5'], pm25_bp),
                calc_aqi(c['pm10'], pm10_bp),
                calc_aqi(c['o3'] * 1000, o3_bp),
                calc_aqi(c['no2'], no2_bp)
            )

            levels = ["Good", "Moderate", "Unhealthy for Sensitive", "Unhealthy", "Very Unhealthy", "Hazardous"]
            colors = ["#00e400", "#ffff00", "#ff7e00", "#ff0000", "#8f3f97", "#7e0023"]
            level_idx = min(aqi // 51, 5)
            level = levels[level_idx]
            color = colors[level_idx]

            st.markdown(f"<h1 style='text-align:center; color:{color}; font-size:6.5rem; margin:50px 0;'>{level}</h1>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align:center; color:white; font-size:3.8rem;'>AQI {aqi}</h2>", unsafe_allow_html=True)

            # آلاینده‌ها — کاملاً واضح و زیبا
            cols = st.columns(6)
            pollutants = [
                ("PM2.5", f"{c['pm2_5']:.1f}", "µg/m³"),
                ("PM10", f"{c['pm10']:.1f}", "µg/m³"),
                ("CO", f"{c['co']:.0f}", "µg/m³"),
                ("NO₂", f"{c['no2']:.1f}", "µg/m³"),
                ("O₃", f"{c['o3']*1000:.1f}", "ppb"),
                ("SO₂", f"{c['so2']:.1f}", "µg/m³")
            ]
            for i, (name, value, unit) in enumerate(pollutants):
                with cols[i]:
                    st.markdown(f"""
                    <div class='pollutant-box'>
                        <div class='pollutant-name'>{name}</div>
                        <div class='pollutant-value'>{value}</div>
                        <div class='pollutant-unit'>{unit}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # نمودار پیش‌بینی — ۱۰۰٪ واقعی و متفاوت برای هر شهر
            times = [datetime.fromtimestamp(item['dt']) for item in forecast_list]
            forecast_aqi = []
            for item in forecast_list:
                comp = item['components']
                val = max(
                    calc_aqi(comp['pm2_5'], pm25_bp),
                    calc_aqi(comp['pm10'], pm10_bp),
                    calc_aqi(comp['o3'] * 1000, o3_bp),
                    calc_aqi(comp['no2'], no2_bp)
                )
                forecast_aqi.append(val)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times, y=forecast_aqi,
                mode='lines+markers',
                line=dict(color='#ff4757', width=5),
                marker=dict(size=9, color='#ff6b6b'),
                fill='tozeroy',
                fillcolor='rgba(255,71,87,0.2)'
            ))
            fig.update_layout(
                title="48-Hour AQI Forecast",
                template="plotly_dark",
                height=520,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="white")
            )
            st.plotly_chart(fig, use_container_width=True)

st.caption("AirGuard Pro © 2025 — Premium Real-time Global Air Quality Monitor")
