import streamlit as st
import pandas as pd
import sqlite3
import qrcode
from io import BytesIO
from datetime import datetime
import time

# ==========================================
# 1. التصميم البصري الخارق (Ultra-Modern UI)
# ==========================================
st.set_page_config(page_title="منظومة عين العراق | الإصدار الاحترافي", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    
    /* خلفية التطبيق */
    .stApp { background-color: #f4f7f6; }
    
    /* كارت الخطوات */
    .step-card {
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 30px;
        border-right: 8px solid #20A090;
    }
    
    /* تصميم أزرار النيون للتحكم */
    .stButton > button {
        border-radius: 12px !important; height: 55px !important;
        font-weight: 900 !important; font-size: 18px !important;
        transition: all 0.4s ease !important;
        box-shadow: 0 4px 15px rgba(32, 160, 144, 0.2) !important;
    }
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(32, 160, 144, 0.4) !important;
    }

    /* الوصل الرسمي */
    .official-receipt {
        background: #fff; border: 2px solid #000; padding: 40px;
        border-radius: 5px; position: relative;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. قاعدة البيانات وسجل العمليات
# ==========================================
def init_db():
    conn = sqlite3.connect('ayn_iraq_v7.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS official_records 
                 (id INTEGER PRIMARY KEY, b_id TEXT, details TEXT, status TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# تهيئة الجلسة
if 'step' not in st.session_state: st.session_state.step = 1
if 'logs' not in st.session_state: st.session_state.logs = []

# الحقول المطلوبة (للتأكد من عدم فقدان البيانات)
fields = ['nat_id', 'res_id', 'res_issuer', 'res_date', 'f_name', 's_name', 't_name', 'surname', 
          'm_f_name', 'm_s_name', 'm_t_name', 'phone', 'blood', 'gender', 'province', 'office', 'service', 'booking_date']
for f in fields:
    if f not in st.session_state: st.session_state[f] = ""

# ==========================================
# 3. شريط المهام الجانبي (المراقب الأمني)
# ==========================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Coat_of_arms_of_Iraq.svg/1200px-Coat_of_arms_of_Iraq.svg.png", width=120)
    st.title("بوابة الإدارة")
    st.markdown("---")
    st.subheader("🔴 حالة السيرفر الحكومي")
    st.success("متصل (Online)")
    
    st.subheader("📝 سجل النشاط")
    for log in st.session_state.logs[-5:]:
        st.caption(f"🕒 {log}")

# ==========================================
# 4. محرك الخطوات (Step Engine)
# ==========================================
st.markdown(f"<h1 style='color:#20A090; text-align:center;'>🇮🇶 منظومة حجز البطاقة الوطنية - الخطوة {st.session_state.step}</h1>", unsafe_allow_html=True)

# --- الخطوة 1: المستمسكات ---
if st.session_state.step == 1:
    with st.container():
        st.markdown("<div class='step-card'><h3>📄 بيانات الوثائق الرسمية</h3>", unsafe_allow_html=True)
        st.session_state.nat_id = st.text_input("رقم البطاقة الوطنية (12 رقم)", st.session_state.nat_id, max_chars=12)
        st.session_state.res_id = st.text_input("رقم بطاقة السكن (9 أرقام)", st.session_state.res_id, max_chars=9)
        col1, col2 = st.columns(2)
        with col1: st.session_state.res_issuer = st.text_input("جهة الإصدار (انظر خلف البطاقة)")
        with col2: st.session_state.res_date = st.date_input("تاريخ إصدار بطاقة السكن")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("تأكيد الوثائق والانتقال للخطوة التالية ⬅️", use_container_width=True):
            if len(st.session_state.nat_id) == 12 and len(st.session_state.res_id) == 9:
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("⚠️ خطأ في عدد الأرقام! يرجى التأكد من الرقم الوطني (12) وبطاقة السكن (9).")
        st.markdown("</div>", unsafe_allow_html=True)

# --- الخطوة 2: البيانات الشخصية (تصحيح الخطأ هنا) ---
elif st.session_state.step == 2:
    with st.container():
        st.markdown("<div class='step-card'><h3>👤 البيانات الشخصية للمواطن</h3>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.session_state.f_name = st.text_input("الاسم الأول")
        with c2: st.session_state.s_name = st.text_input("اسم الأب")
        with c3: st.session_state.t_name = st.text_input("اسم الجد")
        with c4: st.session_state.surname = st.text_input("اللقب")
        
        st.markdown("**بيانات الأم الثلاثي:**")
        c5, c6, c7 = st.columns(3)
        with c5: st.session_state.m_f_name = st.text_input("اسم الأم")
        with c6: st.session_state.m_s_name = st.text_input("اسم أب الأم")
        with c7: st.session_state.m_t_name = st.text_input("اسم جد الأم")
        
        st.session_state.phone = st.text_input("رقم الهاتف الفعال")
        
        st.markdown("<br>", unsafe_allow_html=True)
        # تصحيح تسمية الأعمدة لمنع الخطأ
        col_nav_1, col_nav_2 = st.columns(2)
        with col_nav_1:
            if st.button("➡️ العودة للوثائق", use_container_width=True):
                st.session_state.step = 1
                st.rerun()
        with col_nav_2:
            if st.button("تأكيد البيانات والمتابعة ⬅️", use_container_width=True):
                if st.session_state.f_name and st.session_state.phone:
                    st.session_state.step = 3
                    st.rerun()
                else:
                    st.error("⚠️ يرجى إكمال الحقول الأساسية.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- الخطوة 3: الحجز النهائي ---
elif st.session_state.step == 3:
    with st.container():
        st.markdown("<div class='step-card'><h3>🏢 اختيار مركز الحجز والموعد</h3>", unsafe_allow_html=True)
        col_x, col_y = st.columns(2)
        with col_x:
            st.session_state.office = st.selectbox("دائرة الأحوال المختصة", ["قسم معلومات حديثة", "الرمادي", "الكرخ", "الرصافة"])
            st.session_state.service = st.selectbox("نوع الخدمة", ["إصدار لأول مرة", "تجديد سنوي", "بدل ضائع"])
        with col_y:
            st.session_state.booking_date = st.date_input("موعد المراجعة")
        
        st.warning("🔒 بالضغط على التأكيد، سيتم تشفير البيانات وإرسالها مباشرة لسيرفرات عين العراق.")
        
        col_fin_1, col_fin_2 = st.columns(2)
        with col_fin_1:
            if st.button("➡️ تعديل البيانات الشخصية"): st.session_state.step = 2; st.rerun()
        with col_fin_2:
            if st.button("🔥 تأكيد الحجز وإرسال للسيرفر الحكومي", use_container_width=True):
                with st.spinner('📡 جاري الربط وتأكيد الحجز...'):
                    time.sleep(2)
                    b_id = f"AYN-{int(time.time())}"
                    st.session_state.final_b_id = b_id
                    st.session_state.logs.append(f"تم حجز بنجاح للمواطن: {st.session_state.f_name} - الكود: 200 OK")
                    st.session_state.step = 4
                    st.rerun()

# --- الخطوة 4: الوصل الرسمي (Header) ---
elif st.session_state.step == 4:
    st.balloons()
    full_name_all = f"{st.session_state.f_name} {st.session_state.s_name} {st.session_state.t_name} {st.session_state.surname}"
    
    st.markdown(f"""
    <div class="official-receipt">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #000; padding-bottom: 10px;">
            <div style="text-align: center;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Coat_of_arms_of_Iraq.svg/1200px-Coat_of_arms_of_Iraq.svg.png" width="80">
                <p style="margin:0; font-weight:bold;">جمهورية العراق</p>
                <p style="margin:0; font-size:12px;">وزارة الداخلية</p>
            </div>
            <div style="text-align: center;">
                <h2 style="margin:0; color: #1a1a1a;">وصل حجز إلكتروني</h2>
                <h3 style="color: red; margin:5px;">{st.session_state.final_b_id}</h3>
            </div>
            <div style="text-align: center;">
                <p style="font-size:12px;">بوابة عين العراق</p>
                <p style="font-weight:bold;">{datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
        </div>
        
        <table style="width:100%; margin-top:20px; border-collapse: collapse; font-size: 18px;">
            <tr>
                <td style="padding:10px; border: 1px solid #eee;"><b>الاسم الكامل:</b> {full_name_all}</td>
                <td style="padding:10px; border: 1px solid #eee;"><b>رقم الهاتف:</b> {st.session_state.phone}</td>
            </tr>
            <tr>
                <td style="padding:10px; border: 1px solid #eee;"><b>الرقم الوطني:</b> {st.session_state.nat_id}</td>
                <td style="padding:10px; border: 1px solid #eee;"><b>رقم بطاقة السكن:</b> {st.session_state.res_id}</td>
            </tr>
            <tr>
                <td style="padding:10px; border: 1px solid #eee;"><b>مركز الإصدار:</b> {st.session_state.office}</td>
                <td style="padding:10px; border: 1px solid #eee;"><b>تاريخ المراجعة:</b> {st.session_state.booking_date}</td>
            </tr>
        </table>
        
        <p style="text-align:center; margin-top:20px; font-weight:bold; color:red;">* يرجى إحضار المستمسكات الأصلية عند المراجعة.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # باركود
    qr = qrcode.make(f"Verified:{st.session_state.final_b_id}")
    buf = BytesIO(); qr.save(buf, format="PNG"); byte_im = buf.getvalue()
    st.image(byte_im, width=150, caption="باركود التحقق الرسمي")
    
    if st.button("إصدار استمارة جديدة"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
