import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- إعداد قاعدة البيانات ---
conn = sqlite3.connect('plumbing_shop.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS inventory (item TEXT PRIMARY KEY, price REAL, stock INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY AUTOINCREMENT, item TEXT, qty INTEGER, total REAL, date TEXT)')
conn.commit()

st.set_page_config(page_title="نظام حسابات السباكة", layout="wide")
st.markdown("<style>.main {direction: rtl; text-align: right;}</style>", unsafe_allow_html=True)

st.title("📂 نظام مخازن ومبيعات السباكة")

# --- القائمة الجانبية (إدخال البيانات) ---
with st.sidebar:
    st.header("🛒 إضافة بضاعة")
    name = st.text_input("اسم الصنف (مثل: مواسير 1 بوصة)")
    p = st.number_input("سعر البيع", min_value=0.0)
    q = st.number_input("الكمية المتاحة", min_value=1)
    if st.button("إضافة للمخزن"):
        c.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?)", (name, p, q))
        conn.commit()
        st.success("تم التحديث!")

# --- عرض المربعات (المخزن) ---
st.subheader("📦 جدول المخزن (الإكسيل)")
df_inv = pd.read_sql_query("SELECT item as 'الصنف', price as 'السعر', stock as 'الكمية' FROM inventory", conn)
st.dataframe(df_inv, use_container_width=True) # هذا هو المربع الذي يشبه الإكسيل

# --- قسم البيع ---
st.divider()
st.subheader("💰 تسجيل عملية بيع")
if not df_inv.empty:
    col1, col2 = st.columns(2)
    with col1:
        sel_item = st.selectbox("اختر الصنف", df_inv['الصنف'])
    with col2:
        qty_sell = st.number_input("الكمية المباعة", min_value=1)
    
    if st.button("إتمام البيع"):
        price_item = df_inv[df_inv['الصنف'] == sel_item]['السعر'].values[0]
        total = price_item * qty_sell
        c.execute("INSERT INTO sales (item, qty, total, date) VALUES (?, ?, ?, ?)", 
                  (sel_item, qty_sell, total, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        st.balloons()
        st.success(f"تم البيع! الإجمالي: {total}")

