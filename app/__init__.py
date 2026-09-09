from flask import Flask
from dotenv import load_dotenv
from sqlalchemy import inspect, text

load_dotenv()

from app.config import Config
from app.gamificacao import MAX_CORACOES


def _migrar_colunas_aluno(db):
    """Adiciona colunas novas (nome_social, genero, pontos, coracoes, sparks) em bancos já existentes.

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
        if 'pontos' not in colunas:
            conn.execute(text('ALTER TABLE aluno ADD COLUMN pontos INTEGER NOT NULL DEFAULT 0'))
        if 'coracoes' not in colunas:
            conn.execute(text(
                f'ALTER TABLE aluno ADD COLUMN coracoes INTEGER NOT NULL DEFAULT {MAX_CORACOES}'
            ))
        if 'sparks' not in colunas:
            conn.execute(text('ALTER TABLE aluno ADD COLUMN sparks INTEGER NOT NULL DEFAULT 0'))


def _migrar_colunas_licao_questao(db):
    """Adiciona colunas novas do esquema Módulo → Lição → Questão em bancos já existentes.

    Bancos criados antes do módulo `Modulo` existir têm a tabela `licao` no
    formato antigo (sem nome/ordem/id_modulo) e `questao_instanciada` sem
    `id_licao`, então precisam de ALTER TABLE manual.
    """
    inspector = inspect(db.engine)
    with db.engine.begin() as conn:
        if 'licao' in inspector.get_table_names():
            colunas = {c['name'] for c in inspector.get_columns('licao')}
            if 'nome' not in colunas:
                conn.execute(text("ALTER TABLE licao ADD COLUMN nome VARCHAR(150) NOT NULL DEFAULT 'Lição'"))
            if 'ordem' not in colunas:
                conn.execute(text('ALTER TABLE licao ADD COLUMN ordem INTEGER NOT NULL DEFAULT 0'))
            if 'id_modulo' not in colunas:
                conn.execute(text('ALTER TABLE licao ADD COLUMN id_modulo INTEGER'))

        if 'questao_instanciada' in inspector.get_table_names():
            colunas = {c['name'] for c in inspector.get_columns('questao_instanciada')}
            if 'id_licao' not in colunas:
                conn.execute(text('ALTER TABLE questao_instanciada ADD COLUMN id_licao INTEGER'))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config())

    from app.models import db
    db.init_app(app)

    with app.app_context():
        db.create_all()
        _migrar_colunas_aluno(db)
        _migrar_colunas_licao_questao(db)

    from app.routes import register_routes
    register_routes(app)

    from app.seed import seed_questoes, seed_usuarios_padrao

    @app.cli.command('seed')
    def seed_command():
        """Insere as questões iniciais de Física e os usuários padrão de teste."""
        inseridas = seed_questoes()
        alunos, professores = seed_usuarios_padrao()
        print(f'Questões inseridas agora: {inseridas}')
        print(f'Alunos padrão criados: {alunos}')
        print(f'Professores padrão criados: {professores}')

    return app
