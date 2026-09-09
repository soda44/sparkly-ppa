from app.models import db, Aluno, ModeloQuestao, QuestaoInstanciada
from app.gamificacao import MAX_CORACOES
from app.services import questao_service


def _criar_questao(conteudo, tipo='multipla-escolha'):
    modelo = ModeloQuestao(nome='Questão de teste', tipo=tipo, conteudo=conteudo)
    db.session.add(modelo)
    db.session.flush()
    inst = QuestaoInstanciada(modelo_id=modelo.id, valores_variaveis={})
    db.session.add(inst)
    db.session.commit()
    return modelo, inst


def _criar_aluno(usuario='aluno1', coracoes=MAX_CORACOES, pontos=0, sparks=0):
    aluno = Aluno(
        nome_completo='Aluno Teste', email=f'{usuario}@teste.com', usuario=usuario,
        senha='hash', genero='Prefiro não dizer', coracoes=coracoes, pontos=pontos, sparks=sparks,
    )
    db.session.add(aluno)
    db.session.commit()
    return aluno


def test_avaliar_resposta_multipla_escolha_correta():
    conteudo = {'gabarito': 2}
    assert questao_service.avaliar_resposta('multipla-escolha', conteudo, '2') is True


def test_avaliar_resposta_multipla_escolha_errada():
    conteudo = {'gabarito': 2}
    assert questao_service.avaliar_resposta('multipla-escolha', conteudo, '0') is False


def test_avaliar_resposta_texto_ignora_caixa_e_espacos():
    conteudo = {'gabarito': 'Positiva'}
    assert questao_service.avaliar_resposta('entrada-texto', conteudo, ' positiva ') is True


def test_avaliar_resposta_texto_errada():
    conteudo = {'gabarito': 'Positiva'}
    assert questao_service.avaliar_resposta('entrada-texto', conteudo, 'Negativa') is False


def test_interpolar_enunciado_substitui_variavel():
    texto = 'Qual é a carga? {{ valor }}'
    assert questao_service.interpolar_enunciado(texto, {'valor': 42}) == 'Qual é a carga? 42'


def test_interpolar_enunciado_sem_valores_retorna_texto():
    assert questao_service.interpolar_enunciado('Texto fixo', None) == 'Texto fixo'


def test_listar_questoes_oculta_gabarito(ctx):
    _criar_questao({'enunciado': 'E1', 'alternativas': ['A', 'B'], 'gabarito': 1})
    questoes = questao_service.listar_questoes_do_aluno(aluno_id=1)
    assert len(questoes) == 1
    assert 'gabarito' not in questoes[0]['conteudo']
    assert questoes[0]['ja_respondida'] is False


def test_listar_questoes_marca_respondida(ctx):
    _, inst = _criar_questao({'enunciado': 'E1', 'alternativas': ['A', 'B'], 'gabarito': 1})
    questao_service.registrar_resposta(1, inst.id, '1')
    questoes = questao_service.listar_questoes_do_aluno(aluno_id=1)
    assert questoes[0]['ja_respondida'] is True


def test_registrar_resposta_correta(ctx):
    _, inst = _criar_questao({'enunciado': 'E1', 'alternativas': ['A', 'B'], 'gabarito': 1})
    resultado, erro, codigo = questao_service.registrar_resposta(1, inst.id, '1')
    assert erro is None and codigo == 200
    assert resultado['correto'] is True
    assert resultado['nota'] == 10.0


def test_registrar_resposta_incorreta(ctx):
    _, inst = _criar_questao({'enunciado': 'E1', 'alternativas': ['A', 'B'], 'gabarito': 1})
    resultado, erro, _ = questao_service.registrar_resposta(1, inst.id, '0')
    assert resultado['correto'] is False
    assert resultado['nota'] == 0.0


def test_registrar_resposta_questao_inexistente(ctx):
    resultado, erro, codigo = questao_service.registrar_resposta(1, 9999, '1')
    assert resultado is None and erro and codigo == 404


def test_registrar_resposta_correta_ganha_pontos(ctx):
    aluno = _criar_aluno()
    _, inst = _criar_questao({'enunciado': 'E1', 'alternativas': ['A', 'B'], 'gabarito': 1})
    resultado, erro, codigo = questao_service.registrar_resposta(aluno.id_aluno, inst.id, '1')
    assert erro is None and codigo == 200
    assert resultado['pontos_ganhos'] == 10
    assert resultado['pontos_totais'] == 10
    assert resultado['coracoes'] == MAX_CORACOES
    assert resultado['em_pratica'] is False


def test_registrar_resposta_correta_ganha_sparks(ctx):
    aluno = _criar_aluno()
    _, inst = _criar_questao({'enunciado': 'E1', 'alternativas': ['A', 'B'], 'gabarito': 1})
    resultado, erro, codigo = questao_service.registrar_resposta(aluno.id_aluno, inst.id, '1')
    assert erro is None and codigo == 200
    assert resultado['sparks_ganhos'] == 5
    assert resultado['sparks_totais'] == 5


def test_registrar_resposta_errada_nao_ganha_sparks(ctx):
    aluno = _criar_aluno()
    _, inst = _criar_questao({'enunciado': 'E1', 'alternativas': ['A', 'B'], 'gabarito': 1})
    resultado, erro, codigo = questao_service.registrar_resposta(aluno.id_aluno, inst.id, '0')
    assert erro is None and codigo == 200
    assert resultado['sparks_ganhos'] == 0
    assert resultado['sparks_totais'] == 0


def test_registrar_resposta_errada_perde_coracao(ctx):
    aluno = _criar_aluno()
    _, inst = _criar_questao({'enunciado': 'E1', 'alternativas': ['A', 'B'], 'gabarito': 1})
    resultado, erro, codigo = questao_service.registrar_resposta(aluno.id_aluno, inst.id, '0')
    assert erro is None and codigo == 200
    assert resultado['coracoes'] == MAX_CORACOES - 1
    assert resultado['pontos_ganhos'] == 0


def test_registrar_resposta_bloqueada_sem_coracoes(ctx):
    aluno = _criar_aluno(coracoes=0)
    _, inst = _criar_questao({'enunciado': 'E1', 'alternativas': ['A', 'B'], 'gabarito': 1})
    resultado, erro, codigo = questao_service.registrar_resposta(aluno.id_aluno, inst.id, '1')
    assert resultado is None and codigo == 403


def test_praticar_questao_concluida_nao_perde_coracao_se_errar(ctx):
    aluno = _criar_aluno(coracoes=1, pontos=10)
    _, inst = _criar_questao({'enunciado': 'E1', 'alternativas': ['A', 'B'], 'gabarito': 1})
    # Primeiro acerto: fica concluída.
    questao_service.registrar_resposta(aluno.id_aluno, inst.id, '1')
    # Prática errada: não deve perder coração nem ganhar pontos.
    resultado, erro, codigo = questao_service.registrar_resposta(aluno.id_aluno, inst.id, '0')
    assert erro is None and codigo == 200
    assert resultado['em_pratica'] is True
    assert resultado['pontos_ganhos'] == 0
    aluno_atualizado = db.session.get(Aluno, aluno.id_aluno)
    assert aluno_atualizado.coracoes == 1


def test_praticar_questao_concluida_acerto_devolve_coracao(ctx):
    aluno = _criar_aluno(coracoes=3, pontos=0)
    _, inst = _criar_questao({'enunciado': 'E1', 'alternativas': ['A', 'B'], 'gabarito': 1})
    questao_service.registrar_resposta(aluno.id_aluno, inst.id, '1')  # concluída, ganha 10 pts
    resultado, erro, codigo = questao_service.registrar_resposta(aluno.id_aluno, inst.id, '1')  # prática
    assert erro is None and codigo == 200
    assert resultado['em_pratica'] is True
    assert resultado['coracoes'] == min(3 + 1, MAX_CORACOES)
    assert resultado['pontos_totais'] == 20
    assert resultado['sparks_totais'] == 10


def test_praticar_questao_bloqueada_mesmo_sem_coracoes(ctx):
    aluno = _criar_aluno(coracoes=0, pontos=0)
    _, inst = _criar_questao({'enunciado': 'E1', 'alternativas': ['A', 'B'], 'gabarito': 1})
    # Não pode responder pela primeira vez sem corações.
    resultado, erro, codigo = questao_service.registrar_resposta(aluno.id_aluno, inst.id, '1')
    assert resultado is None and codigo == 403

    # Simula que já havia concluído antes (ex.: ganhou corações depois).
    aluno.coracoes = 1
    db.session.commit()
    questao_service.registrar_resposta(aluno.id_aluno, inst.id, '1')
    aluno.coracoes = 0
    db.session.commit()

    # Agora, mesmo sem corações, pode praticar de graça.
    resultado, erro, codigo = questao_service.registrar_resposta(aluno.id_aluno, inst.id, '1')
    assert erro is None and codigo == 200
    assert resultado['em_pratica'] is True


def test_listar_questoes_marca_bloqueada_sem_coracoes(ctx):
    aluno = _criar_aluno(coracoes=0)
    _criar_questao({'enunciado': 'E1', 'alternativas': ['A', 'B'], 'gabarito': 1})
    questoes = questao_service.listar_questoes_do_aluno(aluno.id_aluno)
    assert questoes[0]['bloqueada'] is True
