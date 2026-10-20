# Arquitetura e persistência

## MVC na implementação

| Camada | Arquivo | Papel |
|---|---|---|
| View | templates/*.html; static/style.css | HTML sem lógica de banco; formulários e leitura dos dados apresentados pelo controlador. |
| Controller | controllers.py | Rotas, sessão, CSRF, perfil, propriedade, tratamento de erros de domínio e redirecionamento. |
| Model / serviços | services.py | Cadastro, transferências, resgates, crédito semestral, notificações e exclusão lógica. |
| Model / DAO | models.py | Conexão, ContaDAO, VantagemDAO, extrato e inicialização. |
| Model / armazenamento | schema.sql; SQLite | Integridade referencial, unicidade, histórico e saldos. |
| Composição | app.py | Factory configurável, registro de rotas e comandos, fechamento da conexão. |
| Operação | commands.py | Carga demo, crédito semestral e processamento SMTP. |

Não há uma API REST separada: o navegador se comunica com o back-end por formulários HTTP e recebe HTML renderizado com Jinja. Isso atende à comunicação front-end/back-end solicitada. Flask é um framework de aplicação web; Jinja renderiza a View; SQLite persiste os dados; Werkzeug calcula/verifica hashes das senhas.

## Relação com o modelo

`ContaAcesso` e os três subtipos são representados por linhas de `contas` com `perfil`. Instituição é `instituicoes`; Vantagem é `vantagens`; TransferenciaMoedas é `transferencias`; Resgate é `resgates`; CreditoSemestral é `creditos`; Notificacao é `notificacoes`. Os modelos de domínio são conceituais; o diagrama inclui o mapeamento para os DAOs/funções usados no código.

## Transação de envio

`POST /transferir` → autorização professor → `transferir()` → bloqueio de escrita → valida perfis/instituição/saldo/motivo → debita professor → credita aluno → registra transferência → grava notificação → commit → redirecionamento ao extrato.

## Transação de resgate

`POST /vantagens/<id>/resgatar` → autorização aluno → `resgatar()` → bloqueio de escrita → valida vantagem/empresa ativas e saldo → debita aluno → registra preço e código → grava mensagens para aluno e empresa → commit. SMTP não participa da transação financeira.

## CRUDs e autorização

| Operação | Aluno | Empresa |
|---|---|---|
| Criar | /cadastro/aluno | /cadastro/empresa |
| Consultar | GET /perfil (própria conta) | GET /perfil (própria conta) |
| Atualizar | POST /perfil | POST /perfil |
| Excluir | POST /perfil/excluir + senha | POST /perfil/excluir + senha |

O identificador da conta é obtido da sessão, não do formulário. Professores só entram por pré-cadastro. Não há painel administrativo global, pois o enunciado não o exige. A leitura do CRUD é a consulta do próprio cadastro; a lista de alunos do professor mostra apenas ID/nome dos alunos ativos da instituição.

## Evolução entre sprints

S1 define requisitos e modelos. S2 entrega esquema, conexão/DAO, autenticação e CRUDs com páginas simples. S3 preserva os CRUDs, acrescenta os fluxos de negócio e interface de extratos/vantagens/notificações. As versões foram organizadas agora; não se fabrica cronologia de commits nem participação semanal.
