import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader # استيراد مكتبة ImageReader

# --- 1. قاعدة بيانات الحسابات ---
USERS_DATABASE = {
    "Beshoy": "2008",
    "Admin": "2024",
    "Staff": "1234"
}

# --- رابط اللوجو الخاص بك هنا ---
# تأكد أن هذا الرابط هو رابط مباشر لصورة اللوجو (ينتهي بـ .png أو .jpg)
LOGO_URL = "https://i.imgur.com/vHq0M9n.png" # مثال، استبدله بالرابط الخاص بك

st.set_page_config(page_title="Marketing Shop Pro", layout="wide")

# تهيئة الجلسة (Session State)
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
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
    st.markdown("<h2 style='text-align: center; color: #2E86C1;'>🏪 Marketing Shop - تسجيل دخول</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            if u in USERS_DATABASE and USERS_DATABASE[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else: st.error("بيانات خاطئة")
    st.stop()

# --- 3. وظيفة إنشاء الفاتورة PDF (تم تحديثها باللوجو) ---
def create_pdf(c_name, items, total, seller, op_type):
    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    
    # --- إضافة اللوجو ---
    try:
        logo = ImageReader(LOGO_URL)
        # يمكنك تعديل (عرض الصورة، ارتفاع الصورة، X-position, Y-position) حسب الحاجة
        p.drawImage(logo, width/2 - 60, height - 120, width=120, height=60, preserveAspectRatio=True)
    except Exception as e:
        st.warning(f"لم يتم تحميل اللوجو: {e}. سيتم استخدام نص بدلاً من ذلك.")
        p.setFont("Helvetica-Bold", 18)
        p.drawCentredString(width/2, height-130, "MARKETING SHOP PRO")

    # QR Code
    qr_data = f"Store: Marketing Shop\nType: {op_type}\nSeller: {seller}\nTotal: {total} EGP"
    qr = qrcode.make(qr_data)
    qr_buf = BytesIO()
    qr.save(qr_buf, format='PNG')
    # يمكنك تعديل (X-position, Y-position) ليتناسب مع اللوجو
    p.drawInlineImage(qr_buf, width/2 - 35, height - 190, width=70, height=70) # تم تعديل مكان الـ QR

    # عنوان الفاتورة (بعد اللوجو والـ QR)
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, height-210, f"INVOICE - {op_type.upper()}") # تم تعديل مكان العنوان
    p.setFont("Helvetica", 10)
    p.drawString(50, height-240, f"Customer: {c_name}")
    p.drawString(50, height-255, f"Seller: {seller}")
    p.drawString(50, height-270, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    y = height - 300 # تم تعديل بداية جدول المنتجات
    p.line(50, y, 550, y)
    p.drawString(60, y-15, "Item Description")
    p.drawString(480, y-15, "Amount")
    y -= 35
    for item in items:
        p.drawString(60, y, f"{item['name']} (x{item['qty']}) - Disc: {item['disc_pct']}%")
        item_total = (item['price'] * item['qty']) * (1 - item['disc_pct']/100)
        p.drawString(480, y, f"{item_total:,.2f}")
        y -= 20
    
    p.line(50, y, 550, y)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(380, y-30, f"Net Total: {total:,.2f} EGP")
    p.save()
    buf.seek(0)
    return buf

# --- 4. القائمة الجانبية ---
with st.sidebar:
    st.title("🏪 Marketing Shop")
    st.write(f"👤 مرحباً: **{st.session_state.current_user}**")
    page = st.radio("القائمة الرئيسية:", ["صالة البيع (POS)", "إضافة منتجات ومجلدات", "سجل العمليات والتقارير"])
    if st.button("🚪 تسجيل خروج"):
        st.session_state.logged_in = False
        st.rerun()

# --- 5. صالة البيع (POS) ---
if page == "صالة البيع (POS)":
    col_pos, col_bill = st.columns([2, 1.3])
    
    with col_pos:
        if st.session_state.nav["main"]:
            if st.button("🔙 عودة"):
                if st.session_state.nav["sub"]: st.session_state.nav["sub"] = None
                else: st.session_state.nav["main"] = None
                st.rerun()

        if not st.session_state.nav["main"]:
            st.subheader("🏢 الشركات الرئيسية")
            cols = st.columns(3)
            for name, color in st.session_state.folders.items():
                st.markdown(f'<style>button[key="m_{name}"] {{background-color: {color} !important; color: white !important;}}</style>', unsafe_allow_html=True)
                if st.button(f"📁 {name}", key=name): st.session_state.nav["main"] = name; st.rerun()
        
        elif not st.session_state.nav["sub"]:
            st.subheader(f"📂 أقسام {st.session_state.nav['main']}")
            subs = st.session_state.sub_folders.get(st.session_state.nav["main"], [])
            for s_name in subs:
                if st.button(f"🏷️ {s_name}"): st.session_state.nav["sub"] = s_name; st.rerun()
        
        else:
            items = [i for i in st.session_state.inventory if i['main']==st.session_state.nav['main'] and i['sub']==st.session_state.nav['sub']]
            for item in items:
                if st.button(f"{item['name']} - {item['price']} ج"):
                    st.session_state.bill_items.append({"name": item['name'], "price": item['price'], "qty": 1, "disc_pct": 0, "id": datetime.now().timestamp()})
                    st.rerun()

    with col_bill:
        st.header("🧾 الفاتورة")
        op_type = st.radio("نوع العملية:", ["مبيعات", "مرتجع"], horizontal=True)
        c_name = st.text_input("اسم العميل")
        c_phone = st.text_input("رقم الواتساب")
        
        grand_total = 0
        for idx, b in enumerate(st.session_state.bill_items):
            st.write(f"**{b['name']}**")
            c1, c2 = st.columns([1, 1])
            b['qty'] = c1.number_input("الكمية", 1, key=f"q_{b['id']}")
            b['disc_pct'] = c2.slider("خصم %", 0, 100, b['disc_pct'], key=f"d_{b['id']}")
            res = (b['price'] * b['qty']) * (1 - b['disc_pct']/100)
            grand_total += res
            if st.button("🗑️ حذف", key=f"del_{b['id']}"): st.session_state.bill_items.pop(idx); st.rerun()

        final_amount = -grand_total if op_type == "مرتجع" else grand_total
        st.write(f"### الإجمالي: {final_amount:,.2f} ج")
        
        if st.button("✅ إتمام العملية"):
            st.session_state.history.append({
                "الوقت": datetime.now().strftime("%H:%M %d-%m"),
                "النوع": op_type,
                "العميل": c_name,
                "المبلغ": final_amount,
                "البائع": st.session_state.current_user
            })
            pdf = create_pdf(c_name, st.session_state.bill_items, final_amount, st.session_state.current_user, op_type)
            st.download_button("📥 تحميل الفاتورة PDF", data=pdf, file_name=f"{op_type}_{c_name}.pdf")
            st.session_state.bill_items = []
            st.success("تم تسجيل العملية!")

# --- 6. سجل العمليات والتقارير ---
elif page == "سجل العمليات والتقارير":
    st.header("📊 التقارير المالية")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        
        # ملخص مالي
        m1, m2, m3 = st.columns(3)
        sales = df[df["النوع"] == "مبيعات"]["المبلغ"].sum()
        returns = df[df["النوع"] == "مرتجع"]["المبلغ"].abs().sum()
        m1.metric("إجمالي المبيعات", f"{sales:,.2f} ج")
        m2.metric("إجمالي المرتجعات", f"{returns:,.2f} ج", delta_color="inverse")
        m3.metric("صافي الدخل", f"{(sales - returns):,.2f} ج")
        
        st.divider()
        st.subheader("📜 سجل العمليات التفصيلي")
        st.table(df)
        
        if st.session_state.current_user == "Beshoy":
            if st.button("⚠️ مسح السجل بالكامل"):
                st.session_state.history = []
                st.rerun()
    else: st.info("لا توجد مبيعات بعد")

# --- 7. صفحة الإعدادات ---
elif page == "إضافة منتجات ومجلدات":
    st.header("⚙️ إدارة البيانات")
    m_name = st.text_input("اسم الشركة (رئيسي)")
    m_color = st.selectbox("اللون", list(COLOR_MAP.keys()))
    if st.button("إضافة مجلد رئيسي"):
        st.session_state.folders[m_name] = COLOR_MAP[m_color]
        st.session_state.sub_folders[m_name] = []
    st.divider()
    p_main = st.selectbox("الشركة التابع لها", list(st.session_state.folders.keys()))
    s_name = st.text_input("اسم القسم (فرعي)")
    if st.button("إضافة مجلد فرعي"): st.session_state.sub_folders[p_main].append(s_name)
    st.divider()
    pn = st.text_input("اسم الصنف")
    pp = st.number_input("سعر القطعة")
    pm = st.selectbox("اختر الشركة", list(st.session_state.folders.keys()))
    ps = st.selectbox("اختر القسم", st.session_state.sub_folders.get(pm, []))
    if st.button("حفظ الصنف"):
        st.session_state.inventory.append({"name": pn, "price": pp, "main": pm, "sub": ps})

