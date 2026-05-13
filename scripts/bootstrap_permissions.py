import os
import sys
from werkzeug.security import generate_password_hash

# 确保可以导入项目模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web import create_app
from db import db
from db.models import Role, Permission, User

def bootstrap():
    app = create_app()
    with app.app_context():
        print("🚀 Bootstrapping permissions...")
        
        # 1. 创建基础权限码
        permissions_data = [
            ('user:read', '查看用户列表'),
            ('user:write', '编辑用户信息'),
            ('user:delete', '删除用户'),
            ('user:freeze', '冻结用户'),
            ('block:read', '查看区块'),
            ('block:mine', '执行挖矿'),
            ('tx:read', '查看交易'),
            ('tx:write', '发起交易'),
            ('sc:deploy', '部署合约'),
            ('sc:call', '调用合约'),
            ('node:read', '查看节点'),
            ('node:write', '管理节点'),
            ('node:verify', '全网节点校验'),
            ('perm:read', '查看权限'),
            ('perm:write', '管理权限'),
            ('config:read', '查看配置'),
            ('config:write', '修改配置'),
            ('log:read', '查看日志'),
            ('audit:read', '查看审计'),
            ('system:reboot', '重启系统')
        ]
        
        perms = []
        for code, name in permissions_data:
            p = Permission.query.filter_by(code=code).first()
            if not p:
                p = Permission(code=code, name=name)
                db.session.add(p)
            perms.append(p)
        
        db.session.commit()
        print(f"✅ {len(perms)} permissions initialized.")
        
        # 2. 创建 Admin 角色并绑定所有权限
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role:
            admin_role = Role(name='Admin')
            db.session.add(admin_role)
        
        admin_role.permissions = perms
        db.session.commit()
        print("✅ Admin role updated with all permissions.")
        
        # 3. 关联默认管理员
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            admin_user.role = admin_role
            db.session.commit()
            print("✅ Default admin user associated with Admin role.")

if __name__ == '__main__':
    bootstrap()
