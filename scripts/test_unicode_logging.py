import sys
import io
import os

# 模拟 run.py 中的修复逻辑
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.logging import setup_logging
import logging

def test_unicode_logging():
    print("--- Starting Unicode Logging Test ---")
    setup_logging()
    
    # 再次测试触发问题的 Emoji
    try:
        logging.info("🔥 Testing Unicode Support: 🚀 Blockchain Node is Running")
        print("✅ Log call successful")
    except Exception as e:
        print(f"❌ Log call failed: {e}")

    # 检查日志文件内容
    log_file = os.path.join("logs", "shuai_coin.log")
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "🚀" in content:
                print("✅ Unicode character found in log file")
            else:
                print("❌ Unicode character NOT found in log file")

if __name__ == "__main__":
    test_unicode_logging()
