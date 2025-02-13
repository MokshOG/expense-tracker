import streamlit as st
import pickle
import os
import sys
import pandas as pd
from datetime import datetime

EXPENSE_FILE = "expense.pkl"

# Initialize session state if not present
if 'expenses' not in st.session_state:
    st.session_state.expenses = []

def add_expense(amount, category):
    current_date = datetime.now().strftime("%d/%m/%Y")
    record = [current_date, amount, category]
    
    # Append to the session state to prevent duplicate entries
    st.session_state.expenses.append(record)
    
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

def export_to_csv(expenses):
    df = pd.DataFrame(expenses, columns=["Date", "Amount", "Category"])
    df.index += 1  # Start index from 1
    csv_file = "expenses.csv"
    df.to_csv(csv_file, index_label="S.No")
    return csv_file

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
    
    # Deduplicate expenses using session state
    if 'expenses' in st.session_state:
        expenses.extend(st.session_state.expenses)
    
    if expenses:
        # Format data with S.No, Date, Category, Amount
        formatted_expenses = [{"S.No": i+1, "Date": exp[0], "Category": exp[2], "Amount": exp[1]} for i, exp in enumerate(expenses)]
        
        st.table(formatted_expenses)
        
        total_balance = sum(exp[1] for exp in expenses)
        st.write(f"### Net Balance: ₹{total_balance}")
        
        # Export to CSV feature
        csv_file = export_to_csv(expenses)
        with open(csv_file, "rb") as file:
            st.download_button(label="Download CSV", data=file, file_name=csv_file, mime="text/csv")
    else:
        st.write("No transactions recorded yet!")

st.sidebar.write("Developed with ❤️ by Moksh")
