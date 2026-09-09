from app.models import db


class Modulo(db.Model):
    """Um módulo agrupa lições de uma matéria, no esquema Módulo → Lição → Questão
    (mesma ideia de uma "unidade"/seção do Duolingo)."""
    __tablename__ = 'modulo'

    id_modulo = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text)
    ordem = db.Column(db.Integer, nullable=False, default=0)
    id_materia = db.Column(db.Integer, db.ForeignKey('materia.id_materia'), nullable=False)

    licoes = db.relationship(
        'Licao', backref='modulo', lazy=True,
        order_by='Licao.ordem', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Modulo {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id_modulo,
            'nome': self.nome,
            'descricao': self.descricao,
            'ordem': self.ordem,
            'id_materia': self.id_materia,
            'total_licoes': len(self.licoes),
        }
