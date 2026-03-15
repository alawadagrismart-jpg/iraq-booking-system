import streamlit as st
import pandas as pd
import sqlite3
import qrcode
from io import BytesIO
from datetime import datetime
import time

# ==========================================
# 1. إعدادات الصفحة الأساسية والتصميم (CSS)
# ==========================================
st.set_page_config(page_title="عين العراق - النظام الشامل", layout="centered", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    .main { background-color: #f7f9fa; }
    
    /* تصميم شريط التقدم (الخطوات) كما في الصور */
    .step-container {
        display: flex; justify-content: space-between; align-items: center;
        background: white; padding: 15px 20px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 30px; border: 1px solid #e0e0e0;
    }
    .step-item { text-align: center; flex: 1; position: relative; }
    .step-item h5 { margin: 0; font-size: 14px; font-weight: 600; color: #888; }
    .step-item.active h5 { color: #20A090; font-weight: 800; }
    .step-icon {
        width: 30px; height: 30px; border-radius: 50%; background: #eee;
        margin: 0 auto 5px; display: flex; align-items: center; justify-content: center;
        font-weight: bold; color: #888;
    }
    .step-item.active .step-icon { background: #20A090; color: white; box-shadow: 0 0 10px rgba(32, 160, 144, 0.4); }
    
    /* تصميم الحقول ليطابق التطبيق */
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stDateInput>div>div>input {
        background-color: #f2f2f2 !important; border-radius: 8px !important;
        border: 1px solid #ddd !important; padding: 10px !important; font-size: 14px !important;
    }
    
    /* أزرار التنقل */
    .btn-next { background-color: #20A090 !important; color: white !important; width: 100%; border-radius: 8px; font-weight: bold; }
    .btn-back { background-color: #9e9e9e !important; color: white !important; width: 100%; border-radius: 8px; font-weight: bold; }
    
    /* الاستمارة النهائية */
    .final-receipt {
        background: white; border-top: 15px solid #20A090; padding: 30px;
        border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. بناء وتجهيز قاعدة البيانات الشاملة
# ==========================================
def init_db():
    conn = sqlite3.connect('ayn_iraq_ultimate.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS official_bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id TEXT,
        nat_id TEXT, res_id TEXT, res_issuer TEXT, res_date TEXT,
        f_name TEXT, s_name TEXT, t_name TEXT, surname TEXT,
        m_f_name TEXT, m_s_name TEXT, m_t_name TEXT,
        phone TEXT, blood TEXT, gender TEXT, dob TEXT,
        province TEXT, office TEXT, service TEXT, booking_date TEXT,
        status TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    return conn

conn = init_db()

# ==========================================
# 3. إدارة جلسة المستخدم (Session State)
# ==========================================
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# تعريف المتغيرات في الجلسة لحفظها بين الخطوات
fields = ['nat_id', 'res_id', 'res_issuer', 'res_date', 
          'f_name', 's_name', 't_name', 'surname', 
          'm_f_name', 'm_s_name', 'm_t_name', 
          'phone', 'blood', 'gender', 'dob',
          'province', 'office', 'service', 'booking_date']

for field in fields:
    if field not in st.session_state:
        st.session_state[field] = ""

def next_step(): st.session_state.current_step += 1
def prev_step(): st.session_state.current_step -= 1

# ==========================================
# 4. واجهة المستخدم - شريط التقدم
# ==========================================
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Coat_of_arms_of_Iraq.svg/120px-Coat_of_arms_of_Iraq.svg.png", width=60)
st.markdown("<h2 style='color:#20A090; margin-top:-10px;'>منظومة الحجز الإلكتروني - عين العراق</h2>", unsafe_allow_html=True)

step1_cls = "active" if st.session_state.current_step == 1 else ""
step2_cls = "active" if st.session_state.current_step == 2 else ""
step3_cls = "active" if st.session_state.current_step == 3 else ""

st.markdown(f"""
    <div class="step-container">
        <div class="step-item {step1_cls}"><div class="step-icon">1</div><h5>معلومات الاستمارة</h5></div>
        <div class="step-item {step2_cls}"><div class="step-icon">2</div><h5>البيانات الشخصية</h5></div>
        <div class="step-item {step3_cls}"><div class="step-icon">3</div><h5>بيانات الحجز</h5></div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 5. الخطوة الأولى: معلومات الاستمارة والمستمسكات
# ==========================================
if st.session_state.current_step == 1:
    st.subheader("📄 معلومات الاستمارة والمستمسكات الثبوتية")
    st.info("يرجى إدخال أرقام البطاقات بدقة كما هي مدونة في المستمسكات الرسمية.")
    
    st.session_state.nat_id = st.text_input("رقم البطاقة الوطنية (12 رقم)", value=st.session_state.nat_id, max_chars=12, help="الرقم الموجود في أعلى البطاقة الوطنية")
    st.session_state.res_id = st.text_input("رقم بطاقة السكن (9 أرقام)", value=st.session_state.res_id, max_chars=9)
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.session_state.res_issuer = st.text_input("جهة إصدار بطاقة السكن", value=st.session_state.res_issuer)
    with col_r2:
        st.session_state.res_date = st.date_input("تاريخ إصدار بطاقة السكن")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("التالي: البيانات الشخصية ⬅️", use_container_width=True):
        if len(st.session_state.nat_id) < 10 or not st.session_state.res_id:
            st.error("⚠️ يرجى التأكد من إدخال رقم البطاقة الوطنية وبطاقة السكن بشكل صحيح.")
        else:
            next_step()

# ==========================================
# 6. الخطوة الثانية: البيانات الشخصية (مطابقة للصورة 100%)
# ==========================================
elif st.session_state.current_step == 2:
    st.subheader("👤 البيانات الشخصية للمواطن")
    
    st.markdown("**بيانات المتقدم:**")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.session_state.f_name = st.text_input("الاسم الاول", value=st.session_state.f_name)
    with c2: st.session_state.s_name = st.text_input("اسم الاب", value=st.session_state.s_name)
    with c3: st.session_state.t_name = st.text_input("اسم الجد", value=st.session_state.t_name)
    with c4: st.session_state.surname = st.text_input("اللقب", value=st.session_state.surname)

    st.markdown("**بيانات الأم:**")
    c5, c6, c7 = st.columns(3)
    with c5: st.session_state.m_f_name = st.text_input("اسم الام الاول", value=st.session_state.m_f_name)
    with c6: st.session_state.m_s_name = st.text_input("اسم اب الام", value=st.session_state.m_s_name)
    with c7: st.session_state.m_t_name = st.text_input("اسم جد الام", value=st.session_state.m_t_name)

    st.markdown("**معلومات إضافية:**")
    c8, c9, c10 = st.columns(3)
    with c8: st.session_state.phone = st.text_input("رقم الهاتف (07...)", value=st.session_state.phone)
    with c9: st.session_state.blood = st.selectbox("فصيلة الدم", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
    with c10: st.session_state.gender = st.selectbox("الجنس", ["ذكر", "أنثى"])

    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("➡️ رجوع", use_container_width=True): prev_step()
    with col_btn2:
        if st.button("التالي: بيانات الحجز ⬅️", use_container_width=True):
            if not st.session_state.f_name or not st.session_state.m_f_name or not st.session_state.phone:
                st.error("⚠️ يرجى إكمال الأسماء ورقم الهاتف.")
            else:
                next_step()

# ==========================================
# 7. الخطوة الثالثة: بيانات الحجز والإرسال النهائي
# ==========================================
elif st.session_state.current_step == 3:
    st.subheader("🏢 بيانات الحجز والمراجعة")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.session_state.province = st.selectbox("المحافظة", ["بغداد", "الأنبار", "البصرة", "نينوى", "النجف", "كربلاء"])
        st.session_state.service = st.selectbox("نوع الخدمة", ["إصدار بطاقة وطنية", "تجديد بطاقة", "واقعة زواج/طلاق", "تغيير مسكن"])
    with col_b2:
        st.session_state.office = st.selectbox("دائرة الأحوال (المركز)", ["قسم معلومات حديثة", "قسم معلومات الرمادي", "أحوال الكرخ", "أحوال الرصافة"])
        st.session_state.booking_date = st.date_input("تاريخ المراجعة")

    st.markdown("<br>", unsafe_allow_html=True)
    st.warning("⚠️ إقرار: أقر بأن كافة البيانات المدخلة صحيحة ومطابقة للمستمسكات الرسمية وأتحمل المسؤولية القانونية بخلاف ذلك.")
    
    col_btn3, col_btn4 = st.columns(2)
    with col_btn3:
        if st.button("➡️ رجوع", use_container_width=True): prev_step()
    with col_btn4:
        if st.button("✅ تأكيد الحجز وإصدار الوصل", use_container_width=True):
            # 1. توليد رقم حجز رسمي
            b_id = f"AYN-{int(time.time())}"
            
            # 2. الحفظ في قاعدة البيانات بكل تفاصيلها
            c = conn.cursor()
            c.execute('''INSERT INTO official_bookings 
                        (booking_id, nat_id, res_id, res_issuer, res_date, 
                         f_name, s_name, t_name, surname, m_f_name, m_s_name, m_t_name, 
                         phone, blood, gender, province, office, service, booking_date, status) 
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                      (b_id, st.session_state.nat_id, st.session_state.res_id, st.session_state.res_issuer, str(st.session_state.res_date),
                       st.session_state.f_name, st.session_state.s_name, st.session_state.t_name, st.session_state.surname,
                       st.session_state.m_f_name, st.session_state.m_s_name, st.session_state.m_t_name,
                       st.session_state.phone, st.session_state.blood, st.session_state.gender,
                       st.session_state.province, st.session_state.office, st.session_state.service, str(st.session_state.booking_date), "مؤكد"))
            conn.commit()
            
            # 3. الانتقال لخطوة النجاح (الوصل)
            st.session_state.final_b_id = b_id
            st.session_state.current_step = 4
            st.rerun()

# ==========================================
# 8. الخطوة الرابعة: الوصل النهائي (QR Code & Receipt)
# ==========================================
elif st.session_state.current_step == 4:
    full_n = f"{st.session_state.f_name} {st.session_state.s_name} {st.session_state.t_name} {st.session_state.surname}"
    mother_full = f"{st.session_state.m_f_name} {st.session_state.m_s_name} {st.session_state.m_t_name}"
    b_id = st.session_state.final_b_id

    # توليد الباركود
    qr_data = f"ID:{b_id}\nNat_ID:{st.session_state.nat_id}\nName:{full_n}\nMother:{mother_full}"
    qr = qrcode.make(qr_data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    qr_bytes = buf.getvalue()

    st.success("🎉 تم تسجيل الحجز بنجاح في المنظومة!")
    
    st.markdown(f"""
    <div class="final-receipt">
        <h3 style="text-align:center; color:#20A090;">جمهورية العراق - وزارة الداخلية</h3>
        <p style="text-align:center; color:#555;">مديرية الأحوال المدنية والجوازات والإقامة</p>
        <hr>
        <h4 style="color:red; text-align:center;">رقم الحجز: {b_id}</h4>
        
        <table style="width:100%; border-collapse: collapse; margin-top:20px;" border="1">
            <tr style="background-color:#f9f9f9;">
                <td style="padding:10px;"><b>الاسم الكامل:</b> {full_n}</td>
                <td style="padding:10px;"><b>اسم الأم:</b> {mother_full}</td>
            </tr>
            <tr>
                <td style="padding:10px;"><b>رقم البطاقة الوطنية:</b> {st.session_state.nat_id}</td>
                <td style="padding:10px;"><b>رقم بطاقة السكن:</b> {st.session_state.res_id}</td>
            </tr>
            <tr style="background-color:#f9f9f9;">
                <td style="padding:10px;"><b>الدائرة/القسم:</b> {st.session_state.office}</td>
                <td style="padding:10px;"><b>نوع الخدمة:</b> {st.session_state.service}</td>
            </tr>
            <tr>
                <td style="padding:10px;"><b>تاريخ المراجعة:</b> {st.session_state.booking_date}</td>
                <td style="padding:10px;"><b>رقم الهاتف:</b> {st.session_state.phone}</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    st.image(qr_bytes, width=150)
    
    if st.button("🔄 حجز جديد", use_container_width=True):
        # تصفير الجلسة للبدء من جديد
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ==========================================
# 9. لوحة تحكم الإدارة (السرية) - لعرض الداتا كاملة
# ==========================================
st.sidebar.markdown("---")
if st.sidebar.checkbox("🛡️ دخول المدير (استخراج الداتا)"):
    st.sidebar.subheader("البيانات الجاهزة للحقن")
    df = pd.read_sql_query("SELECT * FROM official_bookings", conn)
    st.sidebar.dataframe(df)
    
    if st.sidebar.button("تصدير إلى Excel"):
        st.sidebar.success("تم تجهيز الملف للإرسال السحابي.")
