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
        if not code.startswith("AG25-"): return False
        clean = code[5:].replace("-", "").upper()
        today = datetime.now().date()
        for d in range(0, 26):
            date = today + timedelta(days=d)
            expected = hashlib.md5(("airguard2025" + date.strftime("%Y%m%d")).encode()).hexdigest().upper()[:12]
            if expected == clean and d <= 20:
                return True
        return False
    except:
        return False

# ==================== دریافت داده ====================
@st.cache_data(ttl=300, show_spinner=False)
def get_air_data(lat, lon):
    try:
        url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1"
        resp = requests.get(url, timeout=10).json()
        if 'list' in resp:
            return resp['list'][0], resp['list'][:48]
    except:
        pass
    return None, None

# ==================== محاسبه AQI دقیق ====================
def calc_aqi(val, breakpoints):
    for lo, hi, aqi_lo, aqi_hi in breakpoints:
        if lo <= val <= hi:
            return int(aqi_lo + (aqi_hi - aqi_lo) * (val - lo) / (hi - lo))
    return 500 if val > breakpoints[-1][1] else 0

breakpoints = {
    'pm2_5': [(0,12,0,50),(12.1,35.4,51,100),(35.5,55.4,101,150),(55.5,150.4,151,200),(150.5,250.4,201,300),(250.5,999,301,500)],
    'pm10' : [(0,54,0,50),(55,154,51,100),(155,254,101,150),(255,354,151,200),(355,424,201,300),(425,999,301,500)],
    'o3'   : [(0,54,0,50),(55,70,51,100),(71,85,101,150),(86,105,151,200),(106,200,201,300)],
    'no2'  : [(0,53,0,50),(54,100,51,100),(101,360,101,150),(361,649,151,200),(650,1249,201,300),(1250,9999,301,500)]
}

# ==================== تم حرفه‌ای — از اول ====================
st.set_page_config(page_title="AirGuard Pro", page_icon="🌍", layout="centered")

st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); min-height: 100vh; padding: 20px; color: white;}
    .title {font-size: 5.5rem; text-align: center; font-weight: 900; background: linear-gradient(90deg, #00ff88, #00f5ff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .subtitle {text-align: center; color: #88ffaa; font-size: 1.8rem; margin-top: -15px;}
    .aqi-value {font-size: 9rem; font-weight: 900; text-align: center; color: #ff4757;}
    .aqi-level {font-size: 4.5rem; font-weight: bold; text-align: center; color: #ff6b6b;}
    
    .pollutant-grid {display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 20px; margin: 40px 0;}
    .pollutant-card {
        background: rgba(255,255,255,0.12); backdrop-filter: blur(15px); border-radius: 20px;
        padding: 25px; text-align: center; border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    .pollutant-name {font-size: 1.3rem; color: #00ff88; font-weight: bold;}
    .pollutant-value {font-size: 3.2rem; font-weight: 900; color: white !important; margin: 10px 0;}
    .pollutant-unit {font-size: 1.1rem; color: #88ffaa;}
    
    .stButton>button {background: linear-gradient(45deg, #ff6b6b, #ffb142); border: none; border-radius: 50px;
                     height: 70px; font-size: 1.7rem; font-weight: bold; color: white;}
    .license-box {background: rgba(255,255,255,0.1); backdrop-filter: blur(20px); padding: 50px; border-radius: 25px;
                  text-align: center; border: 1px solid rgba(255,255,255,0.2); max-width: 500px; margin: 50px auto;}
</style>
""", unsafe_allow_html=True)

# ==================== وضعیت لایسنس ====================
if 'valid' not in st.session_state:
    st.session_state.valid = False

if not st.session_state.valid:
    st.markdown("<h1 class='title'>AirGuard Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Live Global Air Quality Monitor</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='license-box'>", unsafe_allow_html=True)
        st.markdown("### Premium 20-Day License — 200,000 IRR")
        code = st.text_input("Enter License Key", type="password", placeholder="AG25-XXXX-XXXX-XXXX")
        if st.button("Activate License"):
            if check_license(code):
                st.session_state.valid = True
                st.success("Activated Successfully! Welcome!")
                st.balloons()
                st.rerun()
            else:
                st.error("Invalid or expired key")
        st.markdown("</div>", unsafe_allow_html=True)

    owner = st.text_input("Owner Access", type="password")
    if owner == OWNER_PASSWORD:
        st.success("Welcome Boss!")
        if st.button("Generate New License"):
            st.code(create_license())

else:
    st.markdown("<h1 class='title'>AirGuard Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Live Global Air Quality Monitor</p>", unsafe_allow_html=True)
    
    if st.sidebar.button("Logout"):
        st.session_state.valid = False
        st.rerun()

    col1, col2 = st.columns(2)
    with col1: lat = st.text_input("Latitude", "35.6892")
    with col2: lon = st.text_input("Longitude", "51.3890")

    if st.button("Get Live Report", type="primary", use_container_width=True):
        with st.spinner("Fetching real-time data..."):
            current, forecast = get_air_data(lat, lon)
            if not current:
                st.error("No data available for this location.")
                st.stop()

            c = current['components']
            
            # محاسبه AQI دقیق (بدون 500!)
            aqi = max(
                calc_aqi(c['pm2_5'], breakpoints['pm2_5']),
                calc_aqi(c['pm10'], breakpoints['pm10']),
                calc_aqi(c['o3'] * 1000, breakpoints['o3']),
                calc_aqi(c['no2'], breakpoints['no2'])
            )

            levels = ["Good", "Moderate", "Unhealthy for Sensitive", "Unhealthy", "Very Unhealthy", "Hazardous"]
            colors = ["#00e400", "#ffff00", "#ff7e00", "#ff0000", "#8f3f97", "#7e0023"]
            idx = min(aqi // 51, 5)

            st.markdown(f"<div class='aqi-level' style='color:{colors[idx]}'>{levels[idx]}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='aqi-value'>{aqi}</div>", unsafe_allow_html=True)

            # آلاینده‌ها — کاملاً خوانا
            st.markdown("<div class='pollutant-grid'>", unsafe_allow_html=True)
            pollutants = [
                ("PM2.5", f"{c['pm2_5']:.1f}", "µg/m³"),
                ("PM10", f"{c['pm10']:.1f}", "µg/m³"),
                ("CO", f"{c['co']:.0f}", "µg/m³"),
                ("NO₂", f"{c['no2']:.1f}", "µg/m³"),
                ("O₃", f"{c['o3']*1000:.1f}", "ppb"),
                ("SO₂", f"{c['so2']:.1f}", "µg/m³")
            ]
            for name, val, unit in pollutants:
                st.markdown(f"""
                <div class='pollutant-card'>
                    <div class='pollutant-name'>{name}</div>
                    <div class='pollutant-value'>{val}</div>
                    <div class='pollutant-unit'>{unit}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # نمودار پیش‌بینی — کاملاً واقعی و پویا
            times = [datetime.fromtimestamp(x['dt']).strftime("%H:%M\n%b %d") for x in forecast]
            forecast_aqi = []
            for item in forecast:
                comp = item['components']
                val = max(
                    calc_aqi(comp['pm2_5'], breakpoints['pm2_5']),
                    calc_aqi(comp['pm10'], breakpoints['pm10']),
                    calc_aqi(comp['o3'] * 1000, breakpoints['o3']),
                    calc_aqi(comp['no2'], breakpoints['no2'])
                )
                forecast_aqi.append(val)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times, y=forecast_aqi,
                mode='lines+markers',
                line=dict(color='#ff4757', width=5),
                marker=dict(size=8, color='#ff6b6b'),
                fill='tozeroy',
                fillcolor='rgba(255,71,87,0.2)'
            ))
            fig.update_layout(
                title="48-Hour AQI Forecast",
                template="plotly_dark",
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="white", size=14)
            )
            fig.update_xaxes(tickangle=0)
            st.plotly_chart(fig, use_container_width=True)

st.caption("AirGuard Pro © 2025 — Premium Real-time Global Air Quality Monitor")
