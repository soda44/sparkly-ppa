from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


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


class Materia(db.Model):
    __tablename__ = 'materia'

    id_materia = db.Column(db.Integer, primary_key=True)
    nome_materia = db.Column(db.String(100), nullable=False)
    numero_sala = db.Column(db.String(20))
    id_professor = db.Column(db.Integer, db.ForeignKey('professor.id_professor'))

    licoes = db.relationship('Licao', backref='materia', lazy=True)

    def __repr__(self):
        return f'<Materia {self.nome_materia}>'

    def to_dict(self):
        return {
            'id': self.id_materia,
            'nome': self.nome_materia,
            'numero_sala': self.numero_sala,
            'id_professor': self.id_professor
        }


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

    def __repr__(self):
        return f'<QuestaoInstanciada {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'modelo_id': self.modelo_id,
            'valores_variaveis': self.valores_variaveis
        }


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
