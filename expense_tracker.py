import streamlit as st
import pickle
import os
import sys
import pandas as pd
from datetime import datetime

EXPENSE_FILE = "expense.pkl"

# Initialize session state if not present
if 'expenses' not in st.session_state:
    st.session_state.expenses = {}
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

def add_expense(user, amount, category, transaction_type):
    current_date = datetime.now().strftime("%d/%m/%Y")
    if transaction_type == "Debit":
        amount = -abs(amount)  # Ensure expense is negative
    else:
        amount = abs(amount)  # Ensure income is positive
    record = [current_date, amount, category]
    
    if 'expenses' not in st.session_state:
        st.session_state.expenses = {}
    
    if user not in st.session_state.expenses:
        st.session_state.expenses[user] = []
    
    if record not in st.session_state.expenses[user]:
        st.session_state.expenses[user].append(record)
    
    with open(EXPENSE_FILE, "wb") as file:
        pickle.dump(st.session_state.expenses, file)

def read_expenses():
    if "expenses" not in st.session_state:
        st.session_state.expenses = {}
    
    if os.path.exists(EXPENSE_FILE):
        with open(EXPENSE_FILE, "rb") as file:
            try:
                st.session_state.expenses = pickle.load(file)
            except EOFError:
                st.session_state.expenses = {}

def export_to_csv(user):
    if user in st.session_state.expenses:
        df = pd.DataFrame(st.session_state.expenses[user], columns=["Date", "Amount", "Category"])
        df.index += 1  # Start index from 1
        csv_file = f"{user}_expenses.csv"
        df.to_csv(csv_file, index_label="S.No")
        return csv_file
    return None

def filter_expenses_by_period(user, period):
    if user not in st.session_state.expenses:
        return []
    df = pd.DataFrame(st.session_state.expenses[user], columns=["Date", "Amount", "Category"])
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
    if period == "Monthly":
        df = df[df["Date"].dt.month == datetime.now().month]
    elif period == "Yearly":
        df = df[df["Date"].dt.year == datetime.now().year]
    return df.values.tolist()

def delete_expense(user, index):
    if user in st.session_state.expenses and 0 <= index < len(st.session_state.expenses[user]):
        del st.session_state.expenses[user][index]
        with open(EXPENSE_FILE, "wb") as file:
            pickle.dump(st.session_state.expenses, file)
        st.success("Expense deleted successfully!")

st.title("💰 Family Expense Tracker")

read_expenses()

if not st.session_state.current_user:
    users = list(st.session_state.expenses.keys())
    selected_user = st.selectbox("Select User:", ["New User"] + users)
    if selected_user == "New User":
        new_user = st.text_input("Enter Your Name:").strip()
        if new_user:
            st.session_state.current_user = new_user
            if new_user not in st.session_state.expenses:
                st.session_state.expenses[new_user] = []
    else:
        st.session_state.current_user = selected_user

if st.session_state.current_user:
    user = st.session_state.current_user
    
    menu = ["Add Expense", "View Summary"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Add Expense":
        st.subheader("Add a New Expense or Income")
        transaction_type = st.radio("Select Transaction Type:", ["Credit", "Debit"])
        amount = st.number_input("Enter Amount:", min_value=1, max_value=100000, value=1)
        category = st.text_input("Enter Category:")
        if st.button("Add Transaction"):
            add_expense(user, amount, category, transaction_type)
            st.success("Transaction Added Successfully!")
    
    elif choice == "View Summary":
        st.subheader(f"Expense Summary for {user}")
        expenses = st.session_state.expenses.get(user, [])
        
        period_filter = st.radio("Filter by:", ["All", "Monthly", "Yearly"], index=0)
        if period_filter != "All":
            expenses = filter_expenses_by_period(user, period_filter)
        
        if expenses:
            formatted_expenses = [{"S.No": i+1, "Date": exp[0], "Category": exp[2], "Amount": exp[1]} for i, exp in enumerate(expenses)]
            st.table(formatted_expenses)
            
            total_balance = sum(exp[1] for exp in expenses)
            st.write(f"### Net Balance: ₹{total_balance}")
            
            csv_file = export_to_csv(user)
            if csv_file:
                with open(csv_file, "rb") as file:
                    st.download_button(label="Download CSV", data=file, file_name=csv_file, mime="text/csv")
            
            st.subheader("Delete an Entry")
            delete_index = st.number_input("Enter the S.No of the entry to delete:", min_value=1, max_value=len(expenses), step=1)
            if st.button("Delete Entry"):
                delete_expense(user, delete_index - 1)
        else:
            st.write("No transactions recorded yet!")
    
    st.sidebar.write("Developed with ❤️ by Moksh")
