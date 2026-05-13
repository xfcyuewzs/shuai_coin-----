import logging
import os
import unittest
import sys
import io

class TestLoggingUnicode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 强制测试脚本自身的 stdout 为 utf-8
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

        cls.test_log_dir = "logs_test"
        if not os.path.exists(cls.test_log_dir):
            os.makedirs(cls.test_log_dir)
            
        cls.log_file = os.path.join(cls.test_log_dir, "test_unicode.log")
        if os.path.exists(cls.log_file):
            os.remove(cls.log_file)

        # 获取 root logger
        logger = logging.getLogger("UnicodeTester")
        logger.setLevel(logging.INFO)
        
        # 清除旧的 Handler
        logger.handlers = []

        # 1. 文件处理器：显式指定 UTF-8
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(cls.log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(file_handler)

        # 2. 控制台处理器：模拟生产环境的包装
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('[CONSOLE] %(message)s'))
        logger.addHandler(console_handler)
        
        cls.logger = logger

    def test_emoji_logging(self):
        """测试写入 Emoji"""
        msg = "🚀 Rocket Emoji Test"
        self.logger.info(msg)
        with open(self.log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(msg, content)

    def test_chinese_logging(self):
        """测试写入中文"""
        msg = "中文测试内容"
        self.logger.info(msg)
        with open(self.log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(msg, content)

    def test_special_symbols_logging(self):
        """测试写入特殊符号"""
        msg = "Special Symbols: ¥ © ® ™ 🌍 🔒"
        self.logger.info(msg)
        with open(self.log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(msg, content)

if __name__ == "__main__":
    unittest.main()
