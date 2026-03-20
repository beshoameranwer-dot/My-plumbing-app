import streamlit as st
import pandas as pd
from datetime import datetime

# إعداد الصفحة لتكون بعرض الشاشة بالكامل
st.set_page_config(page_title="نظام كاشير السباكة", layout="wide")

# كود لتنسيق الألوان والمربعات لتشبه الصورة
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; background-color: #f0f2f6; }
    .stButton>button {
        height: 80px;
        font-size: 18px;
        font-weight: bold;
        background-color: #ff9800; /* لون المربعات مثل الصورة */
        color: white;
        border-radius: 10px;
        border: none;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stButton>button:hover { background-color: #e68a00; color: white; }
    .bill-area { background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; height: 600px; overflow-y: auto; }
    </style>
    """, unsafe_allow_html=True)

# قاعدة بيانات المنتجات
if 'inventory' not in st.session_state:
    st.session_state.inventory = [
        {"name": "كوع 1", "price": 15}, {"name": "كوع 2", "price": 25},
        {"name": "ماسورة 3/4", "price": 110}, {"name": "ماسورة 1", "price": 150},
        {"name": "خلاط دش", "price": 950}, {"name": "محبس دفن", "price": 220}
    ]

if 'bill_items' not in st.session_state:
    st.session_state.bill_items = []

# --- تقسيم الشاشة: يمين (الفاتورة) و يسار (المربعات) ---
col_bill, col_products = st.columns([1, 2])

with col_products:
    st.subheader("🛍️ قائمة الأصناف (اضغط للاختيار)")
    # عرض المنتجات في شبكة مربعات (Grid)
    n_cols = 4
    for i in range(0, len(st.session_state.inventory), n_cols):
        cols = st.columns(n_cols)
        for j, item in enumerate(st.session_state.inventory[i:i+n_cols]):
            with cols[j]:
                if st.button(f"{item['name']}\n{item['price']} ج"):
                    st.session_state.bill_items.append({"الصنف": item['name'], "السعر": item['price']})
                    st.rerun()

with col_bill:
    st.subheader("📄 الفاتورة الحالية")
    c_name = st.text_input("اسم العميل", "عميل نقدي")
    
    with st.container():
        if st.session_state.bill_items:
            df = pd.DataFrame(st.session_state.bill_items)
            st.table(df)
            total = df["السعر"].sum()
            st.markdown(f"## 💰 الإجمالي: {total} ج")
            
            if st.button("✅ إتمام وطباعة"):
                st.success("تم حفظ الفاتورة!")
                # هنا يمكن إضافة كود الطباعة لاحقاً
            
            if st.button("🗑️ مسح الكل"):
                st.session_state.bill_items = []
                st.rerun()
        else:
            st.info("الفاتورة فارغة. اضغط على الأصناف لإضافتها.")

# قسم الإدارة (إضافة بضاعة جديدة للمربعات)
with st.expander("⚙️ إضافة أصناف جديدة للمربعات"):
    new_name = st.text_input("اسم الصنف الجديد")
    new_price = st.number_input("السعر", min_value=0)
    if st.button("إضافة للمحل"):
        st.session_state.inventory.append({"name": new_name, "price": new_price})
        st.rerun()

