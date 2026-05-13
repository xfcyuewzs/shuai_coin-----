from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import json

class TransactionSigner:
    @staticmethod
    def sign(private_key_pem, transaction_dict):
        """对交易字典进行签名"""
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'), 
            password=None
        )
        
        # 确保字典排序一致，以便签名验证
        tx_string = json.dumps(transaction_dict, sort_keys=True)
        
        signature = private_key.sign(
            tx_string.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')

    @staticmethod
    def verify(public_key_pem, transaction_dict, signature_b64):
        """验证交易签名是否合法"""
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8')
            )
            
            tx_string = json.dumps(transaction_dict, sort_keys=True)
            signature = base64.b64decode(signature_b64)
            
            public_key.verify(
                signature,
                tx_string.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
