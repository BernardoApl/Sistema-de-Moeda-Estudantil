# Sistema de Moeda Estudantil

Projeto acadêmico em Python e Flask para reconhecimento do mérito estudantil. Professores distribuem moedas, alunos consultam extratos e resgatam vantagens, e empresas parceiras gerenciam ofertas e conferem cupons.

## Como executar

É necessário ter Python 3.12 (testado), Git e acesso à internet para instalar as dependências. No Linux, o Python precisa incluir o módulo `venv` (em Debian ou Ubuntu, instale o pacote correspondente, como `python3-venv`).

Se baixou o ZIP, extraia-o e abra o terminal na pasta que contém este README; nos comandos abaixo, pule `git clone` e `cd Sistema-de-Moeda-Estudantil`.

### Windows (PowerShell)

Abra o PowerShell na pasta em que deseja guardar o projeto e execute:

```powershell
git clone https://github.com/BernardoApl/Sistema-de-Moeda-Estudantil.git
cd Sistema-de-Moeda-Estudantil
cd "Entrega Sprint 3/sistema"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app seed-demo
.\.venv\Scripts\python.exe -m flask --app app creditar-semestre 2026-2
.\.venv\Scripts\python.exe app.py
```

### Linux

Abra o terminal na pasta em que deseja guardar o projeto e execute:

```bash
git clone https://github.com/BernardoApl/Sistema-de-Moeda-Estudantil.git
cd Sistema-de-Moeda-Estudantil
cd "Entrega Sprint 3/sistema"
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m flask --app app seed-demo
./.venv/bin/python -m flask --app app creditar-semestre 2026-2
./.venv/bin/python app.py
```

### Acesso e contas de demonstração

Acesse **http://127.0.0.1:5000** no navegador e entre com uma das contas fictícias:

| Perfil | E-mail | Senha |
|---|---|---|
| Professor | `professor@demo.local` | `Demo12345!` |
| Aluno | `aluno@demo.local` | `Demo12345!` |
| Empresa | `empresa@demo.local` | `Demo12345!` |

O banco SQLite é criado localmente. Os comandos de demonstração não devem ser usados em produção; o crédito para o mesmo semestre não é repetido. Para encerrar o servidor, pressione `Ctrl+C`. Para abrir novamente, entre na pasta `Entrega Sprint 3/sistema` e execute `.\.venv\Scripts\python.exe app.py` no Windows ou `./.venv/bin/python app.py` no Linux.

Para usar SQLite, deixe as variáveis `DATABASE_URL` e `POSTGRES_URL_NON_POOLING` sem definição no terminal. Se a porta 5000 já estiver em uso, encerre o outro processo antes de iniciar a aplicação.

### Executar os testes

Na pasta `Entrega Sprint 3/sistema`, execute no Windows:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

No Linux:

```bash
./.venv/bin/python -m unittest discover -s tests -v
```

O [guia detalhado](<Entrega Sprint 3/README.md>) inclui pré-cadastro de professores, SMTP e outras instruções. A configuração para nuvem utiliza PostgreSQL. O envio efetivo de e-mails exige SMTP configurado e execução do comando da caixa de saída.

## Entregas

| Etapa | Conteúdo e situação |
|---|---|
| [Release 1 — Sprint 1](<Entrega Sprint 1/README.md>) | Requisitos, histórias de usuário e modelos UML. |
| [Release 1 — Sprint 2](<Entrega Sprint 2/README.md>) | Modelo ER, persistência e versão inicial dos CRUDs. |
| [Release 1 — Sprint 3](<Entrega Sprint 3/README.md>) | Aplicação, arquitetura, testes e material de apresentação. |
| [Release 2 — Lab04S01](Lab04S01/README.md) | Diagramas de sequência, visão geral de interação e evolução dos casos de uso. |
| [Release 2 — Lab04S02](Lab04S02/README.md) | Diagrama e instruções de implantação; endereço publicado retornou erro 500 e precisa de correção e teste PostgreSQL. |
| [Release 2 — Lab04S03](Lab04S03/relatorio.md) | Avaliação crítica e três refatorações propostas; publicação do pull request depende de acesso ao repositório avaliado. |

O [roteiro da apresentação da release 2](Lab04S02/roteiro_apresentacao.md) compara os modelos com a implementação e aponta as verificações ainda necessárias.

O [enunciado da release 1](referencias/enunciado_laboratorio_3.pdf) e as [ferramentas](ferramentas/README.md) complementam a documentação. Os arquivos históricos registram resultados de validações anteriores; consulte suas datas e limitações.

## Integrantes

- Bernardo Augusto Pereira
- Bruno Kenji Fantucci
- João Gabriel
- Murilo Duarte Moura
