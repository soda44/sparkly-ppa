from werkzeug.security import check_password_hash, generate_password_hash
from app.models import db, Aluno, Professor


def _verificar_senha(senha_armazenada, senha_informada, usuario):
    """Verifica a senha. Se o banco ainda tiver texto puro, migra para hash no primeiro login."""
    if senha_armazenada.startswith(('scrypt:', 'pbkdf2:')):
        return check_password_hash(senha_armazenada, senha_informada)

    if senha_armazenada == senha_informada:
        usuario.senha = generate_password_hash(senha_informada)
        db.session.commit()
        return True

    return False


def validar_login(usuario_nome, senha):
    """Valida credenciais do aluno. Retorna o aluno ou None."""
    aluno = Aluno.query.filter_by(usuario=usuario_nome).first()
    if not aluno or not _verificar_senha(aluno.senha, senha, aluno):
        return None
    return aluno


def validar_login_professor(usuario_nome, senha):
    """Valida credenciais do professor. Retorna o professor ou None."""
    professor = Professor.query.filter_by(usuario=usuario_nome).first()
    if not professor or not _verificar_senha(professor.senha, senha, professor):
        return None
    return professor
