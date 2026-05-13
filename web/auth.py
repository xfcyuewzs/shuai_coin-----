import hashlib
import uuid
from flask import Blueprint, render_template_string, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from db.models import User
from db import db
from web.templates import AUTH_HTML
from core.response import success_res, error_res
from security.auth import generate_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户注册
    ---
    tags:
      - Auth
    parameters:
      - name: username
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
    responses:
      200:
        description: 注册成功
    """
    if request.method == 'POST':
        username = request.form['username'].strip()
        if User.query.filter_by(username=username).first():
            flash('用户名已被使用', 'danger')
            return redirect(url_for('auth.register'))

        address = '0x' + hashlib.sha256(f"{username}{uuid.uuid4()}".encode()).hexdigest()[:40]
        user = User(
            username=username,
            password_hash=generate_password_hash(request.form['password']),
            tx_password_hash=generate_password_hash(request.form['tx_password']),
            address=address
        )
        db.session.add(user)
        db.session.commit()
        flash('注册成功！', 'success')
        return redirect(url_for('auth.login'))
    return render_template_string(AUTH_HTML, title='注册', action='register')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录 (Session)
    ---
    tags:
      - Auth
    """
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            return redirect(url_for('routes.index'))
        flash('用户名或密码错误', 'danger')
    return render_template_string(AUTH_HTML, title='登录', action='login')

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """
    API 登录 (获取 JWT Token)
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: 登录成功，返回 token
    """
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return error_res("请输入用户名和密码")
    
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        token = generate_token(user.id, is_admin=user.is_admin)
        return success_res({"token": token, "username": user.username, "is_admin": user.is_admin})
    
    return error_res("用户名或密码错误", status_code=401)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
