"""Script fino para popular o banco com as questões iniciais.

A lógica real está em app/seed.py. Este script só cria a app e chama o seed.

Uso: python init_db.py
Equivalente: flask seed
"""
from app import create_app
from app.seed import seed_questoes
from app.models import ModeloQuestao, QuestaoInstanciada

app = create_app()

with app.app_context():
    print("Verificando questoes existentes...")
    inseridas = seed_questoes()
    total = ModeloQuestao.query.count()
    total_inst = QuestaoInstanciada.query.count()

    print("\nConcluido!")
    print(f"  Questoes inseridas agora : {inseridas}")
    print(f"  Total modelo_questao     : {total}")
    print(f"  Total questao_instanciada: {total_inst}")
