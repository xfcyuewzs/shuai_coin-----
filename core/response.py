from flask import jsonify

def success_res(data=None, msg="success"):
    """统一成功返回格式"""
    return jsonify({
        "code": 0,
        "msg": msg,
        "message": msg, # 兼容不同需求
        "data": data
    }), 200

def error_res(msg="error", code=1, status_code=400):
    """统一失败返回格式"""
    return jsonify({
        "code": code,
        "msg": msg,
        "message": msg, # 兼容不同需求
        "data": None
    }), status_code
