import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

# --- 1. إعدادات الحسابات والبيانات ---
USERS_DATABASE = {"Beshoy": "2008", "Admin": "2024", "Staff": "1234"}
LOGO_URL = "https://i.imgur.com/vHq0M9n.png" # استبدل برابط لوجو مباشر

st.set_page_config(page_title="Marketing Shop Pro", layout="wide")

# تهيئة مخزن البيانات المؤقت (سيتم رفعه لجوجل شيت لاحقاً)
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'inventory' not in st.session_state: 
    # مثال لبيانات أولية (الاسم، السعر، الرصيد، الشركة، القسم)
    st.session_state.inventory = [
        {"name": "ماسورة 1 بوصة", "price": 100, "stock": 50, "main": "ايجيك", "sub": "Br"},
        {"name": "كوع 90", "price": 15, "stock": 10, "main": "ايجيك", "sub": "SMART"}
    ]
if 'folders' not in st.session_state: st.session_state.folders = {"ايجيك": "#E67E22"}
if 'sub_folders' not in st.session_state: st.session_state.sub_folders = {"ايجيك": ["Br", "SMART"]}
if 'bill_items' not in st.session_state: st.session_state.bill_items = []
if 'history' not in st.session_state: st.session_state.history = []
if 'nav' not in st.session_state: st.session_state.nav = {"main": None, "sub": None}

COLOR_MAP = {
    "أحمر": "#FF4B4B", "أخضر": "#2ECC71", "أسود": "#1C1C1C",
    "رمادي": "#95A5A6", "أبيض": "#FBFCFC", "برتقالي": "#E67E22", "أزرق": "#3498DB"
}

# --- 2. نظام تسجيل الدخول ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🔐 Marketing Shop - تسجيل دخول</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            if u in USERS_DATABASE and USERS_DATABASE[u] == p:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else: st.error("بيانات الدخول خاطئة")
    st.stop()

# --- 3. وظيفة الفاتورة PDF والـ QR ---
def create_pdf(c_name, items, total, seller, op_type):
    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    
    # إضافة اللوجو
    try:
        logo = ImageReader(LOGO_URL)
        p.drawImage(logo, width/2 - 50, height - 100, width=100, height=50, preserveAspectRatio=True)
    except: p.drawCentredString(width/2, height-80, "MARKETING SHOP PRO")

    # QR Code
    qr = qrcode.make(f"Type: {op_type}\nTotal: {total}\nSeller: {seller}")
    qr_buf = BytesIO()
    qr.save(qr_buf, format='PNG')
    p.drawInlineImage(qr_buf, width - 120, height - 120, width=80, height=80)

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height-140, f"Customer: {c_name}")
    p.drawString(50, height-155, f"Operation: {op_type}")
    p.drawString(50, height-170, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    
    y = height - 210
    p.line(50, y, 550, y)
    p.drawString(60, y-20, "Item")
    p.drawString(400, y-20, "Qty")
    p.drawString(480, y-20, "Total")
    
    y -= 40
    for item in items:
        p.drawString(60, y, item['name'])
        p.drawString(400, y, str(item['qty']))
        item_res = (item['price'] * item['qty']) * (1 - item['disc_pct']/100)
        p.drawString(480, y, f"{item_res:,.2f}")
        y -= 20
        
    p.line(50, y, 550, y)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(350, y-30, f"Net Total: {total:,.2f} EGP")
    p.save()
    buf.seek(0)
    return buf

# --- 4. القائمة الجانبية ---
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    page = st.radio("انتقل إلى:", ["صالة البيع (POS)", "رصيد المخازن", "سجل التقارير", "الإعدادات"])
    if st.button("🚪 خروج"):
        st.session_state.logged_in = False
        st.rerun()

# --- 5. صالة البيع (POS) ---
if page == "صالة البيع (POS)":
    col_pos, col_bill = st.columns([2, 1.2])
    
    with col_pos:
        if st.session_state.nav["main"]:
            if st.button("🔙 عودة"):
                if st.session_state.nav["sub"]: st.session_state.nav["sub"] = None
                else: st.session_state.nav["main"] = None
                st.rerun()

        if not st.session_state.nav["main"]:
            st.subheader("🏢 الشركات")
            cols = st.columns(3)
            for name, color in st.session_state.folders.items():
                st.markdown(f'<style>button[key="{name}"] {{background-color: {color} !important; color: white !important;}}</style>', unsafe_allow_html=True)
                if st.button(f"📁 {name}", key=name): st.session_state.nav["main"] = name; st.rerun()
        
        elif not st.session_state.nav["sub"]:
            subs = st.session_state.sub_folders.get(st.session_state.nav["main"], [])
            for s in subs:
                if st.button(f"🏷️ {s}"): st.session_state.nav["sub"] = s; st.rerun()
        
        else:
            items = [i for i in st.session_state.inventory if i['main']==st.session_state.nav['main'] and i['sub']==st.session_state.nav['sub']]
            for item in items:
                if st.button(f"{item['name']} - {item['price']}ج (المتاح: {item['stock']})"):
                    if item['stock'] > 0:
                        st.session_state.bill_items.append({"name": item['name'], "price": item['price'], "qty": 1, "disc_pct": 0, "id": datetime.now().timestamp()})
                        st.rerun()
                    else: st.error("عفواً، الكمية نفدت!")

    with col_bill:
        st.header("🧾 الفاتورة")
        op_type = st.radio("النوع:", ["مبيعات", "مرتجع"], horizontal=True)
        c_name = st.text_input("اسم العميل")
        
        grand_total = 0
        for idx, b in enumerate(st.session_state.bill_items):
            st.write(f"**{b['name']}**")
            b['qty'] = st.number_input("الكمية", 1, key=f"q_{b['id']}")
            b['disc_pct'] = st.slider("خصم %", 0, 100, key=f"d_{b['id']}")
            res = (b['price'] * b['qty']) * (1 - b['disc_pct']/100)
            grand_total += res
            if st.button("🗑️", key=f"del_{b['id']}"): st.session_state.bill_items.pop(idx); st.rerun()

        final_val = -grand_total if op_type == "مرتجع" else grand_total
        st.write(f"### الإجمالي: {final_val:,.2f} ج")
        
        if st.button("✅ تأكيد العملية"):
            # تحديث رصيد المخزن
            for b in st.session_state.bill_items:
                for inv in st.session_state.inventory:
                    if inv['name'] == b['name']:
                        if op_type == "مبيعات": inv['stock'] -= b['qty']
                        else: inv['stock'] += b['qty']
            
            # حفظ في السجل
            st.session_state.history.append({
                "الوقت": datetime.now().strftime("%H:%M"),
                "النوع": op_type, "العميل": c_name, "المبلغ": final_val, "البائع": st.session_state.user
            })
            
            pdf = create_pdf(c_name, st.session_state.bill_items, final_val, st.session_state.user, op_type)
            st.download_button("📥 تحميل PDF", data=pdf, file_name=f"{c_name}.pdf")
            st.session_state.bill_items = []
            st.success("تم الحفظ وتحديث المخزن!")

# --- 6. رصيد المخازن ---
elif page == "رصيد المخازن":
    st.header("📦 رصيد المخازن الحالي")
    df = pd.DataFrame(st.session_state.inventory)
    st.table(df)
    
    # تنبيه للأصناف المنتهية
    low_stock = [i['name'] for i in st.session_state.inventory if i['stock'] < 5]
    if low_stock: st.warning(f"⚠️ أصناف أوشكت على النفاد: {', '.join(low_stock)}")

# --- 7. السجل والتقارير ---
elif page == "سجل التقارير":
    st.header("📊 ملخص المبيعات")
    if st.session_state.history:
        df_h = pd.DataFrame(st.session_state.history)
        st.table(df_h)
        st.metric("صافي الدخل", f"{df_h['المبلغ'].sum():,.2f} ج")
        
        if st.session_state.user == "Beshoy":
            if st.button("🗑️ مسح السجل"): st.session_state.history = []; st.rerun()
    else: st.info("لا توجد عمليات اليوم")

# --- 8. الإعدادات ---
elif page == "الإعدادات":
    st.header("⚙️ إضافة بيانات")
    col1, col2 = st.columns(2)
    with col1:
        m_n = st.text_input("اسم الشركة")
        m_c = st.selectbox("اللون", list(COLOR_MAP.keys()))
        if st.button("إضافة شركة"):
            st.session_state.folders[m_n] = COLOR_MAP[m_c]
            st.session_state.sub_folders[m_n] = []
    with col2:
        parent = st.selectbox("تابع لشركة", list(st.session_state.folders.keys()))
        s_n = st.text_input("اسم القسم الفرعي")
        if st.button("إضافة قسم"): st.session_state.sub_folders[parent].append(s_n)
    
    st.divider()
    st.subheader("➕ إضافة صنف جديد")
    p_n = st.text_input("اسم المنتج")
    p_p = st.number_input("السعر")
    p_s = st.number_input("الرصيد الافتتاحي", min_value=0)
    p_m = st.selectbox("اختر الشركة", list(st.session_state.folders.keys()))
    p_sub = st.selectbox("اختر القسم", st.session_state.sub_folders.get(p_m, []))
    if st.button("حفظ المنتج للمخزن"):
        st.session_state.inventory.append({"name": p_n, "price": p_p, "stock": p_s, "main": p_m, "sub": p_sub})
        st.success("تم الحفظ")
                            
