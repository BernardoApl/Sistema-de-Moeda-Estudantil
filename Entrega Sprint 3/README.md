# Sistema executável

Aplicação Flask com páginas HTML, persistência SQLite local e suporte a PostgreSQL para implantação. Consulte a [visão da release 2](../README.md) e o [guia de implantação](../Lab04S02/README.md).

## Executar localmente no PowerShell

Na raiz do repositório:

```powershell
cd "Entrega Sprint 3/sistema"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app seed-demo
.\.venv\Scripts\python.exe -m flask --app app creditar-semestre 2026-2
.\.venv\Scripts\python.exe app.py
```

Acesse http://127.0.0.1:5000. O banco SQLite é criado na primeira execução. Para usar o banco local, não defina `DATABASE_URL` nem `POSTGRES_URL_NON_POOLING` no ambiente.

| Perfil | E-mail de demonstração | Senha |
|---|---|---|
| Professor | professor@demo.local | Demo12345! |
| Aluno | aluno@demo.local | Demo12345! |
| Empresa | empresa@demo.local | Demo12345! |

Essas contas são fictícias e não devem ser criadas em produção. O crédito é acumulável e a repetição do mesmo semestre não concede crédito novamente. O semestre é informado como `AAAA-1` ou `AAAA-2`.

## Operação e testes

Para cadastrar um professor vinculado a uma instituição e executar os testes:

```powershell
.\.venv\Scripts\python.exe -m flask --app app cadastrar-professor
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

O comando de cadastro solicita a senha sem exibi-la. CPF e CNPJ novos são validados pelos dígitos verificadores. A empresa pode marcar como utilizado o cupom de sua própria vantagem.

As notificações ficam pendentes até a execução do comando abaixo por um único processo. O envio real exige um provedor SMTP com STARTTLS:

```powershell
$env:SMTP_HOST = "smtp.seu-provedor.com"
$env:SMTP_PORT = "587"
$env:SMTP_USER = "usuario"
$env:SMTP_PASSWORD = "senha-ou-senha-de-aplicativo"
$env:SMTP_FROM = "remetente@exemplo.com"
.\.venv\Scripts\python.exe -m flask --app app enviar-emails
```

Não inclua credenciais no repositório. O teste automatizado de SMTP usa um servidor simulado. Veja também [arquitetura](01_arquitetura_e_persistencia.md) e [validação histórica](03_validacao.md).
