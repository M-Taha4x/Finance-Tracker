import db

db.create_tables()
db.seed_accounts_and_categories()

print(db.get_accounts())
print(db.get_balance(1))
db.insert_transaction("2026-08-19", 1, -50, "spend", 1, "test insert")
print(db.get_all_transactions())