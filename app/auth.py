from app.models import db, Aluno, Professor, Desempenho, Licao
from sqlalchemy import func


def validar_login(usuario, senha):
    """Valida credenciais do aluno."""
    aluno = Aluno.query.filter_by(usuario=usuario).first()
    if not aluno:
        return None
    if aluno.senha != senha:
        return None
    return aluno


def validar_login_professor(usuario, senha):
    """Valida credenciais do professor."""
    professor = Professor.query.filter_by(usuario=usuario).first()
    if not professor:
        return None
    if professor.senha != senha:
        return None
    return professor


def obter_dados_aluno(aluno_id):
    """Obtém dados completos do aluno incluindo desempenho e lições."""
    aluno = Aluno.query.get(aluno_id)
    if not aluno:
        return None

    desempenhos = Desempenho.query.filter_by(id_aluno=aluno_id).all()
    licoes = Licao.query.all()

    notas = [float(d.nota) for d in desempenhos if d.nota]
    media_notas = sum(notas) / len(notas) if notas else 0

    return {
        'aluno': aluno.to_dict(),
        'desempenho': {
            'atividades_completas': len([d for d in desempenhos if d.status == 'concluido']),
            'media_notas': round(media_notas, 2),
            'total_atividades': len(desempenhos)
        },
        'licoes': [
            {'id': l.id_licao, 'tipo': l.tipo, 'descricao': l.descricao}
            for l in licoes
        ]
    }
