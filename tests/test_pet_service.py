from app.models import db, Aluno, Pet
from app.gamificacao import PET_NOME_PADRAO, PET_COR_PADRAO, PET_CORES
from app.services import pet_service


def _criar_aluno(usuario='aluno1', sparks=0):
    aluno = Aluno(
        nome_completo='Aluno Teste', email=f'{usuario}@teste.com', usuario=usuario,
        senha='hash', genero='Prefiro não dizer', sparks=sparks,
    )
    db.session.add(aluno)
    db.session.commit()
    return aluno


def test_obter_ou_criar_pet_cria_com_padroes(ctx):
    aluno = _criar_aluno()
    pet = pet_service.obter_ou_criar_pet(aluno.id_aluno)
    assert pet.nome == PET_NOME_PADRAO
    assert pet.cor_atual == PET_COR_PADRAO
    assert pet.lista_cores_desbloqueadas() == [PET_COR_PADRAO]


def test_obter_ou_criar_pet_idempotente(ctx):
    aluno = _criar_aluno()
    pet1 = pet_service.obter_ou_criar_pet(aluno.id_aluno)
    pet2 = pet_service.obter_ou_criar_pet(aluno.id_aluno)
    assert pet1.id_pet == pet2.id_pet
    assert Pet.query.filter_by(id_aluno=aluno.id_aluno).count() == 1


def test_renomear_pet_sucesso(ctx):
    aluno = _criar_aluno()
    pet, erro, codigo = pet_service.renomear_pet(aluno.id_aluno, 'Faísca')
    assert erro is None and codigo == 200
    assert pet.nome == 'Faísca'


def test_renomear_pet_nome_vazio(ctx):
    aluno = _criar_aluno()
    pet, erro, codigo = pet_service.renomear_pet(aluno.id_aluno, '   ')
    assert pet is None and codigo == 400


def test_renomear_pet_nome_muito_grande(ctx):
    aluno = _criar_aluno()
    pet, erro, codigo = pet_service.renomear_pet(aluno.id_aluno, 'x' * 21)
    assert pet is None and codigo == 400


def test_comprar_cor_sucesso_e_equipa_automaticamente(ctx):
    custo = PET_CORES['verde']['custo']
    aluno = _criar_aluno(sparks=custo)
    pet, erro, codigo = pet_service.comprar_cor(aluno.id_aluno, 'verde')
    assert erro is None and codigo == 200
    assert pet.cor_atual == 'verde'
    assert 'verde' in pet.lista_cores_desbloqueadas()
    assert db.session.get(Aluno, aluno.id_aluno).sparks == 0


def test_comprar_cor_sparks_insuficientes(ctx):
    aluno = _criar_aluno(sparks=1)
    pet, erro, codigo = pet_service.comprar_cor(aluno.id_aluno, 'verde')
    assert pet is None and codigo == 400


def test_comprar_cor_ja_desbloqueada(ctx):
    aluno = _criar_aluno(sparks=100)
    pet, erro, codigo = pet_service.comprar_cor(aluno.id_aluno, PET_COR_PADRAO)
    assert pet is None and codigo == 400


def test_comprar_cor_invalida(ctx):
    aluno = _criar_aluno(sparks=100)
    pet, erro, codigo = pet_service.comprar_cor(aluno.id_aluno, 'inexistente')
    assert pet is None and codigo == 400


def test_equipar_cor_nao_desbloqueada(ctx):
    aluno = _criar_aluno()
    pet, erro, codigo = pet_service.equipar_cor(aluno.id_aluno, 'verde')
    assert pet is None and codigo == 400


def test_equipar_cor_desbloqueada(ctx):
    custo = PET_CORES['azul']['custo']
    aluno = _criar_aluno(sparks=custo)
    pet_service.comprar_cor(aluno.id_aluno, 'azul')
    pet, erro, codigo = pet_service.equipar_cor(aluno.id_aluno, PET_COR_PADRAO)
    assert erro is None and codigo == 200
    assert pet.cor_atual == PET_COR_PADRAO


def test_obter_dados_pet_retorna_catalogo(ctx):
    aluno = _criar_aluno()
    dados = pet_service.obter_dados_pet(aluno.id_aluno)
    assert dados['pet']['nome'] == PET_NOME_PADRAO
    chaves = {c['chave'] for c in dados['cores']}
    assert chaves == set(PET_CORES.keys())
    padrao = next(c for c in dados['cores'] if c['chave'] == PET_COR_PADRAO)
    assert padrao['desbloqueada'] is True and padrao['equipada'] is True
