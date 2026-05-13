import sqlite3
import os

db_path = 'instance/shuai_coin_node_5000.db'
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    print("Columns in 'user' table:")
    for col in columns:
        print(col)
    conn.close()
