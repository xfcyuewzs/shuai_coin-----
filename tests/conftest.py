import pytest
from web import create_app
from db import db
from db.models import Block, User


@pytest.fixture
def app():
    app = create_app()
    # 开启测试模式，并使用纯内存数据库（不修改真实的 .db 文件）
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })

    with app.app_context():
        db.create_all()
        # 创建创世块
        block = Block(index=1, timestamp=0.0, transactions="[]", proof=100, previous_hash="0", hash="genesis",
                      difficulty=4)
        db.session.add(block)
        db.session.commit()

        yield app

        # 测试结束后自动销毁内存数据库
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    # 提供一个模拟的浏览器客户端，用于测试网页 API
    return app.test_client()