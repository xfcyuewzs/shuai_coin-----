from db.models import Transaction
from db import db
from datetime import datetime, timedelta

def clean_stale_transactions(days=7):
    """
    清理超过指定天数仍未打包的异常交易 (脏数据清理)
    """
    threshold = datetime.now() - timedelta(days=days)
    stale_txs = Transaction.query.filter(
        Transaction.block_index == None,
        Transaction.timestamp < threshold
    ).all()
    
    count = len(stale_txs)
    for tx in stale_txs:
        db.session.delete(tx)
    
    db.session.commit()
    print(f"[CLEANUP] Removed {count} stale transactions from mempool.")

if __name__ == "__main__":
    from run import app
    with app.app_context():
        clean_stale_transactions()
