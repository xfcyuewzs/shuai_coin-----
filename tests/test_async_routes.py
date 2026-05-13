import pytest
from flask import url_for
from db import db
from db.models import User, Block

def test_verify_chain_permissions(client, auth):
    """测试 /verify 接口权限：普通用户应能访问，返回 JSON"""
    # 以普通用户登录 (User 2)
    auth.login(username='user2', password='password123')
    
    response = client.get('/verify')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] in ['success', 'error']
    assert 'message' in data
    assert 'data' in data
    assert 'corrupted_blocks' in data['data']

def test_verify_chain_admin(client, auth):
    """测试 /verify 接口权限：管理员应能访问，返回 JSON"""
    auth.login(username='admin', password='admin_password')
    
    response = client.get('/verify')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert "校验完成" in data['message']

def test_mine_json_response(client, auth):
    """测试 /mine 接口返回 JSON 而非重定向"""
    auth.login(username='user2', password='password123')
    
    # 确保有区块可以挖（初始化链）
    response = client.get('/mine')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert "挖矿成功" in data['message']
    assert 'reward' in data['data']

def test_mine_frozen_user(client, auth, app):
    """测试冻结用户挖矿返回 403 JSON"""
    with app.app_context():
        user = User.query.filter_by(username='user2').first()
        user.is_frozen = True
        db.session.commit()
        
    auth.login(username='user2', password='password123')
    
    response = client.get('/mine')
    assert response.status_code == 403
    data = response.get_json()
    assert data['status'] == 'error'
    assert "冻结" in data['message']
    
    # 恢复用户状态
    with app.app_context():
        user = User.query.filter_by(username='user2').first()
        user.is_frozen = False
        db.session.commit()
