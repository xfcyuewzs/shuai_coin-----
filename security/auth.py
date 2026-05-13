import jwt
import datetime
import logging
import os
import uuid
import hashlib
from functools import wraps
from flask import request, current_app, redirect, url_for, jsonify
from flask_login import current_user
from core.response import error_res
from db.models import User

# 内容审核日志
moderator_logger = logging.getLogger('moderator')

def load_moderation_rules():
    """加载审核规则"""
    words = set()
    hashes = set()
    try:
        # 修正路径：从当前文件的上一级目录开始找
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        word_file = os.path.join(base_path, 'config/sensitive_words.txt')
        if os.path.exists(word_file):
            with open(word_file, 'r', encoding='utf-8') as f:
                words = {line.strip() for line in f if line.strip() and not line.startswith('#')}
        
        hash_file = os.path.join(base_path, 'config/image_blacklist.sha256')
        if os.path.exists(hash_file):
            with open(hash_file, 'r', encoding='utf-8') as f:
                hashes = {line.strip() for line in f if line.strip() and not line.startswith('#')}
    except Exception as e:
        logging.error(f"Failed to load moderation rules: {e}")
    return words, hashes

def content_moderator():
    """内容审核装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            sensitive_words, image_hashes = load_moderation_rules()
            trace_id = str(uuid.uuid4())
            
            # 1. 文本审核 (支持 JSON, Form 数据)
            content = ""
            if request.is_json:
                data = request.get_json()
                content = data.get('content', '') or data.get('msg', '') or data.get('payload', '')
            else:
                content = request.form.get('content', '') or request.form.get('msg', '')
            
            for word in sensitive_words:
                if word and word in str(content).lower():
                    moderator_logger.warning(f"[MODERATE_REJECT] user_id={getattr(current_user, 'id', 'anon')}, uri={request.path}, rule={word}, timestamp={datetime.datetime.utcnow().isoformat()}Z")
                    return jsonify({"code": 451, "msg": "Content Blocked", "trace_id": trace_id}), 451
            
            # 2. 图片审核 (SHA256 哈希)
            if 'file' in request.files:
                file = request.files['file']
                file_content = file.read()
                file.seek(0)
                file_hash = hashlib.sha256(file_content).hexdigest()
                if file_hash in image_hashes:
                    moderator_logger.warning(f"[MODERATE_REJECT] user_id={getattr(current_user, 'id', 'anon')}, uri={request.path}, rule={file_hash}, timestamp={datetime.datetime.utcnow().isoformat()}Z")
                    return jsonify({"code": 451, "msg": "Content Blocked", "trace_id": trace_id}), 451

            return f(*args, **kwargs)
        return decorated
    return decorator

def generate_token(user_id, is_admin=False):
    """生成 JWT Token"""
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id,
            'is_admin': is_admin
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return str(e)

def admin_required(f):
    """管理员鉴权装饰器：支持 JWT 和 Session"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        user_from_token = None
        
        # 1. 优先检查 Session
        if current_user.is_authenticated:
            if current_user.is_admin:
                return f(*args, **kwargs)
            else:
                logging.warning(f"[AUTH_REJECT] User {current_user.id} is not admin. Path: {request.path}")
                return error_res("Forbidden: Admin access required", code=403, status_code=403)

        # 2. 检查 JWT
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]

        if not token:
            if request.path.startswith('/api/') or request.path.startswith('/admin/api/'):
                return error_res("Unauthorized: Admin token required", code=401, status_code=401)
            return redirect(url_for('auth.login'))

        try:
            data = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=["HS256"])
            if not data.get('is_admin'):
                return error_res("Forbidden: Admin access required", code=403, status_code=403)
            
            user_from_token = User.query.get(data['sub'])
            if not user_from_token or not user_from_token.is_admin:
                return error_res("Forbidden: User is not admin", code=403, status_code=403)
                
        except Exception as e:
            return error_res(f"Auth failed: {str(e)}", code=401, status_code=401)

        return f(*args, **kwargs)
    return decorated

def require_permission(permission_code):
    """接口级权限校验装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = None
            if current_user.is_authenticated:
                user = current_user
            else:
                # 尝试从 JWT 获取用户
                if 'Authorization' in request.headers:
                    auth_header = request.headers['Authorization']
                    if auth_header.startswith('Bearer '):
                        token = auth_header.split(" ")[1]
                        try:
                            data = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=["HS256"])
                            user = User.query.get(data['sub'])
                        except: pass
            
            if not user:
                return error_res("Unauthorized", code=401, status_code=401)
            
            if user.is_admin: 
                return f(*args, **kwargs)
                
            if user.role and any(p.code == permission_code for p in user.role.permissions):
                return f(*args, **kwargs)
            
            logging.warning(f"[PERMISSION_DENIED] user={user.id}, required={permission_code}, path={request.path}")
            return error_res("Forbidden: Permission denied", code=403, status_code=403)
        return decorated
    return decorator
