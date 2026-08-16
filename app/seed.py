"""Dados iniciais do banco: questões de Física.

Uso (a tabela é criada automaticamente ao subir a app):
    python init_db.py          # script fino na raiz
    flask seed                 # ou via CLI do Flask
"""
from app.models import db, ModeloQuestao, QuestaoInstanciada

# ──────────────────────────────────────────────
#  Questões de Física no formato do banco atual
#  tipo deve ser um dos valores do ENUM:
#    'multipla-escolha' | 'multi-selecao' | 'entrada-texto'
#
#  conteudo JSON:
#    { enunciado, alternativas: [...], gabarito: <indice 0-based> }
# ──────────────────────────────────────────────
QUESTOES_INICIAIS = [
    {
        "nome": "Eletrização por Atrito — Carga do Bastão",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Quando atritamos um bastão de vidro com seda, o bastão fica com carga...",
            "alternativas": [
                "Negativa",
                "Positiva",
                "Neutra",
                "Depende da temperatura"
            ],
            "gabarito": 1   # Positiva
        }
    },
    {
        "nome": "Eletrização por Atrito — Afinidade Eletrônica",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "A eletrização por atrito ocorre pois corpos diferentes têm diferentes...",
            "alternativas": [
                "Massas atômicas",
                "Afinidades eletrônicas",
                "Cargas nucleares",
                "Pressões internas"
            ],
            "gabarito": 1   # Afinidades eletrônicas
        }
    },
    {
        "nome": "Eletrização por Contato — Carga Adquirida",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Na eletrização por contato, o corpo que toca o condutor eletrizado...",
            "alternativas": [
                "Perde toda a carga",
                "Adquire carga do mesmo sinal",
                "Adquire carga de sinal oposto",
                "Fica neutro"
            ],
            "gabarito": 1   # Adquire carga do mesmo sinal
        }
    },
    {
        "nome": "Eletrização por Contato — Tipo de Material",
        "tipo": "multipla-escolha",
        "conteudo": {
            "enunciado": "Para que a eletrização por contato ocorra, os corpos devem ser...",
            "alternativas": [
                "Isolantes",
                "Condutores",
                "Magnéticos",
                "Radioativos"
            ],
            "gabarito": 1   # Condutores
        }
    },
]


def seed_questoes():
    """Insere as questões iniciais que ainda não existem, com suas instâncias.

    Retorna a quantidade de questões inseridas agora. É idempotente: se já
    existir, apenas garante que a instância correspondente também existe.
    """
    inseridas = 0
    for q_data in QUESTOES_INICIAIS:
        existente = ModeloQuestao.query.filter_by(nome=q_data["nome"]).first()
        if existente:
            inst = QuestaoInstanciada.query.filter_by(modelo_id=existente.id).first()
            if not inst:
                db.session.add(QuestaoInstanciada(modelo_id=existente.id, valores_variaveis={}))
            continue

        modelo = ModeloQuestao(
            nome=q_data["nome"],
            tipo=q_data["tipo"],
            conteudo=q_data["conteudo"]
        )
        db.session.add(modelo)
        db.session.flush()

        db.session.add(QuestaoInstanciada(
            modelo_id=modelo.id,
            valores_variaveis={}
        ))
        inseridas += 1

    db.session.commit()
    return inseridas
