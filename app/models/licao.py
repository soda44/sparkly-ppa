from app.models import db


class Licao(db.Model):
    """Uma lição pertence a um módulo e agrupa questões (instâncias),
    no esquema Módulo → Lição → Questão (mesma ideia do Duolingo)."""
    __tablename__ = 'licao'

    id_licao = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text)
    ordem = db.Column(db.Integer, nullable=False, default=0)
    id_modulo = db.Column(db.Integer, db.ForeignKey('modulo.id_modulo'), nullable=False)

    questoes = db.relationship(
        'QuestaoInstanciada', backref='licao', lazy=True,
        order_by='QuestaoInstanciada.id'
    )

    def __repr__(self):
        return f'<Licao {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id_licao,
            'nome': self.nome,
            'descricao': self.descricao,
            'ordem': self.ordem,
            'id_modulo': self.id_modulo,
            'total_questoes': len(self.questoes),
        }
