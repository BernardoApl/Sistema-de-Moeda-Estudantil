# Entrega Sprint 2 — Lab03S02

Versão executável inicial dos CRUDs de aluno e empresa, com front-end HTML, controladores Flask e persistência SQLite via DAO.

## Conteúdo

- `diagramas/04_modelo_er.puml` e `.svg`: modelo entidade-relacionamento completo.
- `01_persistencia.md`: estratégia de acesso, restrições e transações.
- `sistema/`: versão inicial executável, com cadastro, login, consulta, alteração e desativação da própria conta.

## Executar no PowerShell

```powershell
cd "Entrega Sprint 2/sistema"
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m flask --app app seed-demo
.venv\Scripts\python.exe app.py
```

Acesse http://127.0.0.1:5000. E-mails de demonstração: `aluno@demo.local` e `empresa@demo.local`; senha `Demo12345!`. As contas são fictícias. Para testar criação, use os links na tela de login.

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

O esquema completo antecipa as entidades da sprint 3; a interface desta versão expõe apenas os CRUDs. A evolução funcional está em `../Entrega Sprint 3/sistema`. Cada versão usa seu próprio banco local, criado na primeira execução. Não execute ambas na mesma porta simultaneamente.

Versões organizadas nesta entrega, sem atribuição de datas históricas de desenvolvimento.
