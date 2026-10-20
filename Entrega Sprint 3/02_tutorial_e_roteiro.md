# Tutorial das tecnologias e roteiro de apresentação

## Preparação

Requisito: Python 3.12 ou compatível. Os comandos do README criam um ambiente virtual, instalam Flask 3.1.3 e inicializam o banco. Não é necessário Node, Docker ou servidor de banco. A porta padrão é 5000. Encerre com Ctrl+C.

O `seed-demo` cria apenas contas fictícias e uma instituição. Não sobrescreve contas existentes. O comando `creditar-semestre 2026-2` acrescenta 1.000 moedas por professor apenas uma vez. Para dados institucionais reais, é necessário preparar uma rotina de importação com aprovação da instituição; a carga demo não representa integração institucional.

## Tutorial prático

1. **Flask:** abra `app.py`. A factory configura a aplicação, registra o Blueprint e inicializa o banco. Execute `python app.py` e observe o servidor local.
2. **Controller:** abra `controllers.py`. Mostre `/cadastro/<perfil>` recebendo GET e POST; o POST chama o serviço e redireciona após sucesso.
3. **Jinja:** abra `templates/perfil.html`. Mostre `extends`, loops, campos condicionais por perfil e escape automático dos valores.
4. **DAO/SQLite:** abra `models.py` e `schema.sql`. Explique conexão por requisição, parâmetros `?`, chave estrangeira e tabela única de contas.
5. **Domínio:** abra `services.py`. Mostre `BEGIN IMMEDIATE`, verificação de saldo e gravação conjunta do histórico e notificações.
6. **Testes:** execute `python -m unittest discover -s tests -v`. Mostre banco temporário por teste, caminho feliz e rollback quando uma etapa falha.

## Demonstração funcional

1. Na tela de entrada, cadastre um aluno fictício com todos os campos e selecione PUC Minas. Entre, consulte e altere o cadastro.
2. Saia e entre como `empresa@demo.local`. Cadastre uma vantagem com descrição, foto HTTP(S) acessível e custo 50. Edite a descrição para demonstrar atualização.
3. Saia e entre como `professor@demo.local`. Confira saldo 1.000 (em banco novo), selecione o aluno criado e envie 100 moedas com motivo “Participação na atividade”. Mostre saldo 900 e extrato.
4. Entre como o aluno criado. Confira saldo 100, recebimento e notificação. Resgate a vantagem de 50. Confira saldo 50, cupom e extrato.
5. Entre como empresa. Em Notificações, confira o mesmo código do aluno.
6. Use uma conta fictícia descartável para demonstrar exclusão com confirmação de senha. Não exclua o aluno principal antes de concluir a demonstração.
7. Reexecute o crédito do mesmo semestre e comprove que não há duplicação. Mostre teste de saldo insuficiente sem alteração de banco.

## Envio externo de e-mails

No mesmo terminal, configure `SMTP_HOST`, `SMTP_PORT` (padrão 587), `SMTP_USER`, `SMTP_PASSWORD` e `SMTP_FROM` como variáveis de ambiente, usando credenciais do provedor e destinatários de teste autorizados. Não coloque segredos em arquivos versionados. Execute:

```powershell
.venv\Scripts\python.exe -m flask --app app enviar-emails
```

O comando usa STARTTLS, envia as pendências e marca os registros enviados. Erro interrompe o processamento; execute novamente depois de corrigir a configuração. Há possibilidade de reenvio se o servidor aceitar a mensagem e ocorrer falha antes de marcar o banco. Use apenas um processo de envio por vez. Nenhum envio real foi executado na preparação desta entrega.

## Roteiro de 20 minutos

| Tempo | Conteúdo |
|---|---|
| 0–2 min | Problema, atores e requisitos do enunciado. |
| 2–5 min | Modelos revisados: casos de uso, classes e decisões adicionais. |
| 5–8 min | Arquitetura MVC e ER; correspondência com arquivos reais. |
| 8–12 min | Tutorial Flask, Jinja, DAO e transação no código. |
| 12–17 min | Demonstração dos CRUDs e ciclo professor → aluno → empresa. |
| 17–19 min | Testes, autorização, rollback e crédito idempotente. |
| 19–20 min | Limitações e fechamento. |

Abra `apresentacao.html` no navegador. Use setas para navegar, botão “Mostrar todos” para consulta ou Ctrl+P para imprimir. A apresentação é HTML local, não um arquivo PowerPoint; não exige internet.
