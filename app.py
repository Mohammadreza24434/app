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
                return True, f"{20 - d} days left"
        return False
    except:
        return False

# ==================== دریافت داده ====================
@st.cache_data(ttl=300, show_spinner=False)
def get_air_data(lat, lon):
    try:
        current = requests.get(f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1", timeout=10).json()
        forecast = requests.get(f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1", timeout=10).json()
        if 'list' in current and 'list' in forecast:
            return current['list'][0], forecast['list'][:48]
    except:
        pass
    return None, None

# ==================== محاسبه AQI دقیق ====================
def calc_aqi(val, bp):
    for lo, hi, a_lo, a_hi in bp:
        if lo <= val <= hi:
            return int(a_lo + (a_hi - a_lo) * (val - lo) / (hi - lo))
    return 500 if val > bp[-1][1] else 0

pm25_bp = [(0,12,0,50), (12.1,35.4,51,100), (35.5,55.4,101,150), (55.5,150.4,151,200), (150.5,250.4,201,300), (250.5,999,301,500)]
pm10_bp = [(0,54,0,50), (55,154,51,100), (155,254,101,150), (255,354,151,200), (355,424,201,300), (425,999,301,500)]
o3_bp   = [(0,54,0,50), (55,70,51,100), (71,85,101,150), (86,105,151,200), (106,200,201,300)]
no2_bp  = [(0,53,0,50), (54,100,51,100), (101,360,101,150), (361,649,151,200), (650,1249,201,300), (1250,9999,301,500)]

# ==================== تم حرفه‌ای + اعداد ۱۰۰٪ خوانا ====================
st.set_page_config(page_title="AirGuard Pro", page_icon="🌍", layout="centered")

st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); min-height: 100vh; padding: 20px; color: white;}
    .title {font-size: 5.5rem; text-align: center; font-weight: 900; background: linear-gradient(90deg, #00ff88, #00f5ff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 20px 0;}
    .subtitle {text-align: center; color: #88ffaa; font-size: 1.8rem; margin-top: -15px;}
    .aqi-value {font-size: 9rem; font-weight: 900; text-align: center; color: #ff4757; margin: 30px 0;}
    .aqi-level {font-size: 4.5rem; font-weight: bold; text-align: center; margin: 15px 0;}
    
    /* کارت‌های آلاینده — کاملاً خوانا */
    .pollutant-container {display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin: 50px 0;}
    .pollutant-card {
        background: rgba(255,255,255,0.12); backdrop-filter: blur(15px); border-radius: 20px;
        padding: 25px 30px; width: 140px; text-align: center; border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    .pollutant-name {font-size: 1.2rem; color: #00ff88; font-weight: bold; margin-bottom: 10px;}
    .pollutant-value {font-size: 3rem; font-weight: 900; color: white !important; margin: 10px 0;}
    .pollutant-unit {font-size: 1.1rem; color: #88ffaa;}
    
    .stButton>button {background: linear-gradient(45deg, #ff6b6b, #ffb142); border: none; border-radius: 50px;
                     height: 70px; font-size: 1.7rem; font-weight: bold; color: white; width: 100%;}
</style>
""", unsafe_allow_html=True)

# ==================== صفحه اصلی ====================
if 'valid' not in st.session_state:
    st.session_state.valid = False

if not st.session_state.valid:
    # صفحه لایسنس (همون قبلی)
    st.markdown("<h1 class='title'>AirGuard Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Live Global Air Quality Monitor</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='background:rgba(255,255,255,0.1);backdrop-filter:blur(20px);padding:50px;border-radius:25px;text-align:center;border:1px solid rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
        code = st.text_input("Enter License Key", type="password", placeholder="AG25-XXXX-XXXX-XXXX")
        if st.button("Activate License"):
            if check_license(code):
                st.session_state.valid = True
                st.success("Activated Successfully!")
                st.balloons()
                st.rerun()
            else:
                st.error("Invalid or expired key")
        st.markdown("</div>", unsafe_allow_html=True)
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
        with st.spinner("Loading real-time data..."):
            current, forecast = get_air_data(lat, lon)
            if not current:
                st.error("No data for this location.")
                st.stop()

            c = current['components']

            # AQI واقعی و دقیق
            aqi_pm25 = calc_aqi(c['pm2_5'], pm25_bp)
            aqi_pm10 = calc_aqi(c['pm10'], pm10_bp)
            aqi_o3   = calc_aqi(c['o3'] * 1000, o3_bp)
            aqi_no2  = calc_aqi(c['no2'], no2_bp)
            aqi = max(aqi_pm25, aqi_pm10, aqi_o3, aqi_no2)

            levels = ["Good", "Moderate", "Unhealthy for Sensitive", "Unhealthy", "Very Unhealthy", "Hazardous"]
            colors = ["#00e400", "#ffff00", "#ff7e00", "#ff0000", "#8f3f97", "#7e0023"]
            idx = min(aqi // 51, 5)

            st.markdown(f"<div class='aqi-level' style='color:{colors[idx]}'>{levels[idx]}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='aqi-value'>{aqi}</div>", unsafe_allow_html=True)

            # آلاینده‌ها — ۱۰۰٪ خوانا و زیبا
            st.markdown("<div class='pollutant-container'>", unsafe_allow_html=True)
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
            times = [datetime.fromtimestamp(x['dt']).strftime("%H:%M %b %d") for x in forecast]
            forecast_aqi = []
            for item in forecast:
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
                marker=dict(size=8),
                fillcolor='rgba(255,71,87,0.2)',
                fill='tozeroy'
            ))
            fig.update_layout(
                title="48-Hour AQI Forecast",
                template="plotly_dark",
                height=500,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="white")
            )
            st.plotly_chart(fig, use_container_width=True)

st.caption("AirGuard Pro © 2025 — Premium Real-time Global Air Quality Monitor")
