import secrets
from functools import wraps
from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash
from models import db, ContaDAO, VantagemDAO, extrato
from services import salvar_conta, transferir, salvar_vantagem, resgatar, excluir_conta

routes = Blueprint('web', __name__)


@routes.before_request
def preparar():
    session.setdefault('csrf', secrets.token_hex(24))
    g.conta = ContaDAO.obter(session.get('conta_id'))
    if request.method == 'POST' and not secrets.compare_digest(session['csrf'], request.form.get('csrf', '')):
        abort(400, 'Formulário expirado. Atualize a página.')


def acesso(*perfis):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not g.conta:
                return redirect(url_for('web.login'))
            if perfis and g.conta['perfil'] not in perfis:
                abort(403)
            return fn(*args, **kwargs)
        return wrapped
    return decorator


@routes.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        conta = ContaDAO.por_email(request.form.get('email', '').strip())
        if conta and check_password_hash(conta['senha_hash'], request.form.get('senha', '')):
            session.clear()
            session['conta_id'] = conta['id']
            return redirect(url_for('web.index'))
        flash('E-mail ou senha inválidos.', 'erro')
    return render_template('login.html')


@routes.post('/sair')
def sair():
    session.clear()
    return redirect(url_for('web.login'))


@routes.route('/cadastro/<perfil>', methods=['GET','POST'])
def cadastro(perfil):
    if perfil not in ('aluno','empresa'):
        abort(404)
    if request.method == 'POST':
        try:
            salvar_conta(request.form, perfil)
            flash('Cadastro concluído. Entre com seu e-mail e senha.', 'sucesso')
            return redirect(url_for('web.login'))
        except ValueError as error:
            flash(str(error), 'erro')
    return render_template('perfil.html', perfil=perfil, dados=request.form, editando=False, instituicoes=db().execute('SELECT * FROM instituicoes').fetchall())


@routes.route('/perfil', methods=['GET','POST'])
@acesso('aluno','empresa')
def perfil():
    if request.method == 'POST':
        try:
            salvar_conta(request.form, g.conta['perfil'], g.conta['id'])
            flash('Perfil atualizado.', 'sucesso')
            return redirect(url_for('web.perfil'))
        except ValueError as error:
            flash(str(error), 'erro')
    return render_template('perfil.html', perfil=g.conta['perfil'], dados=request.form if request.method=='POST' else g.conta, editando=True, instituicoes=db().execute('SELECT * FROM instituicoes').fetchall())


@routes.post('/perfil/excluir')
@acesso('aluno','empresa')
def excluir():
    if not check_password_hash(g.conta['senha_hash'], request.form.get('senha','')):
        flash('Senha incorreta. A conta não foi excluída.', 'erro')
        return redirect(url_for('web.perfil'))
    excluir_conta(g.conta['id'])
    session.clear()
    flash('Conta desativada. O histórico foi preservado.', 'sucesso')
    return redirect(url_for('web.login'))


@routes.get('/')
@acesso()
def index():
    if g.conta['perfil'] in ('aluno','empresa'):
        return redirect(url_for('web.perfil'))
    return render_template('inicial.html')
