# Sistema de Moeda Estudantil

Aplicação acadêmica da PUC Minas para reconhecimento do mérito estudantil. Professores enviam moedas a alunos da sua instituição; alunos consultam o extrato e resgatam vantagens de empresas parceiras.

**Integrantes:** Henrique Pereira, Gabriel Santos, Luiz Henrique Horta e Luiz Felipe Ribeiro.

## Tecnologias e arquitetura

Java 24 (configurado no `pom.xml`), Spring Boot 3.4.5, Spring MVC, Thymeleaf, Spring Security, Spring Data JPA, H2 em desenvolvimento e PostgreSQL no perfil de produção. O Maven gerencia dependências e testes. Controladores recebem requisições, serviços coordenam as regras, repositórios acessam dados e templates compõem as telas.

## Executar em desenvolvimento

Requisitos: JDK 24 compatível e Maven instalado; não há Maven Wrapper no repositório. Na raiz:

```bash
git clone https://github.com/luizfeliperibs/moeda-estudantil-system.git
cd moeda-estudantil-system
mvn spring-boot:run
```

Acesse <http://localhost:8080>. O perfil `dev` está ativo por padrão e usa H2 em memória: os dados são recriados ao reiniciar. A carga inicial inclui instituições e professores com senha `prof123` e logins `milena.adao`, `joao.silva` e `ana.costa`. Alunos e empresas podem ser cadastrados pela interface. As credenciais são apenas para demonstração.

```bash
mvn test
```

## Configuração e limites

- O perfil `prod` usa PostgreSQL; configure `DATABASE_URL` como URL JDBC, `DATABASE_USERNAME` e `DATABASE_PASSWORD`, e selecione o perfil `prod` pela configuração do Spring. O Hibernate está configurado com `ddl-auto=update`; planeje migrações e backup antes de usar dados importantes.
- Atenção: `DataSeeder` não está restrito ao perfil `dev`. Em um banco vazio, ele também cria contas com senha conhecida no perfil `prod`; revise isso antes de uma implantação pública.
- Sem `spring.mail.host`, as mensagens são registradas em log, não enviadas. Configure o provedor SMTP para testar o envio real. O processamento acontece após o commit, sem fila persistente de reenvio.
- As fotos são gravadas em `uploads/`; em hospedagem com disco efêmero, elas podem desaparecer após reinicialização ou nova implantação.
- O agendador credita moedas em 1º de janeiro e 1º de julho enquanto a aplicação estiver em execução. O código atual não registra idempotência por semestre: múltiplas instâncias ou execuções podem duplicar créditos; uma execução perdida não é recuperada automaticamente.

## Documentação

| Material | Arquivo |
|---|---|
| Requisitos e modelos iniciais | [Sprint 1](docs/Sprint1.md) |
| Persistência e CRUDs | [Sprint 2](docs/sprint2.md) e [modelo ER](docs/modelo-er.mmd) |
| Fluxos da release 2 | [Sprint 4](docs/Sprint4.md), [envio](docs/sequencia-envio-moedas.puml), [resgate](docs/sequencia-resgate.puml) e [visão geral](docs/visao-geral-interacao.puml) |
| Revisão e testes | [revisao-e-testes.md](docs/revisao-e-testes.md) |

As fontes PlantUML e Mermaid podem ser renderizadas em ferramentas compatíveis. Consulte o código para confirmar o estado atual dos fluxos.
