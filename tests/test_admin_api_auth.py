import pytest
from flask_login import login_user
from db.models import User
from db import db
from werkzeug.security import generate_password_hash
from security.auth import generate_token

def test_admin_api_auth_session(client, app):
    """测试管理员 API 的 Session 鉴权"""
    with app.app_context():
        # 1. 创建管理员和普通用户
        admin = User(
            username='admin_auth_test',
            password_hash=generate_password_hash('admin123'),
            tx_password_hash=generate_password_hash('admin123'),
            address='0xADMIN_AUTH',
            is_admin=True
        )
        user = User(
            username='user_auth_test',
            password_hash=generate_password_hash('user123'),
            tx_password_hash=generate_password_hash('user123'),
            address='0xUSER_AUTH',
            is_admin=False
        )
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()

        # 2. 匿名用户访问 -> 401
        res = client.get('/admin/api/users')
        assert res.status_code == 401

        # 3. 普通用户登录后访问 -> 403
        client.post('/login', data={'username': 'user_auth_test', 'password': 'user123'}, follow_redirects=True)
        res = client.get('/admin/api/users')
        assert res.status_code == 403

        # 4. 管理员登录后访问 -> 200
        client.get('/logout', follow_redirects=True)
        client.post('/login', data={'username': 'admin_auth_test', 'password': 'admin123'}, follow_redirects=True)
        res = client.get('/admin/api/users')
        assert res.status_code == 200
        assert res.get_json()['code'] == 0

def test_admin_api_auth_jwt(client, app):
    """测试管理员 API 的 JWT 鉴权"""
    with app.app_context():
        # 获取管理员 ID
        admin = User.query.filter_by(username='admin_auth_test').first()
        token = generate_token(admin.id, is_admin=True)

        # 使用 JWT 访问 -> 200
        res = client.get('/admin/api/users', headers={'Authorization': f'Bearer {token}'})
        assert res.status_code == 200
        assert res.get_json()['code'] == 0

        # 使用错误的 JWT (非管理员) -> 403
        user = User.query.filter_by(username='user_auth_test').first()
        user_token = generate_token(user.id, is_admin=False)
        res = client.get('/admin/api/users', headers={'Authorization': f'Bearer {user_token}'})
        assert res.status_code == 403
