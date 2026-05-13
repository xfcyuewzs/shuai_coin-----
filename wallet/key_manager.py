from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import base64
from .address import generate_address

class WalletManager:
    @staticmethod
    def generate_keypair():
        """生成 RSA 私钥与公钥，并返回对应的钱包地址"""
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        priv_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        pub_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        address = generate_address(pub_pem)
        return priv_pem, pub_pem, address

    @staticmethod
    def export_private_key(private_key_pem, password):
        """对私钥进行二次加密导出 (模拟 keystore)"""
        # 实际开发中会使用 AES 等对称加密
        return base64.b64encode(f"{private_key_pem}:{password}".encode()).decode()
