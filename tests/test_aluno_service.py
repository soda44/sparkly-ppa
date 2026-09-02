from werkzeug.security import check_password_hash
from app.models import db, Aluno
from app.services import aluno_service


def test_cadastrar_aluno_armazena_hash(ctx):
    aluno, erro, codigo = aluno_service.cadastrar_aluno('Ana', 'ana@teste.com', 'ana', 'senha123', genero='Feminino')
    assert erro is None and codigo == 201
    assert check_password_hash(aluno.senha, 'senha123') is True


def test_cadastrar_aluno_com_nome_social(ctx):
    aluno, erro, codigo = aluno_service.cadastrar_aluno(
        'Ana', 'ana2@teste.com', 'ana2', 'senha123', genero='Não-binário', nome_social='Ari'
    )
    assert erro is None and codigo == 201
    assert aluno.nome_social == 'Ari'
    assert aluno.genero == 'Não-binário'


def test_cadastrar_aluno_usuario_duplicado(ctx):
    db.session.add(Aluno(nome_completo='A', email='a@a.com', usuario='dup', senha='x', genero='Masculino'))
    db.session.commit()

    aluno, erro, codigo = aluno_service.cadastrar_aluno('B', 'b@b.com', 'dup', 'y', genero='Masculino')
    assert aluno is None and erro == 'Usuário já existe' and codigo == 409


def test_cadastrar_aluno_email_duplicado(ctx):
    db.session.add(Aluno(nome_completo='A', email='a@a.com', usuario='um', senha='x', genero='Masculino'))
    db.session.commit()

    aluno, erro, codigo = aluno_service.cadastrar_aluno('B', 'a@a.com', 'dois', 'y', genero='Masculino')
    assert aluno is None and erro == 'Email já cadastrado' and codigo == 409


def test_obter_dados_aluno(ctx):
    aluno = Aluno(nome_completo='Ana', email='ana@teste.com', usuario='ana', senha='hash', genero='Feminino')
    db.session.add(aluno)
    db.session.commit()

    dados = aluno_service.obter_dados_aluno(aluno.id_aluno)
    assert dados['aluno']['usuario'] == 'ana'
    assert dados['desempenho']['total_atividades'] == 0


def test_obter_dados_aluno_inexistente(ctx):
    assert aluno_service.obter_dados_aluno(999) is None
