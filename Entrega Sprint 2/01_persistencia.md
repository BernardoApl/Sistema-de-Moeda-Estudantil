# Modelo ER e estratégia de persistência

Foi escolhido o padrão DAO com o módulo `sqlite3` da biblioteca padrão Python. O Flask gerencia uma conexão por contexto de requisição. O banco é criado por `schema.sql`; o caminho é configurável por `create_app`. Consultas usam parâmetros `?`, sem interpolar entradas do usuário em SQL.

## Dicionário de dados

| Tabela | Chave / relações | Responsabilidade e restrições |
|---|---|---|
| instituicoes | PK id | Nome único; lista previamente cadastrada. |
| contas | PK id; FK instituicao_id | Nome, email único, senha_hash, documento único, perfil, RG, endereço, curso, departamento, telefone, saldo >= 0, ativo. Instituição obrigatória para aluno/professor. |
| vantagens | PK id; FK empresa_id -> contas | Descrição, foto URL, custo > 0 e ativo. Serviço/controlador verificam perfil e propriedade. |
| transferencias | PK id; FKs professor_id/aluno_id -> contas | Valor > 0, motivo não vazio, data UTC; perfis e instituição validados no serviço. |
| creditos | PK id; FK professor_id -> contas | Valor fixo 1000, semestre, data; par professor/semestre único. |
| resgates | PK id; FKs aluno_id/vantagem_id | Código único, valor histórico > 0 e data UTC. |
| notificacoes | PK id; FK conta_id -> contas | Destinatário, assunto, mensagem, data e indicador de envio. Destinatário é preservado mesmo se o cadastro mudar. |

O modelo é físico: `perfil` realiza os subtipos do modelo conceitual. As FKs apontam para contas, portanto o tipo do destinatário/proprietário é uma invariável da camada de serviço, não uma garantia isolada do banco. Não há ORM.

## Fluxo de acesso

1. Formulário HTML envia POST para o controlador.
2. Controlador verifica sessão, perfil e token CSRF.
3. Serviço valida dados e regras de negócio.
4. DAO/conexão executa SQL parametrizado em transação.
5. Controlador redireciona e renderiza dados atualizados no template.

Contas são lidas por `ContaDAO`; catálogo por `VantagemDAO`. Escritas transacionais e consultas simples ficam próximas dos serviços/controladores, usando a conexão centralizada. O código não afirma implementar um repositório separado para cada entidade.

## Consistência

`PRAGMA foreign_keys=ON` é ativado em cada conexão. Movimentações executam `BEGIN IMMEDIATE`: a verificação de saldo e as alterações ficam sob o mesmo bloqueio de escrita. Débito, crédito, histórico e notificações confirmam juntos. Exceção causa rollback. O worker SMTP é posterior ao commit.

Saldo é um agregado persistido; créditos, transferências e resgates são o histórico. Não se editam movimentações na interface. Exclusões lógicas evitam apagar esse histórico. O schema não deve ser manipulado diretamente por usuários finais.

## Reprodução e manutenção

Banco `sistema.sqlite3` não é versionado. Faça cópia de segurança antes de qualquer intervenção. O esquema é idempotente para criação; esta entrega não tem migrações de bancos legados. A evolução da sprint 2 para 3 mantém o mesmo esquema. SQLite foi escolhido para demonstração local, sem dependência de servidor de banco.
