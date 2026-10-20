"""Operações administrativas locais; não expostas como rotas públicas."""
import os
import smtplib
import ssl
from email.message import EmailMessage
import click
from werkzeug.security import generate_password_hash
from models import db
from services import creditar_semestre


def register_commands(app):
    @app.cli.command('seed-demo')
    def seed_demo():
        """Cria contas fictícias para demonstração, sem sobrescrever dados."""
        with db():
            for perfil, nome, email, documento in [
                ('professor','Professor Demo','professor@demo.local','00000000001'),
                ('aluno','Aluno Demo','aluno@demo.local','00000000002'),
                ('empresa','Cantina Demo','empresa@demo.local','00000000000003')]:
                db().execute('''INSERT OR IGNORE INTO contas(perfil,nome,email,documento,senha_hash,instituicao_id,rg,endereco,curso,departamento)
                    VALUES(?,?,?,?,?,?,?,?,?,?)''', (perfil,nome,email,documento,generate_password_hash('Demo12345!'),None if perfil=='empresa' else 1,'DEMO','Campus de demonstração','Engenharia de Software','Computação'))
        click.echo('Contas demo criadas. Senha: Demo12345! Execute creditar-semestre AAAA-N antes de enviar moedas.')

    @app.cli.command('creditar-semestre')
    @click.argument('semestre')
    def credito(semestre):
        """Credita 1.000 moedas uma única vez por professor e semestre."""
        try:
            click.echo(f'{creditar_semestre(semestre)} professor(es) creditado(s).')
        except ValueError as error:
            raise click.ClickException(str(error))

    @app.cli.command('enviar-emails')
    def enviar_emails():
        """Envia a caixa de saída via SMTP com STARTTLS; use um único worker."""
        keys = ('SMTP_HOST','SMTP_USER','SMTP_PASSWORD','SMTP_FROM')
        if any(not os.environ.get(key) for key in keys):
            raise click.ClickException('Configure SMTP_HOST, SMTP_USER, SMTP_PASSWORD e SMTP_FROM.')
        with smtplib.SMTP(os.environ['SMTP_HOST'], int(os.environ.get('SMTP_PORT','587')), timeout=20) as smtp:
            smtp.starttls(context=ssl.create_default_context())
            smtp.login(os.environ['SMTP_USER'], os.environ['SMTP_PASSWORD'])
            for item in db().execute('SELECT * FROM notificacoes WHERE enviado=0 ORDER BY id').fetchall():
                msg = EmailMessage()
                msg['From'], msg['To'], msg['Subject'] = os.environ['SMTP_FROM'], item['destinatario'], item['assunto']
                msg['Message-ID'] = f'<moeda-{item["id"]}@{os.environ["SMTP_FROM"].split("@")[-1]}>'
                msg.set_content(item['mensagem'])
                smtp.send_message(msg)
                with db():
                    db().execute('UPDATE notificacoes SET enviado=1 WHERE id=?', (item['id'],))
                click.echo(f'Notificação {item["id"]} enviada.')
