from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.materia import Materia
from app.models.modulo import Modulo
from app.models.licao import Licao
from app.models.questao import ModeloQuestao, QuestaoInstanciada
from app.models.desempenho import Desempenho
from app.models.mensagem import Mensagem
from app.models.pet import Pet
