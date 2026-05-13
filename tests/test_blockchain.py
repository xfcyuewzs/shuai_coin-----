from core.blockchain import create_block, get_pending_transactions
from db.models import Block, Transaction
from db import db


def test_create_block(app):
    """测试：能否成功打包数据库中的交易并生成新区块"""

    with app.app_context():
        # 1. 准备测试数据（持久化到数据库作为待确认交易）
        tx = Transaction(
            tx_hash='test_hash_123', sender='0xAAA', recipient='0xBBB',
            amount=10.0, fee=1.0, tx_type='transfer', block_index=None
        )
        db.session.add(tx)
        db.session.commit()

        # 2. 执行核心函数
        new_block, total_fees = create_block(proof=12345, previous_hash="genesis", miner_address="0xMiner")

        # 3. 断言（Assert）：验证结果是否符合预期
        assert new_block.index == 2
        assert total_fees == 1.0
        assert "test_hash_123" in new_block.transactions

        # 4. 验证数据库中交易的状态是否已更新
        saved_tx = Transaction.query.filter_by(tx_hash='test_hash_123').first()
        assert saved_tx.block_index == 2

        # 5. 验证数据库是否真的落库了
        saved_block = Block.query.filter_by(index=2).first()
        assert saved_block is not None

def test_difficulty_adjustment(app):
    """测试：难度调整逻辑"""
    from core.blockchain import adjust_difficulty
    from config.settings import Config
    
    with app.app_context():
        # 初始难度
        assert adjust_difficulty() == Config.DIFFICULTY
        
        # 模拟 10 个快速生成的区块
        for i in range(2, 12):
            b = Block(
                index=i, timestamp=i * 1.0, transactions="[]", 
                proof=100, previous_hash="hash", hash=f"hash{i}", difficulty=4
            )
            db.session.add(b)
        db.session.commit()
        
        # 预期难度应该增加
        assert adjust_difficulty() > Config.DIFFICULTY
