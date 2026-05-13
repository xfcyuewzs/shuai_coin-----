import logging
import os
import sys
import io
import json
import datetime
import gzip
import shutil
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class JSONFormatter(logging.Formatter):
    """自定义 JSON 格式化器"""
    def format(self, record):
        log_entry = {
            "time": datetime.datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "trace_id": getattr(record, 'trace_id', 'N/A'),
            "user_id": getattr(record, 'user_id', 'anon'),
            "ip": getattr(record, 'ip', 'N/A'),
            "method": getattr(record, 'method', 'N/A'),
            "path": getattr(record, 'path', 'N/A'),
            "status": getattr(record, 'status', 'N/A'),
            "duration_ms": getattr(record, 'duration_ms', 0)
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

class LogRotateHandler(TimedRotatingFileHandler):
    """支持每日切割并压缩的 Handler"""
    def __init__(self, filename, when='midnight', interval=1, backupCount=30, encoding='utf-8', delay=False, utc=True):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc)

    def doRollover(self):
        super().doRollover()
        # 压缩旧日志
        old_log = self.baseFilename + "." + datetime.datetime.now().strftime("%Y-%m-%d")
        if os.path.exists(old_log):
            with open(old_log, 'rb') as f_in:
                with gzip.open(old_log + '.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(old_log)

def setup_logging():
    """初始化生产级 JSON 日志体系"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 1. 基础配置
    formatter = JSONFormatter()
    
    def create_handler(filename):
        h = LogRotateHandler(os.path.join(log_dir, filename))
        h.setFormatter(formatter)
        return h

    # 2. 根日志 (app.log)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(create_handler('app.log'))

    # 3. 模块化拆分
    # Auth 日志
    auth_logger = logging.getLogger('auth')
    auth_logger.propagate = False
    auth_logger.addHandler(create_handler('auth.log'))

    # Moderator 日志
    mod_logger = logging.getLogger('moderator')
    mod_logger.propagate = False
    mod_logger.addHandler(create_handler('moderator.log'))

    # Error 日志
    error_logger = logging.getLogger('error')
    error_logger.setLevel(logging.ERROR)
    error_logger.propagate = False
    error_logger.addHandler(create_handler('error.log'))

    # 控制台输出 (保持兼容性包装)
    output_stream = sys.stdout
    if hasattr(sys.stdout, 'buffer'):
        output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    console_h = logging.StreamHandler(output_stream)
    console_h.setFormatter(formatter)
    root_logger.addHandler(console_h)

    logging.info("🚀 Production JSON logging system initialized")

def get_logger(name):
    """获取指定名称的 Logger"""
    return logging.getLogger(name)
