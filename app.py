import streamlit as st
import pandas as pd
from datetime import datetime

# إعداد الصفحة وتنسيقها
st.set_page_config(page_title="كاشير السباكة الذكي", layout="wide")
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 5px; height: 50px; background-color: #f0f2f6; }
    .bill-box { border: 2px solid #000; padding: 15px; background-color: white; color: black; }
    </style>
    """, unsafe_allow_html=True)

# قاعدة بيانات وهمية للمنتجات (يمكنك تعديلها من هنا)
if 'inventory' not in st.session_state:
    st.session_state.inventory = [
        {"name": "كوع 1 بوصة", "price": 15},
        {"name": "ماسورة 2 متر", "price": 120},
        {"name": "خلاط مياه", "price": 850},
        {"name": "محبس زاوية", "price": 45}
    ]

if 'bill_items' not in st.session_state:
    st.session_state.bill_items = []

st.title("🚰 كاشير محل السباكة")

# قسم البيانات الأساسية
col_cust1, col_cust2 = st.columns(2)
with col_cust1:
    c_name = st.text_input("اسم العميل", "عميل نقدي")
with col_cust2:
    c_phone = st.text_input("رقم الموبايل")

st.divider()

# العرض في أعمدة (المربعات)
st.subheader("📦 اختر المنتجات")
cols = st.columns(4) # 4 مربعات في الصف الواحد
for idx, item in enumerate(st.session_state.inventory):
    with cols[idx % 4]:
        if st.button(f"{item['name']}\n({item['price']} ج)"):
            st.session_state.bill_items.append({"الصنف": item['name'], "السعر": item['price']})
            st.rerun()

st.divider()

# عرض الفاتورة (المربعات/الجدول)
if st.session_state.bill_items:
    st.subheader("🛒 محتويات الفاتورة")
    df = pd.DataFrame(st.session_state.bill_items)
    st.table(df) # تظهر البيانات هنا في مربعات منظمة
    
    total = df["السعر"].sum()
    st.markdown(f"### 💰 الإجمالي: {total} جنيه")
    
    if st.button("🔴 مسح الفاتورة والبدء من جديد"):
        st.session_state.bill_items = []
        st.rerun()

    st.divider()
    
    # شكل الفاتورة النهائي
    if st.button("🖨️ عرض الفاتورة للطباعة"):
        st.markdown(f"""
        <div class="bill-box">
            <h2 style="text-align:center;">فاتورة مبيعات</h2>
            <p><b>العميل:</b> {c_name} | <b>الموبايل:</b> {c_phone}</p>
            <p><b>التاريخ:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <hr>
            <table style="width:100%">
                <tr><th>الصنف</th><th>السعر</th></tr>
                {''.join([f"<tr><td>{i['الصنف']}</td><td>{i['السعر']}</td></tr>" for i in st.session_state.bill_items])}
            </table>
            <hr>
            <h3>الإجمالي النهائي: {total} جنيه</h3>
        </div>
        """, unsafe_allow_html=True)

# إضافة منتج جديد للقائمة
with st.expander("➕ إضافة منتج جديد للمربعات"):
    new_n = st.text_input("اسم المنتج الجديد")
    new_p = st.number_input("سعر المنتج الجديد", min_value=0)
    if st.button("إضافة للمربعات"):
        st.session_state.inventory.append({"name": new_n, "price": new_p})
        st.success("تمت إضافة المنتج للمربعات!")
        st.rerun()
        
