import sqlite3
import pandas as pd


db_path=r"database/finance.db"

def get_conection():
    conn=sqlite3.connect(db_path)
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
