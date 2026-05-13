from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# 初始化限流器，基于访问者的 IP
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # 生产环境可改为 redis://localhost:6379
)