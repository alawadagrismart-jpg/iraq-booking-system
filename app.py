import streamlit as st
import pandas as pd
import sqlite3
import time

# --- التصميم الاحترافي (Cyber-Tech) ---
st.set_page_config(page_title="Saree Iraq - Full Flow", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stExpander"] { border: 1px solid #00f2ff; border-radius: 10px; background: #161b22; }
    .stHeader { color: #00f2ff; text-shadow: 0 0 5px #00f2ff; }
    </style>
    """, unsafe_allow_html=True)

# --- قاعدة البيانات ---
conn = sqlite3.connect('iraq_final_step.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS full_orders 
             (id INTEGER PRIMARY KEY, service TEXT, province TEXT, office TEXT,
              f_name TEXT, s_name TEXT, t_name TEXT, surname TEXT,
              mother TEXT, phone TEXT, family_count INTEGER, status TEXT)''')
conn.commit()

st.title("🇮🇶 بوابة الحجز السريع - النظام المتكامل")

# --- الخطوات قبل الاسم (كما في الفيديو) ---
st.subheader("🛠️ الخطوة 1: تحديد نوع الخدمة والمركز")
col1, col2, col3 = st.columns(3)

with col1:
    service = st.selectbox("نوع الخدمة المطلوبة", ["إصدار لأول مرة", "تجديد بطاقة", "بدل ضائع/تالف"])
with col2:
    province = st.selectbox("المحافظة", ["بغداد", "الأنبار", "البصرة", "أربيل", "نينوى", "النجف"])
with col3:
    # هنا بنحط المكاتب اللي ظهرت في فيديو "عين العراق"
    office = st.selectbox("مركز الإصدار / الدائرة", ["قسم معلومات حديثة", "قسم معلومات الرمادي", "دائرة أحوال الكرخ", "دائرة أحوال الرصافة"])

st.divider()

# --- الخطوة الثانية: البيانات الشخصية ---
st.subheader("👤 الخطوة 2: المعلومات الشخصية للمتقدم")
with st.container():
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        f_name = st.text_input("الاسم الأول")
    with c2:
        s_name = st.text_input("اسم الأب")
    with c3:
        t_name = st.text_input("اسم الجد")
    with c4:
        surname = st.text_input("اللقب / العشيرة")

    c5, c6 = st.columns(2)
    with c5:
        mother = st.text_input("اسم الأم الثلاثي (هام جداً للربط)")
    with c6:
        phone = st.text_input("رقم الهاتف (المسجل في البطاقة)")

st.divider()

# --- الخطوة الثالثة: بيانات العائلة ---
st.subheader("👨‍👩‍👧‍👦 الخطوة 3: أفراد العائلة (المرافقين)")
is_family = st.radio("هل تريد إضافة أفراد عائلة للحجز؟", ["لا، حجز فردي", "نعم، حجز جماعي"], horizontal=True)

f_count = 0
if is_family == "نعم، حجز جماعي":
    f_count = st.number_input("عدد أفراد العائلة الإضافيين", min_value=1, max_value=20)
    st.info("سيتم توليد طلبات تلقائية لكل فرد بناءً على بيانات الأب واللقب.")

# --- زر الحفظ النهائي ---
if st.button("🚀 تثبيت البيانات وإرسالها للسيرفر السحابي"):
    if f_name and mother and phone:
        c.execute('''INSERT INTO full_orders 
                     (service, province, office, f_name, s_name, t_name, surname, mother, phone, family_count, status) 
                     VALUES (?,?,?,?,?,?,?,?,?,?,?)''', 
                  (service, province, office, f_name, s_name, t_name, surname, mother, phone, f_count, "جاهز"))
        conn.commit()
        st.success(f"✅ تم بنجاح! طلبك الآن في 'قائمة الانتظار التوربينية' لمركز {office}")
        st.balloons()
    else:
        st.error("⚠️ من فضلك أكمل الخانات الأساسية (الاسم، الأم، الهاتف) قبل الحفظ.")

# --- لوحة الإرسال التوربيني (للمدير فقط) ---
with st.expander("🛡️ لوحة تحكم الإرسال (Turbo Mode)"):
    df = pd.read_sql_query("SELECT * FROM full_orders WHERE status='جاهز'", conn)
    st.write(df)
    if st.button("إطلاق هجوم الحجز (Start Injection)"):
        st.warning("جاري الاتصال بـ API الوزارة واستخدام الـ Headers المشفرة...")
        # محاكاة الربط الفعلي
        time.sleep(1)
        st.success("تم اختراق الزخم وحجز المواعيد بنجاح!")
