from flask import Blueprint, request, jsonify, session
from app.services import auth_service, aluno_service, questao_service

aluno_bp = Blueprint('aluno', __name__)

GENEROS_VALIDOS = {
    'masculino': 'Masculino',
    'feminino': 'Feminino',
    'nao-binario': 'Não-binário',
    'prefiro-nao-dizer': 'Prefiro não dizer',
}


@aluno_bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    if not dados or not dados.get('usuario') or not dados.get('senha'):
        return jsonify({'sucesso': False, 'erro': 'Usuário e senha são obrigatórios'}), 400

    aluno = auth_service.validar_login(dados['usuario'].strip(), dados['senha'].strip())
    if not aluno:
        return jsonify({'sucesso': False, 'erro': 'Usuário ou senha inválidos'}), 401

    session['aluno_id'] = aluno.id_aluno
    session['aluno'] = aluno.to_dict()

    return jsonify({
        'sucesso': True,
        'aluno_id': aluno.id_aluno,
        'dados': aluno_service.obter_dados_aluno(aluno.id_aluno)
    }), 200


@aluno_bp.route('/aluno', methods=['GET'])
def obter_aluno():
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    dados = aluno_service.obter_dados_aluno(aluno_id)
    if not dados:
        return jsonify({'sucesso': False, 'erro': 'Aluno não encontrado'}), 404

    return jsonify({'sucesso': True, 'dados': dados}), 200


@aluno_bp.route('/cadastro', methods=['POST'])
def cadastro():
    dados = request.get_json()
    if not dados or not all([dados.get('usuario'), dados.get('senha'), dados.get('email'), dados.get('nome')]):
        return jsonify({'sucesso': False, 'erro': 'Todos os campos são obrigatórios'}), 400

    genero_opcao = (dados.get('genero') or '').strip()
    if not genero_opcao:
        return jsonify({'sucesso': False, 'erro': 'Selecione um gênero'}), 400

    if genero_opcao == 'personalizado':
        genero = (dados.get('generoPersonalizado') or '').strip()
        if not genero:
            return jsonify({'sucesso': False, 'erro': 'Informe o gênero personalizado'}), 400
    elif genero_opcao in GENEROS_VALIDOS:
        genero = GENEROS_VALIDOS[genero_opcao]
    else:
        return jsonify({'sucesso': False, 'erro': 'Gênero inválido'}), 400

    nome_social = None
    if dados.get('usaNomeSocial'):
        nome_social = (dados.get('nomeSocial') or '').strip()
        if not nome_social:
            return jsonify({'sucesso': False, 'erro': 'Informe o nome social'}), 400

    aluno, erro, codigo = aluno_service.cadastrar_aluno(
        nome=dados['nome'].strip(),
        email=dados['email'].strip(),
        usuario=dados['usuario'].strip(),
        senha=dados['senha'].strip(),
        genero=genero,
        nome_social=nome_social,
    )
    if erro:
        return jsonify({'sucesso': False, 'erro': erro}), codigo

    return jsonify({
        'sucesso': True,
        'mensagem': 'Cadastro realizado com sucesso!',
        'aluno': aluno.to_dict()
    }), codigo


@aluno_bp.route('/aluno/questoes', methods=['GET'])
def questoes():
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    return jsonify({
        'sucesso': True,
        'questoes': questao_service.listar_questoes_do_aluno(aluno_id)
    }), 200


@aluno_bp.route('/aluno/questoes/<int:questao_id>/responder', methods=['POST'])
def responder(questao_id):
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    dados = request.get_json()
    resposta = dados.get('resposta') if dados else None
    if resposta is None:
        return jsonify({'sucesso': False, 'erro': 'Resposta é obrigatória'}), 400

    resultado, erro, codigo = questao_service.registrar_resposta(aluno_id, questao_id, resposta)
    if erro:
        return jsonify({'sucesso': False, 'erro': erro}), codigo

    return jsonify({'sucesso': True, **resultado}), codigo
