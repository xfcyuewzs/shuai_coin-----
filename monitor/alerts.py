import logging

def check_node_health(height, peers_count):
    """
    监控告警逻辑：当节点高度落后或 Peer 数量过低时触发告警
    """
    if peers_count == 0:
        logging.error("🚨 ALERT: Node is isolated! Zero peers connected.")
        return False
    
    if height < 1:
        logging.warning("⚠️ ALERT: Blockchain height is zero. Genesis block missing?")
    
    return True
