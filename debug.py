import db

accounts = db.get_accounts()
categories = db.get_categories()

print(accounts)
print(categories)
db.insert_transaction("2026-08-16", 1, -50, "spend", 1, "test insert")
print("insert worked")