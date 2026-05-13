import unittest
import json
import os
import hashlib
from flask import Flask, request, jsonify
from security.auth import content_moderator

class TestContentModerator(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test_secret'
        
        # 模拟规则文件
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        os.makedirs(os.path.join(self.base_path, 'config'), exist_ok=True)
        
        with open(os.path.join(self.base_path, 'config/sensitive_words.txt'), 'w', encoding='utf-8') as f:
            f.write("illegal_content\n")
            
        with open(os.path.join(self.base_path, 'config/image_blacklist.sha256'), 'w', encoding='utf-8') as f:
            # sha256 of 'bad_image'
            self.bad_hash = hashlib.sha256(b'bad_image').hexdigest()
            f.write(f"{self.bad_hash}\n")

        @self.app.route('/publish', methods=['POST'])
        @content_moderator()
        def publish():
            return jsonify({"code": 0, "msg": "success"})

        self.client = self.app.test_client()

    def test_sensitive_word_blocked(self):
        """测试敏感词屏蔽"""
        res = self.client.post('/publish', json={"content": "This is some illegal_content here"})
        self.assertEqual(res.status_code, 451)
        self.assertIn("Content Blocked", res.get_json()['msg'])

    def test_image_hash_blocked(self):
        """测试黑名单图片哈希屏蔽"""
        from io import BytesIO
        data = {
            'file': (BytesIO(b'bad_image'), 'test.jpg'),
            'content': 'Normal text'
        }
        res = self.client.post('/publish', data=data, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 451)

    def test_normal_content_passed(self):
        """测试正常内容通过"""
        res = self.client.post('/publish', json={"content": "Hello ShuaiCoin!"})
        self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
