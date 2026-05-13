import os
import sys
import io
import click

# 强制 stdout 使用 UTF-8 编码，杜绝 Windows 环境下因 Emoji 引发的 UnicodeEncodeError
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from werkzeug.security import generate_password_hash
from web import create_app
from db import db
from db.models import Block, User
from core.blockchain import create_block
from config.settings import Config
from core.logging import setup_logging

from flask_migrate import upgrade, migrate, init, stamp

app = create_app()

def init_system():
    """系统初始化：数据库建表、创世块生成、超管创建"""
    with app.app_context():
        db.create_all()
        # 创世节点打包首块
        if not Block.query.first():
            create_block(proof=100, previous_hash='0', miner_address='0xGENESIS_MINER_ACCOUNT')
            print("✅ 创世区块已生成")

        # 注入超级管理员
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                tx_password_hash=generate_password_hash('admin123'),
                address='0xADMIN_MASTER_WALLET',
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ 默认管理员初始化完成: admin / admin123")

def start_all():
    """一键启动：加载配置 -> 初始化 -> 启动服务"""
    print("🌟 ShuaiCoin 系统启动中...")
    
    # 1. 设置日志
    setup_logging()
    
    # 2. 初始化数据库和基础数据
    init_system()
    
    # 3. 启动定时任务（此处预留，未来可对接 apscheduler）
    print("⏰ 定时任务模块已就绪")
    
    # 4. 运行服务
    print(f"🚀 服务运行于 http://0.0.0.0:{Config.PORT}")
    print(f"📚 Swagger 文档: http://localhost:{Config.PORT}/apidocs")
    
    app.run(debug=True, host='0.0.0.0', port=Config.PORT)

@click.group()
def cli():
    pass

@cli.command()
def init_db():
    """手动初始化数据库"""
    init_system()

@cli.group()
def db_mgmt():
    """数据库迁移管理"""
    pass

@db_mgmt.command()
def db_init():
    """初始化迁移仓库"""
    with app.app_context():
        init()

@db_mgmt.command()
@click.option('-m', '--message', default='Initial migration')
def db_migrate(message):
    """生成迁移脚本"""
    with app.app_context():
        migrate(message=message)

@db_mgmt.command()
def db_upgrade():
    """执行迁移升级"""
    with app.app_context():
        upgrade()

@cli.command()
def start():
    """启动服务"""
    start_all()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        cli.add_command(db_mgmt)
        cli()
    else:
        start_all()
