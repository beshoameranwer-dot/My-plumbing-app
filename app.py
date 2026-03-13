import streamlit as st
import pandas as pd
from datetime import datetime

# إعداد الصفحة واللغة
st.set_page_config(page_title="نظام الفواتير الاحترافي", layout="wide")
st.markdown("<style>.main {direction: rtl; text-align: right;}</style>", unsafe_allow_html=True)

st.title("📄 نظام إصدار فواتير السباكة")

# 1. إدخال بيانات الفاتورة
col1, col2 = st.columns(2)
with col1:
    customer_name = st.text_input("اسم العميل")
with col2:
    customer_phone = st.text_input("رقم التليفون")

# 2. إضافة المنتجات للفاتورة
st.divider()
if 'items' not in st.session_state:
    st.session_state.items = []

col_a, col_b, col_c = st.columns([3, 1, 1])
with col_a:
    product = st.text_input("اسم الصنف")
with col_b:
    price = st.number_input("السعر", min_value=0.0)
with col_c:
    qty = st.number_input("الكمية", min_value=1)

if st.button("إضافة للصنف للفاتورة"):
    st.session_state.items.append({"الصنف": product, "السعر": price, "الكمية": qty, "الإجمالي": price * qty})

# 3. عرض الفاتورة (المربعات)
if st.session_state.items:
    df = pd.DataFrame(st.session_state.items)
    st.subheader("🛒 تفاصيل الفاتورة")
    st.table(df) # هذه هي المربعات
    
    total_bill = df["الإجمالي"].sum()
    st.markdown(f"### 💰 إجمالي الفاتورة: {total_bill} جنيه")
    
    # 4. شكل الفاتورة للطباعة
    if st.button("تجهيز الفاتورة للطباعة"):
        st.markdown(f"""
        <div style="border: 2px solid black; padding: 20px; text-align: right; background-color: #f9f9f9;">
            <h2 style="text-align: center;">فاتورة مبيعات</h2>
            <p><strong>التاريخ:</strong> {datetime.now().strftime("%Y-%m-%d")}</p>
            <p><strong>العميل:</strong> {customer_name}</p>
            <p><strong>التليفون:</strong> {customer_phone}</p>
            <hr>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <th>الإجمالي</th><th>الكمية</th><th>السعر</th><th>الصنف</th>
                </tr>
                {"".join([f"<tr><td>{i['الإجمالي']}</td><td>{i['الكمية']}</td><td>{i['السعر']}</td><td>{i['الصنف']}</td></tr>" for i in st.session_state.items])}
            </table>
            <hr>
            <h3>صافي القيمة: {total_bill} جنيه</h3>
        </div>
        """, unsafe_allow_html=True)

    if st.button("مسح الفاتورة لبدء واحدة جديدة"):
        st.session_state.items = []
        st.rerun()
        
