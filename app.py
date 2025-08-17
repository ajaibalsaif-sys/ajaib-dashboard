import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# الاتصال بقاعدة البيانات
conn = sqlite3.connect("expenses.db")
c = conn.cursor()

# إنشاء جدول إذا لم يكن موجود
c.execute('''CREATE TABLE IF NOT EXISTS expenses
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              date TEXT,
              branch TEXT,
              company TEXT,
              expense REAL,
              sales REAL,
              purchases REAL)''')
conn.commit()

st.title("لوحة تحكم المصروفات والمبيعات")

# إدخال بيانات جديدة
with st.form("add_data"):
    date = st.date_input("التاريخ")
    branch = st.text_input("الفرع")
    company = st.text_input("الشركة")
    expense = st.number_input("المصروف", min_value=0.0)
    sales = st.number_input("المبيعات", min_value=0.0)
    purchases = st.number_input("المشتريات", min_value=0.0)
    submitted = st.form_submit_button("إضافة")
    if submitted:
        c.execute("INSERT INTO expenses (date, branch, company, expense, sales, purchases) VALUES (?, ?, ?, ?, ?, ?)",
                  (str(date), branch, company, expense, sales, purchases))
        conn.commit()
        st.success("تمت الإضافة بنجاح")

# جلب البيانات
df = pd.read_sql("SELECT * FROM expenses", conn)

if not df.empty:
    st.subheader("📊 البيانات")
    st.dataframe(df)

    # ملخص شهري
    df['date'] = pd.to_datetime(df['date'])
    monthly = df.groupby(df['date'].dt.to_period("M")).agg({"expense": "sum", "sales": "sum", "purchases": "sum"}).reset_index()
    monthly['profit'] = monthly['sales'] - (monthly['expense'] + monthly['purchases'])
    monthly['expense_ratio'] = (monthly['expense'] / monthly['sales'] * 100).fillna(0)
    monthly['profit_ratio'] = (monthly['profit'] / monthly['sales'] * 100).fillna(0)

    st.subheader("📈 التحليلات الشهرية")
    st.dataframe(monthly)

    fig = px.bar(monthly, x=monthly['date'].astype(str), y=['sales', 'expense', 'purchases', 'profit'], barmode="group")
    st.plotly_chart(fig)
