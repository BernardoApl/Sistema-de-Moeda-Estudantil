# Avaliação crítica — projeto Moeda Estudantil

Projeto avaliado: https://github.com/luizfeliperibs/moeda-estudantil-system, commit `c364d8b`. As observações abaixo distinguem leitura do código de comportamento efetivamente testado.

## Resultado da execução

**O projeto funcionou localmente.** A aplicação iniciou com o perfil de desenvolvimento e banco H2 em memória. Foi possível entrar como professor e acessar as páginas de envio de moedas e extrato. Os **55 testes da versão avaliada passaram**, sem falhas ou erros.

O README original não foi suficiente para reproduzir a execução sozinho: foi necessário obter no código as credenciais e detalhes de configuração. Também foi preciso localizar uma instalação do Maven e ajustar a execução dos testes ao Java 25 disponível na máquina. Não foram verificados PostgreSQL, envio real de e-mails ou implantação em nuvem.

## Arquitetura e tecnologias

O projeto usa Java, Spring Boot, MVC/Thymeleaf, Spring Security, Spring Data JPA, H2 no perfil de desenvolvimento e PostgreSQL no perfil de produção. Controladores delegam a serviços e repositórios; `TransacaoService` coordena as operações transacionais e publica eventos de notificação após o commit. A separação facilita localizar os fluxos, embora algumas responsabilidades de construção e de manipulação de saldo estejam concentradas no serviço.

O agendador chama `ProfessorService.creditarSemestre()` em janeiro e julho. O método soma moedas sem registrar o semestre processado: uma execução repetida ou múltiplas instâncias podem duplicar o crédito, e períodos em que o processo estava desligado não são recuperados automaticamente. Eventos de e-mail após o commit não constituem uma fila persistente; uma falha pode deixar a notificação sem reenvio. `DataSeeder` não possui restrição de perfil e cria professores com senha conhecida quando não há instituições, inclusive em um banco de produção vazio. O upload local também depende de armazenamento persistente.

## Organização e configuração

Há pastas de código, testes e documentação, mas arquivos gerados em `target/` estão versionados, dificultando a revisão e podendo ficar desatualizados em relação às fontes. O README original descreve a execução como futura, usa placeholders no clone, afirma Java 25 enquanto o `pom.xml` configura Java 24, e contém referências antigas ou inexistentes. Não há Maven Wrapper; a máquina precisa ter Maven instalado. O perfil `dev` usa H2 em memória e reinicia os dados ao reiniciar a aplicação.

Na máquina de avaliação foi encontrado Java 25 e Maven em cache, mas não Maven no PATH. A primeira tentativa com Java 25 teve erros de instrumentação do Mockito. Com `-Dnet.bytebuddy.experimental=true`, uma execução incremental falhou porque havia um template antigo em `target/`; após `mvn clean test`, os **57 testes passaram** (incluindo dois testes adicionados à proposta). Essa execução não substitui a verificação com JDK 24 nem testa PostgreSQL ou SMTP reais.

### Execução da versão original

O projeto foi executado no Windows com Java 25 e Maven 3.9.11, usando o perfil `dev` e H2 em memória. Como o comando `mvn` não estava disponível no terminal, foi necessário localizar uma instalação do Maven e executá-la pelo caminho completo. O README não informa o endereço de clone preenchido, as credenciais de demonstração nem todas as instruções de configuração; foi necessário consultar o código para encontrá-las.

Após reconstruir os artefatos, a aplicação iniciou na porta de teste 8092. As páginas de login e cadastro de aluno e empresa responderam com HTTP 200. O professor de demonstração conseguiu autenticar; as páginas de envio e extrato responderam com HTTP 200. A tentativa de acessar a área de vantagens do aluno como professor retornou HTTP 403, conforme a restrição de perfil esperada.

Após reconstruir o projeto, os **55 testes passaram, sem falhas ou erros**. No Java 25, foi necessário usar a opção `-Dnet.bytebuddy.experimental=true` para o Mockito funcionar. O projeto configura Java 24 no Maven, mas essa versão não estava instalada para comparação.

Essa verificação confirma a inicialização local e esses acessos específicos. Não comprova, por si só, entrega de e-mails, implantação em nuvem ou persistência PostgreSQL. O banco de desenvolvimento é descartado ao encerrar o processo.

## Diagramas e alinhamento

- O arquivo `docs/visao-geral-interacao.puml` usa `split` para extrato e envio/resgate, representando fluxos paralelos, embora sejam escolhas independentes do usuário. Os `ref` aparecem como texto em ações de um diagrama de atividades, não como quadros de referência de interação UML.
- `docs/sequencia-resgate.puml` usa `par` para os dois e-mails, mas `NotificacaoListener.aoResgatar` chama `emailService.enviar` sequencialmente. O desenho também não demonstra o cenário de vantagem inexistente.
- `docs/modelo-er.mmd` não representa a exigência de que cada linha de `usuario` tenha exatamente um subtipo; as cardinalidades opcionais, isoladamente, permitem nenhum subtipo. A coluna `foto_url` representa um caminho de arquivo local gerido por `FotoStorageService`, não necessariamente uma URL externa.
- O diagrama de sequência do envio descreve verificações centrais, porém omite alternativas para professor ou aluno inexistente e falha de entrega de e-mail. O evento depois do commit não garante entrega externa.

## Proposta de refatoração GRASP

As alterações propostas são locais, ainda não aceitas pela equipe proprietária. O arquivo de patch acompanha este relatório; ele inclui também a atualização do README e testes.

1. **Criação do envio — Creator:** antes, `TransacaoService` criava `EnvioMoedas` vazio e atribuía professor, aluno, valor e mensagem em quatro chamadas. Depois, `new EnvioMoedas(professor, aluno, valor, mensagem)` concentra a montagem e normalização no objeto que guarda esses dados. A validação do formulário e a transação continuam no serviço.
2. **Criação do resgate — Creator:** antes, o serviço criava `ResgateVantagem` vazio e preenchia seus quatro campos separadamente. Depois, o construtor recebe aluno, vantagem, valor histórico e código em conjunto. Isso torna explícito o conjunto necessário para registrar um resgate; a geração e unicidade do código permanecem no serviço e no banco.
3. **Crédito do professor — Information Expert:** antes, `ProfessorService` lia o saldo e usava `setSaldo(saldo + valor)`. Depois, `Professor.creditar(valor)` atualiza o próprio saldo com `Math.addExact`, detectando overflow; o serviço continua responsável por selecionar professores e controlar a transação. Isso não resolve a idempotência semestral, que exige persistência e coordenação próprias.

## Situação dos pull requests

Ainda não há PR aberto. A integração GitHub retornou 403 ao consultar a permissão de colaboração, e a tentativa de criar uma branch foi rejeitada. Para publicar as alterações, será necessário acesso de escrita a uma branch ou um fork autorizado e uma nova tentativa de criação do PR contra `main`.
