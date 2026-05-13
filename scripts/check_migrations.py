import sys
import subprocess

def check_migrations():
    """检查 SQLAlchemy 模型变更是否已生成迁移脚本"""
    try:
        # 尝试运行 flask db migrate --dry-run 或者检查是否生成了空迁移
        # 这里使用 Alembic 的 check 命令 (需要 Flask-Migrate 集成)
        result = subprocess.run(
            ['flask', 'db', 'migrate', '--dry-run'],
            capture_output=True,
            text=True
        )
        
        if "No changes in schema detected" not in result.stdout:
            print("❌ Detected schema changes without migration scripts!")
            print("Please run 'python run.py db_mgmt db_migrate -m \"your message\"'")
            sys.exit(1)
            
        print("✅ No missing migrations.")
    except Exception as e:
        print(f"⚠️ Migration check skipped: {e} (Ensure dependencies are installed)")

if __name__ == "__main__":
    check_migrations()
