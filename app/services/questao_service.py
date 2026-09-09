from app.models import db, Aluno, Desempenho, ModeloQuestao, QuestaoInstanciada
from app.gamificacao import MAX_CORACOES, PONTOS_POR_QUESTAO, SPARKS_POR_QUESTAO, nivel_do_pet


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
    """Lista as questões instanciadas com enunciado interpolado e gabarito oculto.

    Cada questão indica se já foi respondida, se já foi concluída (acertada)
    e se está bloqueada por falta de corações (vidas) — questões já
    concluídas nunca ficam bloqueadas, pois podem ser praticadas de graça.
    """
    aluno = db.session.get(Aluno, aluno_id)
    sem_coracoes = bool(aluno and aluno.coracoes <= 0)

    desempenhos = {d.id_atividade: d for d in Desempenho.query.filter_by(id_aluno=aluno_id).all()}

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

        desemp = desempenhos.get(inst.id)
        ja_concluida = bool(desemp and desemp.status == 'Concluida')

        resultado.append({
            'id': inst.id,
            'modelo_id': modelo.id,
            'nome': modelo.nome,
            'tipo': modelo.tipo,
            'conteudo': conteudo_publico,
            'ja_respondida': desemp is not None,
            'ja_concluida': ja_concluida,
            'bloqueada': sem_coracoes and not ja_concluida,
        })

    return resultado


def registrar_resposta(aluno_id, questao_id, resposta):
    """Avalia a resposta, atualiza a gamificação (pontos/corações) e grava o desempenho.

    Regras de gamificação (inspiradas no modelo de vidas do Duolingo):
    - Uma questão já concluída (acertada antes) pode ser "praticada" de graça:
      não consome corações mesmo se errada, e se acertada de novo devolve
      1 coração (até o máximo) além dos pontos.
    - Uma questão nova (nunca concluída) consome 1 coração se for errada, e
      não pode ser respondida se o aluno estiver sem corações.
    - Toda resposta correta concede PONTOS_POR_QUESTAO pontos (XP) e
      SPARKS_POR_QUESTAO Sparks (⚡), a moeda gastável na loja.

    Retorna (resultado, erro, codigo).
    """
    inst = db.session.get(QuestaoInstanciada, questao_id)
    if not inst or not inst.modelo:
        return None, 'Questão não encontrada', 404

    aluno = db.session.get(Aluno, aluno_id)
    desemp = Desempenho.query.filter_by(id_aluno=aluno_id, id_atividade=questao_id).first()
    em_pratica = bool(desemp and desemp.status == 'Concluida')

    if aluno and aluno.coracoes <= 0 and not em_pratica:
        return None, 'Você está sem corações. Aguarde a recarga ou visite a loja.', 403

    conteudo = inst.modelo.conteudo
    correto = avaliar_resposta(inst.modelo.tipo, conteudo, resposta)
    nota = 10.0 if correto else 0.0
    pontos_ganhos = 0
    sparks_ganhos = 0
    nivel_pet_anterior = nivel_do_pet(aluno.pontos)['nivel'] if aluno else None

    try:
        if correto:
            if desemp:
                desemp.nota, desemp.status = nota, 'Concluida'
            else:
                db.session.add(Desempenho(id_aluno=aluno_id, id_atividade=questao_id, nota=nota, status='Concluida'))

            if aluno:
                pontos_ganhos = PONTOS_POR_QUESTAO
                sparks_ganhos = SPARKS_POR_QUESTAO
                aluno.pontos += pontos_ganhos
                aluno.sparks += sparks_ganhos
                if em_pratica:
                    aluno.coracoes = min(aluno.coracoes + 1, MAX_CORACOES)
        elif not em_pratica:
            # Só grava/perde coração em tentativas de questões ainda não concluídas.
            if desemp:
                desemp.nota, desemp.status = nota, 'Pendente'
            else:
                db.session.add(Desempenho(id_aluno=aluno_id, id_atividade=questao_id, nota=nota, status='Pendente'))
            if aluno:
                aluno.coracoes = max(aluno.coracoes - 1, 0)
        # Se em_pratica e errou: não altera desempenho nem corações, só não ganha pontos.

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500

    nivel_pet_info = nivel_do_pet(aluno.pontos) if aluno else None
    pet_subiu_nivel = bool(
        nivel_pet_info and nivel_pet_anterior is not None
        and nivel_pet_info['nivel'] > nivel_pet_anterior
    )

    return {
        'correto': correto,
        'nota': nota,
        'gabarito': conteudo.get('gabarito'),
        'alternativas': conteudo.get('alternativas', []),
        'em_pratica': em_pratica,
        'pontos_ganhos': pontos_ganhos,
        'pontos_totais': aluno.pontos if aluno else None,
        'sparks_ganhos': sparks_ganhos,
        'sparks_totais': aluno.sparks if aluno else None,
        'coracoes': aluno.coracoes if aluno else None,
        'coracoes_max': MAX_CORACOES,
        'pet_nivel': nivel_pet_info,
        'pet_subiu_nivel': pet_subiu_nivel,
    }, None, 200
