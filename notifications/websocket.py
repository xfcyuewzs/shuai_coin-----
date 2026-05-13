def push_new_block(block_data):
    """
    通过 WebSocket 向所有连接的客户端推送新区块通知
    (此处为逻辑占位，实际需集成 Flask-SocketIO)
    """
    print(f"[WS_PUSH] New Block Mined: {block_data['index']}")

def push_new_transaction(tx_data):
    """推送新交易入池通知"""
    print(f"[WS_PUSH] New Transaction: {tx_data['tx_hash']}")
