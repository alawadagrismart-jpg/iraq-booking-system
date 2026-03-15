import streamlit as st
import qrcode
import time
import requests # للمستقبل عند ربطه بسيرفر SMS حقيقي
from io import BytesIO
from datetime import datetime

# ==========================================
# 1. إعدادات السيرفر (محاكاة قاعدة بيانات عين العراق)
# ==========================================
# التواريخ المتاحة فعلياً في السيرفر لكل مدينة
SERVER_DATES = {
    "بغداد": {"الكرخ": ["2026-03-20", "2026-03-22"], "الرصافة": ["2026-03-25"]},
    "الأنبار": {"حديثة": ["2026-03-16", "2026-03-18"], "الرمادي": ["2026-03-30"]},
    "البصرة": {"الزبير": ["2026-04-01"], "القرنة": ["2026-04-05"]}
}

# ==========================================
# 2. وظائف النظام (System Functions)
# ==========================================
def send_sms_logic(phone_number):
    """هذه الوظيفة هي التي تتواصل مع مزود الخدمة لإرسال الكود"""
    # في الواقع هنا نضع رابط API مثل Twilio أو Firebase
    actual_code = "5599" # هذا الكود الذي "يفترضه" السيرفر الآن
    return actual_code

# ==========================================
# 3. واجهة المستخدم والتنقل
# ==========================================
st.set_page_config(page_title="منظومة عين العراق المركزية", layout="centered")

# إدارة حالة النظام (State Management)
if 'auth_status' not in st.session_state: st.session_state.auth_status = False
if 'step' not in st.session_state: st.session_state.step = "login"
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = None

# --- المرحلة الأولى: التحقق من الهاتف (Gateway) ---
if st.session_state.step == "login":
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Coat_of_arms_of_Iraq.svg/1200px-Coat_of_arms_of_Iraq.svg.png", width=100)
    st.title("تسجيل الدخول - منظومة عين العراق")
    
    phone = st.text_input("أدخل رقم الهاتف المرتبط بالبطاقة الوطنية", placeholder="07XXXXXXXX")
    
    if st.button("إرسال كود التحقق 📲"):
        if len(phone) >= 10:
            with st.spinner('جاري إرسال الطلب لسيرفرات الاتصالات...'):
                time.sleep(2)
                # السيرفر يولد الكود ويرسله
                st.session_state.generated_otp = send_sms_logic(phone)
                st.session_state.step = "otp_verify"
                st.rerun()
        else:
            st.error("يرجى إدخال رقم هاتف عراقي صحيح")

# --- المرحلة الثانية: إدخال الكود (Handshake) ---
elif st.session_state.step == "otp_verify":
    st.subheader("تأكيد هوية الرقم")
    st.info(f"تم إرسال كود التحقق إلى هاتفك. (لأغراض الفحص الكود هو: {st.session_state.generated_otp})")
    
    user_input_code = st.text_input("أدخل الرمز المكون من 4 أرقام", max_chars=4)
    
    if st.button("تحقق الآن ✅"):
        if user_input_code == st.session_state.generated_otp:
            st.session_state.auth_status = True
            st.session_state.step = "location_selection"
            st.success("تم التحقق بنجاح. جاري فتح استمارة الحجز...")
            time.sleep(1)
            st.rerun()
        else:
            st.error("الرمز غير صحيح، يرجى المحاولة مرة أخرى")

# --- المرحلة الثالثة: اختيار الموقع والتاريخ (Server Sync) ---
elif st.session_state.step == "location_selection":
    st.title("تحديد مركز المراجعة والموعد المتاح")
    
    prov = st.selectbox("المحافظة", list(SERVER_DATES.keys()))
    city = st.selectbox("الدائرة / المركز", list(SERVER_DATES[prov].keys()))
    
    # سحب التواريخ المتاحة لهذا المركز حصراً من السيرفر
    available_days = SERVER_DATES[prov][city]
    
    st.write("🗓️ المواعيد المتوفرة في هذا المركز:")
    final_date = st.radio("اختر موعدك", available_days)
    
    if st.button("تأكيد الموعد والمتابعة ⬅️"):
        st.session_state.selected_loc = f"{prov} - {city}"
        st.session_state.selected_date = final_date
        st.session_state.step = "personal_data"
        st.rerun()

# --- المرحلة الرابعة: المعلومات الشخصية (Final Entry) ---
elif st.session_state.step == "personal_data":
    st.title("إكمال بيانات الاستمارة")
    with st.form("final_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم الرباعي واللقب")
        nid = col2.text_input("رقم البطاقة الوطنية (12 رقم)", max_chars=12)
        
        mother = st.text_input("اسم الأم الثلاثي")
        
        st.markdown("---")
        if st.form_submit_button("إصدار الوصل النهائي وتشفير البيانات"):
            if name and len(nid) == 12:
                st.session_state.final_info = {"name": name, "id": nid, "mother": mother}
                st.session_state.step = "receipt"
                st.rerun()
            else:
                st.error("يرجى التأكد من ملء كافة الحقول بشكل صحيح")

# --- المرحلة الخامسة: الوصل والباركود ---
elif st.session_state.step == "receipt":
    st.success("تم الحجز بنجاح! يرجى تصوير الشاشة أو طباعة الوصل")
    
    # توليد باركود حقيقي يحتوي على بيانات المستخدم التي أدخلها
    qr_content = f"BOOKING_ID:{int(time.time())}\nNID:{st.session_state.final_info['id']}\nDATE:{st.session_state.selected_date}"
    qr = qrcode.make(qr_content)
    buf = BytesIO(); qr.save(buf, format="PNG"); qr_img = buf.getvalue()
    
    st.markdown(f"""
    <div style="border:5px solid #20A090; padding:20px; border-radius:15px; background:white; color:black;">
        <h2 style="text-align:center;">وصل حجز عين العراق</h2>
        <p><b>الاسم:</b> {st.session_state.final_info['name']}</p>
        <p><b>رقم الهوية:</b> {st.session_state.final_info['id']}</p>
        <p><b>المركز:</b> {st.session_state.selected_loc}</p>
        <h3 style="color:red; text-align:center;">الموعد: {st.session_state.selected_date}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.image(qr_img, width=200)
    if st.button("حجز جديد"):
        st.session_state.clear()
        st.rerun()
