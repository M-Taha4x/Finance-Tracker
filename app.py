import streamlit as st 
import db

st.title("Personal Finance Tracker")
st.subheader("Accounts")
st.dataframe(db.get_accounts())
st.subheader("Recent Transactions")
st.dataframe(db.get_all_transactions())
st.subheader("Add a Transaction")
account_df=db.get_accounts()
categories_df=db.get_categories()
with st.form("add_transaction_form"):
    date=st.date_input("Date")
    account_name=st.selectbox("Account",account_df['name'])
    amount=st.number_input("Amount",step=1.0)
    type_=st.selectbox("Type",['spend','income','transfer','loan_given','loan_repaid'])
    category_name=st.selectbox("Category",categories_df['name'])
    note=st.text_input("Note")
    
    submitted=st.form_submit_button("Add Transaction")
    if submitted:
        matching_row = account_df[account_df['name'] == account_name]
        account_id = int(matching_row['account_id'].iloc[0])
        category_id =int(categories_df[categories_df['name'] == category_name]['category_id'].iloc[0])
        if type_ == 'spend' and amount > 0:
            amount = -amount
    
        #st.write("DEBUG account_id:", account_id, type(account_id))
        #st.write("DEBUG category_id:", category_id, type(category_id))
    
        db.insert_transaction(str(date), account_id, amount, type_, category_id, note)
        st.success("Transaction Added!")
        