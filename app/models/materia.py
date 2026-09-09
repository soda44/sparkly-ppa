from app.models import db


class Materia(db.Model):
    __tablename__ = 'materia'

    id_materia = db.Column(db.Integer, primary_key=True)
    nome_materia = db.Column(db.String(100), nullable=False)
    numero_sala = db.Column(db.String(20))
    id_professor = db.Column(db.Integer, db.ForeignKey('professor.id_professor'))

    modulos = db.relationship(
        'Modulo', backref='materia', lazy=True,
        order_by='Modulo.ordem', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Materia {self.nome_materia}>'

    def to_dict(self):
        return {
            'id': self.id_materia,
            'nome': self.nome_materia,
            'numero_sala': self.numero_sala,
            'id_professor': self.id_professor
        }
