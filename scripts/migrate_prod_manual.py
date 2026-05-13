import sqlite3
import os
import sys
import io

# 强制 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 确保脚本可以找到项目根目录
sys.path.append(os.getcwd())

try:
    from config.settings import Config
except ImportError:
    print("❌ Error: Could not import Config.")
    sys.exit(1)

def migrate_production():
    # 获取数据库路径
    db_uri = Config.SQLALCHEMY_DATABASE_URI
    db_path = db_uri.replace('sqlite:///', '')
    
    if not os.path.isabs(db_path):
        db_path = os.path.abspath(db_path)

    print(f"🚀 Starting production migration for: {db_path}")

    if not os.path.exists(db_path):
        # 尝试在 instance 目录下找
        db_path = os.path.join(os.getcwd(), 'instance', os.path.basename(db_path))
        if not os.path.exists(db_path):
            print(f"❌ DB not found at {db_path}")
            return

    # 1. 备份
    backup_path = db_path + ".prod_mig.bak"
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"📦 Backup created at {backup_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 2. 检查列是否存在
        cursor.execute("PRAGMA table_info(user)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'role_id' not in columns:
            print("🔧 Adding 'role_id' column to 'user' table...")
            cursor.execute("ALTER TABLE user ADD COLUMN role_id INTEGER DEFAULT 0")
            conn.commit()
            print("✅ Column 'role_id' added successfully.")
        else:
            print("ℹ️ Column 'role_id' already exists.")
            
        conn.close()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print(f"🔄 Rolling back... (Restoring from {backup_path})")
        shutil.copy2(backup_path, db_path)
        sys.exit(1)

if __name__ == "__main__":
    migrate_production()
