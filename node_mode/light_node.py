# Node Types: Full, Light, Archive
class LightNode:
    def sync_headers_only(self):
        """仅同步区块头 + ZK 最小化证明"""
        pass

class ArchiveNode:
    def store_full_history(self):
        """存储创世以来所有历史状态"""
        pass
