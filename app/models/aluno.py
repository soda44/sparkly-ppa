from app.models import db


class Aluno(db.Model):
    __tablename__ = 'aluno'

    id_aluno = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Aluno {self.usuario}>'

    def to_dict(self):
        return {
            'id': self.id_aluno,
            'nome': self.nome_completo,
            'email': self.email,
            'usuario': self.usuario
        }
