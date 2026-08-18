import sqlite3
import pandas as pd
import os

db_path=r"database/finance.db"
def create_tables():
    conn = get_conection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            starting_balance REAL NOT NULL DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            account_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            category_id INTEGER,
            note TEXT,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id),
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        )
    """)
    conn.commit()
    conn.close()
def seed_accounts_and_categories():
    conn = get_conection()
    existing = pd.read_sql("SELECT COUNT(*) as c FROM accounts", conn)
    if existing['c'].iloc[0] == 0:
        accounts = [("Wallet", 920), ("Meezan Bank", 5415.02), ("EasyPaisa", 0), ("JazzCash", 0), ("Sadapay", 0), ("NayaPay", 0)]
        conn.executemany("INSERT INTO accounts (name, starting_balance) VALUES (?, ?)", accounts)
        categories = ["HangOut","Lunch","Dinner","Essentials","Transport","Turf","Snacks","Donation","Subscription","Loan","Pocket Money","Other"]
        conn.executemany("INSERT INTO categories (name) VALUES (?)", [(c,) for c in categories])
        conn.commit()
    conn.close()
def reset_accounts(new_accounts):
    conn = get_conection()
    conn.execute("DELETE FROM accounts")
    conn.executemany("INSERT INTO accounts (name, starting_balance) VALUES (?, ?)", new_accounts)
    conn.commit()
    conn.close()
def get_conection():
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    return conn
def get_all_transactions():
    conn=get_conection()
    df=pd.read_sql(""" 
            SELECT 
            t.transaction_id,
            t.date,
            a.name AS account_name,
            t.amount,
            t.type,
            c.name AS category_name,
            t.note
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        LEFT JOIN categories c ON t.category_id = c.category_id
        ORDER BY t.date DESC""",conn)
    conn.close()
    return df
def insert_transaction(date,account_id,amount,type_,category_id,note):
    conn=get_conection()
    conn.execute(
        """INSERT INTO transactions(date,account_id,amount,type,category_id,note)
        VALUES(?,?,?,?,?,?)""",
        (date,account_id,amount,type_,category_id,note)
    )
    conn.commit()
    conn.close()
    
def get_accounts():
    conn=get_conection()
    df=pd.read_sql("SELECT * FROM accounts",conn)
    conn.close()
    return df

def get_categories():
    conn=get_conection()
    df=pd.read_sql("SELECT * FROM categories",conn)
    conn.close()
    return df
    
def get_balance(account_id):
    conn=get_conection()
    accounts_df=pd.read_sql(
        "SELECT starting_balance FROM accounts where account_id=?",conn
    ,params=(account_id,))
    
    starting_balance=accounts_df['starting_balance'].iloc[0]
    result_df=pd.read_sql(
        """Select SUM(amount) as total from transactions where account_id=? """,conn,
        params=(account_id,)
    )
    total_spent=result_df['total'].iloc[0]
    if total_spent is None:
        total_spent=0
    total_balance=starting_balance+total_spent
    conn.close()
    return total_balance
def get_spend_by_category():
    conn = get_conection()
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
    conn = get_conection()
    conn.execute("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))
    conn.commit()
    conn.close()