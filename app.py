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
    return f"AG25-{hashlib.md5(raw.encode()).hexdigest().upper()[:12]}"

def check_license(code):
    try:
        if not code.startswith("AG25-"): return False
        clean = code[5:].replace("-", "").upper()
        today = datetime.now().date()
        for d in range(0, 26):
            date = today + timedelta(days=d)
            expected = hashlib.md5(f"airguard2025{date.strftime('%Y%m%d')}".encode()).hexdigest().upper()[:12]
            if expected == clean and d <= 20:
                return True, f"{20 - d} روز باقی مانده"
        return False
    except:
        return False

# ==================== دریافت داده (سریع و کش‌شده) ====================
@st.cache_data(ttl=300, show_spinner=False)  # هر ۵ دقیقه بروز میشه
def get_air_data(lat, lon):
    try:
        url_current = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1"
        url_forecast = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1"
        current = requests.get(url_current, timeout=10).json()
        forecast = requests.get(url_forecast, timeout=10).json()
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

pm25_bp = [(0,12,0,50),(12.1,35.4,51,100),(35.5,55.4,101,150),(55.5,150.4,151,200),(150.5,250.4,201,300),(250.5,500,301,500)]
pm10_bp = [(0,54,0,50),(55,154,51,100),(155,254,101,150),(255,354,151,200),(355,424,201,300),(425,999,301,500)]
o3_bp   = [(0,54,0,50),(55,70,51,100),(71,85,101,150),(86,105,151,200),(106,200,201,300)]
no2_bp  = [(0,53,0,50),(54,100,51,100),(101,360,101,150),(361,649,151,200),(650,1249,201,300),(1250,9999,301,500)]

# ==================== تم حرفه‌ای + اعداد کاملاً خوانا ====================
st.set_page_config(page_title="AirGuard Pro", page_icon="🌍", layout="centered")

st.markdown("""
<style>
    .main {background: #0f0c29; color: white; padding: 20px; min-height: 100vh;}
    .title {font-size: 4.8rem; text-align: center; font-weight: 900; background: linear-gradient(90deg, #00ff88, #00f5ff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .aqi-value {font-size: 7rem; font-weight: 900; text-align: center; color: #ff4757;}
    .aqi-level {font-size: 3.8rem; font-weight: bold; text-align: center;}
    .pollutant-card {
        background: rgba(255,255,255,0.12); border-radius: 18px; padding: 18px; text-align: center;
        border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    }
    .pollutant-name {font-size: 1.1rem; color: #00ff88; margin-bottom: 8px;}
    .pollutant-value {font-size: 2.6rem; font-weight: bold; color: #ffffff !important;}
    .pollutant-unit {font-size: 1rem; color: #88ffaa;}
    .stButton>button {background: linear-gradient(45deg, #ff6b6b, #ffb142); border: none; border-radius: 50px;
                     height: 65px; font-size: 1.6rem; font-weight: bold; color: white;}
</style>
""", unsafe_allow_html=True)

# ==================== صفحه لایسنس ====================
if 'valid' not in st.session_state:
    st.session_state.valid = False

if not st.session_state.valid:
    st.markdown("<h1 class='title'>AirGuard Pro</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#88ffaa;'>مانیتور کیفیت هوای جهانی — نسخه پریمیوم</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='background:rgba(255,255,255,0.1);padding:40px;border-radius:25px;text-align:center;border:1px solid rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
        st.markdown("### لایسنس ۲۰ روزه — ۲۰۰,۰۰۰ تومان")
        code = st.text_input("کد لایسنس را وارد کنید", type="password", placeholder="AG25-XXXX-XXXX-XXXX")
        if st.button("فعال‌سازی لایسنس"):
            if check_license(code):
                st.session_state.valid = True
                st.success("لایسنس با موفقیت فعال شد!")
                st.balloons()
                st.rerun()
            else:
                st.error("کد نامعتبر یا منقضی شده")
        st.markdown("</div>", unsafe_allow_html=True)

    owner = st.text_input("دسترسی مالک", type="password")
    if owner == OWNER_PASSWORD:
        st.success("خوش آمدی رئیس!")
        if st.button("تولید لایسنس جدید"):
            st.code(create_license())

else:
    st.markdown("<h1 class='title'>AirGuard Pro</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center; color:#88ffaa;'>مانیتور زنده کیفیت هوا — نسخه پریمیوم</h4>", unsafe_allow_html=True)
    
    if st.sidebar.button("خروج"):
        st.session_state.valid = False
        st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        lat = st.text_input("عرض جغرافیایی", "35.6892")
    with col2:
        lon = st.text_input("طول جغرافیایی", "51.3890")

    if st.button("دریافت گزارش زنده", type="primary", use_container_width=True):
        with st.spinner("در حال دریافت اطلاعات زنده..."):
            current, forecast = get_air_data(lat, lon)
            if not current:
                st.error("اطلاعات برای این مختصات در دسترس نیست.")
                st.stop()

            c = current['components']

            # محاسبه AQI
            aqi = max(
                calc_aqi(c['pm2_5'], pm25_bp),
                calc_aqi(c['pm10'], pm10_bp),
                calc_aqi(c['o3'] * 1000, o3_bp),
                calc_aqi(c['no2'], no2_bp)
            )

            levels = ["عالی", "متوسط", "ناسالم برای حساس‌ها", "ناسالم", "بسیار ناسالم", "خطرناک"]
            colors = ["#00e400", "#ffff00", "#ff7e00", "#ff0000", "#8f3f97", "#7e0023"]
            idx = min(aqi // 51, 5)

            st.markdown(f"<div class='aqi-level' style='color:{colors[idx]};'>{levels[idx]}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='aqi-value'>{aqi}</div>", unsafe_allow_html=True)

            # آلاینده‌ها — کاملاً خوانا و مرتب
            cols = st.columns(6)
            data = [
                ("PM2.5", f"{c['pm2_5']:.1f}", "µg/m³"),
                ("PM10", f"{c['pm10']:.1f}", "µg/m³"),
                ("CO", f"{c['co']:.0f}", "µg/m³"),
                ("NO₂", f"{c['no2']:.1f}", "µg/m³"),
                ("O₃", f"{c['o3']*1000:.1f}", "ppb"),
                ("SO₂", f"{c['so2']:.1f}", "µg/m³")
            ]
            for col, (name, val, unit) in zip(cols, data):
                with col:
                    st.markdown(f"""
                    <div class='pollutant-card'>
                        <div class='pollutant-name'>{name}</div>
                        <div class='pollutant-value'>{val}</div>
                        <div class='pollutant-unit'>{unit}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # نمودار سریع و واقعی
            times = [datetime.fromtimestamp(x['dt']).strftime("%H:%M\n%d/%m") for x in forecast]
            forecast_aqi = [max(
                calc_aqi(x['components']['pm2_5'], pm25_bp),
                calc_aqi(x['components']['pm10'], pm10_bp),
                calc_aqi(x['components']['o3']*1000, o3_bp),
                calc_aqi(x['components']['no2'], no2_bp)
            ) for x in forecast]

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=times, y=forecast_aqi, mode='lines+markers',
                                   line=dict(color='#ff4757', width=4), marker=dict(size=8)))
            fig.update_layout(title="پیش‌بینی ۴۸ ساعته AQI", template="plotly_dark", height=480,
                            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

st.caption("AirGuard Pro © 2025 — پریمیوم | دقیق | زنده | جهانی")
