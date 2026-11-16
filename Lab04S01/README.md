# Lab04S01 · Sistema de Moeda Estudantil

Entrega com dez diagramas de sequência, uma Visão Geral de Interação e o código do pré-cadastro institucional de professores. A base é o commit `1ddc782` da branch `main`. Comparei as pastas `Entrega Sprint 2/sistema` e `Entrega Sprint 3/sistema` e usei o modelo de casos de uso da Sprint 1 para conferir a cobertura.

## Diagramas de sequência

Cada sequência detalha a ordem das mensagens entre os participantes de um fluxo. As operações HTTP privadas partem de uma sessão válida. Os POSTs passam pela proteção CSRF. Os desenhos mostram as verificações centrais de cada caso e agrupam chamadas de apoio para manter a leitura. Os fragmentos `alt` separam resultados alternativos, `opt` representa comportamento condicional e `loop` marca repetições.

| ID | O que o diagrama mostra | Arquivos |
|---|---|---|
| **SD01 · Autenticação** | O controlador procura uma conta ativa, verifica o hash da senha e cria a sessão. Credenciais inválidas levam de volta ao formulário. | [PlantUML](diagramas/SD01-autenticacao.puml) · [SVG](diagramas/SD01-autenticacao.svg) |
| **SD02 · Cadastro e perfil** | Reúne o cadastro público, a consulta e a alteração da própria conta. Na desativação, a senha é confirmada e a sessão é encerrada. | [PlantUML](diagramas/SD02-cadastro-e-perfil.puml) · [SVG](diagramas/SD02-cadastro-e-perfil.svg) |
| **SD03 · Pré-cadastro institucional** | O operador cadastra o professor da lista da instituição. O serviço cria ou reutiliza a instituição e grava a conta na mesma transação. | [PlantUML](diagramas/SD03-pre-cadastro-professor.puml) · [SVG](diagramas/SD03-pre-cadastro-professor.svg) |
| **SD04 · Crédito semestral** | O comando percorre professores ativos e acrescenta 1.000 moedas apenas quando insere um crédito novo para aquele professor e semestre. | [PlantUML](diagramas/SD04-credito-semestral.puml) · [SVG](diagramas/SD04-credito-semestral.svg) |
| **SD05 · Envio de moedas** | Valida quantidade, motivo, vínculo institucional e saldo. Os dois saldos, o lançamento e o aviso são gravados na mesma transação. | [PlantUML](diagramas/SD05-enviar-moedas.puml) · [SVG](diagramas/SD05-enviar-moedas.svg) |
| **SD06 · Painel** | O controlador consulta os dados e a visão mostra saldo, extrato, catálogo ou vantagens próprias conforme o perfil. | [PlantUML](diagramas/SD06-consultar-painel.puml) · [SVG](diagramas/SD06-consultar-painel.svg) |
| **SD07 · Vantagens** | Separa cadastro, edição e desativação. As operações sobre uma vantagem existente usam a empresa da sessão para conferir a propriedade. | [PlantUML](diagramas/SD07-gerenciar-vantagens.puml) · [SVG](diagramas/SD07-gerenciar-vantagens.svg) |
| **SD08 · Resgate** | Verifica disponibilidade e saldo. Debita as moedas, registra o custo e gera um único código, incluído nos avisos do aluno e da empresa. | [PlantUML](diagramas/SD08-resgatar-vantagem.puml) · [SVG](diagramas/SD08-resgatar-vantagem.svg) |
| **SD09 · Notificações** | A consulta usa o identificador da conta autenticada e apresenta as mensagens e seus estados de envio. | [PlantUML](diagramas/SD09-consultar-notificacoes.puml) · [SVG](diagramas/SD09-consultar-notificacoes.svg) |
| **SD10 · Envio por e-mail** | O operador processa a caixa de saída. Cada aviso aceito pelo servidor SMTP é marcado como enviado. | [PlantUML](diagramas/SD10-enviar-emails.puml) · [SVG](diagramas/SD10-enviar-emails.svg) |

## Visão Geral de Interação

O IOD01 organiza os fluxos da aplicação web e da operação institucional. Cada quadro `ref` remete a um diagrama de sequência identificado pelo código `SD`. O círculo preenchido indica o início, os losangos representam decisão ou reunião de caminhos alternativos e o círculo duplo indica o fim do cenário mostrado.

Na parte web, o cadastro é opcional para quem já tem conta. Depois do login bem-sucedido, o painel oferece caminhos de acordo com o perfil. A parte institucional separa pré-cadastro, concessão de crédito e envio de e-mails. O SMTP lê notificações que o envio de moedas e o resgate gravaram anteriormente. Essa dependência é pelo banco e por isso os comandos aparecem como caminhos independentes da sessão web.

[Fonte PlantUML com bloco Graphviz `@startdot`](diagramas/IOD01-visao-geral.puml) · [Visão Geral em SVG](diagramas/IOD01-visao-geral.svg) · [UML 2.5.1, seção 17.10](https://www.omg.org/spec/UML/2.5.1/PDF)

## Comparação de releases e implementação

| Caso de uso | O que já estava no repositório | Situação nesta entrega |
|---|---|---|
| Autenticar e gerenciar cadastro de aluno e empresa | Fluxos web disponíveis na Sprint 2 e preservados na Sprint 3. | Modelados em SD01 e SD02. |
| Crédito semestral e envio de e-mails | Os dois comandos já existiam na Sprint 2 e foram mantidos na Sprint 3. | Modelados em SD04 e SD10. |
| Enviar moedas, consultar saldo e extrato, gerenciar e consultar vantagens, resgatar e consultar notificações | Os serviços e o esquema já apareciam na Sprint 2. A Sprint 3 integrou os fluxos às rotas e telas. | Modelados em SD05 a SD09. |
| Pré-cadastrar professor de instituição parceira | A inicialização incluía uma instituição de referência e `seed-demo` carregava professores fictícios. | Implementei `cadastrar-professor` e modelei em SD03. |

O novo comando cadastra **um professor por execução**, a partir da lista fornecida pela instituição. Use o mesmo nome para reutilizar uma instituição já cadastrada. A senha inicial é digitada sem eco e armazenada como hash. Em caso de duplicidade de CPF ou e-mail, a transação é revertida, incluindo eventual inclusão da instituição. O cadastro público continua disponível para aluno e empresa.

### Executar e testar

O código do pré-cadastro já está integrado à pasta `Entrega Sprint 3/sistema`. Execute a partir da raiz do projeto extraído.

```powershell
cd "Entrega Sprint 3/sistema"
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m flask --app app cadastrar-professor
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Após o cadastro, o professor pode autenticar com o e-mail e a senha inicial. Para atribuir saldo aos professores ativos, execute `flask --app app creditar-semestre AAAA-N` no ambiente virtual, informando o semestre desejado.

Validei a renderização dos 11 diagramas e executei os **23 testes da Sprint 3** com sucesso. O novo teste cobre cadastro pelo comando, vínculo institucional, normalização do CPF, armazenamento por hash, login e reversão em caso de duplicidade. A suíte testa SMTP com servidor simulado.

## Fontes do projeto

[Enunciado, seção 2](https://github.com/BernardoApl/Sistema-de-Moeda-Estudantil/blob/1ddc782/referencias/enunciado_laboratorio_3.pdf) · [Casos de uso da Sprint 1](https://github.com/BernardoApl/Sistema-de-Moeda-Estudantil/tree/1ddc782/Entrega%20Sprint%201) · [Implementação da Sprint 2](https://github.com/BernardoApl/Sistema-de-Moeda-Estudantil/tree/1ddc782/Entrega%20Sprint%202/sistema) · [Implementação da Sprint 3](https://github.com/BernardoApl/Sistema-de-Moeda-Estudantil/tree/1ddc782/Entrega%20Sprint%203/sistema)
