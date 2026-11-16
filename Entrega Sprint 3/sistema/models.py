"""DAO SQLite: conexões por requisição e transações explícitas nos serviços."""
import sqlite3
from pathlib import Path
from flask import current_app, g


def db():
    if 'db' not in g:
        if current_app.config.get('DATABASE_URL'):
            from postgres_db import Postgres
            g.db = Postgres(current_app.config['DATABASE_URL'])
        else:
            g.db = sqlite3.connect(current_app.config['DATABASE'], timeout=15)
            g.db.row_factory = sqlite3.Row
            g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


def close_db(error=None):
    connection = g.pop('db', None)
    if connection is not None:
        connection.close()


def init_db():
    db().executescript(Path(__file__).with_name('schema.sql').read_text(encoding='utf-8'))
    with db():
        if 'utilizado_em' not in {col['name'] for col in db().execute('PRAGMA table_info(resgates)')}:
            db().execute('ALTER TABLE resgates ADD COLUMN utilizado_em TEXT')
        db().execute("INSERT OR IGNORE INTO instituicoes(id,nome) VALUES(1,'PUC Minas')")


class ContaDAO:
    @staticmethod
    def obter(id):
        return db().execute('SELECT * FROM contas WHERE id=? AND ativo=1', (id,)).fetchone()

    @staticmethod
    def por_email(email):
        return db().execute('SELECT * FROM contas WHERE email=? AND ativo=1', (email,)).fetchone()

    @staticmethod
    def alunos(instituicao):
        return db().execute("SELECT id,nome FROM contas WHERE perfil='aluno' AND ativo=1 AND instituicao_id=? ORDER BY nome", (instituicao,)).fetchall()


class VantagemDAO:
    @staticmethod
    def listar(empresa=None):
        sql = 'SELECT v.*, c.nome AS empresa FROM vantagens v JOIN contas c ON c.id=v.empresa_id WHERE v.ativo=1 AND c.ativo=1'
        return db().execute(sql + (' AND empresa_id=?' if empresa else '') + ' ORDER BY v.id DESC', (empresa,) if empresa else ()).fetchall()


def extrato(conta):
    return db().execute('''
        SELECT data_hora, 'Recebimento: ' || motivo AS descricao, valor FROM transferencias WHERE aluno_id=?
        UNION ALL SELECT data_hora, 'Envio: ' || motivo, -valor FROM transferencias WHERE professor_id=?
        UNION ALL SELECT r.data_hora, 'Resgate: ' || v.descricao || ' | Cupom: ' || r.codigo, -r.valor
          FROM resgates r JOIN vantagens v ON v.id=r.vantagem_id WHERE aluno_id=?
        UNION ALL SELECT data_hora, 'Crédito semestral: ' || semestre, valor FROM creditos WHERE professor_id=?
        ORDER BY data_hora DESC
    ''', (conta, conta, conta, conta)).fetchall()
