import streamlit as st
import pandas as pd
from datetime import datetime

# إعداد الصفحة وتنسيق الألوان
st.set_page_config(page_title="نظام مبيعات السباكة", layout="wide")

st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; background-color: #f8f9fa; }
    .stButton>button {
        height: 80px; font-size: 18px; font-weight: bold;
        background-color: #ff9800; color: white; border-radius: 12px; border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover { background-color: #e68a00; }
    .invoice-box {
        background-color: white; padding: 25px; border-radius: 15px;
        border: 2px solid #eee; box-shadow: 0 10px 20px rgba(0,0,0,0.05);
    }
    .total-section {
        background-color: #2c3e50; color: white; padding: 15px;
        border-radius: 10px; text-align: center; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# قاعدة بيانات المنتجات (يمكنك مسحها وإضافة منتجاتك من داخل التطبيق)
if 'inventory' not in st.session_state:
    st.session_state.inventory = [
        {"name": "كوع 1 بوصة", "price": 25}, {"name": "ماسورة 2 متر", "price": 180},
        {"name": "خلاط مياه ميكسر", "price": 1450}, {"name": "محبس زاوية تركي", "price": 75},
        {"name": "تيس بلاستيك", "price": 40}, {"name": "جلبة إصلاح", "price": 30}
    ]

if 'bill_items' not in st.session_state:
    st.session_state.bill_items = []

st.title("🏗️ كاشير السباكة المطور")

# تقسيم الشاشة
col_bill, col_products = st.columns([1.5, 2])

# --- قسم المربعات (يسار الشاشة) ---
with col_products:
    st.subheader("📦 قائمة البضاعة (اضغط للإضافة)")
    n_cols = 3
    for i in range(0, len(st.session_state.inventory), n_cols):
        cols = st.columns(n_cols)
        for j, item in enumerate(st.session_state.inventory[i:i+n_cols]):
            with cols[j]:
                if st.button(f"{item['name']}\n{item['price']} ج"):
                    st.session_state.bill_items.append({
                        "id": datetime.now().timestamp(), # معرف فريد لكل بند
                        "الصنف": item['name'],
                        "السعر": item['price'],
                        "الكمية": 1,
                        "الخصم %": 0.0
                    })
                    st.rerun()

# --- قسم الفاتورة (يمين الشاشة) ---
with col_bill:
    st.markdown('<div class="invoice-box">', unsafe_allow_html=True)
    st.subheader("📝 تفاصيل الفاتورة")
    
    cust_name = st.text_input("اسم العميل / المقاول", "عميل نقدي")
    
    if st.session_state.bill_items:
        bill_display = []
        grand_total = 0
        
        for idx, item in enumerate(st.session_state.bill_items):
            with st.expander(f"⚙️ {item['الصنف']} - {item['السعر']} ج", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 0.5])
                with c1:
                    item['الكمية'] = st.number_input(f"الكمية", min_value=1, value=item['الكمية'], key=f"q_{item['id']}")
                with c2:
                    item['الخصم %'] = st.number_input(f"نسبة الخصم %", min_value=0.0, max_value=100.0, value=item['الخصم %'], key=f"d_{item['id']}")
                with c3:
                    if st.button("❌", key=f"del_{item['id']}"):
                        st.session_state.bill_items.pop(idx)
                        st.rerun()
                
                # الحسابات البرمجية لكل بند
                subtotal = item['السعر'] * item['الكمية']
                discount_val = subtotal * (item['الخصم %'] / 100)
                net = subtotal - discount_val
                grand_total += net
                
                bill_display.append({
                    "البند": item['الصنف'],
                    "السعر": item['السعر'],
                    "الكمية": item['الكمية'],
                    "الخصم": f"{item['الخصم %']}%",
                    "الصافي": f"{net:,.2f} ج"
                })

        st.divider()
        st.table(pd.DataFrame(bill_display))
        
        st.markdown(f"""
            <div class="total-section">
                <h3>إجمالي الفاتورة المطلوب</h3>
                <h1>{grand_total:,.2f} جنيه مصري</h1>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("💾 حفظ وطباعة الفاتورة (PDF)"):
            st.balloons()
            st.success("تم تسجيل الفاتورة في النظام!")
            
        if st.button("🚫 إلغاء العملية"):
            st.session_state.bill_items = []
            st.rerun()
    else:
        st.info("قم بالضغط على مربعات البضاعة في اليسار لبدء البيع")
    st.markdown('</div>', unsafe_allow_html=True)

# إضافة بضاعة جديدة للمربعات
with st.expander("⚙️ إعدادات: إضافة أصناف جديدة للمربعات"):
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        new_name = st.text_input("اسم المنتج الجديد")
    with col_in2:
        new_price = st.number_input("سعر البيع الافتراضي", min_value=0)
    if st.button("إضافة للمحل"):
        st.session_state.inventory.append({"name": new_name, "price": new_price})
        st.success(f"تمت إضافة {new_name} بنجاح!")
        st.rerun()
        
