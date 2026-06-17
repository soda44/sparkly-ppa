"""
Script para inicializar o banco de dados com questoes iniciais.
Popula as tabelas modelo_questao e questao_instanciada com as
questoes de Fisica definidas abaixo.

Uso: python init_db.py
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from app import app, db
from app.models import ModeloQuestao, QuestaoInstanciada


# ──────────────────────────────────────────────
#  Questoes de Fisica no formato do banco atual
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


def init_db():
    with app.app_context():
        print("Verificando questoes existentes...")

        inseridas = 0
        for q_data in QUESTOES_INICIAIS:
            # Evita duplicata pelo nome
            existente = ModeloQuestao.query.filter_by(nome=q_data["nome"]).first()
            if existente:
                print(f"  [ja existe] {q_data['nome']}")
                # Garante que a instancia existe
                inst = QuestaoInstanciada.query.filter_by(modelo_id=existente.id).first()
                if not inst:
                    inst = QuestaoInstanciada(modelo_id=existente.id, valores_variaveis={})
                    db.session.add(inst)
                    print(f"    -> instancia criada para questao existente")
                continue

            modelo = ModeloQuestao(
                nome=q_data["nome"],
                tipo=q_data["tipo"],
                conteudo=q_data["conteudo"]
            )
            db.session.add(modelo)
            db.session.flush()  # gera o id

            instancia = QuestaoInstanciada(
                modelo_id=modelo.id,
                valores_variaveis={}
            )
            db.session.add(instancia)
            inseridas += 1
            print(f"  [inserida] {q_data['nome']}")

        db.session.commit()

        total = ModeloQuestao.query.count()
        total_inst = QuestaoInstanciada.query.count()
        print(f"\nConcluido!")
        print(f"  Questoes inseridas agora : {inseridas}")
        print(f"  Total modelo_questao     : {total}")
        print(f"  Total questao_instanciada: {total_inst}")


if __name__ == '__main__':
    try:
        init_db()
    except Exception as e:
        print(f"\nErro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
