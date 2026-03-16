import streamlit as st
import sqlite3
import pandas as pd
import requests
import time

# ==========================================
# 1. إعداد المخزن (قاعدة بيانات المواطنين)
# ==========================================
def init_db():
    conn = sqlite3.connect('ayniq_pro.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS citizens 
                 (id INTEGER PRIMARY KEY, f_name TEXT, s_name TEXT, t_name TEXT, l_name TEXT,
                  phone TEXT, mother_name TEXT, birth_date TEXT, gender TEXT, 
                  family_booking TEXT, family_count INTEGER, status TEXT DEFAULT 'Pending')''')
    conn.commit()
    return conn

conn = init_db()

# ==========================================
# 2. واجهة الإدارة والتنقل
# ==========================================
st.sidebar.title("🛠️ لوحة التحكم")
page = st.sidebar.radio("انتقل إلى:", ["إضافة بيانات المواطنين", "المخزن والإرسال المجمع"])

# --- الصفحة الأولى: إضافة البيانات (مطابقة للفيديو) ---
if page == "إضافة بيانات المواطنين":
    st.title("📝 استمارة معلومات المواطن")
    st.info("أدخل البيانات بدقة كما تظهر في البطاقة الموحدة")

    with st.form("citizen_form"):
        col1, col2, col3, col4 = st.columns(4)
        f_name = col1.text_input("الاسم الأول")
        s_name = col2.text_input("اسم الأب")
        t_name = col3.text_input("اسم الجد")
        l_name = col4.text_input("اللقب")

        col_p1, col_p2 = st.columns(2)
        phone = col_p1.text_input("رقم الهاتف (07XXXXXXXX)")
        mother = col_p2.text_input("اسم الأم الثلاثي")

        col_d1, col_d2 = st.columns(2)
        birth_date = col_d1.date_input("تاريخ التولد")
        gender = col_d2.selectbox("الجنس", ["ذكر", "أنثى"])

        st.markdown("---")
        st.subheader("👨‍👩‍👧‍👦 خيارات الحجز العائلي")
        family_check = st.checkbox("حجز لعائلة؟")
        f_count = st.number_input("عدد أفراد الأسرة الإضافيين", min_value=0, max_value=9, value=0)

        if st.form_submit_button("حفظ في المخزن المحلي 📥"):
            if f_name and phone and len(phone) >= 10:
                c = conn.cursor()
                c.execute("""INSERT INTO citizens 
                             (f_name, s_name, t_name, l_name, phone, mother_name, birth_date, gender, family_booking, family_count) 
                             VALUES (?,?,?,?,?,?,?,?,?,?)""", 
                          (f_name, s_name, t_name, l_name, phone, mother, str(birth_date), gender, str(family_check), f_count))
                conn.commit()
                st.success(f"تم حفظ بيانات {f_name} بنجاح!")
            else:
                st.error("يرجى إكمال الحقول الأساسية (الاسم الأول ورقم الهاتف)")

# --- الصفحة الثانية: المخزن ومحرك الإرسال (الدورة الكاملة) ---
elif page == "المخزن والإرسال المجمع":
    st.title("🚀 محرك الحجز الآلي")
    
    df = pd.read_sql_query("SELECT * FROM citizens WHERE status = 'Pending'", conn)
    st.write(f"عدد الملفات الجاهزة: **{len(df)}**")
    st.dataframe(df)

    if st.button("بدء عملية الدخول والحجز المجمع 🔥"):
        for index, row in df.iterrows():
            st.subheader(f"معالجة: {row['f_name']} {row['l_name']}")
            
            # الخطوة 1: طلب الـ OTP
            with st.spinner(f"جاري طلب كود التحقق للرقم {row['phone']}..."):
                # هنا نضع رابط الـ Login الحقيقي
                # api_response = requests.post("https://api.ayniq.app/api/v1/auth/login", json={"phone": row['phone']})
                time.sleep(2) # محاكاة
                st.success(f"تم طلب الكود لـ {row['f_name']}. بانتظار إدخال الـ OTP...")
                
                # ملاحظة للمبرمج: في هذه المرحلة نحتاج واجهة سريعة لإدخال الكود المستلم 
                # أو نظام يقرأ الرسائل تلقائياً إذا كان هناك ربط مع سيرفر SMS
            
            st.markdown("---")
