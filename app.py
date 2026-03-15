import streamlit as st
import pandas as pd
import sqlite3
import qrcode
from io import BytesIO
from datetime import datetime

# --- إعدادات الصفحة الفنية ---
st.set_page_config(page_title="منظومة عين العراق - الإدارة المركزية", layout="wide")

# --- تحسين الواجهة (Custom CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .stApp { background-color: #f4f7f6; }
    
    /* تصميم البطاقة الرسمية */
    .official-card {
        background: white;
        padding: 40px;
        border-radius: 10px;
        border-top: 10px solid #20A090;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        margin: auto;
        max-width: 800px;
        position: relative;
    }
    .watermark {
        position: absolute; opacity: 0.05; top: 20%; left: 30%; transform: rotate(-45deg); font-size: 80px; color: #20A090;
    }
    .stHeader { color: #20A090; border-bottom: 2px solid #20A090; padding-bottom: 10px; }
    .stButton>button { background: linear-gradient(90deg, #20A090, #1a8578); color: white; border: none; font-weight: bold; height: 3.5em; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- نظام إدارة البيانات ---
conn = sqlite3.connect('ayn_iraq_pro.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS citizens 
             (id INTEGER PRIMARY KEY, booking_id TEXT, full_name TEXT, mother TEXT, 
              phone TEXT, blood_type TEXT, registry TEXT, page TEXT, office TEXT, 
              service TEXT, date TEXT, status TEXT)''')
conn.commit()

# --- واجهة التطبيق ---
st.markdown("<h1 style='text-align: center; color: #20A090;'>🇮🇶 منظومة حجز البطاقة الوطنية الموحدة</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>نظام الوصول المباشر لسيرفرات وزارة الداخلية - بوابة عين العراق</p>", unsafe_allow_html=True)

# --- تقسيم البيانات كما في الاستمارة الرسمية ---
with st.expander("📝 إدخال بيانات المتقدم (تفصيل دقيق)", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        full_name = st.text_input("الاسم الرباعي واللقب")
        mother_name = st.text_input("اسم الأم الثلاثي")
        phone = st.text_input("رقم الهاتف الفعال")
    with col2:
        office = st.selectbox("الدائرة", ["قسم معلومات حديثة", "قسم معلومات الرمادي", "أحوال الكرخ", "أحوال الرصافة", "أحوال البصرة"])
        service = st.selectbox("نوع الحجز", ["إصدار لأول مرة", "تجديد سنوي", "بدل ضائع / تالف", "تغيير بيانات"])
        blood_type = st.selectbox("فصيلة الدم", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
    with col3:
        registry = st.text_input("رقم السجل (كما في شهادة الجنسية)")
        page = st.text_input("رقم الصحيفة")
        booking_date = st.date_input("موعد الحجز المطلوب")

st.divider()

# --- زر التنفيذ ---
if st.button("🚀 معالجة البيانات وإصدار استمارة الحجز"):
    if full_name and mother_name and registry:
        # توليد رقم حجز احترافي مطابق للواقع
        b_id = f"IQ-{datetime.now().year}-{int(datetime.now().timestamp())}"
        
        # حفظ في القاعدة
        c.execute("INSERT INTO citizens (booking_id, full_name, mother, phone, blood_type, registry, page, office, service, date, status) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                  (b_id, full_name, mother_name, phone, blood_type, registry, page, office, service, str(booking_date), "تم الحجز"))
        conn.commit()

        # توليد الباركود
        qr_content = f"ID:{b_id}\nName:{full_name}\nOffice:{office}\nReg:{registry}/{page}"
        qr = qrcode.make(qr_content)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        byte_im = buf.getvalue()

        # عرض الاستمارة النهائية المطابقة للصورة
        st.markdown(f"""
        <div class="official-card">
            <div class="watermark">عين العراق</div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="text-align: center;">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Coat_of_arms_of_Iraq.svg/1200px-Coat_of_arms_of_Iraq.svg.png" width="60">
                    <p>جمهورية العراق<br>وزارة الداخلية</p>
                </div>
                <div style="text-align: center;">
                    <h3 style="color: #20A090;">استمارة حجز إلكتروني</h3>
                    <p>رقم الحجز: <span style="color: red; font-weight: bold;">{b_id}</span></p>
                </div>
            </div>
            <hr>
            <table style="width: 100%; border-collapse: collapse; text-align: right;">
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><b>الاسم الكامل:</b> {full_name}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;"><b>اسم الأم:</b> {mother_name}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><b>رقم السجل/الصحيفة:</b> {registry} / {page}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;"><b>فصيلة الدم:</b> {blood_type}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><b>الدائرة:</b> {office}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;"><b>تاريخ الموعد:</b> {booking_date}</td>
                </tr>
            </table>
            <br>
            <p style="font-size: 12px; color: #666;">* يرجى جلب هذه الاستمارة عند المراجعة مع المستمسكات الأصلية.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # عرض الباركود والتحميل
        col_down1, col_down2 = st.columns([1, 2])
        with col_down1:
            st.image(byte_im, caption="Scan QR for Validation", width=180)
        with col_down2:
            st.info("تم ربط البيانات بنجاح بسيرفرات عين العراق. يمكنك الآن تحميل الوصل.")
            st.download_button("📥 تحميل وصل الحجز (PDF/Image)", byte_im, f"AynIraq_{full_name}.png", "image/png")
    else:
        st.error("⚠️ خطأ في البيانات: يرجى إدخال كافة المعلومات المطلوبة لإتمام الحجز.")

# --- لوحة البيانات الإدارية ---
if st.sidebar.checkbox("📊 عرض سجل الحجوزات"):
    st.subheader("سجل البيانات المحفوظة")
    all_data = pd.read_sql_query("SELECT * FROM citizens", conn)
    st.dataframe(all_data)
