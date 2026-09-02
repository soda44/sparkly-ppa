from flask import Flask
from dotenv import load_dotenv
from sqlalchemy import inspect, text

load_dotenv()

from app.config import Config


def _migrar_colunas_aluno(db):
    """Adiciona colunas novas (nome_social, genero) em bancos já existentes.

    db.create_all() só cria tabelas que não existem, então bancos antigos
    (criados antes desses campos) precisam de um ALTER TABLE manual.
    """
    inspector = inspect(db.engine)
    if 'aluno' not in inspector.get_table_names():
        return

    colunas = {c['name'] for c in inspector.get_columns('aluno')}
    with db.engine.begin() as conn:
        if 'nome_social' not in colunas:
            conn.execute(text('ALTER TABLE aluno ADD COLUMN nome_social VARCHAR(150)'))
        if 'genero' not in colunas:
            conn.execute(text(
                "ALTER TABLE aluno ADD COLUMN genero VARCHAR(60) NOT NULL DEFAULT 'Prefiro não dizer'"
            ))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())

    from app.models import db
    db.init_app(app)

    with app.app_context():
        db.create_all()
        _migrar_colunas_aluno(db)

    from app.routes import register_routes
    register_routes(app)

    from app.seed import seed_questoes

    @app.cli.command('seed')
    def seed_command():
        """Insere as questões iniciais de Física no banco."""
        inseridas = seed_questoes()
        print(f'Questões inseridas agora: {inseridas}')

    return app
