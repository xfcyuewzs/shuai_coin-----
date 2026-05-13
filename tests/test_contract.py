from core.contract import execute_smart_contract
from db.models import SmartContractState
from db import db

def test_smart_contract_execution(app):
    """测试：智能合约状态变更"""
    with app.app_context():
        # 1. 模拟一个部署合约的交易
        tx_deploy = {
            'tx_hash': 'h1', 'sender': '0x1', 'recipient': '0x0_CONTRACT',
            'amount': 0, 'fee': 0, 'type': 'deploy_contract',
            'payload': 'init_state: {"owner": "0x1", "balance": 100}'
        }
        
        # 假设 execute_smart_contract 会根据 payload 更新 SmartContractState
        # 注意：这里需要根据实际的 execute_smart_contract 实现来编写
        execute_smart_contract(tx_deploy)
        
        state = SmartContractState.query.filter_by(contract_address='0x0_CONTRACT').first()
        # 这里取决于你的合约引擎具体实现，假设它存入了 JSON
        assert state is not None
