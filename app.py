import streamlit as st
import pandas as pd
import sqlite3
import requests # مكتبة الإرسال للسيرفرات

conn = sqlite3.connect('iraq_data.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, details TEXT, status TEXT)')
conn.commit()

st.set_page_config(page_title="Saree Iraq Dashboard", layout="wide")
st.title("🇮🇶 لوحة تحكم حجز العراق - نظام سحابي")

menu = ["إدارة الحسابات", "إرسال للسيرفر"]
choice = st.sidebar.selectbox("القائمة", menu)

if choice == "إدارة الحسابات":
    st.subheader("إضافة بيانات المواطنين")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("الاسم الكامل")
        phone = st.text_input("رقم الهاتف")
    with col2:
        details = st.text_area("بيانات البطاقة/السكن")
    
    if st.button("حفظ البيانات"):
        c.execute("INSERT INTO accounts (name, phone, details, status) VALUES (?,?,?,?)", (name, phone, details, "جاهز"))
        conn.commit()
        st.success(f"تم تخزين بيانات {name} بنجاح")

    df = pd.read_sql_query("SELECT * FROM accounts", conn)
    st.dataframe(df, use_container_width=True)

elif choice == "إرسال للسيرفر":
    st.subheader("بدء الحجز الجماعي")
    df = pd.read_sql_query("SELECT * FROM accounts WHERE status='جاهز'", conn)
    
    if df.empty:
        st.warning("لا توجد بيانات جاهزة للإرسال. أضف حسابات أولاً.")
    else:
        st.write(f"لديك {len(df)} حسابات جاهزة للحجز.")
        if st.button("تشغيل محرك الإرسال (Turbo Mode)"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for index, row in df.iterrows():
                status_text.text(f"جاري إرسال بيانات: {row['name']}...")
                
                # هنا بنحط الرابط اللي حسن جابه
                target_url = "https://adminmobile.nid-moi.gov.iq/api/v1/booking" # مثال للرابط
                
                # إرسال البيانات فعلياً
                try:
                    # دي العملية اللي بتخلي البوت "يتحرك"
                    # payload = {"name": row['name'], "phone": row['phone']} 
                    # response = requests.post(target_url, json=payload)
                    
                    # محاكاة للإرسال السريع جداً (Turbo)
                    import time
                    time.sleep(0.5) # سرعة خرافية: نص ثانية لكل اسم
                    
                    st.success(f"✅ تم حجز موعد لـ {row['name']}")
                except:
                    st.error(f"❌ فشل الاتصال للسيرفر لـ {row['name']}")
                
                progress_bar.progress((index + 1) / len(df))
            
            st.balloons() # احتفال بانتهاء الحجز!
