import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# --- 1. إعدادات الحسابات ---
USERS_DATABASE = {"Beshoy": "2008", "Admin": "2024", "Staff": "1234"}

st.set_page_config(page_title="Marketing Shop Pro", layout="wide")

# تهيئة مخزن البيانات (Session State)
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'inventory' not in st.session_state: st.session_state.inventory = []
if 'folders' not in st.session_state: st.session_state.folders = {}
if 'sub_folders' not in st.session_state: st.session_state.sub_folders = {}
if 'bill_items' not in st.session_state: st.session_state.bill_items = []
if 'history' not in st.session_state: st.session_state.history = []
if 'nav' not in st.session_state: st.session_state.nav = {"main": None, "sub": None}

COLOR_MAP = {
    "أحمر": "#FF4B4B", "أخضر": "#2ECC71", "أسود": "#1C1C1C",
    "رمادي": "#95A5A6", "أبيض": "#FBFCFC", "برتقالي": "#E67E22", "أزرق": "#3498DB"
}

# --- 2. نظام تسجيل الدخول ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🔐 تسجيل الدخول - Marketing Shop</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            if u in USERS_DATABASE and USERS_DATABASE[u] == p:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else: st.error("بيانات الدخول غير صحيحة")
    st.stop()

# --- 3. وظيفة الفاتورة PDF والـ QR ---
def create_pdf(c_name, c_phone, items, total, seller, op_type):
    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    
    p.setFont("Helvetica-Bold", 22)
    p.drawCentredString(width/2, height - 60, "MARKETING SHOP PRO")
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, height - 90, f"INVOICE - {op_type}")

    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(f"Type: {op_type}\nTotal: {total}\nSeller: {seller}\nCustomer: {c_name}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    
    qr_buf = BytesIO()
    qr_img.save(qr_buf, format='PNG')
    qr_buf.seek(0)
    p.drawInlineImage(qr_buf, width - 110, height - 110, width=80, height=80)

    p.setFont("Helvetica", 12)
    p.drawString(50, height - 130, f"Customer: {c_name}")
    p.drawString(50, height - 145, f"Phone: {c_phone}")
    p.drawString(50, height - 160, f"Seller: {seller}")
    p.drawString(50, height - 175, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    y = height - 205
    p.line(50, y, 550, y)
    p.drawString(60, y - 20, "Item Name")
    p.drawString(400, y - 20, "Qty")
    p.drawString(480, y - 20, "Total")
    
    y -= 40
    for item in items:
        p.drawString(60, y, item['name'])
        p.drawString(400, y, str(item['qty']))
        item_res = (item['price'] * item['qty']) * (1 - item['disc_pct']/100)
        p.drawString(480, y, f"{item_res:,.2f}")
        y -= 20
        
    p.line(50, y, 550, y)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(380, y - 30, f"Grand Total: {total:,.2f} EGP")
    p.save()
    buf.seek(0)
    return buf

# --- 4. القائمة الجانبية ---
with st.sidebar:
    st.title("🏪 القائمة")
    st.write(f"👤 المستخدم: **{st.session_state.user}**")
    page = st.radio("اختر الصفحة:", ["صالة البيع", "المخزن", "التقارير", "الإعدادات"])
    if st.button("🚪 تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

# --- 5. صالة البيع (POS) ---
if page == "صالة البيع":
    col_pos, col_bill = st.columns([2, 1.2])
    with col_pos:
        if st.session_state.nav["main"]:
            if st.button("🔙 عودة"):
                if st.session_state.nav["sub"]: st.session_state.nav["sub"] = None
                else: st.session_state.nav["main"] = None
                st.rerun()

        if not st.session_state.nav["main"]:
            st.subheader("📁 الشركات")
            cols = st.columns(3)
            for name, color in st.session_state.folders.items():
                st.markdown(f'<style>button[key="{name}"] {{background-color: {color} !important; color: white !important;}}</style>', unsafe_allow_html=True)
                if st.button(f"🏢 {name}", key=name): st.session_state.nav["main"] = name; st.rerun()
        
        elif not st.session_state.nav["sub"]:
            subs = st.session_state.sub_folders.get(st.session_state.nav["main"], [])
            for s in subs:
                if st.button(f"🏷️ {s}"): st.session_state.nav["sub"] = s; st.rerun()
        
        else:
            items = [i for i in st.session_state.inventory if i['main']==st.session_state.nav['main'] and i['sub']==st.session_state.nav['sub']]
            for item in items:
                if st.button(f"📦 {item['name']} | {item['price']} ج (رصيد: {item['stock']})"):
                    if item['stock'] > 0:
                        st.session_state.bill_items.append({"name": item['name'], "price": item['price'], "qty": 1, "disc_pct": 0, "id": datetime.now().timestamp()})
                        st.rerun()
                    else: st.error("الكمية نفدت!")

    with col_bill:
        st.subheader("🧾 الفاتورة")
        op_type = st.radio("نوع العملية:", ["مبيعات", "مرتجع"], horizontal=True)
        c_name = st.text_input("اسم العميل")
        c_phone = st.text_input("رقم الموبايل (واتساب)")
        
        grand_total = 0
        for idx, b in enumerate(st.session_state.bill_items):
            st.write(f"**{b['name']}**")
            b['qty'] = st.number_input("الكمية", 1, key=f"q_{b['id']}")
            b['disc_pct'] = st.slider("خصم %", 0, 100, key=f"d_{b['id']}")
            res = (b['price'] * b['qty']) * (1 - b['disc_pct']/100)
            grand_total += res
            if st.button("🗑️ حذف", key=f"del_{b['id']}"): st.session_state.bill_items.pop(idx); st.rerun()

        final_val = -grand_total if op_type == "مرتجع" else grand_total
        st.write(f"### الإجمالي: {final_val:,.2f} ج")
        
        if st.button("✅ تأكيد وحفظ"):
            for b in st.session_state.bill_items:
                for inv in st.session_state.inventory:
                    if inv['name'] == b['name']:
                        if op_type == "مبيعات": inv['stock'] -= b['qty']
                        else: inv['stock'] += b['qty']
            
            # إرسال رسالة واتساب
            msg = f"مرحباً {c_name}، شكراً لتعاملك مع Marketing Shop. فاتورة {op_type} بمبلغ {final_val} ج. نتمنى زيارتكم قريباً!"
            wa_link = f"https://wa.me/{c_phone}?text={urllib.parse.quote(msg)}"
            
            st.session_state.history.append({
                "الوقت": datetime.now().strftime("%H:%M"), 
                "النوع": op_type, "العميل": c_name, "الموبايل": c_phone, 
                "المبلغ": final_val, "البائع": st.session_state.user
            })
            
            pdf = create_pdf(c_name, c_phone, st.session_state.bill_items, final_val, st.session_state.user, op_type)
            st.download_button("📥 تحميل الفاتورة", data=pdf, file_name=f"Invoice_{c_name}.pdf")
            st.markdown(f'[💬 إرسال واتساب]({wa_link})', unsafe_allow_html=True)
            st.session_state.bill_items = []

# --- الصفحات الأخرى ---
elif page == "المخزن":
    st.header("📦 رصيد المخزن")
    if st.session_state.inventory:
        st.table(pd.DataFrame(st.session_state.inventory))
    else: st.info("المخزن فارغ")

elif page == "التقارير":
    st.header("📊 التقارير")
    if st.session_state.history:
        df_h = pd.DataFrame(st.session_state.history)
        st.table(df_h)
        st.metric("صافي الربح اليومي", f"{df_h['المبلغ'].sum()} ج")
        if st.session_state.user == "Beshoy" and st.button("🗑️ مسح السجل"):
            st.session_state.history = []; st.rerun()
    else: st.info("لا توجد مبيعات بعد")

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
        s_n = st.text_input("اسم القسم")
        if st.button("إضافة قسم"): st.session_state.sub_folders[parent].append(s_n)
    
    st.divider()
    st.subheader("➕ إضافة صنف")
    pn = st.text_input("الاسم")
    pp = st.number_input("السعر")
    ps = st.number_input("الكمية", min_value=0)
    pm = st.selectbox("الشركة", list(st.session_state.folders.keys()))
    pb = st.selectbox("القسم", st.session_state.sub_folders.get(pm, []))
    if st.button("حفظ"):
        st.session_state.inventory.append({"name": pn, "price": pp, "stock": ps, "main": pm, "sub": pb})
        st.success("تم الحفظ")
