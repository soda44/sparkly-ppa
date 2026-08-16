#!/usr/bin/env python
"""Script de teste para verificar se a aplicação funciona"""

import sys
import os

# Adicionar o diretório ao path
sys.path.insert(0, os.path.dirname(__file__))

try:
    print("1. Importando app...")
    from app import create_app
    from app.models import db
    app = create_app()
    print("   ✅ App importado")

    print("2. Testando conexão com banco...")
    from sqlalchemy import text
    with app.app_context():
        result = db.session.execute(text('SELECT 1'))
        print("   ✅ Conexão OK")

    print("3. Buscando usuário giovane.costa...")
    from app.models import Aluno
    with app.app_context():
        usuario = Aluno.query.filter_by(usuario='giovane.costa').first()
        if usuario:
            print(f"   ✅ Usuário encontrado: {usuario.nome_completo}")
        else:
            print("   ❌ Usuário não encontrado")

    print("\n4. Iniciando servidor Flask...")
    app.run(debug=True, host='localhost', port=5000)

except Exception as e:
    print(f"\n❌ ERRO: {type(e).__name__}")
    print(f"   {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
