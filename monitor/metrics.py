import time
from db.models import Block, Transaction

class MetricsCollector:
    @staticmethod
    def get_system_stats():
        """获取系统核心指标"""
        total_blocks = Block.query.count()
        total_txs = Transaction.query.count()
        
        # 计算最近 24 小时的交易量
        # 这里仅作演示，返回基础数据
        return {
            "height": total_blocks,
            "total_transactions": total_txs,
            "timestamp": time.time()
        }

    @staticmethod
    def log_mining_event(duration, difficulty):
        """记录挖矿事件指标"""
        print(f"[METRIC] Block mined in {duration:.2f}s with difficulty {difficulty}")
