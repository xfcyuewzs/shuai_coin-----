from datetime import datetime
from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    tx_password_hash = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_frozen = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref=db.backref('users', lazy='dynamic'))

class Block(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.Float, nullable=False)
    transactions = db.Column(db.Text, nullable=False)
    proof = db.Column(db.Integer, nullable=False)
    previous_hash = db.Column(db.String(120), nullable=False)
    hash = db.Column(db.String(120), nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tx_hash = db.Column(db.String(120), unique=True, nullable=False)
    sender = db.Column(db.String(120), nullable=False)
    recipient = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    fee = db.Column(db.Float, default=0.0)
    tx_type = db.Column(db.String(50), nullable=False)
    payload = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    block_index = db.Column(db.Integer, nullable=True) # 修改为可空，支持持久化 Mempool

class AdminLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

class SmartContractState(db.Model):
    """【智能合约】存储合约的世界状态 (KV 数据库)"""
    id = db.Column(db.Integer, primary_key=True)
    contract_address = db.Column(db.String(120), index=True)
    state_key = db.Column(db.String(120))
    state_value = db.Column(db.Text)

# RBAC 权限扩展表
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    permissions = db.relationship('Permission', secondary=role_permissions, backref=db.backref('roles', lazy='dynamic'))

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False) # 权限码，如 'user:read'
    name = db.Column(db.String(100), nullable=False)