from app.models import db, Desempenho, ModeloQuestao, QuestaoInstanciada


def interpolar_enunciado(texto_base, valores_variaveis):
    """Substitui {{ variavel }} pelo valor correspondente em valores_variaveis."""
    if not texto_base or not valores_variaveis:
        return texto_base or ''
    resultado = texto_base
    for chave, valor in valores_variaveis.items():
        resultado = resultado.replace('{{' + chave + '}}', str(valor))
        resultado = resultado.replace('{{ ' + chave + ' }}', str(valor))
    return resultado


def avaliar_resposta(tipo, conteudo, resposta):
    """Retorna True/False se a resposta está correta conforme o tipo da questão."""
    gabarito = conteudo.get('gabarito')
    if tipo in ('multipla-escolha', 'multi-selecao', 'multipla_escolha', 'verdadeiro_falso'):
        try:
            return int(resposta) == int(gabarito)
        except (ValueError, TypeError):
            return False
    return str(resposta).strip().lower() == str(gabarito).strip().lower()


def listar_questoes_do_aluno(aluno_id):
    """Lista as questões instanciadas com enunciado interpolado e gabarito oculto."""
    respondidas = set()
    for d in Desempenho.query.filter_by(id_aluno=aluno_id).all():
        respondidas.add(d.id_atividade)

    resultado = []
    for inst in QuestaoInstanciada.query.all():
        modelo = inst.modelo
        if not modelo:
            continue

        conteudo = dict(modelo.conteudo) if modelo.conteudo else {}
        texto_base = conteudo.get('texto_base', conteudo.get('enunciado', ''))

        conteudo_publico = dict(conteudo)
        conteudo_publico['enunciado'] = interpolar_enunciado(texto_base, inst.valores_variaveis or {})
        conteudo_publico.pop('gabarito', None)
        conteudo_publico.pop('texto_base', None)

        resultado.append({
            'id': inst.id,
            'modelo_id': modelo.id,
            'nome': modelo.nome,
            'tipo': modelo.tipo,
            'conteudo': conteudo_publico,
            'ja_respondida': inst.id in respondidas,
        })

    return resultado


def registrar_resposta(aluno_id, questao_id, resposta):
    """Avalia a resposta e grava/atualiza o desempenho. Retorna (resultado, erro, codigo)."""
    inst = db.session.get(QuestaoInstanciada, questao_id)
    if not inst or not inst.modelo:
        return None, 'Questão não encontrada', 404

    conteudo = inst.modelo.conteudo
    correto = avaliar_resposta(inst.modelo.tipo, conteudo, resposta)
    nota = 10.0 if correto else 0.0
    status = 'Concluida' if correto else 'Pendente'

    try:
        desemp = Desempenho.query.filter_by(id_aluno=aluno_id, id_atividade=questao_id).first()
        if desemp:
            desemp.nota, desemp.status = nota, status
        else:
            db.session.add(Desempenho(id_aluno=aluno_id, id_atividade=questao_id, nota=nota, status=status))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500

    return {
        'correto': correto,
        'nota': nota,
        'gabarito': conteudo.get('gabarito'),
        'alternativas': conteudo.get('alternativas', []),
    }, None, 200
