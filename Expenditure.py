import streamlit as st
import pandas as pd
from datetime import datetime
import os
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Expense Tracker",
    page_icon=r"D:\\Python study\\Expenditure\\shoppy.png",
    layout="wide"
)

# Local Excel file path
excel_file_path = "expenses.xlsx"

# Save data to Excel
def save_to_excel(entry):
    try:
        if os.path.exists(excel_file_path):
            df = pd.read_excel(excel_file_path)
        else:
            df = pd.DataFrame(columns=["Type", "Date", "Time", "Details", "EnteredBy", "PaymentMethod", "Amount"])
        
        new_entry_df = pd.DataFrame([entry], columns=df.columns)
        df = pd.concat([df, new_entry_df], ignore_index=True)
        df.to_excel(excel_file_path, index=False)
    except Exception as e:
        st.error(f"Error saving to Excel: {e}")

# Fetch data from Excel
def fetch_data():
    try:
        data = pd.read_excel(excel_file_path)
        return data
    except Exception as e:
        st.error(f"Error fetching data from Excel: {e}")
        return pd.DataFrame()

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Entry Page", "Analysis"])

# Entry Page
if page == "Entry Page":
    st.title("💰 Expense Tracker - Entry Page")

    with st.form(key="expense_form"):
        st.subheader("Enter Expense Details")
        col1, col2 = st.columns(2)
        with col1:
            expense_type = st.selectbox("Type", ["Grocery", "Cosmetics", "Clothes", "Travel","Food", "Vegetables", "Medicine","Others", "EB-bill"], key="type")
            entry_date = st.date_input("Date", datetime.today(), key="date")
            
            # Manual time selection
            hours = st.selectbox("Hour", range(0, 24), key="hour")
            minutes = st.selectbox("Minute", range(0, 60), key="minute")
            entry_time = datetime.strptime(f"{hours}:{minutes}", "%H:%M").time()
            
            entered_by = st.selectbox("Entered By", ["Vethik", "Ishwarya"], key="person")
        with col2:
            details = st.text_area("Details", placeholder="Enter additional details about the expense...", key="details")
            payment_method = st.selectbox("Payment Method", ["cash", "phonepay"], key="payment")
            amount = st.number_input("Amount", min_value=0, step=1, key="amount")
        
        save_button = st.form_submit_button(label="💾 Save Entry")
        if save_button:
            entry = (expense_type, entry_date, entry_time, details, entered_by, payment_method, amount)
            save_to_excel(entry)
            st.success("✅ Entry saved to the Excel file!")

# Analysis Page
elif page == "Analysis":
    st.title("📊 Expense Analysis")

    data = fetch_data()
    if data.empty:
        st.warning("No data available to visualize.")
    else:
        st.sidebar.subheader("Filter Options")
        
        expense_type_filter = st.sidebar.multiselect("Select Expense Type", options=data['Type'].unique(), default=data['Type'].unique())
        payment_method_filter = st.sidebar.multiselect("Select Payment Method", options=data['PaymentMethod'].unique(), default=data['PaymentMethod'].unique())
        entered_by_filter = st.sidebar.multiselect("Select Entered By", options=data['EnteredBy'].unique(), default=data['EnteredBy'].unique())
        date_filter = st.sidebar.date_input("Select Date Range", [min(data['Date']), max(data['Date'])])

        filtered_data = data[
            data['Type'].isin(expense_type_filter) &
            data['PaymentMethod'].isin(payment_method_filter) &
            data['EnteredBy'].isin(entered_by_filter) &
            (data['Date'] >= pd.to_datetime(date_filter[0])) & 
            (data['Date'] <= pd.to_datetime(date_filter[1]))
        ]

         # Calculate the total expense
        total_expense = filtered_data['Amount'].sum()
        # Display Total Expense below the title
        st.subheader(f"💵 Total Expense: ₹{total_expense:,.2f}")

        st.dataframe(filtered_data, use_container_width=True)

       

        # Expense type distribution
        type_insight = filtered_data.groupby('Type')['Amount'].sum().reset_index()
        fig1 = px.bar(type_insight, x='Type', y='Amount', title="Expense Type Distribution")
        # Add values on the bars
        fig1.update_traces(text=type_insight['Amount'], textposition='outside')

        # Improve layout for better visibility
        fig1.update_layout(
            xaxis_title="Type",
            yaxis_title="Total Amount",
            showlegend=False
        )
        
        # Pie Chart for Expense Type
        pie_chart = px.pie(type_insight, values='Amount', names='Type', title="Expense Type Breakdown")

        # Daily Expenditure Trend
        trend_data = filtered_data.groupby('Date')['Amount'].sum().reset_index()
        fig2 = px.bar(trend_data, x='Date', y='Amount', title="Daily Expenditure Trend")

        # Add values on the bars
        fig2.update_traces(text=trend_data['Amount'], textposition='outside')

        # Improve layout for better visibility
        fig2.update_layout(
            xaxis_title="Date",
            yaxis_title="Total Amount",
            showlegend=False,
            title_x=0.5  # Center-align the title
        )

        # Layout: Bar and Pie chart side by side
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            st.plotly_chart(pie_chart, use_container_width=True)
        
        # Layout: Daily Expenditure Trend full width
        st.plotly_chart(fig2, use_container_width=True)

        

