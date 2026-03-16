import streamlit as st
import qrcode
import time
import requests
import sqlite3
import pandas as pd
from io import BytesIO

# ==========================================
# 1. إعداد قاعدة البيانات المحلية (المخزن)
# ==========================================
def init_db():
    conn = sqlite3.connect('ayniq_internal.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings 
                 (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, nid TEXT, 
                  location TEXT, date TEXT, status TEXT DEFAULT 'Pending')''')
    conn.commit()
    return conn

conn = init_db()

# ==========================================
# 2. محرك الربط مع API عين العراق (Real Engine)
# ==========================================
def call_ayniq_api(endpoint, data):
    """
    هذه الوظيفة تحاكي تطبيق الأندرويد وترسل البيانات للرابط الحقيقي
    """
    base_url = "https://api.ayniq.app/api/v1"
    url = f"{base_url}/{endpoint}"
    
    # الـ Headers التي استخرجناها من الكاناري لمحاكاة التطبيق
    headers = {
        "Host": "api.ayniq.app",
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "Dart/3.0 (dart:io)",  # الهوية التي يراها السيرفر
        "Accept-Encoding": "gzip"
    }
    
    try:
        # إرسال طلب حقيقي للسيرفر
        response = requests.post(url, json=data, headers=headers, timeout=10)
        return response.status_code, response.json()
    except Exception as e:
        return 500, str(e)

# ==========================================
# 3. واجهة النظام وتوزيع المراحل
# ==========================================
st.set_page_config(page_title="منظومة عين العراق | إدارة الحجز المجمع", layout="wide")

# إدارة الحالة (State Management)
if 'step' not in st.session_state: st.session_state.step = 1
if 'user_data' not in st.session_state: st.session_state.user_data = {}

# --- شريط جانبي للإحصائيات (Sidebar) ---
st.sidebar.title("📊 حالة النظام")
total_in_vault = pd.read_sql_query("SELECT COUNT(*) FROM bookings", conn).iloc[0,0]
st.sidebar.metric("المخزن المحلي", f"{total_in_vault} شخص")
if st.sidebar.button("🧹 تفريغ المخزن"):
    conn.cursor().execute("DELETE FROM bookings")
    conn.commit()
    st.rerun()

# --- المرحلة 1: تجميع البيانات (Data Collection) ---
if st.session_state.step == 1:
    st.title("📥 تجميع بيانات المواطنين للمخزن")
    st.info("قم بإدخال البيانات هنا ليتم حفظها في القاعدة وإرسالها لاحقاً بشكل مجمع.")
    
    with st.form("collection_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم الرباعي")
        phone = col2.text_input("رقم الهاتف (07XXXXXXXX)")
        nid = col1.text_input("الرقم الوطني (12 رقم)", max_chars=12)
        location = col2.selectbox("المحافظة/الدائرة", ["بغداد - الكرخ", "بغداد - الرصافة", "البصرة", "الأنبار"])
        
        if st.form_submit_button("حفظ في الانتظار 💾"):
            if len(nid) == 12 and len(phone) >= 10:
                c = conn.cursor()
                c.execute("INSERT INTO bookings (name, phone, nid, location) VALUES (?, ?, ?, ?)", 
                          (name, phone, nid, location))
                conn.commit()
                st.success(f"تمت إضافة {name} للمخزن بنجاح!")
            else:
                st.error("تأكد من كتابة الرقم الوطني (12 رقم) ورقم الهاتف بشكل صحيح.")
    
    if st.button("انتقل إلى محرك الإرسال المجمع 🚀"):
        st.session_state.step = 2
        st.rerun()

# --- المرحلة 2: محرك الإرسال المجمع (The Mass Trigger) ---
elif st.session_state.step == 2:
    st.title("🚀 محرك الإرسال لـ API عين العراق")
    
    # جلب البيانات التي لم تُرسل بعد
    df = pd.read_sql_query("SELECT * FROM bookings WHERE status = 'Pending'", conn)
    st.write("الأشخاص الجاهزون للإرسال:")
    st.table(df[['name', 'phone', 'nid', 'location']])
    
    col_back, col_send = st.columns(2)
    
    if col_back.button("➡️ رجوع للإضافة"):
        st.session_state.step = 1
        st.rerun()
        
    if col_send.button("إرسال الطلبات للسيرفر الآن 🔥"):
        if len(df) == 0:
            st.warning("المخزن فارغ!")
        else:
            progress = st.progress(0)
            for index, row in df.iterrows():
                st.write(f"جاري إرسال طلب لـ: {row['name']}...")
                
                # تنفيذ الربط الحقيقي
                status_code, response = call_ayniq_api("auth/login", {"phone": row['phone']})
                
                if status_code == 200:
                    st.toast(f"✅ نجح الإرسال لـ {row['name']}")
                    conn.cursor().execute("UPDATE bookings SET status = 'Sent' WHERE id = ?", (row['id'],))
                    conn.commit()
                else:
                    st.error(f"❌ فشل لـ {row['name']}: {response}")
                
                progress.progress((index + 1) / len(df))
                time.sleep(1) # فاصل زمني بسيط لتجنب الحظر
            
            st.success("اكتملت العملية!")

# ==========================================
# 4. تذييل الصفحة
# ==========================================
st.markdown("---")
st.caption("نظام إدارة حجز البطاقة الوطنية - نسخة الربط المباشر بـ API عين العراق")
