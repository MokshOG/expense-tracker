import streamlit as st
import pickle
import os
import sys
from datetime import datetime

EXPENSE_FILE = "expense.pkl"

def add_expense(amount, category):
    current_date = datetime.now().strftime("%Y-%m-%d")
    record = [current_date, amount, category]
    
    # Append to the file
    with open(EXPENSE_FILE, "ab") as file:
        pickle.dump(record, file)

def read_expenses():
    expenses = []
    if os.path.exists(EXPENSE_FILE):
        with open(EXPENSE_FILE, "rb") as file:
            while True:
                try:
                    expenses.append(pickle.load(file))
                except EOFError:
                    break
    return expenses

# Check if Streamlit is installed
if "streamlit" not in sys.modules:
    st.error("Streamlit module is not found. Please ensure it is installed using 'pip install streamlit'.")
    sys.exit(1)

# Streamlit UI
st.title("💰 Family Expense Tracker")

menu = ["Add Expense", "View Summary"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Expense":
    st.subheader("Add a New Expense or Income")
    amount = st.number_input("Enter Amount (Use negative for expense, positive for income):", min_value=-100000, max_value=100000, value=0)
    category = st.text_input("Enter Category:")
    if st.button("Add Transaction"):
        if amount == 0:
            st.warning("Amount cannot be zero!")
        else:
            add_expense(amount, category)
            st.success("Transaction Added Successfully!")

elif choice == "View Summary":
    st.subheader("Expense Summary")
    expenses = read_expenses()
    if expenses:
        total_balance = sum(exp[1] for exp in expenses)
        st.write(f"### Net Balance: ₹{total_balance}")
        st.table(expenses)
    else:
        st.write("No transactions recorded yet!")

st.sidebar.write("Developed with ❤️ by Moksh")
