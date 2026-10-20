"""Regras do domínio. Saldos, histórico e notificações são gravados atomicamente."""
import re
import secrets
import sqlite3
from werkzeug.security import generate_password_hash
from models import db, ContaDAO


def positivo(value):
    try:
        if not re.fullmatch(r'[0-9]+', str(value)):
            raise ValueError()
        number = int(value)
        if not 0 < number <= 1000000000:
            raise ValueError()
        return number
    except (ValueError, TypeError):
        raise ValueError('Informe uma quantidade inteira positiva de até 1 bilhão.')


def salvar_conta(data, perfil, id=None):
    if perfil not in ('aluno', 'empresa'):
        raise ValueError('Perfil não permitido para cadastro público.')
    values = {key: data.get(key, '').strip() for key in ('nome','email','documento','rg','endereco','curso','telefone')}
    for field in ('nome','email','documento','endereco') + (('rg','curso') if perfil == 'aluno' else ()):
        if not values[field] or len(values[field]) > 250:
            raise ValueError('Preencha os campos obrigatórios com até 250 caracteres.')
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', values['email']):
        raise ValueError('Informe um e-mail válido.')
    values['email'] = values['email'].lower()
    values['documento'] = re.sub(r'\D', '', values['documento'])
    if len(values['documento']) != (11 if perfil == 'aluno' else 14):
        raise ValueError('CPF deve ter 11 dígitos; CNPJ deve ter 14 dígitos.')
    instituicao = data.get('instituicao_id') if perfil == 'aluno' else None
    if perfil == 'aluno' and not db().execute('SELECT id FROM instituicoes WHERE id=?', (instituicao,)).fetchone():
        raise ValueError('Selecione uma instituição cadastrada.')
    senha = data.get('senha', '')
    if (not id or senha) and len(senha) < 8:
        raise ValueError('A senha deve ter pelo menos 8 caracteres.')
    values['instituicao_id'] = instituicao
    if senha:
        values['senha_hash'] = generate_password_hash(senha)
    try:
        with db():
            if id:
                db().execute('UPDATE contas SET '+','.join(k+'=?' for k in values)+' WHERE id=? AND perfil=? AND ativo=1', (*values.values(), id, perfil))
            else:
                values['perfil'] = perfil
                cursor = db().execute('INSERT INTO contas ('+','.join(values)+') VALUES ('+','.join('?' for _ in values)+')', tuple(values.values()))
                id = cursor.lastrowid
        return id
    except sqlite3.IntegrityError:
        raise ValueError('E-mail ou documento já cadastrado.')


def notificar(conta, assunto, mensagem):
    db().execute('INSERT INTO notificacoes(conta_id,destinatario,assunto,mensagem) VALUES(?,?,?,?)', (conta['id'], conta['email'], assunto, mensagem))


def creditar_semestre(semestre):
    if not re.fullmatch(r'20\d{2}-[12]', semestre):
        raise ValueError('Semestre deve seguir AAAA-1 ou AAAA-2.')
    count = 0
    with db():
        db().execute('BEGIN IMMEDIATE')
        for professor in db().execute("SELECT id FROM contas WHERE perfil='professor' AND ativo=1").fetchall():
            result = db().execute('INSERT OR IGNORE INTO creditos(professor_id,semestre) VALUES(?,?)', (professor['id'], semestre))
            if result.rowcount:
                db().execute('UPDATE contas SET saldo=saldo+1000 WHERE id=?', (professor['id'],))
                count += 1
    return count


def transferir(professor_id, aluno_id, valor, motivo):
    valor = positivo(valor)
    motivo = motivo.strip()
    if not motivo or len(motivo) > 1000:
        raise ValueError('Informe um motivo de até 1.000 caracteres.')
    with db():
        db().execute('BEGIN IMMEDIATE')
        professor, aluno = ContaDAO.obter(professor_id), ContaDAO.obter(aluno_id)
        if not professor or professor['perfil'] != 'professor' or not aluno or aluno['perfil'] != 'aluno':
            raise ValueError('Professor ou aluno inválido.')
        if professor['instituicao_id'] != aluno['instituicao_id']:
            raise ValueError('Selecione um aluno da sua instituição.')
        if professor['saldo'] < valor:
            raise ValueError('Saldo insuficiente.')
        db().execute('UPDATE contas SET saldo=saldo-? WHERE id=?', (valor, professor_id))
        db().execute('UPDATE contas SET saldo=saldo+? WHERE id=?', (valor, aluno_id))
        db().execute('INSERT INTO transferencias(professor_id,aluno_id,valor,motivo) VALUES(?,?,?,?)', (professor_id,aluno_id,valor,motivo))
        notificar(aluno, 'Você recebeu moedas', f'{professor["nome"]} enviou {valor} moedas. Motivo: {motivo}')


def salvar_vantagem(empresa, data, id=None):
    custo = positivo(data.get('custo'))
    descricao, foto = data.get('descricao', '').strip(), data.get('foto', '').strip()
    if not descricao or len(descricao) > 500 or not re.fullmatch(r'https?://[^\s]+', foto):
        raise ValueError('Informe descrição (até 500 caracteres) e URL HTTP(S) da foto.')
    with db():
        if id:
            result = db().execute('UPDATE vantagens SET descricao=?,foto=?,custo=? WHERE id=? AND empresa_id=? AND ativo=1', (descricao,foto,custo,id,empresa))
            if not result.rowcount:
                raise ValueError('Vantagem não encontrada.')
        else:
            db().execute('INSERT INTO vantagens(empresa_id,descricao,foto,custo) VALUES(?,?,?,?)', (empresa,descricao,foto,custo))


def resgatar(aluno_id, vantagem_id):
    with db():
        db().execute('BEGIN IMMEDIATE')
        aluno = ContaDAO.obter(aluno_id)
        vantagem = db().execute('SELECT v.* FROM vantagens v JOIN contas c ON c.id=v.empresa_id WHERE v.id=? AND v.ativo=1 AND c.ativo=1', (vantagem_id,)).fetchone()
        if not aluno or aluno['perfil'] != 'aluno' or not vantagem:
            raise ValueError('Aluno ou vantagem inválido.')
        if aluno['saldo'] < vantagem['custo']:
            raise ValueError('Saldo insuficiente.')
        codigo = secrets.token_hex(12).upper()
        db().execute('UPDATE contas SET saldo=saldo-? WHERE id=?', (vantagem['custo'],aluno_id))
        db().execute('INSERT INTO resgates(aluno_id,vantagem_id,valor,codigo) VALUES(?,?,?,?)', (aluno_id,vantagem_id,vantagem['custo'],codigo))
        mensagem = f'Cupom {codigo}. Vantagem: {vantagem["descricao"]}. Aluno: {aluno["nome"]}. Valor: {vantagem["custo"]} moedas.'
        notificar(aluno, 'Cupom de resgate', mensagem)
        notificar(ContaDAO.obter(vantagem['empresa_id']), 'Conferência de resgate', mensagem)
    return codigo


def excluir_conta(id):
    with db():
        db().execute('UPDATE contas SET ativo=0 WHERE id=?', (id,))
        db().execute('UPDATE vantagens SET ativo=0 WHERE empresa_id=?', (id,))
