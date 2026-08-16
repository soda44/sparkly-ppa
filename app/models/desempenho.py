from app.models import db


class Desempenho(db.Model):
    __tablename__ = 'desempenho'

    id_desempenho = db.Column(db.Integer, primary_key=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey('aluno.id_aluno'), nullable=False)
    id_atividade = db.Column(db.Integer, db.ForeignKey('questao_instanciada.id'))
    nota = db.Column(db.Numeric(5, 2))
    status = db.Column(db.String(50))

    aluno = db.relationship('Aluno', backref='desempenhos')

    def __repr__(self):
        return f'<Desempenho aluno={self.id_aluno}>'
