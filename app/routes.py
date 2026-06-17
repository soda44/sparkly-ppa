from flask import render_template, request, jsonify, session
from app import app, db
from app.auth import validar_login, validar_login_professor, obter_dados_aluno
from app.models import Aluno, Professor, Materia, Licao, ModeloQuestao, QuestaoInstanciada, Desempenho
import json

# ==================== PÁGINAS ====================

@app.route('/')
@app.route('/tela-inicial')
def telaInicial():
    return render_template("tela-inicial.html")

@app.route('/cadastro')
def cadastro():
    return render_template("cadastro.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/aluno-dashboard')
def alunoDashboard():
    return render_template("aluno-dashboard.html")

@app.route('/aluno-trilhas')
def alunoTrilhas():
    return render_template("aluno-trilhas.html")

@app.route('/aluno-desafio')
def alunoDesafio():
    return render_template("aluno-desafio.html")

@app.route('/professor-dashboard')
def professorDashboard():
    return render_template("professor-dashboard.html")


@app.route('/api/professor/sincronizar-instancias', methods=['POST'])
def api_sincronizar_instancias():
    """Cria questao_instanciada para todo modelo_questao que ainda nao tem nenhuma."""
    professor_id = session.get('professor_id')
    if not professor_id:
        return jsonify({'sucesso': False, 'erro': 'Nao autenticado'}), 401
    try:
        modelos = ModeloQuestao.query.all()
        criadas = 0
        for modelo in modelos:
            existe = QuestaoInstanciada.query.filter_by(modelo_id=modelo.id).first()
            if not existe:
                inst = QuestaoInstanciada(modelo_id=modelo.id, valores_variaveis={})
                db.session.add(inst)
                criadas += 1
        db.session.commit()
        return jsonify({'sucesso': True, 'instancias_criadas': criadas}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500



@app.route('/api/professor/questoes/<int:questao_id>', methods=['PUT'])
def api_professor_editar_questao(questao_id):
    professor_id = session.get('professor_id')
    if not professor_id:
        return jsonify({'sucesso': False, 'erro': 'Nao autenticado'}), 401

    questao = ModeloQuestao.query.get(questao_id)
    if not questao:
        return jsonify({'sucesso': False, 'erro': 'Questao nao encontrada'}), 404

    dados = request.get_json()
    if not dados:
        return jsonify({'sucesso': False, 'erro': 'Dados invalidos'}), 400

    try:
        if dados.get('nome'):
            questao.nome = dados['nome'].strip()
        if dados.get('tipo'):
            questao.tipo = dados['tipo'].strip()
        if dados.get('conteudo') is not None:
            questao.conteudo = dados['conteudo']
        db.session.commit()
        return jsonify({'sucesso': True, 'questao': questao.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

# ==================== API ALUNO ====================

@app.route('/api/login', methods=['POST'])
def api_login():
    dados = request.get_json()
    if not dados or not dados.get('usuario') or not dados.get('senha'):
        return jsonify({'sucesso': False, 'erro': 'Usuário e senha são obrigatórios'}), 400

    usuario = dados.get('usuario').strip()
    senha = dados.get('senha').strip()
    aluno = validar_login(usuario, senha)

    if not aluno:
        return jsonify({'sucesso': False, 'erro': 'Usuário ou senha inválidos'}), 401

    session['aluno_id'] = aluno.id_aluno
    session['aluno'] = aluno.to_dict()
    dados_completos = obter_dados_aluno(aluno.id_aluno)

    return jsonify({'sucesso': True, 'aluno_id': aluno.id_aluno, 'dados': dados_completos}), 200


@app.route('/api/aluno', methods=['GET'])
def api_obter_aluno():
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    dados = obter_dados_aluno(aluno_id)
    if not dados:
        return jsonify({'sucesso': False, 'erro': 'Aluno não encontrado'}), 404

    return jsonify({'sucesso': True, 'dados': dados}), 200


@app.route('/api/cadastro', methods=['POST'])
def api_cadastro():
    dados = request.get_json()
    if not dados or not all([dados.get('usuario'), dados.get('senha'), dados.get('email'), dados.get('nome')]):
        return jsonify({'sucesso': False, 'erro': 'Todos os campos são obrigatórios'}), 400

    usuario = dados.get('usuario').strip()
    email = dados.get('email').strip()
    nome = dados.get('nome').strip()
    senha = dados.get('senha').strip()

    if Aluno.query.filter_by(usuario=usuario).first():
        return jsonify({'sucesso': False, 'erro': 'Usuário já existe'}), 409

    if Aluno.query.filter_by(email=email).first():
        return jsonify({'sucesso': False, 'erro': 'Email já cadastrado'}), 409

    try:
        novo_aluno = Aluno(nome_completo=nome, email=email, usuario=usuario, senha=senha)
        db.session.add(novo_aluno)
        db.session.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Cadastro realizado com sucesso!', 'aluno': novo_aluno.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


# ==================== API PROFESSOR ====================

@app.route('/api/professor/login', methods=['POST'])
def api_professor_login():
    dados = request.get_json()
    if not dados or not dados.get('usuario') or not dados.get('senha'):
        return jsonify({'sucesso': False, 'erro': 'Usuário e senha são obrigatórios'}), 400

    usuario = dados.get('usuario').strip()
    senha = dados.get('senha').strip()
    professor = validar_login_professor(usuario, senha)

    if not professor:
        return jsonify({'sucesso': False, 'erro': 'Usuário ou senha inválidos'}), 401

    session['professor_id'] = professor.id_professor
    session['professor'] = professor.to_dict()

    return jsonify({'sucesso': True, 'professor_id': professor.id_professor, 'dados': professor.to_dict()}), 200


@app.route('/api/professor/logout', methods=['POST'])
def api_professor_logout():
    session.pop('professor_id', None)
    session.pop('professor', None)
    return jsonify({'sucesso': True}), 200


@app.route('/api/professor/turmas', methods=['GET'])
def api_professor_turmas():
    professor_id = session.get('professor_id')
    if not professor_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    materias = Materia.query.filter_by(id_professor=professor_id).all()

    turmas = []
    for m in materias:
        # contar alunos através de desempenhos ligados a lições desta matéria
        licao_ids = [l.id_licao for l in m.licoes]
        total_alunos = 0
        if licao_ids:
            total_alunos = db.session.query(Desempenho.id_aluno)\
                .filter(Desempenho.id_atividade.in_(licao_ids))\
                .distinct().count()

        turmas.append({
            'id': m.id_materia,
            'nome': m.nome_materia,
            'numero_sala': m.numero_sala,
            'total_licoes': len(m.licoes),
            'total_alunos': total_alunos
        })

    return jsonify({'sucesso': True, 'turmas': turmas}), 200


@app.route('/api/professor/turmas/<int:materia_id>', methods=['GET'])
def api_professor_turma_detalhe(materia_id):
    professor_id = session.get('professor_id')
    if not professor_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    materia = Materia.query.filter_by(id_materia=materia_id, id_professor=professor_id).first()
    if not materia:
        return jsonify({'sucesso': False, 'erro': 'Turma não encontrada'}), 404

    licoes = [l.to_dict() for l in materia.licoes]

    # alunos com desempenho nessa matéria
    licao_ids = [l.id_licao for l in materia.licoes]
    alunos_data = []
    if licao_ids:
        desempenhos = Desempenho.query.filter(Desempenho.id_atividade.in_(licao_ids)).all()
        aluno_ids = list(set([d.id_aluno for d in desempenhos]))
        for aid in aluno_ids:
            aluno = Aluno.query.get(aid)
            if aluno:
                notas = [float(d.nota) for d in desempenhos if d.id_aluno == aid and d.nota]
                media = round(sum(notas)/len(notas), 2) if notas else 0
                alunos_data.append({
                    'id': aluno.id_aluno,
                    'nome': aluno.nome_completo,
                    'usuario': aluno.usuario,
                    'media': media,
                    'atividades': len([d for d in desempenhos if d.id_aluno == aid])
                })

    return jsonify({
        'sucesso': True,
        'turma': materia.to_dict(),
        'licoes': licoes,
        'alunos': alunos_data
    }), 200


@app.route('/api/professor/questoes', methods=['GET'])
def api_professor_questoes():
    professor_id = session.get('professor_id')
    if not professor_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    questoes = ModeloQuestao.query.all()
    return jsonify({'sucesso': True, 'questoes': [q.to_dict() for q in questoes]}), 200


@app.route('/api/professor/questoes', methods=['POST'])
def api_professor_criar_questao():
    professor_id = session.get('professor_id')
    if not professor_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    dados = request.get_json()
    if not dados or not dados.get('nome') or not dados.get('tipo') or not dados.get('conteudo'):
        return jsonify({'sucesso': False, 'erro': 'Campos obrigatórios: nome, tipo, conteudo'}), 400

    try:
        nova_questao = ModeloQuestao(
            nome=dados['nome'].strip(),
            tipo=dados['tipo'].strip(),
            conteudo=dados['conteudo']
        )
        db.session.add(nova_questao)
        db.session.flush()  # gera o id sem commitar ainda

        # Cria automaticamente uma instância para que os alunos vejam a questão.
        # valores_variaveis vazio = sem interpolação, enunciado fixo.
        instancia = QuestaoInstanciada(
            modelo_id=nova_questao.id,
            valores_variaveis={}
        )
        db.session.add(instancia)
        db.session.commit()

        return jsonify({'sucesso': True, 'questao': nova_questao.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


@app.route('/api/professor/questoes/<int:questao_id>', methods=['DELETE'])
def api_professor_deletar_questao(questao_id):
    professor_id = session.get('professor_id')
    if not professor_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    questao = ModeloQuestao.query.get(questao_id)
    if not questao:
        return jsonify({'sucesso': False, 'erro': 'Questão não encontrada'}), 404

    try:
        db.session.delete(questao)
        db.session.commit()
        return jsonify({'sucesso': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


# ==================== API ALUNO — QUESTÕES ====================

def _interpolar_enunciado(texto_base, valores_variaveis):
    """Substitui {{ variavel }} pelo valor correspondente em valores_variaveis."""
    if not texto_base or not valores_variaveis:
        return texto_base or ''
    resultado = texto_base
    for chave, valor in valores_variaveis.items():
        resultado = resultado.replace('{{' + chave + '}}', str(valor))
        resultado = resultado.replace('{{ ' + chave + ' }}', str(valor))
    return resultado


@app.route('/api/aluno/questoes', methods=['GET'])
def api_aluno_questoes():
    """Lista questões instanciadas com enunciado interpolado."""
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    # Buscar quais questões este aluno já respondeu (via desempenho)
    respondidas = set()
    desempenhos = Desempenho.query.filter_by(id_aluno=aluno_id).all()
    for d in desempenhos:
        respondidas.add(d.id_atividade)

    # Buscar as questões instanciadas e seus modelos
    instanciadas = QuestaoInstanciada.query.all()

    resultado = []
    for inst in instanciadas:
        modelo = inst.modelo  # relacionamento backref
        if not modelo:
            continue

        conteudo = dict(modelo.conteudo) if modelo.conteudo else {}

        # Interpolação: substitui {{ variavel }} no texto_base pelos valores_variaveis
        texto_base = conteudo.get('texto_base', conteudo.get('enunciado', ''))
        enunciado_final = _interpolar_enunciado(texto_base, inst.valores_variaveis or {})

        conteudo_publico = dict(conteudo)
        conteudo_publico['enunciado'] = enunciado_final
        # Não expor gabarito para o aluno
        conteudo_publico.pop('gabarito', None)
        conteudo_publico.pop('texto_base', None)

        resultado.append({
            'id': inst.id,
            'modelo_id': modelo.id,
            'nome': modelo.nome,
            'tipo': modelo.tipo,
            'conteudo': conteudo_publico,
            'ja_respondida': inst.id in respondidas,
        })

    return jsonify({'sucesso': True, 'questoes': resultado}), 200


@app.route('/api/aluno/questoes/<int:questao_id>/responder', methods=['POST'])
def api_aluno_responder(questao_id):
    """Aluno submete resposta para uma questão instanciada."""
    aluno_id = session.get('aluno_id')
    if not aluno_id:
        return jsonify({'sucesso': False, 'erro': 'Não autenticado'}), 401

    dados = request.get_json()
    resposta = dados.get('resposta')
    if resposta is None:
        return jsonify({'sucesso': False, 'erro': 'Resposta é obrigatória'}), 400

    # Busca pela QuestaoInstanciada (id vem do instanciada.id)
    inst = QuestaoInstanciada.query.get(questao_id)
    if not inst or not inst.modelo:
        return jsonify({'sucesso': False, 'erro': 'Questão não encontrada'}), 404

    questao = inst.modelo
    conteudo = questao.conteudo
    gabarito = conteudo.get('gabarito')
    tipo = questao.tipo

    # Avaliar resposta
    # tipo usa hifem conforme enum do banco: 'multipla-escolha', 'multi-selecao', 'entrada-texto'
    correto = False
    if tipo in ('multipla-escolha', 'multi-selecao', 'multipla_escolha', 'verdadeiro_falso'):
        try:
            correto = (int(resposta) == int(gabarito))
        except (ValueError, TypeError):
            correto = False
    else:
        # entrada-texto / dissertativa: comparacao simples
        correto = str(resposta).strip().lower() == str(gabarito).strip().lower()

    nota = 10.0 if correto else 0.0
    # Valores que o ENUM do banco aceita: 'Concluida' ou 'Pendente'
    status = 'Concluida' if correto else 'Pendente'

    try:
        # Salvar ou atualizar desempenho
        desemp = Desempenho.query.filter_by(id_aluno=aluno_id, id_atividade=questao_id).first()
        if desemp:
            desemp.nota = nota
            desemp.status = status
        else:
            desemp = Desempenho(
                id_aluno=aluno_id,
                id_atividade=questao_id,
                nota=nota,
                status=status
            )
            db.session.add(desemp)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

    resposta_retorno = {
        'sucesso': True,
        'correto': correto,
        'nota': nota,
        'gabarito': gabarito,
        'alternativas': conteudo.get('alternativas', [])
    }
    return jsonify(resposta_retorno), 200
