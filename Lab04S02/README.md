# Lab04S02 — Implantação

O repositório contém a configuração Flask para Vercel e um adaptador PostgreSQL. O [diagrama de implantação em PlantUML](implantacao.puml) descreve a topologia pretendida; não comprova que os serviços estejam ativos. A aplicação também funciona localmente com SQLite, conforme o [guia de execução](../Entrega%20Sprint%203/README.md).

## Preparação da nuvem

1. Crie um banco PostgreSQL dedicado e preserve sua URL de conexão como segredo. Em um banco novo e vazio, aplique uma única vez `Entrega Sprint 3/sistema/schema_postgres.sql` com um cliente PostgreSQL. O script cria as tabelas e uma instituição inicial; não é uma migração idempotente e não deve ser reaplicado sobre um banco existente.
2. Importe o repositório na Vercel, selecione `Entrega Sprint 3/sistema` como diretório raiz do projeto e configure `DATABASE_URL` com a URL PostgreSQL e `SECRET_KEY` com um valor aleatório, longo e estável. Restrinja o acesso às credenciais. O arquivo `vercel.json` identifica o framework Flask.
3. Implante e verifique a URL gerada: cadastro e login, persistência após nova sessão e fluxos de transferência e resgate. Verifique também os logs e a conexão segura ao banco conforme o provedor. A chave de sessão precisa ser igual entre instâncias; sem `SECRET_KEY`, a aplicação gera uma chave temporária e sessões podem ser invalidadas.
4. Execute os comandos administrativos em um ambiente de operação com o mesmo `DATABASE_URL` e dependências instaladas: `flask --app app cadastrar-professor`, `flask --app app creditar-semestre AAAA-N` e, quando configurado SMTP, `flask --app app enviar-emails`. A execução desses comandos não é automática pela função web. Use apenas um processo de envio de e-mails por vez.

Não execute `seed-demo` em produção. O código não inicializa o esquema PostgreSQL automaticamente. Não há migração automática dos dados do SQLite. Faça backup antes de alterar um banco existente.

## Situação e validação pendente

Há código e configuração de implantação, mas este repositório não registra URL de produção, evidência de implantação ativa nem resultado de teste integrado com PostgreSQL. É necessário registrar esses dados após verificar o ambiente real. O envio SMTP real e o agendamento operacional de créditos e notificações também dependem de configuração externa.
