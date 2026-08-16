from flask import Blueprint, request, jsonify, session
from app.services import auth_service, professor_service

professor_bp = Blueprint('professor', __name__)


def _autenticar():
    """Retorna o professor_id se autenticado, senão None."""
    return session.get('professor_id')


@professor_bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    if not dados or not dados.get('usuario') or not dados.get('senha'):
        return jsonify({'sucesso': False, 'erro': 'Usuário e senha são obrigatórios'}), 400

    professor = auth_service.validar_login_professor(dados['usuario'].strip(), dados['senha'].strip())
    if not professor:
        return jsonify({'sucesso': False, 'erro': 'Usuário ou senha inválidos'}), 401

    session['professor_id'] = professor.id_professor
    session['professor'] = professor.to_dict()

    return jsonify({
        'sucesso': True,
        'professor_id': professor.id_professor,
        'dados': professor.to_dict()
    }), 200


@professor_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('professor_id', None)
    session.pop('professor', None)
    return jsonify({'sucesso': True}), 200


@professor_bp.route('/turmas', methods=['GET'])
def turmas():
    if not _autenticar():
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401
    return jsonify({'sucesso': True, 'turmas': professor_service.listar_turmas(_autenticar())}), 200


@professor_bp.route('/turmas/<int:materia_id>', methods=['GET'])
def turma_detalhe(materia_id):
    if not _autenticar():
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    dados = professor_service.obter_turma(materia_id, _autenticar())
    if not dados:
        return jsonify({'sucesso': False, 'erro': 'Turma não encontrada'}), 404

    return jsonify({'sucesso': True, **dados}), 200


@professor_bp.route('/questoes', methods=['GET'])
def questoes():
    if not _autenticar():
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401
    return jsonify({'sucesso': True, 'questoes': professor_service.listar_questoes()}), 200


@professor_bp.route('/questoes', methods=['POST'])
def criar_questao():
    if not _autenticar():
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    dados = request.get_json()
    if not dados or not dados.get('nome') or not dados.get('tipo') or not dados.get('conteudo'):
        return jsonify({'sucesso': False, 'erro': 'Campos obrigatórios: nome, tipo, conteudo'}), 400

    questao, erro, codigo = professor_service.criar_questao(dados['nome'], dados['tipo'], dados['conteudo'])
    if erro:
        return jsonify({'sucesso': False, 'erro': erro}), codigo

    return jsonify({'sucesso': True, 'questao': questao.to_dict()}), codigo


@professor_bp.route('/questoes/<int:questao_id>', methods=['PUT'])
def editar_questao(questao_id):
    if not _autenticar():
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    dados = request.get_json()
    if not dados:
        return jsonify({'sucesso': False, 'erro': 'Dados inválidos'}), 400

    questao, erro, codigo = professor_service.editar_questao(questao_id, dados)
    if erro:
        return jsonify({'sucesso': False, 'erro': erro}), codigo

    return jsonify({'sucesso': True, 'questao': questao.to_dict()}), codigo


@professor_bp.route('/questoes/<int:questao_id>', methods=['DELETE'])
def deletar_questao(questao_id):
    if not _autenticar():
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    resultado, erro, codigo = professor_service.deletar_questao(questao_id)
    if erro:
        return jsonify({'sucesso': False, 'erro': erro}), codigo

    return jsonify({'sucesso': True}), codigo


@professor_bp.route('/sincronizar-instancias', methods=['POST'])
def sincronizar_instancias():
    if not _autenticar():
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    criadas, erro, codigo = professor_service.sincronizar_instancias()
    if erro:
        return jsonify({'sucesso': False, 'erro': erro}), codigo

    return jsonify({'sucesso': True, 'instancias_criadas': criadas}), codigo
