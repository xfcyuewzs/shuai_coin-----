import requests
import json
from urllib.parse import urlparse
from db import db
from db.models import Block, Transaction, SmartContractState
from core.contract import execute_smart_contract
from core.utils import hash_block

network_peers = set()

def valid_chain(chain):
    """验证链的合法性 (PoW和哈希链)"""
    from core.blockchain import valid_proof
    last_block = chain[0]
    current_index = 1

    while current_index < len(chain):
        block = chain[current_index]
        # 1. 验证前序哈希
        if block['previous_hash'] != last_block['hash']:
            return False
        # 2. 验证 PoW
        if not valid_proof(last_block['proof'], block['proof'], block['difficulty']):
            return False
        # 3. 验证区块内容哈希
        block_for_hash = {
            'index': block['index'],
            'timestamp': block['timestamp'],
            'transactions': json.loads(block['transactions']) if isinstance(block['transactions'], str) else block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
            'difficulty': block['difficulty']
        }
        if block['hash'] != hash_block(block_for_hash):
            return False

        last_block = block
        current_index += 1
    return True

def register_node(address):
    parsed_url = urlparse(address)
    if parsed_url.netloc:
        network_peers.add(parsed_url.netloc)
    elif parsed_url.path:
        network_peers.add(parsed_url.path)
    else:
        raise ValueError('Invalid URL')

def resolve_conflicts():
    """共识：验证并拉取全网最长合法链"""
    longest_chain = None
    max_length = Block.query.count()

    for node in network_peers:
        try:
            response = requests.get(f'http://{node}/api/chain', timeout=3)
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                # 增加合法性校验
                if length > max_length and valid_chain(chain):
                    max_length = length
                    longest_chain = chain
        except:
            continue

    if longest_chain:
        # 重建整个本地账本和合约状态
        db.session.query(Block).delete()
        db.session.query(Transaction).delete()
        db.session.query(SmartContractState).delete()

        for b in longest_chain:
            blk = Block(
                index=b['index'], timestamp=b['timestamp'], transactions=b['transactions'],
                proof=b['proof'], previous_hash=b['previous_hash'], hash=b['hash'], difficulty=b['difficulty']
            )
            db.session.add(blk)
            txs = json.loads(b['transactions'])
            for tx in txs:
                db.session.add(Transaction(
                    tx_hash=tx['tx_hash'], sender=tx['sender'], recipient=tx['recipient'],
                    amount=tx['amount'], fee=tx['fee'], tx_type=tx['type'],
                    payload=tx.get('payload', ''), block_index=b['index']
                ))
                execute_smart_contract(tx)
        db.session.commit()
        return True
    return False