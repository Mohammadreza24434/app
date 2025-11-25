import streamlit as st
import requests
from datetime import datetime, timedelta
import hashlib
import plotly.graph_objects as go

# ==================== لایسنس ====================
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

# ==================== دریافت داده ====================
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

# ==================== محاسبه AQI دقیق ====================
def calc_aqi(val, bp):
    for lo, hi, a_lo, a_hi in bp:
        if lo <= val <= hi:
            return round(a_lo + (a_hi - a_lo) * (val - lo) / (hi - lo))
    return 500 if val > bp[-1][1] else 0

pm25_bp = [(0,12,0,50),(12.1,35.4,51,100),(35.5,55.4,101,150),(55.5,150.4,151,200),(150.5,250.4,201,300),(250.5,500,301,500)]
pm10_bp = [(0,54,0,50),(55,154,51,100),(155,254,101,150),(255,354,151,200),(355,424,201,300),(425,604,301,500)]
o3_bp   = [(0,54,0,50),(55,70,51,100),(71,85,101,150),(86,105,151,200),(106,200,201,300)]
no2_bp  = [(0,53,0,50),(54,100,51,100),(101,360,101,150),(361,649,151,200),(650,1249,201,300),(1250,2049,301,500)]

# ==================== تم فوق حرفه‌ای ====================
st.set_page_config(page_title="AirGuard Pro", page_icon="🌍", layout="centered")

st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); min-height: 100vh; padding: 20px; color: white;}
    .title {font-size: 5.5rem; text-align: center; font-weight: 900; background: linear-gradient(90deg, #00ff88, #00f5ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;}
    .subtitle {text-align: center; color: #88ffaa; font-size: 1.7rem; margin-top: -10px;}
    
    .aqi-big {font-size: 8rem; font-weight: 900; text-align: center; margin: 20px 0;}
    .level-text {font-size: 4.5rem; font-weight: bold; text-align: center; margin: 10px 0;}
    
    .pollutant-grid {display: grid; grid-template-columns: repeat(6, 1fr); gap: 20px; margin: 40px 0;}
    .pollutant-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .pollutant-name {font-size: 1.1rem; color: #cccccc; margin-bottom: 8px;}
    .pollutant-value {font-size: 2.8rem; font-weight: bold; color: white; margin: 10px 0;}
    .pollutant-unit {font-size: 1rem; color: #88ffaa;}
    
    .stButton>button {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        border: none;
        border-radius: 50px;
        height: 70px;
        font-size: 1.6rem;
        font-weight: bold;
        color: white;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ==================== لایسنس ====================
if 'valid' not in st.session_state:
    st.session_state.valid = False

if not st.session_state.valid:
    st.markdown("<h1 class='title'>AirGuard Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Live Global Air Quality Monitor</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='background: rgba(255,255,255,0.1); backdrop-filter: blur(20px); padding: 40px; border-radius: 25px; text-align: center; border: 1px solid rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
        st.markdown("### Premium 20-Day License — 200,000 IRR")
        code = st.text_input("Enter License Key", type="password", placeholder="AG25-XXXX-XXXX-XXXX")
        if st.button("Activate License"):
            ok, msg = check_license(code)
            if ok:
                st.session_state.valid = True
                st.success(f"✓ Activated! {msg}")
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
            st.code(create_license(), language="text")

else:
    st.markdown("<h1 class='title'>AirGuard Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Live Global Air Quality Monitor</p>", unsafe_allow_html=True)
    
    if st.sidebar.button("Logout"):
        st.session_state.valid = False
        st.rerun()

    col1, col2 = st.columns([1, 1])
    with col1:
        lat = st.text_input("Latitude", "35.6892", key="lat_input")
    with col2:
        lon = st.text_input("Longitude", "51.3890", key="lon_input")

    if st.button("Get Live Report", type="primary"):
        with st.spinner("Fetching real-time data..."):
            current_item, forecast_list = get_air_data(lat, lon)
            if not current_item:
                st.error("No data available for this location.")
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

            st.markdown(f"<div class='level-text' style='color:{color};'>{level}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='aqi-big' style='color:{color};'>{aqi}</div>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align:center; color:#cccccc;'>Current AQI</h3>", unsafe_allow_html=True)

            # آلاینده‌ها — کاملاً مرتب و حرفه‌ای
            st.markdown("<div class='pollutant-grid'>", unsafe_allow_html=True)
            pollutants = [
                ("PM2.5", f"{c['pm2_5']:.1f}", "µg/m³"),
                ("PM10", f"{c['pm10']:.1f}", "µg/m³"),
                ("CO", f"{c['co']:.0f}", "µg/m³"),
                ("NO₂", f"{c['no2']:.1f}", "µg/m³"),
                ("O₃", f"{c['o3']*1000:.1f}", "ppb"),
                ("SO₂", f"{c['so2']:.1f}", "µg/m³")
            ]
            for name, value, unit in pollutants:
                st.markdown(f"""
                <div class='pollutant-card'>
                    <div class='pollutant-name'>{name}</div>
                    <div class='pollutant-value'>{value}</div>
                    <div class='pollutant-unit'>{unit}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # نمودار پیش‌بینی — کاملاً واقعی و پویا
            times = [datetime.fromtimestamp(x['dt']) for x in forecast_list]
            forecast_aqi = []
            for x in forecast_list:
                comp = x['components']
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
                marker=dict(size=8, color='#ff6b6b'),
                fill='tozeroy',
                fillcolor='rgba(255,71,87,0.15)'
            ))
            fig.update_layout(
                title="48-Hour AQI Forecast",
                template="plotly_dark",
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#ffffff", size=14)
            )
            st.plotly_chart(fig, use_container_width=True)

st.caption("AirGuard Pro © 2025 — Premium Real-time Global Air Quality Monitor")
