from web import create_app
from db import db
import os

def rebuild_db():
    app = create_app()
    with app.app_context():
        # 1. 备份旧数据库 (如果有)
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        db_path = db_uri.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            db_path = os.path.join(app.root_path, '..', db_path)
        
        if os.path.exists(db_path):
            backup_path = db_path + ".bak"
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"✅ Backup created at {backup_path}")

        # 2. 删除并重建
        print("🛠️ Dropping all tables...")
        db.drop_all()
        print("🛠️ Creating all tables with new schema...")
        db.create_all()
        print("✅ Database rebuilt successfully.")

if __name__ == "__main__":
    rebuild_db()
