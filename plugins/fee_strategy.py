from config.settings import Config

def calculate_required_fee(tx_type, payload_size):
    """自定义手续费计算策略"""
    base_fee = Config.MIN_FEE
    
    if tx_type == 'transfer':
        return base_fee
    elif tx_type in ['deploy_contract', 'call_contract']:
        # 智能合约根据 payload 大小加收费用
        return base_fee + (payload_size * 0.01)
    
    return base_fee
