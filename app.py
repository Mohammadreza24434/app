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

# ==================== تم حرفه‌ای + خوانایی کامل ====================
st.set_page_config(page_title="AirGuard Pro", page_icon="🌍", layout="centered")

st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); min-height: 100vh; padding: 20px; color: white;}
    .title {font-size: 5.5rem; text-align: center; font-weight: 900; background: linear-gradient(90deg, #00ff88, #00f5ff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;}
    .subtitle {text-align: center; color: #88ffaa; font-size: 1.8rem; margin-bottom: 40px;}
    
    .aqi-big {font-size: 10rem; text-align: center; font-weight: 900; color: #ff4757; margin: 30px 0 10px 0;}
    .aqi-level {font-size: 4rem; text-align: center; font-weight: bold; margin-bottom: 40px;}
    
    .pollutants-bar {
        background: rgba(255,255,255,0.12); border-radius: 25px; padding: 20px; text-align: center;
        margin: 30px 0; backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.2);
        font-size: 1.8rem; font-weight: bold;
    }
    .pollutant {display: inline-block; margin: 0 30px;}
    .p-name {color: #00ff88; font-size: 1.4rem;}
    .p-value {color: black; background: white; padding: 8px 18px; border-radius: 12px; font-size: 2rem; font-weight: 900; margin: 8px 0;}
    .p-unit {color: #88ffaa; font-size: 1.2rem;}

    .stButton>button {background: linear-gradient(45deg, #ff6b6b, #ffb142); border: none; border-radius: 50px;
                     height: 70px; font-size: 1.7rem; font-weight: bold; color: white;}
    .license-box {background: rgba(255,255,255,0.1); backdrop-filter: blur(20px); padding: 50px; border-radius: 25px;
                  text-align: center; border: 1px solid rgba(255,255,255,0.2); max-width: 500px; margin: 50px auto;}
</style>
""", unsafe_allow_html=True)

# ==================== لایسنس ====================
if 'valid' not in st.session_state:
    st.session_state.valid = False

if not st.session_state.valid:
    st.markdown("<h1 class='title'>AirGuard Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Live Global Air Quality Monitor</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='license-box'>", unsafe_allow_html=True)
    code = st.text_input("Enter License Key", type="password", placeholder="AG25-XXXX-XXXX-XXXX to activate")
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
    st.stop()

# ==================== صفحه اصلی ====================
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
        try:
            url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1"
            data = requests.get(url, timeout=10).json()['list']
            current = data[0]['components']
            forecast = data[:48]
        except:
            st.error("No data for this location.")
            st.stop()

        # محاسبه AQI دقیق
        def calc(val, bp):
            for lo, hi, a_lo, a_hi in bp:
                if lo <= val <= hi:
                    return int(a_lo + (a_hi - a_lo) * (val - lo) / (hi - lo))
            return 500 if val > bp[-1][1] else 0

        aqi_pm25 = calc(current['pm2_5'], [(0,12,0,50),(12.1,35.4,51,100),(35.5,55.4,101,150),(55.5,150.4,151,200),(150.5,250.4,201,300),(250.5,999,301,500)])
        aqi_pm10 = calc(current['pm10'],  [(0,54,0,50),(55,154,51,100),(155,254,101,150),(255,354,151,200),(355,424,201,300),(425,999,301,500)])
        aqi_o3   = calc(current['o3']*1000, [(0,54,0,50),(55,70,51,100),(71,85,101,150),(86,105,151,200),(106,200,201,300)])
        aqi_no2  = calc(current['no2'],   [(0,53,0,50),(54,100,51,100),(101,360,101,150),(361,649,151,200),(650,1249,201,300),(1250,9999,301,500)])

        aqi = max(aqi_pm25, aqi_pm10, aqi_o3, aqi_no2)

        levels = ["Good", "Moderate", "Unhealthy for Sensitive", "Unhealthy", "Very Unhealthy", "Hazardous"]
        colors = ["#00e400", "#ffff00", "#ff7e00", "#ff0000", "#8f3f97", "#7e0023"]
        idx = min(aqi // 51, 5)

        st.markdown(f"<div class='aqi-level' style='color:{colors[idx]}'>{levels[idx]}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='aqi-big'>{aqi}</div>", unsafe_allow_html=True)

        # ترکیبات شیمیایی — عدد بزرگ و مشکی
        st.markdown(f"""
        <div class='pollutants-bar'>
            <div class='pollutant'>
                <div class='p-name'>PM2.5</div>
                <div class='p-value'>{current['pm2_5']:.1f}</div>
                <div class='p-unit'>µg/m³</div>
            </div>
            <div class='pollutant'>
                <div class='p-name'>PM10</div>
                <div class='p-value'>{current['pm10']:.1f}</div>
                <div class='p-unit'>µg/m³</div>
            </div>
            <div class='pollutant'>
                <div class='p-name'>O₃</div>
                <div class='p-value'>{current['o3']*1000:.1f}</div>
                <div class='p-unit'>ppb</div>
            </div>
            <div class='pollutant'>
                <div class='p-name'>NO₂</div>
                <div class='p-value'>{current['no2']:.1f}</div>
                <div class='p-unit'>µg/m³</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # نمودار پیش‌بینی — کاملاً واقعی و دقیق
        times = [datetime.fromtimestamp(x['dt']).strftime("%H:%M") for x in forecast[::2]]
        forecast_aqi = []
        for item in forecast[::2]:
            c = item['components']
            val = max(
                calc(c['pm2_5'], [(0,12,0,50),(12.1,35.4,51,100),(35.5,55.4,101,150),(55.5,150.4,151,200),(150.5,250.4,201,300),(250.5,999,301,500)]),
                calc(c['pm10'],  [(0,54,0,50),(55,154,51,100),(155,254,101,150),(255,354,151,200),(355,424,201,300),(425,999,301,500)]),
                calc(c['o3']*1000, [(0,54,0,50),(55,70,51,100),(71,85,101,150),(86,105,151,200),(106,200,201,300)]),
                calc(c['no2'],   [(0,53,0,50),(54,100,51,100),(101,360,101,150),(361,649,151,200),(650,1249,201,300),(1250,9999,301,500)])
            )
            forecast_aqi.append(val)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times, y=forecast_aqi,
            mode='lines+markers',
            line=dict(color='#ff4757', width=6),
            marker=dict(size=10),
            fill='tozeroy',
            fillcolor='rgba(255,71,87,0.2)'
        ))
        fig.update_layout(
            title="48-Hour AQI Forecast",
            height=500,
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            xaxis=dict(tickangle=0)
        )
        st.plotly_chart(fig, use_container_width=True)

st.caption("AirGuard Pro © 2025 — Premium Real-time Global Air Quality Monitor")
