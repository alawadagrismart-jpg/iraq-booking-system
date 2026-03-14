import streamlit as st
import pandas as pd
import sqlite3

# إنشاء قاعدة بيانات للحسابات
conn = sqlite3.connect('iraq_data.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, details TEXT, status TEXT)')
conn.commit()

st.set_page_config(page_title="Saree Iraq Dashboard", layout="wide")
st.title("🇮🇶 لوحة تحكم حجز العراق - نظام سحابي")

menu = ["إدارة الحسابات", "إرسال للسيرفر"]
choice = st.sidebar.selectbox("القائمة", menu)

if choice == "إدارة الحسابات":
    st.subheader("إضافة بيانات المواطنين (تخزين سحابي)")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("الاسم الكامل")
        phone = st.text_input("رقم الهاتف")
    with col2:
        details = st.text_area("بيانات إضافية (رقم البطاقة/السكن)")
    
    if st.button("حفظ البيانات"):
        c.execute("INSERT INTO accounts (name, phone, details, status) VALUES (?,?,?,?)", (name, phone, details, "جاهز"))
        conn.commit()
        st.success(f"تم تخزين بيانات {name} بنجاح")

    st.divider()
    df = pd.read_sql_query("SELECT * FROM accounts", conn)
    st.dataframe(df, use_container_width=True)

elif choice == "إرسال للسيرفر":
    st.subheader("بدء الحجز الجماعي")
    st.warning("سيتم استخدام الـ APIs المكتشفة لإرسال البيانات دفعة واحدة")
    if st.button("تشغيل محرك الإرسال (Turbo Mode)"):
        st.info("جاري الاتصال بـ adminmobile.nid-moi.gov.iq...")
