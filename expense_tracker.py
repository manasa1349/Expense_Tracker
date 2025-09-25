import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO

# ---------------- Database Setup ----------------
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    category TEXT,
    date TEXT,
    note TEXT
)
""")
conn.commit()

# ---------------- Functions ----------------
def add_expense(amount, category, note, date):
    cursor.execute("INSERT INTO expenses (amount, category, date, note) VALUES (?, ?, ?, ?)",
                   (amount, category, date, note))
    conn.commit()

def get_expenses():
    return pd.read_sql_query("SELECT * FROM expenses", conn)

def monthly_summary(df):
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    summary = df.groupby('month')['amount'].sum()
    return summary

def category_summary(df):
    summary = df.groupby('category')['amount'].sum()
    return summary

def plot_and_display(fig):
    # Save figure to BytesIO buffer and display as image for fixed size
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    st.image(buf)
    plt.close(fig)

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Personal Expense Tracker", layout="wide")
st.title("📊 Personal Expense Tracker")

# --- Add Expense Form ---
st.header("Add New Expense")
categories = ["Food", "Travel", "Bills", "Shopping", "Entertainment", "Others"]

with st.form("expense_form", clear_on_submit=True):
    amount = st.number_input("Amount", min_value=0.01, format="%.2f")
    category = st.selectbox("Category", categories)
    date = st.date_input("Date", datetime.today())
    note = st.text_input("Note (optional)")
    submitted = st.form_submit_button("Add Expense")
    if submitted:
        add_expense(amount, category, note, date.strftime("%Y-%m-%d"))
        st.success("Expense added successfully!")

# --- View Expenses ---
st.header("All Expenses")
df = get_expenses()
if df.empty:
    st.info("No expenses recorded yet.")
else:
    st.dataframe(df)

# --- Total Expense ---
if not df.empty:
    total_amount = df['amount'].sum()
    st.subheader(f"💰 Total Expense: {total_amount:.2f}")

# --- Vertically Stacked Charts (Balanced Size) ---
if not df.empty:
    # Monthly Summary
    st.header("Monthly Expenses")
    ms = monthly_summary(df)
    monthly_fig, ax = plt.subplots(figsize=(5,4))  # width=5, height=4
    ms.plot(kind="bar", ax=ax, color="skyblue")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Amount")
    ax.set_title("Monthly Expenses")
    plot_and_display(monthly_fig)

    # Category Summary
    st.header("Category-wise Expenses")
    cs = category_summary(df)
    category_fig, ax = plt.subplots(figsize=(5,4))  # same size as bar chart
    cs.plot(kind="pie", autopct="%1.1f%%", ax=ax, startangle=90)
    ax.set_ylabel("")
    ax.set_title("Expenses by Category")
    plot_and_display(category_fig)
