from app.models import db, Aluno
from app.gamificacao import MAX_CORACOES, MISSOES, SPARKS_PARA_RECARGA
from app.services import gamificacao_service


def _criar_aluno(usuario='aluno1', nome='Aluno Teste', coracoes=MAX_CORACOES, pontos=0, sparks=0, nome_social=None):
    aluno = Aluno(
        nome_completo=nome, email=f'{usuario}@teste.com', usuario=usuario,
        senha='hash', genero='Prefiro não dizer', coracoes=coracoes, pontos=pontos,
        sparks=sparks, nome_social=nome_social,
    )
    db.session.add(aluno)
    db.session.commit()
    return aluno


def test_listar_missoes_progresso(ctx):
    aluno = _criar_aluno(pontos=25)
    missoes = gamificacao_service.listar_missoes(aluno.id_aluno)
    assert len(missoes) == len(MISSOES)
    primeira = missoes[0]
    assert primeira['meta'] == MISSOES[0]
    assert primeira['concluida'] is True  # 25 >= 20
    ultima = missoes[-1]
    assert ultima['concluida'] is False


def test_listar_missoes_aluno_sem_pontos(ctx):
    aluno = _criar_aluno(pontos=0)
    missoes = gamificacao_service.listar_missoes(aluno.id_aluno)
    assert all(m['concluida'] is False for m in missoes)
    assert missoes[0]['progresso'] == 0.0


def test_listar_missoes_aluno_inexistente(ctx):
    missoes = gamificacao_service.listar_missoes(999)
    assert missoes[0]['pontos_atuais'] == 0


def test_listar_ranking_ordena_por_pontos(ctx):
    _criar_aluno('a', pontos=10)
    _criar_aluno('b', pontos=50)
    _criar_aluno('c', pontos=30)

    ranking = gamificacao_service.listar_ranking()
    assert [r['usuario'] for r in ranking] == ['b', 'c', 'a']
    assert ranking[0]['posicao'] == 1


def test_listar_ranking_usa_nome_social(ctx):
    _criar_aluno('d', nome='Nome Legal', pontos=5, nome_social='Apelido')
    ranking = gamificacao_service.listar_ranking()
    assert ranking[0]['nome'] == 'Apelido'


def test_listar_ranking_respeita_limite(ctx):
    for i in range(15):
        _criar_aluno(f'u{i}', pontos=i)
    ranking = gamificacao_service.listar_ranking(limite=10)
    assert len(ranking) == 10


def test_recarregar_coracoes_sucesso(ctx):
    aluno = _criar_aluno(coracoes=2, sparks=SPARKS_PARA_RECARGA)
    resultado, erro, codigo = gamificacao_service.recarregar_coracoes(aluno.id_aluno)
    assert erro is None and codigo == 200
    assert resultado.coracoes == MAX_CORACOES
    assert resultado.sparks == 0


def test_recarregar_coracoes_ja_cheio(ctx):
    aluno = _criar_aluno(coracoes=MAX_CORACOES, sparks=100)
    resultado, erro, codigo = gamificacao_service.recarregar_coracoes(aluno.id_aluno)
    assert resultado is None and codigo == 400


def test_recarregar_coracoes_sparks_insuficientes(ctx):
    aluno = _criar_aluno(coracoes=1, sparks=SPARKS_PARA_RECARGA - 1)
    resultado, erro, codigo = gamificacao_service.recarregar_coracoes(aluno.id_aluno)
    assert resultado is None and codigo == 400


def test_recarregar_coracoes_aluno_inexistente(ctx):
    resultado, erro, codigo = gamificacao_service.recarregar_coracoes(999)
    assert resultado is None and codigo == 404
