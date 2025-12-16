import os

from flask import Flask


def create_app() -> Flask:
    """Pomodoro WebアプリのFlaskアプリを生成する。"""
    package_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(package_dir, os.pardir))
    app = Flask(
        __name__,
        template_folder=os.path.join(project_root, "templates"),
        static_folder=os.path.join(project_root, "static"),
    )

    # ルート登録
    from .routes import bp

    app.register_blueprint(bp)

    return app
