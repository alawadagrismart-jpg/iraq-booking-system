import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime

# ==========================================
# 1. إعدادات الهوية البصرية (Cyber-Iraq Design)
# ==========================================
st.set_page_config(page_title="منظومة عين العراق المطورة", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    .main { background-color: #0b0e14; color: #e0e0e0; }
    
    /* ستايل البطاقة التعريفية */
    .stApp { background: linear-gradient(135deg, #0b0e14 0%, #1a1f25 100%); }
    
    /* الحقول الرقمية والمدخلات */
    .stTextInput>div>div>input {
        background-color: #1f262e !important;
        color: #00ffcc !important;
        border: 1px solid #20A090 !important;
        border-radius: 10px !important;
        font-size: 18px !important;
        text-align: center !important;
    }

    /* أزرار عين العراق */
    .stButton>button {
        background: linear-gradient(90deg, #20A090 0%, #168174 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 30px !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(32, 160, 144, 0.6) !important;
        transform: scale(1.02);
    }

    /* مؤشر الخطوات */
    .step-bar {
        display: flex; justify-content: space-around; margin-bottom: 40px;
        padding: 10px; background: rgba(255,255,255,0.05); border-radius: 15px;
    }
    .step { color: #666; font-weight: bold; }
    .step-active { color: #20A090; border-bottom: 3px solid #20A090; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. قاعدة البيانات (نظام قائمة الانتظار)
# ==========================================
def init_db():
    conn = sqlite3.connect('ayn_iraq_queue.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS waitlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT,
        province TEXT,
        city TEXT,
        family_members TEXT,
        status TEXT DEFAULT 'في انتظار الرفع',
        created_at TEXT
    )''')
    conn.commit()
    return conn

conn = init_db()

# ==========================================
# 3. منطق الخطوات (Session State)
# ==========================================
if 'step' not in st.session_state:
    st.session_state.step = 1

def change_step(s): st.session_state.step = s

# ==========================================
# 4. واجهة المستخدم الرسومية
# ==========================================
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Coat_of_arms_of_Iraq.svg/120px-Coat_of_arms_of_Iraq.svg.png", width=70)
st.title("بوابة عين العراق الذكية")
st.markdown("---")

# عرض الخطوات
steps_html = f"""
<div class="step-bar">
    <div class="step {'step-active' if st.session_state.step == 1 else ''}">1. التحقق (SMS)</div>
    <div class="step {'step-active' if st.session_state.step == 2 else ''}">2. الموقع السكني</div>
    <div class="step {'step-active' if st.session_state.step == 3 else ''}">3. بيانات العائلة</div>
</div>
"""
st.markdown(steps_html, unsafe_allow_html=True)

# --- الخطوة 1: رقم الهاتف ---
if st.session_state.step == 1:
    st.subheader("📲 الخطوة الأولى: التحقق من الهاتف")
    phone = st.text_input("أدخل رقم الهاتف لتصلك رسالة الرمز", placeholder="07XXXXXXXXX")
    
    if st.button("إرسال رمز SMS ⬅️"):
        if len(phone) >= 10:
            with st.spinner('جاري إرسال الرمز...'):
                time.sleep(1.5) # محاكاة للإرسال
                st.session_state.user_phone = phone
                st.success("تم إرسال الرمز بنجاح!")
                change_step(2)
                st.rerun()
        else:
            st.error("يرجى إدخال رقم هاتف عراقي صحيح")

# --- الخطوة 2: المحافظة والمدينة ---
elif st.session_state.step == 2:
    st.subheader("📍 الخطوة الثانية: الموقع الجغرافي")
    
    col1, col2 = st.columns(2)
    with col1:
        province = st.selectbox("المحافظة", ["بغداد", "الأنبار", "البصرة", "نينوى", "النجف", "كربلاء", "ديالى", "ذي قار"])
    with col2:
        city = st.text_input("المدينة / القضاء", placeholder="مثال: الفلوجة، الكرخ، الرمادي")

    if st.button("التالي (بيانات العائلة) ⬅️"):
        if city:
            st.session_state.province = province
            st.session_state.city = city
            change_step(3)
            st.rerun()
        else:
            st.error("يرجى كتابة اسم المدينة")

# --- الخطوة 3: تفاصيل العائلة وقائمة الانتظار ---
elif st.session_state.step == 3:
    st.subheader("👨‍👩‍👧‍👦 الخطوة الثالثة: تفاصيل العائلة")
    family_details = st.text_area("أدخل أسماء أفراد العائلة المشمولين بالحجز", placeholder="مثال:\n1. أحمد محمد (الأب)\n2. سارة علي (الأم)")
    
    st.info("💡 بمجرد التأكيد، سيتم إدراجك في قائمة الانتظار ليقوم النظام برفع طلبك آلياً للحجز.")

    if st.button("✅ تأكيد الإرسال لقائمة الانتظار"):
        if family_details:
            # حفظ في قاعدة البيانات
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c = conn.cursor()
            c.execute("INSERT INTO waitlist (phone, province, city, family_members, created_at) VALUES (?,?,?,?,?)",
                      (st.session_state.user_phone, st.session_state.province, st.session_state.city, family_details, now))
            conn.commit()
            
            st.session_state.step = 4
            st.rerun()
        else:
            st.error("يرجى إدخال تفاصيل العائلة")

# --- الخطوة النهائية: النجاح ---
elif st.session_state.step == 4:
    st.balloons()
    st.success("تم تسجيلك في قائمة الانتظار بنجاح!")
    st.markdown(f"""
    <div style="background: rgba(32, 160, 144, 0.1); padding: 20px; border-radius: 15px; border: 1px solid #20A090;">
        <h4 style="color: #00ffcc; text-align: center;">حالة الطلب: قيد المعالجة (الرفع التلقائي)</h4>
        <p><b>رقم الهاتف:</b> {st.session_state.user_phone}</p>
        <p><b>الموقع:</b> {st.session_state.province} - {st.session_state.city}</p>
        <hr>
        <p style="text-align: center; font-size: 14px;">سيصلك إشعار فور إتمام عملية الحجز الرسمي.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 تسجيل حجز جديد"):
        st.session_state.step = 1
        st.rerun()

# ==========================================
# لوحة التحكم (مخفية للمدير فقط)
# ==========================================
with st.sidebar:
    st.title("⚙️ الإدارة")
    if st.checkbox("عرض قائمة الانتظار"):
        df = pd.read_sql_query("SELECT * FROM waitlist", conn)
        st.dataframe(df)
