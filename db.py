import psycopg2
import pandas as pd
import streamlit as st

def get_connection():
    conn=psycopg2.connect(st.secrets["postgres_url"])
    return conn

def insert_transaction(date,account_id,amount,type_,category_id,note):
    conn=get_connection()
    cur=conn.cursor()
    cur.execute(
        """Insert Into transactions(date,account_id,amount,type_,category_id,note)
        Values(%s,%s,%s,%s,%s,%s)""",
        (date,account_id,amount,type_,category_id,note)
    )
    conn.commit()
    cur.close()
    conn.close()

def create_tables():
    conn = get_connection()
    cur=conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id Serial Primary Key,
            name TEXT NOT NULL,
            starting_balance REAL NOT NULL DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id Serial Primary Key,
            name TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id serial primary key,
            date TEXT NOT NULL,
            account_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            type_ TEXT NOT NULL,
            category_id INTEGER,
            note TEXT,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id),
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    
def seed_accounts_and_categories():
    conn = get_connection()
    curr=conn.cursor()
    existing = pd.read_sql("SELECT COUNT(*) as c FROM accounts", conn)
    if existing['c'].iloc[0] == 0:
        accounts = [("Wallet", 920), ("Meezan Bank", 5415.02), ("EasyPaisa", 0), ("JazzCash", 0), ("Sadapay", 0), ("NayaPay", 0)]
        curr.executemany("INSERT INTO accounts (name, starting_balance) VALUES (%s, %s)", accounts)
        categories = ["HangOut","Lunch","Dinner","Breakfast","Essentials","Transport","Snacks/Drinks","Donation","Subscription","Loan","Pocket Money","Other"]
        curr.executemany("INSERT INTO categories (name) VALUES (%s)", [(c,) for c in categories])
        conn.commit()
    curr.close()
    conn.close()
    
def reset_accounts(new_accounts):
    conn = get_connection()
    curr=conn.cursor()
    curr.execute("DELETE FROM accounts")
    curr.executemany("INSERT INTO accounts (name, starting_balance) VALUES (%s, %s)", new_accounts)
    conn.commit()
    curr.close()
    conn.close()

def get_all_transactions():
    conn=get_connection()
    df=pd.read_sql(""" 
            SELECT 
            t.transaction_id,
            t.date,
            a.name AS account_name,
            t.amount,
            t.type_,
            c.name AS category_name,
            t.note
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        LEFT JOIN categories c ON t.category_id = c.category_id
        ORDER BY t.date DESC""",conn)
    conn.close()
    return df
    
def get_accounts():
    conn=get_connection()
    df=pd.read_sql("SELECT * FROM accounts",conn)
    conn.close()
    return df

def get_categories():
    conn=get_connection()
    df=pd.read_sql("SELECT * FROM categories",conn)
    conn.close()
    return df
    
def get_balance(account_id):
    conn=get_connection()
    accounts_df=pd.read_sql(
        "SELECT starting_balance FROM accounts where account_id=%s",conn
    ,params=(account_id,))
    
    starting_balance=accounts_df['starting_balance'].iloc[0]
    result_df=pd.read_sql(
        """Select SUM(amount) as total from transactions where account_id=%s """,conn,
        params=(account_id,)
    )
    total_spent=result_df['total'].iloc[0]
    if total_spent is None:
        total_spent=0
    total_balance=starting_balance+total_spent
    conn.close()
    return total_balance

def get_spend_by_category():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            c.name AS category_name,
            SUM(t.amount) AS total_spent
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.type = 'spend'
        GROUP BY c.name
        ORDER BY total_spent
    """, conn)
    conn.close()
    return df

def delete_transaction(transaction_id):
    conn = get_connection()
    curr=conn.cursor()
    curr.execute("DELETE FROM transactions WHERE transaction_id = %s", (transaction_id,))
    conn.commit()
    curr.close()
    conn.close()
