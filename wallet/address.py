import hashlib

def generate_address(public_key_pem):
    """根据公钥生成钱包地址 (类似 Ethereum)"""
    # 1. 对公钥 PEM 进行 SHA256
    sha256_hash = hashlib.sha256(public_key_pem.encode('utf-8')).hexdigest()
    # 2. 取前 40 位并加上 0x 前缀
    return f"0x{sha256_hash[:40]}"

def validate_address(address):
    """校验地址格式"""
    return address.startswith("0x") and len(address) == 42
