from werkzeug.security import generate_password_hash
from app.models import db, Aluno
from app.services import auth_service


def _criar_aluno(usuario='maria', senha='segredo'):
    aluno = Aluno(
        nome_completo='Maria',
        email=f'{usuario}@teste.com',
        usuario=usuario,
        senha=generate_password_hash(senha),
        genero='Feminino'
    )
    db.session.add(aluno)
    db.session.commit()
    return aluno


def test_validar_login_correto(ctx):
    _criar_aluno()
    aluno = auth_service.validar_login('maria', 'segredo')
    assert aluno is not None
    assert aluno.usuario == 'maria'


def test_validar_login_senha_errada(ctx):
    _criar_aluno()
    assert auth_service.validar_login('maria', 'errada') is None


def test_validar_login_usuario_inexistente(ctx):
    assert auth_service.validar_login('ninguem', 'x') is None


def test_validar_login_senha_legada_migra_para_hash(ctx):
    db.session.add(Aluno(
        nome_completo='Legado',
        email='legado@teste.com',
        usuario='legado',
        senha='textopuro',
        genero='Prefiro não dizer'
    ))
    db.session.commit()

    aluno = auth_service.validar_login('legado', 'textopuro')
    assert aluno is not None
    db.session.refresh(aluno)
    assert aluno.senha.startswith('scrypt:')
