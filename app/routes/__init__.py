from app.routes.paginas import paginas_bp
from app.routes.aluno import aluno_bp
from app.routes.professor import professor_bp


def register_routes(app):
    app.register_blueprint(paginas_bp)
    app.register_blueprint(aluno_bp, url_prefix='/api')
    app.register_blueprint(professor_bp, url_prefix='/api/professor')
