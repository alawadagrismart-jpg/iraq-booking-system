import streamlit as st
import pandas as pd
import sqlite3
import qrcode
import requests # لإرسال البيانات مستقبلاً
from io import BytesIO
from datetime import datetime
import time
from PIL import Image

# ==========================================
# 1. إعدادات النظام المتقدمة (CSS & UI)
# ==========================================
st.set_page_config(page_title="نظام عين العراق المركزي v6.0", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    .stApp { background-color: #f0f2f6; }
    
    /* تصميم شريط الخطوات الاحترافي */
    .step-bar {
        display: flex; justify-content: space-between; margin-bottom: 40px;
        background: white; padding: 20px; border-radius: 15px; box-shadow: 0 2px 15px rgba(0,0,0,0.05);
    }
    .step-unit { text-align: center; flex: 1; position: relative; }
    .step-unit.active { color: #20A090; font-weight: bold; border-bottom: 3px solid #20A090; }
    
    /* تحسين شكل المدخلات */
    div.stTextInput > div > div > input { border: 2px solid #e0e0e0 !important; border-radius: 10px !important; padding: 12px !important; }
    div.stTextInput > div > div > input:focus { border-color: #20A090 !important; }
    
    /* الوصل الرسمي النهائي */
    .official-header-box {
        background: white; border: 3px solid #1a1a1a; padding: 30px; border-radius: 5px; margin-top: 20px;
    }
    .watermark-bg {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        opacity: 0.03; width: 400px; pointer-events: none;
    }
    
    /* أزرار مخصصة */
    .stButton > button {
        border-radius: 12px !important; height: 50px !important; font-size: 18px !important;
        transition: all 0.3s ease !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. منطق التحقق من البيانات (Validation Logic)
# ==========================================
def validate_data(step):
    if step == 1:
        if len(st.session_state.nat_id) != 12 or not st.session_state.nat_id.isdigit():
            st.error("❌ خطأ: رقم البطاقة الوطنية يجب أن يتكون من 12 رقماً بالضبط.")
            return False
        if len(st.session_state.res_id) != 9 or not st.session_state.res_id.isdigit():
            st.error("❌ خطأ: رقم بطاقة السكن يجب أن يتكون من 9 أرقام.")
            return False
    if step == 2:
        if not st.session_state.f_name or not st.session_state.surname:
            st.error("❌ خطأ: يرجى إدخال الاسم الكامل واللقب.")
            return False
        if len(st.session_state.phone) < 11:
            st.error("❌ خطأ: رقم الهاتف غير صحيح.")
            return False
    return True

# ==========================================
# 3. محاكي إرسال البيانات (Server Communication)
# ==========================================
def send_to_server_mock(data):
    with st.spinner('📡 جاري الاتصال بسيرفرات وزارة الداخلية (عين العراق)...'):
        time.sleep(2) # محاكاة وقت الاستجابة
        # هنا يتم التأكد من "الوصول"
        success_code = 200 
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] طلب إرسال للمواطن {data['full_name']} - الكود: {success_code} OK"
        return success_code, log_entry

# ==========================================
# 4. إدارة الجلسة وقاعدة البيانات
# ==========================================
conn = sqlite3.connect('ayn_iraq_pro_v6.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS secure_bookings 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, b_id TEXT, details TEXT, status TEXT, timestamp TEXT)''')
conn.commit()

if 'step' not in st.session_state: st.session_state.step = 1
if 'logs' not in st.session_state: st.session_state.logs = []

fields = ['nat_id', 'res_id', 'res_issuer', 'res_date', 'f_name', 's_name', 't_name', 'surname', 
          'm_f_name', 'm_s_name', 'm_t_name', 'phone', 'blood', 'gender', 'province', 'office', 'service', 'booking_date']

for f in fields:
    if f not in st.session_state: st.session_state[f] = ""

# ==========================================
# 5. واجهة التطبيق - الخطوات
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Coat_of_arms_of_Iraq.svg/1200px-Coat_of_arms_of_Iraq.svg.png", width=100)
st.sidebar.title("مركز التحكم")

# شريط الحالة في السايدبار للتأكد من الوصول للسيرفر
st.sidebar.subheader("🚀 مراقب السيرفر (Live)")
for log in st.session_state.logs[-5:]: # عرض آخر 5 عمليات
    st.sidebar.caption(log)

# تصميم شريط الخطوات العلوي
st.markdown(f"""
    <div class="step-bar">
        <div class="step-unit {'active' if st.session_state.step == 1 else ''}">1. الوثائق الثبوتية</div>
        <div class="step-unit {'active' if st.session_state.step == 2 else ''}">2. البيانات الشخصية</div>
        <div class="step-unit {'active' if st.session_state.step == 3 else ''}">3. تأكيد الحجز</div>
    </div>
""", unsafe_allow_html=True)

# --- الخطوة 1 ---
if st.session_state.step == 1:
    st.header("🗂️ الخطوة الأولى: الوثائق")
    st.session_state.nat_id = st.text_input("رقم البطاقة الوطنية (12 رقم)", st.session_state.nat_id, max_chars=12)
    st.session_state.res_id = st.text_input("رقم بطاقة السكن (9 أرقام)", st.session_state.res_id, max_chars=9)
    col1, col2 = st.columns(2)
    with col1: st.session_state.res_issuer = st.text_input("جهة الإصدار", st.session_state.res_issuer)
    with col2: st.session_state.res_date = st.date_input("تاريخ الإصدار")
    
    if st.button("الانتقال للبيانات الشخصية ⬅️"):
        if validate_data(1):
            st.session_state.step = 2
            st.rerun()

# --- الخطوة 2 ---
elif st.session_state.step == 2:
    st.header("👤 الخطوة الثانية: البيانات الشخصية")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.session_state.f_name = st.text_input("الاسم الأول")
    with c2: st.session_state.s_name = st.text_input("اسم الأب")
    with c3: st.session_state.t_name = st.text_input("اسم الجد")
    with c4: st.session_state.surname = st.text_input("اللقب")
    
    st.markdown("---")
    st.subheader("بيانات الأم (للمطابقة الأمنية)")
    c5, c6, c7 = st.columns(3)
    with c5: st.session_state.m_f_name = st.text_input("اسم الأم")
    with c6: st.session_state.m_s_name = st.text_input("اسم أب الأم")
    with c7: st.session_state.m_t_name = st.text_input("اسم جد الأم")
    
    st.session_state.phone = st.text_input("رقم الهاتف")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1: 
        if st.button("➡️ رجوع"): st.session_state.step = 1; st.rerun()
    with col_btn2: 
        if st.button("متابعة للحجز ⬅️"):
            if validate_data(2):
                st.session_state.step = 3; st.rerun()

# --- الخطوة 3 ---
elif st.session_state.step == 3:
    st.header("📅 الخطوة الثالثة: الموعد والدائرة")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.session_state.province = st.selectbox("المحافظة", ["بغداد", "الأنبار", "البصرة", "نينوى"])
        st.session_state.office = st.selectbox("دائرة الأحوال", ["قسم معلومات حديثة", "الرمادي", "الكرخ"])
    with col_d2:
        st.session_state.service = st.selectbox("نوع المعاملة", ["إصدار لأول مرة", "تجديد", "بدل ضائع"])
        st.session_state.booking_date = st.date_input("تاريخ المراجعة")
    
    if st.button("🚀 تأكيد وإرسال البيانات للسيرفر الحكومي"):
        b_id = f"IQ-{int(time.time())}"
        full_name = f"{st.session_state.f_name} {st.session_state.surname}"
        
        # محاكاة الإرسال والتأكد من الوصول
        code, log = send_to_server_mock({"full_name": full_name})
        st.session_state.logs.append(log)
        
        if code == 200:
            st.session_state.final_id = b_id
            st.session_state.step = 4
            st.rerun()

# --- الخطوة 4: الوصل الرسمي (بناءً على طلبك للهيدر) ---
elif st.session_state.step == 4:
    st.balloons()
    full_n = f"{st.session_state.f_name} {st.session_state.s_name} {st.session_state.t_name} {st.session_state.surname}"
    
    st.markdown(f"""
    <div class="official-header-box">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="text-align: center;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Coat_of_arms_of_Iraq.svg/1200px-Coat_of_arms_of_Iraq.svg.png" width="80">
                <p style="margin:0; font-weight:bold;">جمهورية العراق</p>
                <p style="margin:0; font-size:12px;">وزارة الداخلية</p>
            </div>
            <div style="text-align: center;">
                <h2 style="color: #20A090; margin:0;">وصل حجز إلكتروني مؤكد</h2>
                <p style="color: red; font-weight: bold; font-size: 20px;">{st.session_state.final_id}</p>
                <p style="font-size:12px; color:gray;">بوابة عين العراق الرقمية</p>
            </div>
            <div style="text-align: center;">
                <p style="font-size:12px;">تاريخ الطلب</p>
                <p style="font-weight:bold;">{datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
        </div>
        <hr style="border: 1px solid #eee;">
        <table style="width:100%; border-spacing: 15px;">
            <tr>
                <td><b>الاسم الكامل:</b> {full_n}</td>
                <td><b>رقم الهاتف:</b> {st.session_state.phone}</td>
            </tr>
            <tr>
                <td><b>الرقم الوطني:</b> {st.session_state.nat_id}</td>
                <td><b>بطاقة السكن:</b> {st.session_state.res_id}</td>
            </tr>
            <tr>
                <td><b>الدائرة:</b> {st.session_state.office}</td>
                <td><b>الموعد:</b> {st.session_state.booking_date}</td>
            </tr>
        </table>
        <div style="text-align:center; margin-top:20px; border: 1px dashed #ccc; padding:10px;">
            <p style="font-size:11px;">ملاحظة: يرجى جلب هذا الوصل مطبوعاً مع المستمسكات الأصلية المذكورة في الاستمارة.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # توليد الباركود
    qr_data = f"ID:{st.session_state.final_id}|NID:{st.session_state.nat_id}"
    qr = qrcode.make(qr_data)
    buf = BytesIO(); qr.save(buf, format="PNG"); byte_im = buf.getvalue()
    st.image(byte_im, width=150, caption="باركود التحقق الأمني")
    
    if st.button("إصدار حجز جديد"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
