from app.models import db


class Professor(db.Model):
    __tablename__ = 'professor'

    id_professor = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(100))
    usuario = db.Column(db.String(50))
    senha = db.Column(db.String(255))

    materias = db.relationship('Materia', backref='professor', lazy=True)

    def __repr__(self):
        return f'<Professor {self.nome_completo}>'

    def to_dict(self):
        return {
            'id': self.id_professor,
            'nome': self.nome_completo,
            'email': self.email,
            'usuario': self.usuario
        }
