from app.models import db, ModeloQuestao, QuestaoInstanciada
from app.services import questao_service


def _criar_questao(conteudo, tipo='multipla-escolha'):
    modelo = ModeloQuestao(nome='Questão de teste', tipo=tipo, conteudo=conteudo)
    db.session.add(modelo)
    db.session.flush()
    inst = QuestaoInstanciada(modelo_id=modelo.id, valores_variaveis={})
    db.session.add(inst)
    db.session.commit()
    return modelo, inst


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
