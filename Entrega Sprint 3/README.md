cd "Entrega Sprint 3/sistema"

python -m venv .venv

.\.venv\Scripts\python.exe -m pip install -r requirements.txt

.\.venv\Scripts\python.exe -m flask --app app seed-demo

.\.venv\Scripts\python.exe -m flask --app app creditar-semestre 2026-2

.\.venv\Scripts\python.exe app.py

Senhas:
| Perfil | E-mail | Senha |
|---|---|---|
| Professor | professor@demo.local | Demo12345! |
| Aluno | aluno@demo.local | Demo12345! |
| Empresa | empresa@demo.local | Demo12345! |

Para cadastrar um professor da instituição, execute dentro de `Entrega Sprint 3/sistema`:

```powershell
.\.venv\Scripts\python.exe -m flask --app app cadastrar-professor
```

O comando solicita os dados e a senha inicial sem exibi-la. Depois, o professor pode acessar o sistema com o e-mail e a senha cadastrados. Para conceder moedas, execute o comando `creditar-semestre` com o semestre desejado.


### Cupons e documentos

CPF e CNPJ informados em novos cadastros ou altera??es s?o validados pelos d?gitos verificadores. Na ?rea da empresa, confira o c?digo apresentado pelo aluno e marque o cupom correspondente como utilizado. A data ? registrada e apenas a empresa respons?vel pela vantagem pode efetuar a marca??o.

### Envio de e-mails

Configure as vari?veis de ambiente do provedor SMTP com STARTTLS e execute um ?nico processo de envio:

```powershell
$env:SMTP_HOST = "smtp.seu-provedor.com"
$env:SMTP_PORT = "587"
$env:SMTP_USER = "usuario"
$env:SMTP_PASSWORD = "senha-ou-senha-de-aplicativo"
$env:SMTP_FROM = "remetente@exemplo.com"
.\.venv\Scripts\python.exe -m flask --app app enviar-emails
```

Use credenciais reais apenas no ambiente local e n?o as inclua no reposit?rio. O envio real depende de um provedor configurado; a su?te usa SMTP simulado.
