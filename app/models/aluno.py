from app.models import db
from app.gamificacao import MAX_CORACOES


class Aluno(db.Model):
    __tablename__ = 'aluno'

    id_aluno = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(150), nullable=False)
    nome_social = db.Column(db.String(150))
    genero = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)

    # Gamificação: pontos (XP) acumulados e corações (vidas) disponíveis.
    pontos = db.Column(db.Integer, nullable=False, default=0)
    coracoes = db.Column(db.Integer, nullable=False, default=MAX_CORACOES)

    # Sparks (⚡): moeda gastável na loja, ganha ao acertar questões.
    sparks = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<Aluno {self.usuario}>'

    def to_dict(self):
        return {
            'id': self.id_aluno,
            'nome': self.nome_completo,
            'email': self.email,
            'usuario': self.usuario,
            'nomeSocial': self.nome_social,
            'genero': self.genero,
            'pontos': self.pontos,
            'coracoes': self.coracoes,
            'coracoesMax': MAX_CORACOES,
            'sparks': self.sparks,
        }
