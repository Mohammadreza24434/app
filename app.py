# app.py - نسخه نهایی، ساده، امن و پولی (بدون JSON!)
import streamlit as st
import pandas as pd
import requests
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go

# تنظیمات صفحه
st.set_page_config(page_title="AirGuard Pro - پولی", page_icon="🔒", layout="centered")

# استایل زیبا
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #1e3c72, #2a5298); min-height: 100vh; color: white; padding: 20px;}
    .title {font-size: 4rem; text-align: center; font-weight: bold; margin: 50px 0; text-shadow: 2px 2px 10px rgba(0,0,0,0.5);}
    .card {background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto; backdrop-filter: blur(10px);}
    .stButton>button {background: #ff6b6b; color: white; font-size: 1.3rem; height: 60px; border-radius: 15px;}
</style>
""", unsafe_allow_html=True)

# لیست کدهای معتبر (اینجا کدهای خودت رو بنویس)
VALID_CODES = {
    "AIR2025-PRO-001": False,  # False یعنی هنوز استفاده نشده
    "AIR2025-PRO-002": False,
    "TEHRAN-1404": False,
    "POLLUTION2025": False,
    "TEST123": True,  # این فقط برای تست خودت
}

# ذخیره وضعیت کدهای استفاده شده (در حافظه Streamlit)
if 'used_codes' not in st.session_state:
    st.session_state.used_codes = []

# صفحه قفل
if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False

if not st.session_state.access_granted:
    st.markdown("<h1 class='title'>🔒 AirGuard Pro</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### دسترسی فقط با پرداخت")
        st.markdown("**قیمت دسترسی دائمی: ۲۹۰,۰۰۰ تومان**")
        st.markdown("بعد از پرداخت، کد دریافت می‌کنید")
        
        code = st.text_input("کد دسترسی را وارد کنید:", type="password")
        
        if st.button("ورود به سیستم", type="primary"):
            if code in VALID_CODES and not VALID_CODES[code] and code not in st.session_state.used_codes:
                st.session_state.access_granted = True
                st.session_state.used_codes.append(code)
                st.success("دسترسی فعال شد! خوش آمدید 👋")
                st.balloons()
                st.rerun()
            elif code in st.session_state.used_codes:
                st.error("این کد قبلاً استفاده شده!")
            else:
                st.error("کد نامعتبر است!")
        
        st.markdown("**برای خرید کد دسترسی:** @YourTelegramID")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.success("✅ دسترسی فعال است")
    st.markdown("### پیش‌بینی کیفیت هوا - ۴۸ ساعت آینده")
    
    col1, col2 = st.columns(2)
    with col1:
        lat = st.text_input("عرض جغرافیایی", "35.6892")
    with col2:
        lon = st.text_input("طول جغرافیایی", "51.3890")
    
    if st.button("دریافت پیش‌بینی", type="primary"):
        with st.spinner("در حال دریافت داده..."):
            try:
                url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid=c6c11b2ee2dc5eb38c9d834e9031e7e1"
                data = requests.get(url).json()
                
                records = []
                for item in data['list'][:48]:
                    comp = item['components']
                    aqi = max(
                        (comp.get('pm2_5',0) or 0),
                        (comp.get('pm10',0) or 0)/5,
                        (comp.get('no2',0) or 0)/10,
                        (comp.get('o3',0) or 0)*10
                    )
                    aqi = min(max(aqi, 0), 500)
                    dt = datetime.fromtimestamp(item['dt'])
                    records.append({"زمان": dt, "AQI": aqi})
                
                df = pd.DataFrame(records)
                current_aqi = df['AQI'].iloc[0]
                
                st.metric("AQI فعلی", f"{current_aqi:.1f}")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df['زمان'], y=df['AQI'], mode='lines+markers', name='AQI'))
                fig.update_layout(title="پیش‌بینی ۴۸ ساعت آینده", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                
            except:
                st.error("خطای اتصال به سرور")

# خروج
if st.sidebar.button("خروج از حساب"):
    st.session_state.access_granted = False
    st.rerun()
