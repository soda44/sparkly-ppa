from app.models import db


class ModeloQuestao(db.Model):
    __tablename__ = 'modelo_questao'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(256), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    conteudo = db.Column(db.JSON, nullable=False)

    questoes_instanciadas = db.relationship('QuestaoInstanciada', backref='modelo', lazy=True)

    def __repr__(self):
        return f'<ModeloQuestao {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'conteudo': self.conteudo
        }


class QuestaoInstanciada(db.Model):
    __tablename__ = 'questao_instanciada'

    id = db.Column(db.Integer, primary_key=True)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo_questao.id'))
    valores_variaveis = db.Column(db.JSON)
    id_licao = db.Column(db.Integer, db.ForeignKey('licao.id_licao'))

    def __repr__(self):
        return f'<QuestaoInstanciada {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'modelo_id': self.modelo_id,
            'valores_variaveis': self.valores_variaveis,
            'id_licao': self.id_licao,
        }
