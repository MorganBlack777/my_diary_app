from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from markupsafe import Markup
import mistune

db = SQLAlchemy()
login_manager = LoginManager()
markdown = mistune.create_markdown()


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Add nl2br filter for nice line breaks in entries
    @app.template_filter('nl2br')
    def nl2br_filter(s):
        if not s:
            return s
        return Markup(s.replace('\n', '<br>'))

    # Add markdown filter
    @app.template_filter('markdown')
    def markdown_filter(text):
        if not text:
            return ''
        return Markup(markdown(text))

    # Создаем папку instance если ее нет
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from app.routes import main_bp
    from app.auth import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()

    return app