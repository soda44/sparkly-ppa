"""Script fino para popular o banco com as questões iniciais.

A lógica real está em app/seed.py. Este script só cria a app e chama o seed.

Uso: python init_db.py
Equivalente: flask seed
"""
from app import create_app
from app.seed import seed_questoes, seed_usuarios_padrao
from app.models import ModeloQuestao, QuestaoInstanciada, Aluno, Professor

app = create_app()

with app.app_context():
    print("Verificando questoes existentes...")
    inseridas = seed_questoes()
    total = ModeloQuestao.query.count()
    total_inst = QuestaoInstanciada.query.count()

    print("Verificando usuarios padrao...")
    alunos_criados, professores_criados = seed_usuarios_padrao()
    total_alunos = Aluno.query.count()
    total_professores = Professor.query.count()

    print("\nConcluido!")
    print(f"  Questoes inseridas agora : {inseridas}")
    print(f"  Total modelo_questao     : {total}")
    print(f"  Total questao_instanciada: {total_inst}")
    print(f"  Alunos padrao criados    : {alunos_criados}")
    print(f"  Professores padrao criados: {professores_criados}")
    print(f"  Total alunos             : {total_alunos}")
    print(f"  Total professores        : {total_professores}")
