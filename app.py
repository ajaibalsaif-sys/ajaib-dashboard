import streamlit as st
import pandas as pd
import sqlite3

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("expenses.db")
c = conn.cursor()

# إنشاء الجدول إذا غير موجود
c.execute('''
CREATE TABLE IF NOT EXISTS branches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    branch TEXT,
    month TEXT,
    sales REAL,
    costs REAL,
    expenses REAL
)
''')
conn.commit()

st.title("📊 لوحة التحكم الرئيسية - فروع الشركة")

# --- إدخال البيانات ---
st.header("➕ إضافة بيانات فرع")
with st.form("add_data"):
    branch = st.selectbox("اختر الفرع", ["الرياض", "جدة", "مكة", "الدمام", "المدينة"])
    month = st.text_input("الشهر (مثال: 2025-08)")
    sales = st.number_input("المبيعات", min_value=0.0, format="%.2f")
    costs = st.number_input("التكلفة", min_value=0.0, format="%.2f")
    expenses = st.number_input("المصروفات", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("إضافة")
    if submitted:
        c.execute("INSERT INTO branches (branch, month, sales, costs, expenses) VALUES (?, ?, ?, ?, ?)",
                  (branch, month, sales, costs, expenses))
        conn.commit()
        st.success("✅ تم إضافة البيانات")

# --- عرض البيانات ---
st.header("📑 جدول التحليل لكل فرع")

df = pd.read_sql("SELECT * FROM branches", conn)

if not df.empty:
    # الحسابات
    df["Expense %"] = (df["expenses"] / df["sales"] * 100).round(2)
    df["Profit"] = (df["sales"] - df["costs"] - df["expenses"]).round(2)
    df["Profit %"] = (df["Profit"] / df["sales"] * 100).round(2)

    st.dataframe(df[["branch", "month", "sales", "costs", "expenses", "Expense %", "Profit", "Profit %"]])

    # ملخص حسب الفروع
    st.subheader("📌 ملخص الفروع")
    summary = df.groupby("branch").agg({
        "sales": "sum",
        "costs": "sum",
        "expenses": "sum",
        "Profit": "sum"
    }).reset_index()

    summary["Expense %"] = (summary["expenses"] / summary["sales"] * 100).round(2)
    summary["Profit %"] = (summary["Profit"] / summary["sales"] * 100).round(2)

    st.table(summary)

else:
    st.info("ℹ️ لا توجد بيانات بعد، الرجاء إضافة بيانات الفروع.")
