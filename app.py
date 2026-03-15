import streamlit as st
import pandas as pd
import sqlite3
import qrcode
from io import BytesIO
from datetime import datetime
from PIL import Image

# --- إعدادات الصفحة الفنية ---
st.set_page_config(page_title="منظومة عين العراق - الإدارة المركزية", layout="wide")

# --- تحسين الواجهة (Custom CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .stApp { background-color: #f4f7f6; }
    
    .official-card {
        background: white;
        padding: 40px;
        border-radius: 10px;
        border-top: 12px solid #20A090;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        margin: auto;
        max-width: 850px;
        position: relative;
    }
    .stHeader { color: #20A090; border-bottom: 2px solid #20A090; padding-bottom: 10px; }
    .stButton>button { 
        background: linear-gradient(90deg, #20A090, #1a8578); 
        color: white; border: none; font-weight: bold; 
        height: 3.5em; border-radius: 12px; width: 100%;
    }
    .info-box {
        background-color: #e8f4f2;
        padding: 15px;
        border-radius: 8px;
        border-right: 5px solid #20A090;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- نظام إدارة البيانات ---
conn = sqlite3.connect('ayn_iraq_v5.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS citizens 
             (id INTEGER PRIMARY KEY, booking_id TEXT, full_name TEXT, mother TEXT, 
              phone TEXT, blood_type TEXT, registry TEXT, page TEXT, office TEXT, 
              service TEXT, date TEXT, status TEXT)''')
conn.commit()

# --- واجهة التطبيق ---
st.markdown("<h1 style='text-align: center; color: #20A090;'>🇮🇶 منظومة حجز البطاقة الوطنية - عين العراق</h1>", unsafe_allow_html=True)

# --- تفاصيل البيانات الدقيقة ---
with st.container():
    st.markdown("<div class='info-box'>يرجى إدخال البيانات بدقة طبقاً للمستمسكات الرسمية لضمان قبول الحجز في السيرفر الحكومي.</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        full_name = st.text_input("الاسم الرباعي واللقب")
        mother_name = st.text_input("اسم الأم الثلاثي")
        phone = st.text_input("رقم الهاتف الفعال")
    with col2:
        office = st.selectbox("الدائرة / مركز الإصدار", ["قسم معلومات حديثة", "قسم معلومات الرمادي", "أحوال الكرخ", "أحوال الرصافة", "أحوال النجف"])
        service_type = st.selectbox("نوع الحجز", ["إصدار لأول مرة", "تجديد سنوي", "بدل ضائع / تالف", "تعديل بيانات"])
        blood_type = st.selectbox("فصيلة الدم", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
    with col3:
        registry = st.text_input("رقم السجل")
        page = st.text_input("رقم الصحيفة")
        booking_date = st.date_input("موعد المراجعة المطلوب")

st.divider()

if st.button("🚀 معالجة البيانات وإرسال الحجز للسيرفر"):
    if full_name and mother_name and registry and phone:
        # توليد رقم حجز احترافي
        b_id = f"IQ-{datetime.now().year}-{int(datetime.now().timestamp())}"
        
        # حفظ في القاعدة
        c.execute("INSERT INTO citizens (booking_id, full_name, mother, phone, blood_type, registry, page, office, service, date, status) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                  (b_id, full_name, mother_name, phone, blood_type, registry, page, office, service_type, str(booking_date), "تم الحجز"))
        conn.commit()

        # توليد الباركود
        qr_content = f"ID:{b_id}\nName:{full_name}\nOffice:{office}\nRef:{registry}/{page}"
        qr = qrcode.make(qr_content)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        byte_im = buf.getvalue()

        # عرض الاستمارة الرسمية
        st.markdown(f"""
        <div class="official-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="text-align: center;">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Coat_of_arms_of_Iraq.svg/1200px-Coat_of_arms_of_Iraq.svg.png" width="70">
                    <p>جمهورية العراق<br>وزارة الداخلية</p>
                </div>
                <div style="text-align: center;">
                    <h2 style="color: #20A090; margin:0;">وصل حجز إلكتروني</h2>
                    <p>الرقم المرجعي: <span style="color: red; font-weight: bold;">{b_id}</span></p>
                </div>
            </div>
            <hr style="border: 1px solid #20A090;">
            <table style="width: 100%; text-align: right; border-spacing: 10px;">
                <tr>
                    <td><b>الاسم الكامل:</b> {full_name}</td>
                    <td><b>اسم الأم:</b> {mother_name}</td>
                </tr>
                <tr>
                    <td><b>رقم السجل:</b> {registry}</td>
                    <td><b>رقم الصحيفة:</b> {page}</td>
                </tr>
                <tr>
                    <td><b>الدائرة:</b> {office}</td>
                    <td><b>تاريخ الموعد:</b> {booking_date}</td>
                </tr>
                <tr>
                    <td><b>نوع الخدمة:</b> {service_type}</td>
                    <td><b>فصيلة الدم:</b> {blood_type}</td>
                </tr>
            </table>
            <p style="text-align:center; font-size:12px; margin-top:20px;">* يرجى إبراز هذا الوصل عند مراجعة الدائرة المختصة.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_qr, col_txt = st.columns([1, 2])
        with col_qr:
            st.image(byte_im, width=200)
        with col_txt:
            st.success("🎯 تم إرسال البيانات لسيرفر عين العراق بنجاح!")
            st.download_button("📥 تحميل وصل الحجز كصورة", byte_im, f"AynIraq_{full_name}.png", "image/png")
    else:
        st.error("⚠️ يرجى إدخال كافة البيانات (الاسم، الأم، الهاتف، السجل) لإتمام العملية.")

# --- لوحة تحكم حسن (Admin) ---
st.sidebar.markdown("### 🛠️ لوحة تحكم المدير")
if st.sidebar.checkbox("عرض قاعدة البيانات"):
    df = pd.read_sql_query("SELECT * FROM citizens", conn)
    st.sidebar.dataframe(df)
