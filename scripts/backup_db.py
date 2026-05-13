import shutil
import os
from datetime import datetime
from config.settings import Config

def backup():
    """备份数据库文件"""
    # 确保备份目录存在
    backup_dir = os.path.join(Config.BASE_DIR, "backup")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    # 获取当前数据库路径
    # 注意：SQLALCHEMY_DATABASE_URI 是 'sqlite:///path/to/db'
    db_path = Config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
    if not os.path.isabs(db_path):
        db_path = os.path.join(Config.BASE_DIR, db_path)

    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"backup_{timestamp}.db")
        shutil.copy2(db_path, backup_file)
        print(f"✅ 数据库已备份至: {backup_file}")
    else:
        print(f"❌ 找不到数据库文件: {db_path}")

if __name__ == "__main__":
    backup()
