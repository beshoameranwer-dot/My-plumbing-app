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
    .invoice-card { background-color: white; padding: 20px; border-radius: 15px; border: 2px solid #ddd; color: black; font-family: 'Arial'; }
    .item-row { border-bottom: 1px dashed #ccc; padding: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تهيئة البيانات ---
if 'inventory' not in st.session_state: st.session_state.inventory = []
if 'folders' not in st.session_state: st.session_state.folders = {}
if 'bill_items' not in st.session_state: st.session_state.bill_items = []
if 'history' not in st.session_state: st.session_state.history = []
if 'current_folder' not in st.session_state: st.session_state.current_folder = None

# --- 3. القائمة الجانبية ---
with st.sidebar:
    st.title("🏪 Marketing Shop")
    page = st.radio("القائمة الرئيسية:", ["واجهة الكاشير (POS)", "رصيد المخازن", "إضافة منتجات ومجلدات", "سجل الفواتير"])
    st.divider()
    full_data = {"inv": st.session_state.inventory, "fold": st.session_state.folders, "hist": st.session_state.history}
    st.download_button("💾 تحميل نسخة احتياطية", json.dumps(full_data), "shop_data.json")

# --- 4. واجهة الكاشير (POS) ---
if page == "واجهة الكاشير (POS)":
    col_pos, col_bill = st.columns([2, 1.4])

    with col_pos:
        st.subheader("🛍️ معرض المنتجات")
        if st.session_state.current_folder:
            if st.button("⬅️ العودة للمجلدات"): st.session_state.current_folder = None; st.rerun()
            items = [i for i in st.session_state.inventory if i['folder'] == st.session_state.current_folder]
            p_cols = st.columns(3)
            for idx, item in enumerate(items):
                with p_cols[idx % 3]:
                    if st.button(f"{item['name']}\n{item['price']} ج", key=f"p_{idx}"):
                        st.session_state.bill_items.append({
                            "name": item['name'], "price": item['price'], "qty": 1, "disc": 0.0, "id": datetime.now().timestamp()
                        })
                        st.rerun()
        else:
            f_cols = st.columns(4)
            for idx, (name, color) in enumerate(st.session_state.folders.items()):
                with f_cols[idx % 4]:
                    st.markdown(f'<style>button[key="f_{name}"] {{background-color: {color} !important; color: white;}}</style>', unsafe_allow_html=True)
                    if st.button(f"📁 {name}", key=f"f_{name}"):
                        st.session_state.current_folder = name; st.rerun()

    with col_bill:
        st.markdown('<div class="invoice-card">', unsafe_allow_html=True)
        st.header("🧾 فاتورة بيع")
        
        # بيانات العميل الأساسية
        c_name = st.text_input("اسم العميل")
        c_phone = st.text_input("رقم الواتساب")
        pay_mode = st.radio("طريقة الدفع", ["نقدي", "فيزا", "آجل"], horizontal=True)
        
        st.markdown("---")
        st.write("**المنتجات المضافة:**")
        
        total_before_delivery = 0
        # عرض وتعديل بنود الفاتورة
        for idx, b in enumerate(st.session_state.bill_items):
            with st.container():
                col_n, col_q, col_d, col_x = st.columns([2, 1, 1, 0.5])
                col_n.write(f"**{b['name']}**")
                b['qty'] = col_q.number_input("الكمية", 1, key=f"q_{b['id']}")
                b['disc'] = col_d.number_input("خصم ج", 0.0, key=f"d_{b['id']}")
                
                line_total = (b['price'] * b['qty']) - b['disc']
                total_before_delivery += line_total
                
                if col_x.button("❌", key=f"del_{b['id']}"):
                    st.session_state.bill_items.pop(idx)
                    st.rerun()
                st.markdown(f"<small>السعر: {b['price']} | الإجمالي: {line_total} ج</small>", unsafe_allow_html=True)
                st.markdown('<div class="item-row"></div>', unsafe_allow_html=True)

        st.divider()
        delivery = st.number_input("رسوم التوصيل", 0.0)
        grand_total = total_before_delivery + delivery
        
        st.write(f"### الإجمالي النهائي: {grand_total:,.2f} ج")
        
        if st.button("✅ إتمام وحفظ"):
            if not st.session_state.bill_items:
                st.error("الفاتورة فارغة!")
            else:
                # 1. تجهيز نص الرسالة للواتساب (كتابة المنتجات)
                bill_text = f"📄 *Marketing Shop - فاتورة بيع*\n"
                bill_text += f"👤 العميل: {c_name}\n"
                bill_text += f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')}\n"
                bill_text += "--------------------------\n"
                for i in st.session_state.bill_items:
                    i_total = (i['price'] * i['qty']) - i['disc']
                    bill_text += f"🔹 {i['name']}\n   {i['qty']} × {i['price']} ج (خصم {i['disc']}) = {i_total} ج\n"
                bill_text += "--------------------------\n"
                if delivery > 0: bill_text += f"🚚 التوصيل: {delivery} ج\n"
                bill_text += f"💰 *الإجمالي النهائي: {grand_total} ج*\n"
                bill_text += f"💳 طريقة الدفع: {pay_mode}\n"
                bill_text += "شكراً لتعاملكم معنا!"

                # 2. الحفظ في السجل
                st.session_state.history.append({
                    "id": datetime.now().strftime("%H%M%S"), "customer": c_name, 
                    "items": len(st.session_state.bill_items), "total": grand_total, 
                    "type": pay_mode, "date": str(datetime.now())
                })
                
                # 3. رابط الواتساب
                url = f"https://wa.me/{c_phone}?text={urllib.parse.quote(bill_text)}"
                st.markdown(f'<a href="{url}" target="_blank" style="background-color: #25D366; color: white; padding: 15px; text-decoration: none; border-radius: 10px; display: block; text-align: center;">📲 إرسال الفاتورة عبر واتساب</a>', unsafe_allow_html=True)
                
                st.session_state.bill_items = [] # تصفير
                st.balloons()
        
        if st.button("🆕 فاتورة جديدة"):
            st.session_state.bill_items = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- الصفحات الأخرى (بدون تغيير) ---
elif page == "إضافة منتجات ومجلدات":
    st.header("⚙️ الإعدادات")
    f_n = st.text_input("اسم المجلد")
    f_c = st.selectbox("اللون", ["orange", "green", "blue", "red", "purple", "black"])
    if st.button("حفظ المجلد"): st.session_state.folders[f_n] = f_c; st.rerun()
    st.divider()
    p_n = st.text_input("اسم المنتج")
    p_p = st.number_input("السعر")
    p_f = st.selectbox("المجلد", list(st.session_state.folders.keys()))
    if st.button("حفظ المنتج"):
        st.session_state.inventory.append({"name": p_n, "price": p_p, "folder": p_f})
        st.success("تم الحفظ!")
elif page == "رصيد المخازن":
    st.header("📦 جرد المخزن")
    if st.session_state.inventory: st.table(pd.DataFrame(st.session_state.inventory))
elif page == "سجل الفواتير":
    st.header("📜 المبيعات")
    if st.session_state.history: st.dataframe(pd.DataFrame(st.session_state.history))
                    
