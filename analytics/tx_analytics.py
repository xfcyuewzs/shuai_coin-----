from db.models import Transaction
from db import db
from sqlalchemy import func

class TransactionAnalytics:
    @staticmethod
    def get_daily_volume():
        """统计每日交易量 (示例逻辑)"""
        # 使用 SQLAlchemy 进行分组统计
        results = db.session.query(
            func.date(Transaction.timestamp), 
            func.sum(Transaction.amount)
        ).group_by(func.date(Transaction.timestamp)).all()
        
        return {str(date): amount for date, amount in results}

    @staticmethod
    def get_top_senders(limit=5):
        """获取交易金额排名前几的地址"""
        results = db.session.query(
            Transaction.sender, 
            func.sum(Transaction.amount).label('total')
        ).group_by(Transaction.sender).order_by(db.text('total DESC')).limit(limit).all()
        
        return [{"address": r[0], "total": r[1]} for r in results]
