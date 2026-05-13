import pytest
from db.models import User
from db import db
from werkzeug.security import generate_password_hash

def test_auth_pages(client):
    """测试：注册和登录页面访问"""
    res = client.get('/register')
    assert res.status_code == 200
    res = client.get('/login')
    assert res.status_code == 200

def test_user_registration(client, app):
    """测试：用户注册流程"""
    with app.app_context():
        res = client.post('/register', data={
            'username': 'testuser',
            'password': 'password123',
            'tx_password': 'txpassword123'
        }, follow_redirects=True)
        
        assert b'\xe6\xb3\xa8\xe5\x86\x8c\xe6\x88\x90\xe5\x8a\x9f' in res.data # "注册成功"
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.address.startswith('0x')

def test_api_chain(client):
    """测试：公共 API 获取链数据"""
    res = client.get('/api/chain')
    assert res.status_code == 200
    data = res.get_json()
    assert 'chain' in data
    assert data['length'] == 1 # 创世块

def test_admin_page_rendering(client, app):
    """测试：管理员页面正常渲染"""
    with app.app_context():
        # 1. 创建管理员用户
        admin = User(
            username='admin_test',
            password_hash=generate_password_hash('admin123'),
            tx_password_hash=generate_password_hash('admin123'),
            address='0xADMIN',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

        # 2. 模拟登录
        client.post('/login', data={
            'username': 'admin_test',
            'password': 'admin123'
        }, follow_redirects=True)

        # 3. 访问管理页面
        res = client.get('/admin')
        assert res.status_code == 200
        assert b'ShuaiCoin \xe7\xae\xa1\xe7\x90\x86\xe5\x91\x98\xe7\xb3\xbb\xe7\xbb\x9f' in res.data # "ShuaiCoin 管理员系统"
        assert b'text/html' in res.content_type
