from flask import Flask
from flask_login import LoginManager
from flasgger import Swagger
from flask_migrate import Migrate
from config.settings import Config
from db import db
from db.models import User
from security.anti_ddos import limiter

login_manager = LoginManager()
swagger = Swagger()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # 初始化 Swagger
    swagger.init_app(app)

    limiter.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_globals():
        from core.utils import mask_address
        return dict(mask=mask_address, config=Config)

    from web.auth import auth_bp
    from web.routes import routes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)

    return app