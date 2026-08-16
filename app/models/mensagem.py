from datetime import datetime

from app.models import db


class Mensagem(db.Model):
    __tablename__ = 'mensagem'

    id_mensagem = db.Column(db.Integer, primary_key=True)
    tipo_remetente = db.Column(db.String(50))
    id_remetente = db.Column(db.Integer)
    tipo_destinatario = db.Column(db.String(50))
    id_destinatario = db.Column(db.Integer)
    conteudo = db.Column(db.Text)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Mensagem {self.id_mensagem}>'
