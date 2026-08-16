from app.models import db


class Licao(db.Model):
    __tablename__ = 'licao'

    id_licao = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text)
    nota = db.Column(db.Numeric(5, 2))
    id_materia = db.Column(db.Integer, db.ForeignKey('materia.id_materia'))

    def __repr__(self):
        return f'<Licao {self.id_licao}>'

    def to_dict(self):
        return {
            'id': self.id_licao,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'nota': float(self.nota) if self.nota else None,
            'id_materia': self.id_materia
        }
