import pytest
from db.models import User
from db import db
from werkzeug.security import generate_password_hash

def test_user_role_id_persistence(app):
    """验证 User 模型中 role_id 字段的持久化与读取"""
    with app.app_context():
        # 1. 创建并保存一个含 role_id 的用户
        test_user = User(
            username='role_test_user',
            password_hash=generate_password_hash('pass'),
            tx_password_hash=generate_password_hash('pass'),
            address='0xROLE_TEST',
            role_id=1 # 假设存在 id 为 1 的角色
        )
        db.session.add(test_user)
        db.session.commit()

        # 2. 从数据库重新查询
        saved_user = User.query.filter_by(username='role_test_user').first()
        
        # 3. 断言校验
        assert saved_user is not None
        assert saved_user.role_id == 1
        print("\n✅ User role_id persistence test passed.")

        # 4. 清理测试数据
        db.session.delete(saved_user)
        db.session.commit()
