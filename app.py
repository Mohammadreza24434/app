import streamlit as st
import requests
from datetime import datetime, timedelta
import hashlib
import plotly.graph_objects as go

# رمز عبور فقط برای تو (اینجا عوضش کن به هر چی دوست داری)
OWNER_PASSWORD = "244343696Mzt"   # ← فقط خودت اینو بلد باشی

# تابع ساخت کد 20 روزه
def create_license():
    expiry = (datetime.now() + timedelta(days=20)).strftime("%Y%m%d")
    secret = "airguard_secret_2025_salt"
    raw = f"{secret}{expiry}{datetime.now().microsecond}"
    hash_part = hashlib.md5(raw.encode()).hexdigest()[:12]
    return f"AG25-{hash_part[:4]}-{hash_part[4:8]}-{hash_part[8:]}".upper()

# تابع چک کردن کد
def check_license(code):
    try:
        if not code.startswith("AG25-"): return False, "نامعتبر"
        clean = code[5:].replace("-", "").lower()
        if len(clean) != 12: return False, "نامعتبر"
        for i in range(-5, 25):
            test_date = (datetime.now() + timedelta(days=i)).strftime("%Y%m%d")
            test_raw = f"airguard_secret_2025_salt{test_date}"
            if hashlib.md5(test_raw.encode()).hexdigest()[:12] == clean:
                days_left = 20 - i if i <= 20 else 0
                if days_left > 0:
                    return True, f"{days_left} روز باقی‌مانده"
                else:
                    return False, "منقضی شده"
        return False, "نامعتبر"
    except:
        return False, "خطا"

# صفحه
st.set_page_config(page_title="AirGuard Pro", page_icon="🌍", layout="centered")
st.markdown("<style>.main{background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);color:white;min-height:100vh;padding:20px;}.title{font-size:4.5rem;text-align:center;background:linear-gradient(90deg,#00ff88,#00f5ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}.card{background:rgba(255,255,255,0.12);padding:40px;border-radius:25px;max-width:650px;margin:40px auto;text-align:center;backdrop-filter:blur(15px);}.license{font-family:monospace;font-size:2rem;background:#000;color:#0f0;padding:20px;border-radius:12px;letter-spacing:6px;}.stButton>button{background:linear-gradient(45deg,#ff6b6b,#feca57);border:none;border-radius:20px;height:70px;font-size:1.5rem;}</style>", unsafe_allow_html=True)

if 'valid' not in st.session_state:
    st.session_state.valid = False

# صفحه ورود کاربر
if not st.session_state.valid:
    st.markdown("<h1 class='title'>AirGuard Pro</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;color:#88ffaa;'>وضعیت لحظه‌ای + پیش‌بینی ۴۸ ساعت آینده</h3>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### لایسنس ۲۰ روزه فقط ۲۰۰,۰۰۰ تومان")
        code = st.text_input("کد لایسنس را وارد کنید:", type="password", placeholder="مثل AG25-8X4M-K9P2-Q7F1")
        if st.button("فعال‌سازی لایسنس", type="primary"):
            ok, msg = check_license(code)
            if ok:
                st.session_state.valid = True
                st.success(f"لایسنس فعال شد! {msg}")
                st.balloons()
                st.rerun()
            else:
                st.error(msg)
        st.markdown("**خرید لایسنس:** @YourTelegramID")
        st.markdown("</div>", unsafe_allow_html=True)

    # ←←← فقط تو این بخش رو می‌بینی (با رمز عبور)
    owner_pass = st.text_input("رمز صاحب اپ (فقط خودت)", type="password")
    if owner_pass == OWNER_PASSWORD:
        st.success("خوش آمدی رئیس!")
        if st.button("تولید کد لایسنس ۲۰ روزه جدید برای مشتری"):
            new_code = create_license()
            st.markdown(f"<div class='license'>{new_code}</div>", unsafe_allow_html=True)
            st.success("کد آماده است! کپی کن و به مشتری بده")
            st.info("این کد دقیقاً ۲۰ روز کار می‌کنه")

else:
    st.success("لایسنس فعال است ✅")
    if st.sidebar.button("خروج"): st.session_state.valid = False; st.rerun()

    # اینجا بخش کیفیت هوا (همون قبلی)
    col1, col2 = st.columns(2)
    with col1: lat = st.text_input("عرض جغرافیایی", "35.6892")
    with col2: lon = st.text_input("طول جغرافیایی", "51.3890")
    if st.button("دریافت گزارش کامل", type="primary", use_container_width=True):
        # همون کد قبلی کیفیت هوا رو بذار (من برات کاملش کردم پایین)
        st.write("در حال بارگذاری...")

# ←←← بخش کامل کیفیت هوا (کپی کن و بذار بعد از خط بالا)
    try:
        current = requests.get(f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1").json()
        forecast = requests.get(f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1").json()
        c = current['list'][0]['components']
        aqi = max(c['pm2_5'], c['pm10']//2, c['no2'], c['o3']*1000//50)
        aqi = min(max(int(aqi),0),500)
        level = ["خوب","متوسط","ناسالم برای گروه حساس","ناسالم","بسیار ناسالم","خطرناک"][min(aqi//51,5)]
        color = ["#00e400","#ffff00","#ff7e00","#ff0000","#8f3f97","#7e0023"][min(aqi//51,5)]
        st.markdown(f"<h2 style='text-align:center;color:{color}'>AQI فعلی: {aqi} - {level}</h2>", unsafe_allow_html=True)
        cols = st.columns(6)
        for i, (n, v) in enumerate(zip(["PM2.5","PM10","CO","NO₂","O₃","SO₂"], [c['pm2_5'],c['pm10'],c['co'],c['no2'],c['o3'],c['so2']])):
            with cols[i]: st.metric(n, f"{v:.1f}")
        # نمودار
        import pandas as pd
        df = pd.DataFrame([{"زمان": datetime.fromtimestamp(item['dt']), "AQI": max(item['components']['pm2_5'], item['components']['pm10']//2)} for item in forecast['list'][:48]])
        fig = go.Figure(go.Scatter(x=df['زمان'], y=df['AQI'], mode='lines+markers', line=dict(color='#ff6b6b', width=4)))
        fig.update_layout(title="پیش‌بینی ۴۸ ساعت آینده", template="plotly_dark", height=500)
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.error("مختصات اشتباه یا خطای اتصال")

st.caption("AirGuard Pro © ۱۴۰۴ - فقط با لایسنس ۲۰ روزه")
