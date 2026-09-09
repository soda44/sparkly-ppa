from app.models import db, Aluno, Desempenho, Modulo
from app.services.questao_service import interpolar_enunciado


def _questao_publica(inst, desempenhos, sem_coracoes):
    """Monta o dict público de uma questão instanciada (sem gabarito)."""
    modelo = inst.modelo
    conteudo = dict(modelo.conteudo) if modelo.conteudo else {}
    texto_base = conteudo.get('texto_base', conteudo.get('enunciado', ''))

    conteudo_publico = dict(conteudo)
    conteudo_publico['enunciado'] = interpolar_enunciado(texto_base, inst.valores_variaveis or {})
    conteudo_publico.pop('gabarito', None)
    conteudo_publico.pop('texto_base', None)

    desemp = desempenhos.get(inst.id)
    ja_concluida = bool(desemp and desemp.status == 'Concluida')

    return {
        'id': inst.id,
        'modelo_id': modelo.id,
        'nome': modelo.nome,
        'tipo': modelo.tipo,
        'conteudo': conteudo_publico,
        'ja_respondida': desemp is not None,
        'ja_concluida': ja_concluida,
        'bloqueada': sem_coracoes and not ja_concluida,
    }


def listar_modulos_do_aluno(aluno_id):
    """Lista o percurso completo do aluno no esquema Módulo → Lição → Questão.

    Segue o mesmo princípio do Duolingo: as lições formam uma trilha única
    e sequencial. Uma lição só é desbloqueada quando a lição anterior da
    trilha foi concluída (todas as suas questões acertadas ao menos uma
    vez). A primeira lição do curso já começa desbloqueada.
    """
    aluno = db.session.get(Aluno, aluno_id)
    sem_coracoes = bool(aluno and aluno.coracoes <= 0)
    desempenhos = {d.id_atividade: d for d in Desempenho.query.filter_by(id_aluno=aluno_id).all()}

    modulos = Modulo.query.order_by(Modulo.id_materia, Modulo.ordem, Modulo.id_modulo).all()

    resultado = []
    licao_anterior_completa = True  # a primeira lição da trilha sempre começa destravada

    for modulo in modulos:
        licoes_dict = []
        for licao in sorted(modulo.licoes, key=lambda l: (l.ordem, l.id_licao)):
            questoes = [q for q in licao.questoes if q.modelo]
            total = len(questoes)
            concluidas = sum(
                1 for q in questoes
                if desempenhos.get(q.id) and desempenhos[q.id].status == 'Concluida'
            )
            licao_completa = total > 0 and concluidas == total
            desbloqueada = licao_anterior_completa or licao_completa

            licoes_dict.append({
                'id': licao.id_licao,
                'nome': licao.nome,
                'descricao': licao.descricao,
                'ordem': licao.ordem,
                'id_modulo': modulo.id_modulo,
                'total_questoes': total,
                'questoes_concluidas': concluidas,
                'completa': licao_completa,
                'desbloqueada': desbloqueada,
            })
            licao_anterior_completa = licao_completa

        total_licoes = len(licoes_dict)
        licoes_completas = sum(1 for l in licoes_dict if l['completa'])

        resultado.append({
            'id': modulo.id_modulo,
            'nome': modulo.nome,
            'descricao': modulo.descricao,
            'ordem': modulo.ordem,
            'id_materia': modulo.id_materia,
            'total_licoes': total_licoes,
            'licoes_completas': licoes_completas,
            'completo': total_licoes > 0 and licoes_completas == total_licoes,
            'licoes': licoes_dict,
        })

    return resultado


def listar_questoes_da_licao(aluno_id, licao_id):
    """Lista as questões de uma lição específica, já interpoladas e sem gabarito.

    Retorna (dados, erro, codigo). A lição precisa existir e estar
    desbloqueada na trilha do aluno.
    """
    modulos = listar_modulos_do_aluno(aluno_id)

    licao_info = None
    for modulo in modulos:
        for licao in modulo['licoes']:
            if licao['id'] == licao_id:
                licao_info = licao
                break
        if licao_info:
            break

    if not licao_info:
        return None, 'Lição não encontrada', 404

    if not licao_info['desbloqueada']:
        return None, 'Esta lição ainda está bloqueada. Conclua a lição anterior primeiro.', 403

    from app.models import Licao  # import local para evitar ciclo
    licao = db.session.get(Licao, licao_id)

    aluno = db.session.get(Aluno, aluno_id)
    sem_coracoes = bool(aluno and aluno.coracoes <= 0)
    desempenhos = {d.id_atividade: d for d in Desempenho.query.filter_by(id_aluno=aluno_id).all()}

    questoes = [
        _questao_publica(inst, desempenhos, sem_coracoes)
        for inst in sorted(licao.questoes, key=lambda q: q.id)
        if inst.modelo
    ]

    return {
        'licao': {
            'id': licao.id_licao,
            'nome': licao.nome,
            'descricao': licao.descricao,
            'id_modulo': licao.id_modulo,
        },
        'questoes': questoes,
    }, None, 200
