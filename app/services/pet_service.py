from app.models import db, Aluno, Pet
from app.gamificacao import PET_CORES, PET_COR_PADRAO, PET_NOME_PADRAO, PET_NOME_TAMANHO_MAX


def _catalogo_com_status(pet):
    """Monta o catálogo de cores da loja com o status de cada uma para o pet."""
    desbloqueadas = set(pet.lista_cores_desbloqueadas())
    catalogo = []
    for chave, info in PET_CORES.items():
        catalogo.append({
            'chave': chave,
            'nome': info['nome'],
            'hex': info['hex'],
            'custo': info['custo'],
            'desbloqueada': chave in desbloqueadas,
            'equipada': chave == pet.cor_atual,
        })
    return catalogo


def obter_ou_criar_pet(aluno_id):
    """Retorna o pet do aluno, criando um (com nome e cor padrão) se ainda não existir."""
    pet = Pet.query.filter_by(id_aluno=aluno_id).first()
    if pet:
        return pet

    pet = Pet(id_aluno=aluno_id, nome=PET_NOME_PADRAO, cor_atual=PET_COR_PADRAO,
              cores_desbloqueadas=PET_COR_PADRAO)
    db.session.add(pet)
    db.session.commit()
    return pet


def obter_dados_pet(aluno_id):
    """Retorna o pet (dict) junto com o catálogo de cores da loja."""
    pet = obter_ou_criar_pet(aluno_id)
    return {
        'pet': pet.to_dict(),
        'cores': _catalogo_com_status(pet),
    }


def renomear_pet(aluno_id, novo_nome):
    """Define um novo nome para o pet do aluno. Retorna (pet, erro, codigo)."""
    novo_nome = (novo_nome or '').strip()
    if not novo_nome:
        return None, 'Informe um nome para o pet', 400
    if len(novo_nome) > PET_NOME_TAMANHO_MAX:
        return None, f'O nome pode ter no máximo {PET_NOME_TAMANHO_MAX} caracteres', 400

    pet = obter_ou_criar_pet(aluno_id)
    try:
        pet.nome = novo_nome
        db.session.commit()
        return pet, None, 200
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500


def comprar_cor(aluno_id, cor):
    """Gasta Sparks do aluno para desbloquear uma cor nova do pet.

    Retorna (pet, erro, codigo).
    """
    if cor not in PET_CORES:
        return None, 'Cor inválida', 400

    aluno = db.session.get(Aluno, aluno_id)
    if not aluno:
        return None, 'Aluno não encontrado', 404

    pet = obter_ou_criar_pet(aluno_id)
    if cor in pet.lista_cores_desbloqueadas():
        return None, 'Você já tem essa cor', 400

    custo = PET_CORES[cor]['custo']
    if aluno.sparks < custo:
        return None, 'Sparks insuficientes para comprar essa cor', 400

    try:
        aluno.sparks -= custo
        pet.desbloquear_cor(cor)
        pet.cor_atual = cor
        db.session.commit()
        return pet, None, 200
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500


def equipar_cor(aluno_id, cor):
    """Troca a cor atual do pet para uma cor já desbloqueada. Retorna (pet, erro, codigo)."""
    if cor not in PET_CORES:
        return None, 'Cor inválida', 400

    pet = obter_ou_criar_pet(aluno_id)
    if cor not in pet.lista_cores_desbloqueadas():
        return None, 'Você ainda não desbloqueou essa cor', 400

    try:
        pet.cor_atual = cor
        db.session.commit()
        return pet, None, 200
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500
