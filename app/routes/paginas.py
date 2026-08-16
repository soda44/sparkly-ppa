from flask import Blueprint, render_template

paginas_bp = Blueprint('paginas', __name__)


@paginas_bp.route('/')
@paginas_bp.route('/tela-inicial')
def tela_inicial():
    return render_template("tela-inicial.html")


@paginas_bp.route('/cadastro')
def cadastro():
    return render_template("cadastro.html")


@paginas_bp.route('/login')
def login():
    return render_template("login.html")


@paginas_bp.route('/aluno-dashboard')
def aluno_dashboard():
    return render_template("aluno-dashboard.html")


@paginas_bp.route('/aluno-trilhas')
def aluno_trilhas():
    return render_template("aluno-trilhas.html")


@paginas_bp.route('/aluno-desafio')
def aluno_desafio():
    return render_template("aluno-desafio.html")


@paginas_bp.route('/professor-dashboard')
def professor_dashboard():
    return render_template("professor-dashboard.html")
