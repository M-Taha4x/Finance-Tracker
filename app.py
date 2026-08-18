import streamlit as st 
import db
import io

def check_password():
    def password_entered():
        if st.session_state['password']==st.secrets['app_password']:
            st.session_state['password_correct']=True
            del st.session_state['password']
        else:
            st.session_state['password_correct']=False
    
    if "password_correct" not in st.session_state:
        st.header("Welcome,Taha")
        st.text_input("Please Enter Your Password",type="password",on_change=password_entered,key='password')        
        return False
    elif not st.session_state['password_correct']:
        st.header("Welcome,Taha")
        st.text_input("Please Enter Your Correct Password",type='password',on_change=password_entered,key='password')
        st.error("Incorrect Password")
        return False
    else:
        return True
    
if not check_password():
    st.stop()

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
st.subheader("Recent Transaction")
col1,col2,col3=st.columns(3)
with col1:
    data_range=st.date_input("Date Range: ",value=[])
with col2:
    selected_accounts=st.multiselect("Accounts ",account_df['name'])
with col3:
    selected_categories=st.multiselect("Categories",categories_df['name'])
all_transactions=db.get_all_transactions()
filtered=all_transactions.copy()
if selected_accounts:
    selected_account_id=account_df[account_df['name'].isin(selected_accounts)]['account_id']
    filtered=filtered[filtered['account_id'].isin(selected_account_id)]
if selected_categories:
    selected_category_id=categories_df[categories_df['name'].isin(selected_categories)]['category_id']
    filtered=filtered[filtered['category_id'].isin(selected_category_id)]
if len(data_range)==2:
    start,end=data_range
    filtered=filtered[(filtered['date'] >= str(start)) & (filtered['date'] <= str(end))]
st.dataframe(filtered)
csv_data=filtered.to_csv(index=False)
st.download_button("Download as CSV",data=csv_data,file_name='transaction.csv',mime='text/csv')
buffer=io.BytesIO()
filtered.to_excel(buffer,index=False,engine='openpyxl')
st.download_button("Download as Excel",data=buffer.getvalue(),file_name='transactions.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')