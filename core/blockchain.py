import hashlib
import json
from time import time
from datetime import datetime
from db import db
from db.models import Block, Transaction
from core.utils import hash_block, generate_tx_hash
from core.contract import execute_smart_contract
from config.settings import Config

# 内存交易池 (已废弃，改用数据库持久化以支持多进程/重启)
def get_pending_transactions():
    """从数据库获取待确认交易"""
    txs = Transaction.query.filter_by(block_index=None).all()
    return [{
        'tx_hash': tx.tx_hash, 'sender': tx.sender, 'recipient': tx.recipient,
        'amount': tx.amount, 'fee': tx.fee, 'type': tx.tx_type,
        'payload': tx.payload, 'timestamp': str(tx.timestamp)
    } for tx in txs]


def adjust_difficulty():
    """动态难度调整(DDA)"""
    last_10_blocks = Block.query.order_by(Block.index.desc()).limit(10).all()
    if len(last_10_blocks) < 10:
        return Config.DIFFICULTY

    time_taken = last_10_blocks[0].timestamp - last_10_blocks[-1].timestamp
    expected_time = 10 * Config.TARGET_BLOCK_TIME

    if time_taken < expected_time / 2:
        return Config.DIFFICULTY + 1
    elif time_taken > expected_time * 2 and Config.DIFFICULTY > 1:
        return Config.DIFFICULTY - 1
    return Config.DIFFICULTY


def valid_proof(last_proof, proof, difficulty):
    guess = f'{last_proof}{proof}'.encode()
    return hashlib.sha256(guess).hexdigest()[:difficulty] == '0' * difficulty


def proof_of_work(last_proof, difficulty):
    proof = 0
    while not valid_proof(last_proof, proof, difficulty):
        proof += 1
    return proof


def create_block(proof, previous_hash, miner_address):
    # 获取待确认交易并排序 (竞价机制)
    pending_txs = get_pending_transactions()
    pending_txs.sort(key=lambda x: x.get('fee', 0), reverse=True)
    total_fees = sum(tx['fee'] for tx in pending_txs)

    current_diff = adjust_difficulty()
    
    coinbase_tx_dict = {
        'tx_hash': generate_tx_hash('0x0', miner_address, Config.BLOCK_REWARD, 0, time()),
        'sender': '0x000000000000_SYSTEM',
        'recipient': miner_address,
        'amount': Config.BLOCK_REWARD + total_fees,
        'fee': 0,
        'type': 'mine',
        'payload': '',
        'timestamp': str(datetime.now())
    }

    txs_to_pack = [coinbase_tx_dict] + pending_txs

    # 执行合约逻辑
    for tx in txs_to_pack:
        if tx['type'] in ['deploy_contract', 'call_contract']:
            execute_smart_contract(tx)

    last_block = Block.query.order_by(Block.index.desc()).first()
    index = last_block.index + 1 if last_block else 1

    block_dict = {
        'index': index, 'timestamp': time(), 'transactions': txs_to_pack,
        'proof': proof, 'previous_hash': previous_hash or "0", 'difficulty': current_diff
    }
    block_hash = hash_block(block_dict)

    # 创建区块记录
    new_block = Block(
        index=index, timestamp=block_dict['timestamp'], transactions=json.dumps(txs_to_pack),
        proof=proof, previous_hash=block_dict['previous_hash'], hash=block_hash, difficulty=current_diff
    )
    db.session.add(new_block)

    # 1. 保存 Coinbase 交易到数据库
    db.session.add(Transaction(
        tx_hash=coinbase_tx_dict['tx_hash'], sender=coinbase_tx_dict['sender'], 
        recipient=coinbase_tx_dict['recipient'], amount=coinbase_tx_dict['amount'], 
        fee=coinbase_tx_dict['fee'], tx_type=coinbase_tx_dict['type'],
        payload=coinbase_tx_dict.get('payload', ''), block_index=index
    ))

    # 2. 更新已打包交易的状态，将其关联到当前区块
    for tx_data in pending_txs:
        db_tx = Transaction.query.filter_by(tx_hash=tx_data['tx_hash']).first()
        if db_tx:
            db_tx.block_index = index

    db.session.commit()
    Config.DIFFICULTY = current_diff  # 更新全局难度状态（虽然建议持久化，但此处维持现状以减少侵入）
    return new_block, total_fees
