from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())

    from app.models import db
    db.init_app(app)

    with app.app_context():
        db.create_all()

    from app.routes import register_routes
    register_routes(app)

    from app.seed import seed_questoes

    @app.cli.command('seed')
    def seed_command():
        """Insere as questões iniciais de Física no banco."""
        inseridas = seed_questoes()
        print(f'Questões inseridas agora: {inseridas}')

    return app
