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

def add_expense(amount, category, transaction_type):
    current_date = datetime.now().strftime("%d/%m/%Y")
    if transaction_type == "Debit":
        amount = -abs(amount)  # Ensure expense is negative
    else:
        amount = abs(amount)  # Ensure income is positive
    record = [current_date, amount, category]
    
    # Append to session state to prevent duplicate entries
    if record not in st.session_state.expenses:
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
                    record = pickle.load(file)
                    if record not in expenses:  # Prevent duplicate loading
                        expenses.append(record)
                except EOFError:
                    break
    return expenses

def export_to_csv(expenses):
    df = pd.DataFrame(expenses, columns=["Date", "Amount", "Category"])
    df.index += 1  # Start index from 1
    csv_file = "expenses.csv"
    df.to_csv(csv_file, index_label="S.No")
    return csv_file

def filter_expenses_by_period(expenses, period):
    df = pd.DataFrame(expenses, columns=["Date", "Amount", "Category"])
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
    if period == "Monthly":
        df = df[df["Date"].dt.month == datetime.now().month]
    elif period == "Yearly":
        df = df[df["Date"].dt.year == datetime.now().year]
    return df.values.tolist()

def delete_expense(index):
    if 0 <= index < len(st.session_state.expenses):
        del st.session_state.expenses[index]
        with open(EXPENSE_FILE, "wb") as file:
            for record in st.session_state.expenses:
                pickle.dump(record, file)
        st.success("Expense deleted successfully!")

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
    transaction_type = st.radio("Select Transaction Type:", ["Credit", "Debit"])
    amount = st.number_input("Enter Amount:", min_value=1, max_value=100000, value=0)
    category = st.text_input("Enter Category:")
    if st.button("Add Transaction"):
        if amount == 0:
            st.warning("Amount cannot be zero!")
        else:
            add_expense(amount, category, transaction_type)
            st.success("Transaction Added Successfully!")

elif choice == "View Summary":
    st.subheader("Expense Summary")
    expenses = read_expenses()
    
    # Deduplicate expenses using session state
    if 'expenses' in st.session_state:
        for exp in st.session_state.expenses:
            if exp not in expenses:
                expenses.append(exp)
    
    period_filter = st.radio("Filter by:", ["All", "Monthly", "Yearly"], index=0)
    if period_filter != "All":
        expenses = filter_expenses_by_period(expenses, period_filter)
    
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
        
        # Delete Expense Feature
        st.subheader("Delete an Entry")
        delete_index = st.number_input("Enter the S.No of the entry to delete:", min_value=1, max_value=len(expenses), step=1)
        if st.button("Delete Entry"):
            delete_expense(delete_index - 1)
    else:
        st.write("No transactions recorded yet!")

st.sidebar.write("Developed with ❤️ by Moksh")
