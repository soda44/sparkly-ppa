from app.models import db, Aluno
from app.gamificacao import MAX_CORACOES, MISSOES, SPARKS_PARA_RECARGA


def listar_missoes(aluno_id):
    """Lista as missões (metas de XP) com o progresso atual do aluno."""
    aluno = db.session.get(Aluno, aluno_id)
    pontos = aluno.pontos if aluno else 0

    missoes = []
    for meta in MISSOES:
        progresso = min(100.0, round((pontos / meta) * 100, 1)) if meta else 0.0
        missoes.append({
            'titulo': f'Ganhe {meta} XP',
            'meta': meta,
            'pontos_atuais': pontos,
            'progresso': progresso,
            'concluida': pontos >= meta,
        })
    return missoes


def listar_ranking(limite=10):
    """Retorna os alunos com mais pontos (ranking geral), do maior para o menor."""
    alunos = (
        Aluno.query
        .order_by(Aluno.pontos.desc(), Aluno.nome_completo.asc())
        .limit(limite)
        .all()
    )
    return [
        {
            'posicao': i + 1,
            'id': aluno.id_aluno,
            'nome': aluno.nome_social or aluno.nome_completo,
            'usuario': aluno.usuario,
            'pontos': aluno.pontos,
        }
        for i, aluno in enumerate(alunos)
    ]


def recarregar_coracoes(aluno_id):
    """Gasta Sparks para recarregar os corações do aluno até o máximo.

    Retorna (aluno, erro, codigo).
    """
    aluno = db.session.get(Aluno, aluno_id)
    if not aluno:
        return None, 'Aluno não encontrado', 404

    if aluno.coracoes >= MAX_CORACOES:
        return None, 'Seus corações já estão cheios', 400

    if aluno.sparks < SPARKS_PARA_RECARGA:
        return None, 'Sparks insuficientes para recarregar', 400

    try:
        aluno.coracoes = MAX_CORACOES
        aluno.sparks -= SPARKS_PARA_RECARGA
        db.session.commit()
        return aluno, None, 200
    except Exception as e:
        db.session.rollback()
        return None, str(e), 500
