from app.models import db, ModeloQuestao, QuestaoInstanciada
from app.services import professor_service


def test_criar_questao_cria_instancia(ctx):
    questao, erro, codigo = professor_service.criar_questao('Q1', 'multipla-escolha', {'gabarito': 0})
    assert erro is None and codigo == 201
    assert QuestaoInstanciada.query.filter_by(modelo_id=questao.id).count() == 1


def test_sincronizar_instancias_eh_idempotente(ctx):
    professor_service.criar_questao('Q1', 'multipla-escolha', {'gabarito': 0})
    criadas, erro, codigo = professor_service.sincronizar_instancias()
    assert erro is None and codigo == 200
    assert criadas == 0


def test_editar_questao(ctx):
    questao, _, _ = professor_service.criar_questao('Q1', 'multipla-escolha', {'gabarito': 0})
    editada, erro, codigo = professor_service.editar_questao(questao.id, {'nome': 'Q2'})
    assert erro is None and codigo == 200
    assert editada.nome == 'Q2'


def test_editar_questao_inexistente(ctx):
    resultado, erro, codigo = professor_service.editar_questao(999, {'nome': 'X'})
    assert resultado is None and codigo == 404


def test_deletar_questao(ctx):
    questao, _, _ = professor_service.criar_questao('Q1', 'multipla-escolha', {'gabarito': 0})
    resultado, erro, codigo = professor_service.deletar_questao(questao.id)
    assert resultado is True and erro is None and codigo == 200
    assert db.session.get(ModeloQuestao, questao.id) is None


def test_listar_questoes(ctx):
    professor_service.criar_questao('Q1', 'multipla-escolha', {'gabarito': 0})
    assert len(professor_service.listar_questoes()) == 1
