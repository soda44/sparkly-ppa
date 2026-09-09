from app.models import db
from app.gamificacao import PET_NOME_PADRAO, PET_COR_PADRAO, nivel_do_pet


class Pet(db.Model):
    """Bichinho de estimação do aluno (mascote do Sparkly).

    Cada aluno tem um único pet, criado automaticamente no primeiro acesso.
    O aluno pode dar um nome a ele e comprar novas cores na loja usando
    Sparks. As cores já compradas ficam salvas em `cores_desbloqueadas`
    (lista separada por vírgulas) e podem ser trocadas livremente depois.
    """
    __tablename__ = 'pet'

    id_pet = db.Column(db.Integer, primary_key=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey('aluno.id_aluno'), nullable=False, unique=True)

    nome = db.Column(db.String(30), nullable=False, default=PET_NOME_PADRAO)
    cor_atual = db.Column(db.String(30), nullable=False, default=PET_COR_PADRAO)
    cores_desbloqueadas = db.Column(db.String(255), nullable=False, default=PET_COR_PADRAO)

    aluno = db.relationship('Aluno', backref=db.backref('pet', uselist=False))

    def lista_cores_desbloqueadas(self):
        return [c for c in (self.cores_desbloqueadas or '').split(',') if c]

    def desbloquear_cor(self, cor):
        cores = self.lista_cores_desbloqueadas()
        if cor not in cores:
            cores.append(cor)
            self.cores_desbloqueadas = ','.join(cores)

    def __repr__(self):
        return f'<Pet {self.nome} ({self.cor_atual})>'

    def to_dict(self):
        pontos = self.aluno.pontos if self.aluno else 0
        return {
            'id': self.id_pet,
            'nome': self.nome,
            'corAtual': self.cor_atual,
            'coresDesbloqueadas': self.lista_cores_desbloqueadas(),
            'nivel': nivel_do_pet(pontos),
        }
