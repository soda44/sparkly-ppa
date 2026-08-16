from app.models import db, Aluno, Materia, ModeloQuestao, QuestaoInstanciada, Desempenho


def listar_turmas(professor_id):
    """Lista as turmas (matérias) do professor com totais de lições e alunos."""
    turmas = []
    for m in Materia.query.filter_by(id_professor=professor_id).all():
        licao_ids = [l.id_licao for l in m.licoes]
        total_alunos = 0
        if licao_ids:
            total_alunos = db.session.query(Desempenho.id_aluno)\
                .filter(Desempenho.id_atividade.in_(licao_ids))\
                .distinct().count()

        turmas.append({
            'id': m.id_materia,
            'nome': m.nome_materia,
            'numero_sala': m.numero_sala,
            'total_licoes': len(m.licoes),
            'total_alunos': total_alunos
        })
    return turmas


def obter_turma(materia_id, professor_id):
    """Detalhe da turma (lições + alunos com média). Retorna dict ou None."""
    materia = Materia.query.filter_by(id_materia=materia_id, id_professor=professor_id).first()
    if not materia:
        return None

    licoes = [l.to_dict() for l in materia.licoes]
    licao_ids = [l.id_licao for l in materia.licoes]
    alunos_data = []

    if licao_ids:
        desempenhos = Desempenho.query.filter(Desempenho.id_atividade.in_(licao_ids)).all()
        for aid in sorted({d.id_aluno for d in desempenhos}):
            aluno = db.session.get(Aluno, aid)
            if not aluno:
                continue
            notas = [float(d.nota) for d in desempenhos if d.id_aluno == aid and d.nota]
            alunos_data.append({
                'id': aluno.id_aluno,
                'nome': aluno.nome_completo,
                'usuario': aluno.usuario,
                'media': round(sum(notas) / len(notas), 2) if notas else 0,
                'atividades': len([d for d in desempenhos if d.id_aluno == aid])
            })

    return {
        'turma': materia.to_dict(),
        'licoes': licoes,
        'alunos': alunos_data
    }


def listar_questoes():
    return [q.to_dict() for q in ModeloQuestao.query.all()]


def criar_questao(nome, tipo, conteudo):
    """Cria a questão-modelo e uma instância. Retorna (questao, erro, codigo)."""
    try:
        questao = ModeloQuestao(nome=nome.strip(), tipo=tipo.strip(), conteudo=conteudo)
        db.session.add(questao)
        db.session.flush()
        db.session.add(QuestaoInstanciada(modelo_id=questao.id, valores_variaveis={}))
        db.session.commit()
        return questao, None, 201
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500


def editar_questao(questao_id, dados):
    """Edita uma questão-modelo. Retorna (questao, erro, codigo)."""
    questao = db.session.get(ModeloQuestao, questao_id)
    if not questao:
        return None, 'Questão não encontrada', 404

    try:
        if dados.get('nome'):
            questao.nome = dados['nome'].strip()
        if dados.get('tipo'):
            questao.tipo = dados['tipo'].strip()
        if dados.get('conteudo') is not None:
            questao.conteudo = dados['conteudo']
        db.session.commit()
        return questao, None, 200
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500


def deletar_questao(questao_id):
    """Exclui uma questão-modelo. Retorna (resultado, erro, codigo)."""
    questao = db.session.get(ModeloQuestao, questao_id)
    if not questao:
        return None, 'Questão não encontrada', 404

    try:
        db.session.delete(questao)
        db.session.commit()
        return True, None, 200
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500


def sincronizar_instancias():
    """Cria instâncias para modelos sem nenhuma. Retorna (criadas, erro, codigo)."""
    criadas = 0
    try:
        for modelo in ModeloQuestao.query.all():
            existe = QuestaoInstanciada.query.filter_by(modelo_id=modelo.id).first()
            if not existe:
                db.session.add(QuestaoInstanciada(modelo_id=modelo.id, valores_variaveis={}))
                criadas += 1
        db.session.commit()
        return criadas, None, 200
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500
