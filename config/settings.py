import os
import uuid


class Config:
    # 动态获取端口，方便本地启动多个节点测试P2P
    PORT = int(os.environ.get('PORT', 5000))

    # Flask及数据库配置
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    # 优先使用环境变量中的 SECRET_KEY，若无则使用基于端口的固定字符串
    SECRET_KEY = os.environ.get('SECRET_KEY', f'shuai_coin_ultimate_secret_key_{PORT}')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "instance", f"shuai_coin_node_{PORT}.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 链上共识参数
    DIFFICULTY = 4  # 初始挖矿难度
    TARGET_BLOCK_TIME = 30  # 目标出块时间（秒）
    BLOCK_REWARD = 10.0  # 基础区块奖励
    MIN_FEE = 0.1  # 最低交易手续费

    # 节点标识
    NODE_IDENTIFIER = str(uuid.uuid4()).replace('-', '')