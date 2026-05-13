import sqlite3
import os
import sys
from config.settings import Config

def validate_fix():
    db_uri = Config.SQLALCHEMY_DATABASE_URI
    db_path = db_uri.replace('sqlite:///', '')
    if not os.path.isabs(db_path):
        base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(base_dir, "instance", os.path.basename(db_path))

    print(f"🔍 Validating fix for: {db_path}")

    if not os.path.exists(db_path):
        print("❌ Database file missing!")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. 检查列定义
    cursor.execute("PRAGMA table_info(user)")
    columns = {col[1]: col[2] for col in cursor.fetchall()}
    
    if 'role_id' in columns:
        print(f"✅ 'role_id' column exists. Type: {columns['role_id']}")
    else:
        print("❌ 'role_id' column still missing!")
        sys.exit(1)

    # 2. 尝试插入数据验证
    try:
        cursor.execute("INSERT INTO user (username, password_hash, tx_password_hash, address, is_admin, is_frozen, role_id) VALUES ('test_val', 'h', 'h', '0xVAL', 0, 0, NULL)")
        conn.rollback() # 不真插入
        print("✅ Insert test with 'role_id' passed.")
    except Exception as e:
        print(f"❌ Insert test failed: {e}")
        sys.exit(1)

    conn.close()
    print("🏁 Validation COMPLETED successfully.")

if __name__ == "__main__":
    validate_fix()
