import hashlib
import json
from db import db
from db.models import Transaction


def mask_address(address):
    """隐私保护：地址脱敏"""
    if len(address) > 10:
        return f"{address[:6]}...{address[-4:]}"
    return address


def generate_tx_hash(sender, recipient, amount, fee, timestamp, payload=""):
    """防重放：生成唯一交易哈希"""
    tx_string = f"{sender}{recipient}{amount}{fee}{timestamp}{payload}".encode()
    return hashlib.sha256(tx_string).hexdigest()


def hash_block(block_dict):
    """计算区块哈希"""
    block_string = json.dumps(block_dict, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()


def calculate_balance(address, pending_txs=None):
    """余额计算（支持扣除Mempool中的待确认资金）"""
    if pending_txs is None:
        pending_txs = []

    incoming = db.session.query(db.func.sum(Transaction.amount)).filter_by(recipient=address).scalar() or 0.0
    outgoing = db.session.query(db.func.sum(Transaction.amount)).filter_by(sender=address).scalar() or 0.0
    fee_outgoing = db.session.query(db.func.sum(Transaction.fee)).filter_by(sender=address).scalar() or 0.0
    balance = incoming - outgoing - fee_outgoing

    for tx in pending_txs:
        if tx['sender'] == address:
            balance -= (tx['amount'] + tx['fee'])
    return balance