"""Adaptador PostgreSQL para a implantação serverless."""
import re
import sqlite3
import psycopg
from psycopg.rows import dict_row


class Row(dict):
    def __getitem__(self, key):
        return list(self.values())[key] if isinstance(key, int) else super().__getitem__(key)


class Result:
    def __init__(self, cursor, lastrowid=None):
        self.cursor, self.lastrowid = cursor, lastrowid
        self.rowcount = cursor.rowcount

    def fetchone(self):
        row = self.cursor.fetchone()
        return Row(row) if row is not None else None

    def fetchall(self):
        return [Row(row) for row in self.cursor.fetchall()]

    def __iter__(self):
        return iter(self.fetchall())


class Postgres:
    def __init__(self, url):
        self.connection = psycopg.connect(url, autocommit=True, row_factory=dict_row, prepare_threshold=None)

    def execute(self, sql, args=()):
        if sql.strip().upper() == 'BEGIN IMMEDIATE':
            # Serialize balance mutations, including concurrent credits, transfers and redemptions.
            sql = 'SELECT pg_advisory_xact_lock(184037210)'
        ignore = bool(re.match(r'\s*INSERT OR IGNORE', sql, re.I))
        sql = re.sub(r'INSERT OR IGNORE', 'INSERT', sql, flags=re.I)
        if ignore:
            sql = sql.rstrip().rstrip(';') + ' ON CONFLICT DO NOTHING'
        returns_id = bool(re.match(r'\s*INSERT INTO contas\s*\(', sql, re.I)) and not ignore
        if returns_id:
            sql = sql.rstrip().rstrip(';') + ' RETURNING id'
        sql = sql.replace('?', '%s')
        try:
            cursor = self.connection.execute(sql, args)
            lastrowid = cursor.fetchone()['id'] if returns_id else None
            return Result(cursor, lastrowid)
        except psycopg.IntegrityError as error:
            raise sqlite3.IntegrityError(str(error)) from error

    def __enter__(self):
        self.transaction = self.connection.transaction()
        self.transaction.__enter__()
        return self

    def __exit__(self, *args):
        return self.transaction.__exit__(*args)

    def close(self):
        self.connection.close()
