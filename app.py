import streamlit as st
import requests
from datetime import datetime, timedelta
import hashlib
import plotly.graph_objects as go
import pandas as pd

# فقط این رمز رو عوض کن به هر چی خودت دوست داری
OWNER_PASSWORD = "244343696Mzt"   # ← فقط خودت بلدی

# تولید کد 20 روزه
def create_license():
    expiry = datetime.now() + timedelta(days=20)
    date_str = expiry.strftime("%Y%m%d")
    raw = "airguard2025" + date_str
    h = hashlib.md5(raw.encode()).hexdigest().upper()[:12]
    return f"AG25-{h[:4]}-{h[4:8]}-{h[8:]}"

# چک کردن کد
def check_license(code):
    try:
        if not code.startswith("AG25-"):
            return False, "باید با AG25 شروع بشه"
        clean = code[5:].replace("-", "").upper()
        if len(clean) != 12:
            return False, "کد اشتباهه"

        today = datetime.now().date()
        for days in range(0, 26):  # از امروز تا 25 روز بعد
            check_date = today + timedelta(days=days)
            date_str = check_date.strftime("%Y%m%d")
            raw = "airguard2025" + date_str
            expected = hashlib.md5(raw.encode()).hexdigest().upper()[:12]
            if expected == clean:
                days_left = 20 - days
                if days_left >= 0:
                    return True, f"{days_left} روز باقی‌مانده"
                else:
                    return False, "منقضی شده"
        return False, "نامعتبر"
    except:
        return False, "خطا"

# صفحه
st.set_page_config(page_title="AirGuard Pro", page_icon="🌍", layout="centered")
st.markdown("""
<style>
    .main {background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);color:white;min-height:100vh;padding:20px;}
    .title {font-size:4.5rem;text-align:center;background:linear-gradient(90deg,#00ff88,#00f5ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .card {background:rgba(255,255,255,0.12);padding:40px;border-radius:25px;max-width:650px;margin:40px auto;text-align:center;backdrop-filter:blur(15px);}
    .license {font-family:monospace;font-size:2rem;background:#000;color:#0f0;padding:20px;border-radius:12px;letter-spacing:6px;}
</style>
""", unsafe_allow_html=True)

if 'valid' not in st.session_state:
    st.session_state.valid = False

# صفحه ورود
if not st.session_state.valid:
    st.markdown("<h1 class='title">AirGuard Pro</h1>")
    st.markdown("<h3 style='text-align:center;color:#88ffaa;'>وضعیت لحظه‌ای + پیش‌بینی ۴۸ ساعت آینده</h3>")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### لایسنس ۲۰ روزه فقط ۲۰۰,۰۰۰ تومان")
        code = st.text_input("کد لایسنس:", type="password", placeholder="AG25-XXXX-XXXX-XXXX")
        
        if st.button("فعال‌سازی لایسنس", type="primary"):
            ok, msg = check_license(code)
            if ok:
                st.session_state.valid = True
                st.session_state.code = code
                st.success(f"لایسنس فعال شد! {msg}")
                st.balloons()
                st.rerun()
            else:
                st.error(msg)
        
        st.markdown("**خرید لایسنس:** @YourTelegramID")
        st.markdown("</div>", unsafe_allow_html=True)

    # فقط تو می‌بینی
    owner = st.text_input("رمز صاحب اپ (فقط خودت)", type="password", key="owner")
    if owner == OWNER_PASSWORD:
        st.success("خوش آمدی رئیس!")
        if st.button("تولید کد جدید ۲۰ روزه"):
            new_code = create_license()
            st.markdown(f"<div class='license'>{new_code}</div>", unsafe_allow_html=True)
            st.success("کد آماده! کپی کن و بفروش")
            st.info("این کد دقیقاً ۲۰ روز کار می‌کنه")

else:
    st.success("لایسنس فعال است ✅")
    if st.sidebar.button("خروج"):
        st.session_state.valid = False
        st.rerun()

    # بخش کیفیت هوا (کامل و کارکرده)
    col1, col2 = st.columns(2)
    with col1: lat = st.text_input("عرض جغرافیایی", "35.6892")
    with col2: lon = st.text_input("طول جغرافیایی", "51.3890")

    if st.button("دریافت گزارش کامل", type="primary", use_container_width=True):
        with st.spinner("در حال دریافت داده..."):
            try:
                current = requests.get(f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1").json()['list'][0]['components']
                forecast = requests.get(f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1").json()['list'][:48]

                aqi = max(current['pm2_5'], current['pm10']//2, current['no2'])
                aqi = min(max(int(aqi),0),500)
                level = ["خوب","متوسط","ناسالم برای گروه حساس","ناسالم","بسیار ناسالم","خطرناک"][min(aqi//51,5)]
                color = ["#00e400","#ffff00","#ff7e00","#ff0000","#8f3f97","#7e0023"][min(aqi//51,5)]
                
                st.markdown(f"<h2 style='text-align:center;color:{color}'>AQI فعلی: {aqi} - {level}</h2>", unsafe_allow_html=True)
                
                cols = st.columns(6)
                for i, (n, k) in enumerate(zip(["PM2.5","PM10","CO","NO₂","O₃","SO₂"], ['pm2_5','pm10','co','no2','o3','so2'])):
                    with cols[i]:
                        st.metric(n, f"{current[k]:.1f}")

                df = pd.DataFrame([{"زمان": datetime.fromtimestamp(item['dt']), "AQI": max(item['components']['pm2_5'], item['components']['pm10']//2)} for item in forecast])
                fig = go.Figure(go.Scatter(x=df['زمان'], y=df['AQI'], mode='lines+markers', line=dict(color='#ff6b6b', width=4)))
                fig.update_layout(title="پیش‌بینی ۴۸ ساعت آینده", template="plotly_dark", height=500)
                st.plotly_chart(fig, use_container_width=True)
                
            except:
                st.error("خطا در دریافت داده")

st.caption("AirGuard Pro © ۱۴۰۴")
