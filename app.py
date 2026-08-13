import streamlit as st 
import db

st.title("Personal Finance Tracker")
st.subheader("Accounts")
st.dataframe(db.get_accounts())
st.subheader("Recent Transactions")
st.dataframe(db.get_all_transactions())