import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import json

# --- 1. إعدادات الواجهة ---
st.set_page_config(page_title="Marketing Shop POS", layout="wide")

st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .stButton>button { border-radius: 10px; height: 60px; font-weight: bold; width: 100%; color: white; border: none; }
    .invoice-card { background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #ddd; color: black; }
    .sidebar-section { background-color: #f1f3f5; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تهيئة البيانات في الذاكرة ---
if 'inventory' not in st.session_state:
    st.session_state.inventory = [] # المنتجات
if 'folders' not in st.session_state:
    st.session_state.folders = {} # المجلدات وألوانها
if 'bill_items' not in st.session_state:
    st.session_state.bill_items = [] # الفاتورة الحالية
if 'history' not in st.session_state:
    st.session_state.history = [] # سجل المبيعات
if 'current_folder' not in st.session_state:
    st.session_state.current_folder = None

# --- 3. القائمة الجانبية (التنقل) ---
with st.sidebar:
    st.title("🏪 Marketing Shop")
    page = st.radio("القائمة الرئيسية:", ["واجهة الكاشير (POS)", "رصيد المخازن", "إضافة منتجات ومجلدات", "سجل الفواتير"])
    st.divider()
    # ميزة الحفظ اليدوي بديلة للسحابة
    st.subheader("💾 حفظ البيانات")
    full_data = {"inv": st.session_state.inventory, "fold": st.session_state.folders, "hist": st.session_state.history}
    st.download_button("تحميل نسخة احتياطية (Excel/JSON)", json.dumps(full_data), "shop_data.json")

# --- 4. صفحة الإعدادات (إضافة الأصناف والمجلدات) ---
if page == "إضافة منتجات ومجلدات":
    st.header("📂 تنظيم المجلدات والأصناف")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 إنشاء مجلد جديد")
        f_name = st.text_input("اسم المجلد (مثلاً: سباكة)")
        f_color = st.selectbox("لون المجلد", ["green", "orange", "gray", "black", "purple", "yellow", "red", "blue"])
        if st.button("حفظ المجلد"):
            st.session_state.folders[f_name] = f_color
            st.rerun()

    with col2:
        st.subheader("📦 إضافة منتج")
        p_name = st.text_input("اسم المنتج")
        p_price = st.number_input("السعر", min_value=0.0)
        p_stock = st.number_input("الكمية المتاحة", min_value=0)
        p_folder = st.selectbox("المجلد التابع له", list(st.session_state.folders.keys()))
        if st.button("إضافة للمخزن"):
            st.session_state.inventory.append({"name": p_name, "price": p_price, "stock": p_stock, "folder": p_folder})
            st.success("تمت الإضافة!")

# --- 5. واجهة الكاشير (POS) ---
elif page == "واجهة الكاشير (POS)":
    col_pos, col_bill = st.columns([2, 1.3])

    with col_pos:
        st.subheader("🛍️ معرض المنتجات")
        # زر العودة من المجلد للمجلدات الرئيسية
        if st.session_state.current_folder:
            if st.button("⬅️ العودة للمجلدات الرئيسية"):
                st.session_state.current_folder = None
                st.rerun()
            
            # عرض المنتجات داخل المجلد المختار
            items = [i for i in st.session_state.inventory if i['folder'] == st.session_state.current_folder]
            p_cols = st.columns(3)
            for idx, item in enumerate(items):
                with p_cols[idx % 3]:
                    if st.button(f"{item['name']}\n{item['price']} ج", key=f"p_{idx}"):
                        st.session_state.bill_items.append({"name": item['name'], "price": item['price'], "qty": 1, "disc": 0.0})
                        st.rerun()
        else:
            # عرض المجلدات الملونة
            f_cols = st.columns(4)
            for idx, (name, color) in enumerate(st.session_state.folders.items()):
                with f_cols[idx % 4]:
                    st.markdown(f'<style>button[key="f_{name}"] {{background-color: {color} !important; color: white;}}</style>', unsafe_allow_html=True)
                    if st.button(f"📁 {name}", key=f"f_{name}"):
                        st.session_state.current_folder = name
                        st.rerun()

    with col_bill:
        st.markdown('<div class="invoice-card">', unsafe_allow_html=True)
        st.header("🧾 الفاتورة")
        pay_mode = st.radio("طريقة الدفع", ["نقدي", "فيزا", "آجل"], horizontal=True)
        
        total = 0
        for idx, b in enumerate(st.session_state.bill_items):
            c1, c2, c3 = st.columns([2, 1, 0.5])
            c1.write(f"**{b['name']}**")
            b['qty'] = c2.number_input("الكمية", 1, key=f"q_{idx}")
            if c3.button("❌", key=f"del_{idx}"):
                st.session_state.bill_items.pop(idx)
                st.rerun()
            total += (b['price'] * b['qty'])

        st.divider()
        c_name = st.text_input("اسم العميل")
        c_phone = st.text_input("رقم الواتساب")
        
        if st.button("✅ إتمام وحفظ الفاتورة"):
            # حفظ في السجل الداخلي
            bill_id = datetime.now().strftime("%H%M%S")
            st.session_state.history.append({"id": bill_id, "customer": c_name, "total": total, "type": pay_mode, "date": str(datetime.now())})
            
            # تجهيز رسالة واتساب
            msg = f"فاتورة من Marketing Shop\nالعميل: {c_name}\nالإجمالي: {total} ج\nالدفع: {pay_mode}"
            url = f"https://wa.me/{c_phone}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{url}" target="_blank">📲 اضغط هنا للإرسال عبر واتساب</a>', unsafe_allow_html=True)
            
            st.session_state.bill_items = [] # تصفير الفاتورة
            st.balloons()
            st.success("تم الحفظ في سجل اليوم!")

        if st.button("🆕 فاتورة جديدة"):
            st.session_state.bill_items = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 6. الصفحات الأخرى ---
elif page == "رصيد المخازن":
    st.header("📦 حالة المخزن")
    if st.session_state.inventory:
        st.table(pd.DataFrame(st.session_state.inventory))
    else:
        st.info("لا توجد أصناف مضافة")

elif page == "سجل الفواتير":
    st.header("📜 سجل المبيعات")
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history))
    else:
        st.info("السجل فارغ")

