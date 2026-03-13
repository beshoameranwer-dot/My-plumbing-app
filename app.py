import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import urllib.parse

# --- 1. Database Setup ---
conn = sqlite3.connect('plumbing_data.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS inventory (item TEXT PRIMARY KEY, price REAL, qty INTEGER, category TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS customers (phone TEXT PRIMARY KEY, name TEXT, debt REAL)')
c.execute('CREATE TABLE IF NOT EXISTS sales (id TEXT, total REAL, date TEXT)')
conn.commit()

# --- 2. Page Config ---
st.set_page_config(page_title="نظام سباكة برو", layout="wide")

st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    div.stButton > button:first-child { width: 100%; border-radius: 10px; height: 60px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚰 متجر السباكة الذكي")

# --- Simple Menu for adding items ---
with st.expander("🛠️ إضافة بضاعة جديدة"):
    name = st.text_input("الصنف")
    price = st.number_input("السعر", min_value=0.0)
    cat = st.selectbox("القسم", ["مواسير", "خلاطات", "أخرى"])
    if st.button("حفظ"):
        c.execute("INSERT OR REPLACE INTO inventory VALUES (?, ?, ?, ?)", (name, price, 10, cat))
        conn.commit()
        st.success("تم الحفظ!")

# --- View Items ---
items = c.execute("SELECT * FROM inventory").fetchall()
for item in items:
    st.write(f"📦 {item[0]} - السعر: {item[1]}")
