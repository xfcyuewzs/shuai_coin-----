from cryptography.fernet import Fernet
import base64
from config.settings import Config

# 使用 SECRET_KEY 生成 Fernet 密钥
# 实际生产中应使用独立的密钥管理系统
def get_cipher():
    key = base64.urlsafe_b64encode(Config.SECRET_KEY.encode().ljust(32)[:32])
    return Fernet(key)

def encrypt_data(data_string):
    """对称加密敏感数据"""
    cipher = get_cipher()
    return cipher.encrypt(data_string.encode()).decode()

def decrypt_data(encrypted_string):
    """解密敏感数据"""
    cipher = get_cipher()
    return cipher.decrypt(encrypted_string.encode()).decode()
