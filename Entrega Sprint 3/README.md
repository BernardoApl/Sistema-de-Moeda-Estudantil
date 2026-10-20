# Entrega Sprint 3 — Lab03S03

## Conteúdo

- `sistema/`: versão final dos CRUDs e protótipo funcional de moedas, vantagens e resgates.
- `01_arquitetura_e_persistencia.md`: arquitetura MVC e correspondência entre modelo/código.
- `02_tutorial_e_roteiro.md`: instalação, tecnologias, demonstração e roteiro de 20 minutos.
- `03_validacao.md`: testes executados, critérios de aceite e limites.
- `apresentacao.html`: slides locais, abertos diretamente no navegador, com navegação por setas e impressão.

## Início rápido (PowerShell)

```powershell
cd "Entrega Sprint 3/sistema"
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m flask --app app seed-demo
.venv\Scripts\python.exe -m flask --app app creditar-semestre 2026-2
.venv\Scripts\python.exe app.py
```

Acesse **http://127.0.0.1:5000**. Contas fictícias:

| Perfil | E-mail | Senha |
|---|---|---|
| Professor | professor@demo.local | Demo12345! |
| Aluno | aluno@demo.local | Demo12345! |
| Empresa | empresa@demo.local | Demo12345! |

Para executar testes:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

SMTP é opcional para executar o protótipo. As notificações ficam disponíveis na interface e persistidas no banco; o envio real requer as variáveis descritas no tutorial. Não publique o ambiente com contas demo. A aplicação se vincula somente a `127.0.0.1`.

Os diagramas finais estão em `../Entrega Sprint 1/diagramas` e o ER em `../Entrega Sprint 2/diagramas`. As três pastas compõem a entrega completa. Apresentação em aula e publicação no GitHub não estão realizadas por estes arquivos.
