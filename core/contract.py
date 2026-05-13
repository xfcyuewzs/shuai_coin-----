import json
from db import db
from db.models import SmartContractState

def execute_smart_contract(tx):
    """极简状态机：ShuaiVM"""
    if not tx.get('payload'):
        return
    try:
        payload = json.loads(tx['payload'])
        contract_addr = tx['recipient']

        if payload.get('action') == 'store':
            k, v = payload.get('key'), payload.get('value')
            state = SmartContractState.query.filter_by(contract_address=contract_addr, state_key=k).first()
            if state:
                state.state_value = str(v)
            else:
                db.session.add(SmartContractState(contract_address=contract_addr, state_key=k, state_value=str(v)))

        elif payload.get('action') == 'mint_token':
            token_name = payload.get('token_name', 'UNKNOWN')
            supply = payload.get('supply', 0)
            db.session.add(SmartContractState(contract_address=contract_addr, state_key='NAME', state_value=token_name))
            db.session.add(SmartContractState(contract_address=contract_addr, state_key=f'BAL_{tx["sender"]}', state_value=str(supply)))

    except Exception as e:
        print(f"Contract Execution Failed: {str(e)}")