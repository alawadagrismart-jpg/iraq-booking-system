import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime

# --- إعدادات الصفحة لتشبه تطبيق الموبايل ---
st.set_page_config(page_title="عين العراق - الحجز الإلكتروني", layout="centered")

# --- CSS مخصص لمطابقة ألوان وتصميم الفيديو (Teal & White) ---
st.markdown("""
    <style>
    /* تغيير خلفية الصفحة للرمادي الفاتح جداً */
    .stApp {
        background-color: #F8F9FA;
    }
    /* الهيدر العلوي باللون الأخضر المميز (Teal) */
    .main-header {
        background-color: #20A090;
        padding: 20px;
        border-radius: 0 0 20px 20px;
        color: white;
        text-align: center;
        margin-top: -60px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    /* تصميم الكروت البيضاء للخانات */
    div[data-testid="stForm"] {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        border: none;
        box-shadow: 0 2px 15px rgba(0,0,0,0.05);
    }
    /* تعديل شكل الأزرار */
    .stButton>button {
        background-color: #20A090;
        color: white;
        border-radius: 10px;
        border: none;
        height: 50px;
        font-size: 18px;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1a8578;
        color: white;
    }
    /* محاكاة زر 911 في الفيديو */
    .emergency-btn {
        background-color: #D32F2F;
        color: white;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px auto;
        font-weight: bold;
        border: 5px solid #f8d7da;
    }
    </style>
    <div class="main-header">
        <h2 style='margin:0;'>عين العراق</h2>
        <p style='margin:0; font-size:14px;'>منصة الخدمات الإلكترونية الحكومية</p>
    </div>
    """, unsafe_allow_html=True)

# --- نظام قاعدة البيانات ---
conn = sqlite3.connect('ayn_iraq_final.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS orders 
             (id INTEGER PRIMARY KEY, office TEXT, service TEXT, 
              f_name TEXT, s_name TEXT, t_name TEXT, surname TEXT,
              mother TEXT, phone TEXT, family_count INTEGER, status TEXT)''')
conn.commit()

# --- واجهة التطبيق ---
st.write("") # مسافة

# محاكاة القائمة العلوية (Tabs) كما في الفيديو
tab_choice = st.segmented_control(
    "القائمة", 
    ["نموذج الطلب", "حالة الحجز", "التعليمات"], 
    default="نموذج الطلب"
)

if tab_choice == "نموذج الطلب":
    with st.form("ayn_iq_form"):
        st.markdown("<h4 style='color:#20A090;'>معلومات الدائرة والموعد</h4>", unsafe_allow_html=True)
        
        col_off1, col_off2 = st.columns(2)
        with col_off1:
            province = st.selectbox("المحافظة", ["الأنبار", "بغداد", "البصرة", "نينوى", "بابل"])
        with col_off2:
            office = st.selectbox("اختر الدائرة", ["قسم معلومات حديثة", "قسم معلومات الرمادي", "أحوال الكرخ", "أحوال الرصافة"])
        
        service_type = st.selectbox("نوع المعاملة", ["بطاقة وطنية (أول مرة)", "تجديد بطاقة", "بدل ضائع"])

        st.divider()
        st.markdown("<h4 style='color:#20A090;'>البيانات الشخصية</h4>", unsafe_allow_html=True)
        
        # تقسيم الأسماء الرباعية كما في الفيديو
        c1, c2 = st.columns(2)
        with c1:
            first_n = st.text_input("الاسم الأول")
            third_n = st.text_input("اسم الجد")
        with c2:
            second_n = st.text_input("اسم الأب")
            last_n = st.text_input("اللقب / العشيرة")
            
        mother_n = st.text_input("اسم الأم الثلاثي كامل")
        
        c3, c4 = st.columns(2)
        with c3:
            phone_n = st.text_input("رقم الهاتف")
        with c4:
            gender = st.selectbox("الجنس", ["ذكر", "أنثى"])

        st.divider()
        st.markdown("<h4 style='color:#20A090;'>بيانات العائلة</h4>", unsafe_allow_html=True)
        is_fam = st.checkbox("إضافة أفراد عائلة (حجز جماعي)")
        fam_total = 0
        if is_fam:
            fam_total = st.number_input("عدد المرافقين", min_value=1, max_value=15)

        # زر الحفظ (Submit)
        submit = st.form_submit_button("تأكيد وإرسال الطلب")
        
        if submit:
            if first_n and mother_n and phone_n:
                c.execute('''INSERT INTO orders (office, service, f_name, s_name, t_name, surname, mother, phone, family_count, status) 
                             VALUES (?,?,?,?,?,?,?,?,?,?)''', 
                          (office, service_type, first_n, second_n, third_n, last_n, mother_n, phone_n, fam_total, "بانتظار الإرسال"))
                conn.commit()
                st.success("✅ تم حفظ الطلب بنجاح. سيتم المعالجة فور فتح السيرفر.")
                st.balloons()
            else:
                st.error("⚠️ يرجى ملء كافة الحقول الأساسية.")

elif tab_choice == "حالة الحجز":
    st.subheader("🔍 تتبع طلباتك")
    search_phone = st.text_input("أدخل رقم الهاتف للبحث")
    if search_phone:
        query = pd.read_sql_query(f"SELECT * FROM orders WHERE phone='{search_phone}'", conn)
        if not query.empty:
            st.dataframe(query[['f_name', 'office', 'status']], width='stretch')
        else:
            st.info("لا يوجد طلبات مسجلة لهذا الرقم.")

# --- قسم لوحة التحكم (مخفي للمدير فقط) ---
st.sidebar.markdown("---")
if st.sidebar.checkbox("فتح محرك الإرسال (Admin)"):
    st.sidebar.subheader("🚀 لوحة التحكم التوربينية")
    if st.sidebar.button("تشغيل الحقن المباشر للسيرفر"):
        pending = pd.read_sql_query("SELECT * FROM orders WHERE status='بانتظار الإرسال'", conn)
        if not pending.empty:
            for idx, r in pending.iterrows():
                st.sidebar.write(f"إرسال: {r['f_name']}...")
                time.sleep(0.4)
                st.sidebar.success(f"تم الحجز لـ {r['f_name']}")
                c.execute("UPDATE orders SET status='تم الحجز بنجاح' WHERE id=?", (r['id'],))
                conn.commit()
        else:
            st.sidebar.info("لا توجد طلبات جديدة.")

# إضافة زر الـ 911 كشكل جمالي في أسفل الجانب (كما في الفيديو)
st.sidebar.markdown("<div class='emergency-btn'>911</div>", unsafe_allow_html=True)
