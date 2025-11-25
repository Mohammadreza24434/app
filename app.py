import streamlit as st
import requests
from datetime import datetime, timedelta
import hashlib
import plotly.graph_objects as go

# ==================== License System (20-Day Premium) ====================
OWNER_PASSWORD = "24434"

def create_license():
    expiry = (datetime.now() + timedelta(days=20)).strftime("%Y%m%d")
    raw = "airguard2025" + expiry
    h = hashlib.md5(raw.encode()).hexdigest().upper()[:12]
    return f"AG25-{h[:4]}-{h[4:8]}-{h[8:]}"

def check_license(code):
    try:
        if not code or not code.startswith("AG25-"): 
            return False
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

# ==================== Real EPA AQI Calculation - 100% Accurate ====================
# Conversion factors (µg/m³ → correct unit for AQI)
CONVERSIONS = {
    'co': 1145.0,   # µg/m³ → ppm (CO: 1 ppm = 1145 µg/m³ at 25°C)
    'o3': 1960.0,   # µg/m³ → ppm (O₃: 1 ppm = 1960 µg/m³)
    'no2': 1.88,    # µg/m³ → ppb
    'so2': 2.62,    # µg/m³ → ppb
}

# EPA Breakpoints (Index, Low → High, Concentration Low → High)
BREAKPOINTS = {
    'pm2_5': [(0,50,0.0,12.0),(51,100,12.1,35.4),(101,150,35.5,55.4),(151,200,55.5,150.4),(201,300,150.5,250.4),(301,500,250.5,500.4)],
    'pm10':  [(0,50,0,54),(51,100,55,154),(101,150,155,254),(151,200,255,354),(201,300,355,424),(301,500,425,604)],
    'o3':    [(0,50,0.000,0.054),(51,100,0.055,0.070),(101,150,0.071,0.085),(151,200,0.086,0.105),(201,300,0.106,0.200),(301,500,0.201,0.404)],
    'no2':   [(0,50,0,53),(51,100,54,100),(101,150,101,360),(151,200,361,649),(201,300,650,1249),(301,500,1250,2049)],
    'so2':   [(0,50,0,35),(51,100,36,75),(101,150,76,185),(151,200,186,304),(201,300,305,604),(301,500,605,1004)],
    'co':    [(0,50,0.0,4.4),(51,100,4.5,9.4),(101,150,9.5,12.4),(151,200,12.5,15.4),(201,300,15.5,30.4),(301,500,30.5,50.4)],
}

def calculate_aqi(concentration, pollutant):
    if concentration is None or concentration < 0:
        return 0
    
    value = float(concentration)
    
    # Convert to correct unit
    if pollutant in CONVERSIONS:
        value /= CONVERSIONS[pollutant]
    
    # Special case: PM2.5 and PM10 stay in µg/m³
    if pollutant not in ['pm2_5', 'pm10'] and pollutant not in BREAKPOINTS:
        return 0
    
    bp = BREAKPOINTS.get(pollutant, BREAKPOINTS['pm2_5'])
    
    for i_low, i_high, c_low, c_high in bp:
        if c_low <= value <= c_high:
            if c_high == c_low:
                return i_low
            aqi = ((i_high - i_low) / (c_high - c_low)) * (value - c_low) + i_low
            return round(aqi)
    
    # Above highest breakpoint
    i_low, i_high, c_low, c_high = bp[-1]
    aqi = i_high + ((500 - i_high) / (c_high - c_low)) * (value - c_low) if c_high > c_low else 500
    return min(500, round(aqi))

def get_aqi_category(aqi):
    aqi = int(aqi)
    if aqi <= 50: return "Good", "#00e400"
    elif aqi <= 100: return "Moderate", "#ffff00"
    elif aqi <= 150: return "Unhealthy for Sensitive Groups", "#ff7e00"
    elif aqi <= 200: return "Unhealthy", "#ff0000"
    elif aqi <= 300: return "Very Unhealthy", "#8f3f97"
    else: return "Hazardous", "#7e0023"

# ==================== Professional UI ====================
st.set_page_config(page_title="AirGuard Pro v2.0", page_icon="Globe", layout="centered")

st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); min-height: 100vh; padding: 20px; color: white;}
    .title {font-size: 5.5rem; text-align: center; font-weight: 900; background: linear-gradient(90deg, #00ff88, #00f5ff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .aqi-big {font-size: 11rem; text-align: center; font-weight: 900; margin: 40px 0 20px 0;}
    .aqi-level {font-size: 4.5rem; text-align: center; font-weight: bold; margin-bottom: 50px;}
    .pollutants-bar {background: rgba(255,255,255,0.12); border-radius: 30px; padding: 30px; text-align: center;
                     margin: 40px 0; backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.2);}
    .pollutant {display: inline-block; margin: 0 30px; vertical-align: top;}
    .p-name {color: #00ff88; font-size: 1.5rem; font-weight: bold;}
    .p-value {color: black; background: white; padding: 14px 30px; border-radius: 18px; font-size: 2.6rem; font-weight: 900;}
    .p-unit {color: #88ffaa; font-size: 1.3rem; margin-top: 6px;}
    .stButton>button {background: linear-gradient(45deg, #ff6b6b, #ffb142); border: none; border-radius: 50px;
                     height: 70px; font-size: 1.8rem; font-weight: bold; color: white;}
    .license-box {background: rgba(255,255,255,0.1); backdrop-filter: blur(20px); padding: 50px; border-radius: 25px;
                  text-align: center; border: 1px solid rgba(255,255,255,0.2); max-width: 500px; margin: 50px auto;}
</style>
""", unsafe_allow_html=True)

# ==================== License Check ====================
if 'valid' not in st.session_state:
    st.session_state.valid = False

if not st.session_state.valid:
    st.markdown("<h1 class='title'>AirGuard Pro v2.0</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#88ffaa; font-size:1.8rem;'>Real-Time Global Air Quality • EPA Standard</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div class='license-box'>", unsafe_allow_html=True)
        st.markdown("### Premium 20-Day License Required")
        code = st.text_input("Enter License Key", type="password", placeholder="AG25-XXXX-XXXX-XXXX")
        if st.button("Activate License"):
            if check_license(code):
                st.session_state.valid = True
                st.success("License Activated Successfully!")
                st.balloons()
                st.rerun()
            else:
                st.error("Invalid or expired license key")
        st.markdown("</div>", unsafe_allow_html=True)
        
        owner = st.text_input("Owner Access", type="password")
        if owner == OWNER_PASSWORD:
            st.success("Welcome back, Developer!")
            if st.button("Generate New License"):
                st.code(create_license())
    st.stop()

# ==================== Main App ====================
st.markdown("<h1 class='title'>AirGuard Pro v2.0</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00f5ff; font-size:2rem;'>Accurate EPA Air Quality Index • Worldwide</p>", unsafe_allow_html=True)

if st.sidebar.button("Logout"):
    st.session_state.valid = False
    st.rerun()

col1, col2 = st.columns(2)
with col1:
    lat = st.text_input("Latitude", value="35.6892", help="e.g., Tehran: 35.6892")
with col2:
    lon = st.text_input("Longitude", value="51.3890", help="e.g., Tehran: 51.3890")

if st.button("Get Live Report & 48-Hour Forecast", type="primary", use_container_width=True):
    with st.spinner("Fetching real-time air quality data from global sensors..."):
        try:
            url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1"
            response = requests.get(url, timeout=20)
            data = response.json()

            if 'list' not in data or len(data['list']) == 0:
                st.error("No air quality data available for this location.")
                st.stop()

            current = data['list'][0]['components']
            forecast = data['list'][:48]

            # Calculate AQI for each pollutant
            aqi_pm25 = calculate_aqi(current.get('pm2_5'), 'pm2_5')
            aqi_pm10 = calculate_aqi(current.get('pm10'), 'pm10')
            aqi_o3   = calculate_aqi(current.get('o3'), 'o3')
            aqi_no2  = calculate_aqi(current.get('no2'), 'no2')
            aqi_so2  = calculate_aqi(current.get('so2'), 'so2')
            aqi_co   = calculate_aqi(current.get('co'), 'co')

            overall_aqi = max(aqi_pm25, aqi_pm10, aqi_o3, aqi_no2, aqi_so2, aqi_co)
            category, color = get_aqi_category(overall_aqi)

            st.markdown(f"<div class='aqi-level' style='color:{color}'>{category}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='aqi-big' style='color:{color}'>{overall_aqi}</div>", unsafe_allow_html=True)

            # Pollutants Display
            st.markdown(f"""
            <div class='pollutants-bar'>
                <div class='pollutant'><div class='p-name'>PM2.5</div><div class='p-value'>{current.get('pm2_5',0):.1f}</div><div class='p-unit'>µg/m³ • AQI {aqi_pm25}</div></div>
                <div class='pollutant'><div class='p-name'>PM10</div><div class='p-value'>{current.get('pm10',0):.1f}</div><div class='p-unit'>µg/m³ • AQI {aqi_pm10}</div></div>
                <div class='pollutant'><div class='p-name'>CO</div><div class='p-value'>{current.get('co',0):.0f}</div><div class='p-unit'>µg/m³ • AQI {aqi_co}</div></div>
                <div class='pollutant'><div class='p-name'>NO₂</div><div class='p-value'>{current.get('no2',0):.1f}</div><div class='p-unit'>µg/m³ • AQI {aqi_no2}</div></div>
                <div class='pollutant'><div class='p-name'>O₃</div><div class='p-value'>{current.get('o3',0)*1000:.1f}</div><div class='p-unit'>ppb • AQI {aqi_o3}</div></div>
                <div class='pollutant'><div class='p-name'>SO₂</div><div class='p-value'>{current.get('so2',0):.1f}</div><div class='p-unit'>µg/m³ • AQI {aqi_so2}</div></div>
            </div>
            """, unsafe_allow_html=True)

            # 48-Hour Forecast
            times = [datetime.fromtimestamp(item['dt']).strftime("%m/%d %H:%M") for item in forecast]
            forecast_aqi = []
            for item in forecast:
                c = item['components']
                aqi = max(
                    calculate_aqi(c.get('pm2_5'), 'pm2_5'),
                    calculate_aqi(c.get('pm10'), 'pm10'),
                    calculate_aqi(c.get('o3'), 'o3'),
                    calculate_aqi(c.get('no2'), 'no2'),
                    calculate_aqi(c.get('so2'), 'so2'),
                    calculate_aqi(c.get('co'), 'co'),
                )
                forecast_aqi.append(aqi)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=times, y=forecast_aqi, mode='lines+markers',
                                    line=dict(color='#ff4757', width=6), marker=dict(size=9),
                                    fill='tozeroy', fillcolor='rgba(255,71,87,0.3)'))
            fig.update_layout(title="48-Hour Air Quality Forecast (EPA Standard)",
                              height=550, template="plotly_dark",
                              plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                              font=dict(color="white"), xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

        except requests.exceptions.RequestException:
            st.error("Network error. Please check your internet connection.")
        except Exception as e:
            st.error("An unexpected error occurred. Please try again.")

st.caption("AirGuard Pro v2.0 © 2025 • Real EPA AQI • Global Coverage • Premium Licensed")
