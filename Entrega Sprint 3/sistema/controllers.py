import secrets
from functools import wraps
from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash
from models import db, ContaDAO, VantagemDAO, extrato
from services import salvar_conta, transferir, salvar_vantagem, resgatar, excluir_conta, utilizar_cupom

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
    cupons = db().execute('''SELECT r.id, r.codigo, r.utilizado_em, v.descricao, c.nome AS aluno
        FROM resgates r JOIN vantagens v ON v.id=r.vantagem_id JOIN contas c ON c.id=r.aluno_id
        WHERE v.empresa_id=? ORDER BY r.id DESC''', (g.conta['id'],)).fetchall() if g.conta['perfil']=='empresa' else []
    return render_template('index.html', movimentos=extrato(g.conta['id']), alunos=ContaDAO.alunos(g.conta['instituicao_id']) if g.conta['perfil']=='professor' else [], vantagens=VantagemDAO.listar(g.conta['id'] if g.conta['perfil']=='empresa' else None), cupons=cupons)


@routes.post('/cupons/<int:id>/utilizar')
@acesso('empresa')
def marcar_cupom(id):
    try:
        utilizar_cupom(g.conta['id'], id)
        flash('Cupom marcado como utilizado.', 'sucesso')
    except ValueError as error:
        flash(str(error), 'erro')
    return redirect(url_for('web.index'))


@routes.post('/transferir')
@acesso('professor')
def enviar():
    try:
        transferir(g.conta['id'], request.form.get('aluno_id'), request.form.get('valor'), request.form.get('motivo',''))
        flash('Moedas enviadas. Notificação registrada.', 'sucesso')
    except ValueError as error:
        flash(str(error), 'erro')
    return redirect(url_for('web.index'))


@routes.route('/vantagens/nova', methods=['GET','POST'])
@routes.route('/vantagens/<int:id>/editar', methods=['GET','POST'])
@acesso('empresa')
def vantagem(id=None):
    dados = db().execute('SELECT * FROM vantagens WHERE id=? AND empresa_id=? AND ativo=1', (id,g.conta['id'])).fetchone() if id else {}
    if id and not dados:
        abort(404)
    if request.method == 'POST':
        try:
            salvar_vantagem(g.conta['id'],request.form,id)
            flash('Vantagem salva.', 'sucesso')
            return redirect(url_for('web.index'))
        except ValueError as error:
            flash(str(error), 'erro')
        dados = request.form
    return render_template('vantagem.html', dados=dados)


@routes.post('/vantagens/<int:id>/excluir')
@acesso('empresa')
def excluir_vantagem(id):
    with db():
        result = db().execute('UPDATE vantagens SET ativo=0 WHERE id=? AND empresa_id=?', (id,g.conta['id']))
        if not result.rowcount:
            abort(404)
    flash('Vantagem desativada.', 'sucesso')
    return redirect(url_for('web.index'))


@routes.post('/vantagens/<int:id>/resgatar')
@acesso('aluno')
def resgate(id):
    try:
        codigo = resgatar(g.conta['id'],id)
        flash('Resgate concluído. Cupom: '+codigo, 'sucesso')
    except ValueError as error:
        flash(str(error), 'erro')
    return redirect(url_for('web.index'))


@routes.get('/notificacoes')
@acesso()
def notificacoes():
    itens = db().execute('SELECT * FROM notificacoes WHERE conta_id=? ORDER BY id DESC', (g.conta['id'],)).fetchall()
    return render_template('notificacoes.html', itens=itens)
