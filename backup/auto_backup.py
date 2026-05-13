import shutil
import time
import schedule
from datetime import datetime
import os

DB_PATH = "../shuai_coin_node_5000.db"
BACKUP_DIR = "./data_backups/"

def backup_database():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"db_backup_{timestamp}.db")
    try:
        shutil.copy2(DB_PATH, backup_file)
        print(f"[{datetime.now()}] ✅ 数据库备份成功: {backup_file}")
    except FileNotFoundError:
        print(f"[{datetime.now()}] ❌ 未找到数据库文件: {DB_PATH}")

if __name__ == "__main__":
    schedule.every().day.at("02:00").do(backup_database) # 每天凌晨2点备份
    print("🔄 自动备份服务已启动...")
    while True:
        schedule.run_pending()
        time.sleep(60)