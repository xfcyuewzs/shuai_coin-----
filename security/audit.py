from datetime import datetime
from db import db
from db.models import AdminLog

class AuditLogger:
    @staticmethod
    def log_action(admin_name, action):
        """记录敏感操作审计日志"""
        log = AdminLog(
            admin_name=admin_name,
            action=action,
            timestamp=datetime.now()
        )
        db.session.add(log)
        db.session.commit()
        print(f"[AUDIT] {admin_name}: {action}")

    @staticmethod
    def check_large_transaction(sender, amount, threshold=1000.0):
        """大额交易监控"""
        if amount > threshold:
            print(f"[ALERT] Large transaction detected from {sender}: {amount} SHUAI")
            return True
        return False
