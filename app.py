import streamlit as st
import requests
from datetime import datetime, timedelta
import hashlib
import plotly.graph_objects as go

# ==================== لایسنس (برگشت!) ====================
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

# ==================== تم تیره + گزارش ساده و خوانا ====================
st.set_page_config(page_title="AirGuard Pro", page_icon="🌍", layout="centered")

st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); min-height: 100vh; padding: 20px; color: white;}
    .title {font-size: 5.5rem; text-align: center; font-weight: 900; background: linear-gradient(90deg, #00ff88, #00f5ff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .subtitle {text-align: center; color: #88ffaa; font-size: 1.8rem; margin-top: -15px;}
    .aqi-value {font-size: 9rem; font-weight: 900; text-align: center; color: #ff4757; margin: 30px 0;}
    .aqi-level {font-size: 4.5rem; font-weight: bold; text-align: center;}

    /* کارت ساده و کاملاً خوانا */
    .pollutant-card {
        background: rgba(255,255,255,0.12);
        border-radius: 25px;
        padding: 30px;
        text-align: center;
        margin: 15px 0;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    .pollutant-name {font-size: 1.8rem; color: #00ff88; font-weight: bold; margin-bottom: 15px;}
    .pollutant-value {font-size: 4.5rem; font-weight: 900; color: white; margin: 15px 0;}
    .pollutant-unit {font-size: 1.4rem; color: #88ffaa;}

    .stButton>button {background: linear-gradient(45deg, #ff6b6b, #ffb142); border: none; border-radius: 50px;
                     height: 70px; font-size: 1.7rem; font-weight: bold; color: white;}
    .license-box {background: rgba(255,255,255,0.1); backdrop-filter: blur(20px); padding: 50px; border-radius: 25px;
                  text-align: center; border: 1px solid rgba(255,255,255,0.2); max-width: 500px; margin: 50px auto;}
</style>
""", unsafe_allow_html=True)

# ==================== وضعیت لایسنس ====================
if 'valid' not in st.session_state:
    st.session_state.valid = False

# ==================== صفحه لایسنس ====================
if not st.session_state.valid:
    st.markdown("<h1 class='title'>AirGuard Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Live Global Air Quality Monitor</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='license-box'>", unsafe_allow_html=True)
    st.markdown("### Premium 20-Day License")
    code = st.text_input("Enter License Key", type="password", placeholder="AG25-XXXX-XXXX-XXXX")
    if st.button("Activate License"):
        if check_license(code):
            st.session_state.valid = True
            st.success("Activated Successfully! 🎉")
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

    st.stop()

# ==================== صفحه اصلی (گزارش ساده و خوانا) ====================
st.markdown("<h1 class='title'>AirGuard Pro</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Live Global Air Quality Monitor</p>", unsafe_allow_html=True)

if st.sidebar.button("Logout"):
    st.session_state.valid = False
    st.rerun()

col1, col2 = st.columns(2)
with col1: lat = st.text_input("Latitude", "35.6892")
with col2: lon = st.text_input("Longitude", "51.6890")

if st.button("Get Live Report", type="primary", use_container_width=True):
    with st.spinner("Loading real-time data..."):
        try:
            url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1"
            data = requests.get(url, timeout=10).json()['list']
            current = data[0]['components']
            forecast = data[:48]
        except:
            st.error("No data available for this location.")
            st.stop()

        # محاسبه AQI
        def calc(val, bp):
            for lo, hi, a_lo, a_hi in bp:
                if lo <= val <= hi:
                    return int(a_lo + (a_hi - a_lo) * (val - lo) / (hi - lo))
            return 500 if val > bp[-1][1] else 0

        aqi = max(
            calc(current['pm2_5'], [(0,12,0,50),(12.1,35.4,51,100),(35.5,55.4,101,150),(55.5,150.4,151,200),(150.5,250.4,201,300),(250.5,999,301,500)]),
            calc(current['pm10'],  [(0,54,0,50),(55,154,51,100),(155,254,101,150),(255,354,151,200),(355,999,201,500)]),
            calc(current['o3']*1000, [(0,54,0,50),(55,70,51,100),(71,85,101,150),(86,105,151,200),(106,200,201,300)]),
            calc(current['no2'],   [(0,53,0,50),(54,100,51,100),(101,360,101,150),(361,649,151,200),(650,9999,201,500)])
        )

        levels = ["Good", "Moderate", "Unhealthy for Sensitive", "Unhealthy", "Very Unhealthy", "Hazardous"]
        colors = ["#00e400", "#ffff00", "#ff7e00", "#ff0000", "#8f3f97", "#7e0023"]
        idx = min(aqi // 51, 5)

        st.markdown(f"<div class='aqi-level' style='color:{colors[idx]}'>{levels[idx]}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='aqi-value'>{aqi}</div>", unsafe_allow_html=True)

        # گزارش ساده و خوانا (هر آلاینده یک کارت جدا)
        pollutants = [
            ("PM2.5", f"{current['pm2_5']:.1f}", "µg/m³"),
            ("PM10",  f"{current['pm10']:.1f}",  "µg/m³"),
            ("CO",    f"{current['co']:.0f}",    "µg/m³"),
            ("NO₂",   f"{current['no2']:.1f}",   "µg/m³"),
            ("O₃",    f"{current['o3']*1000:.1f}", "ppb"),
            ("SO₂",   f"{current['so2']:.1f}",   "µg/m³")
        ]

        cols = st.columns(3)
        for i, (name, val, unit) in enumerate(pollutants):
            with cols[i % 3]:
                st.markdown(f"""
                <div class='pollutant-card'>
                    <div class='pollutant-name'>{name}</div>
                    <div class='pollutant-value'>{val}</div>
                    <div class='pollutant-unit'>{unit}</div>
                </div>
                """, unsafe_allow_html=True)

        # نمودار پیش‌بینی — سریع و واقعی
        times = [datetime.fromtimestamp(x['dt']).strftime("%H:%M") for x in forecast[::3]]
        forecast_aqi = []
        for x in forecast[::3]:
            c = x['components']
            val = max(
                calc(c['pm2_5'], [(0,12,0,50),(12.1,35.4,51,100),(35.5,55.4,101,150),(55.5,150.4,151,200),(150.5,250.4,201,300),(250.5,999,301,500)]),
                calc(c['pm10'],  [(0,54,0,50),(55,154,51,100),(155,254,101,150),(255,354,151,200),(355,999,201,500)])
            )
            forecast_aqi.append(val)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=forecast_aqi, mode='lines+markers',
                                line=dict(color='#ff4757', width=6), marker=dict(size=10),
                                fill='tozeroy', fillcolor='rgba(255,71,87,0.25)'))
        fig.update_layout(title="48-Hour AQI Forecast", height=450, template="plotly_dark",
                         plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)

st.caption("AirGuard Pro © 2025 — Premium Real-time Global Air Quality Monitor")
