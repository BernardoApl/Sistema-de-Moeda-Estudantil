# Requisitos e histórias do usuário

Fonte: enunciado fornecido, “Laboratório 3 - Segundo Semestre/2026”, seções 2, 3 e 4. O PDF é referência do trabalho; não é registro de tarefas já realizadas.

## Atores

Aluno, professor, empresa parceira, operador institucional e serviço SMTP externo. O operador é uma decisão técnica para representar a importação/carga de dados e o crédito semestral via comandos locais; não existe cadastro público de professor.

## Regras de negócio

| ID | Regra |
|---|---|
| RN01 | Aluno informa nome, e-mail, CPF, RG, endereço, instituição e curso. |
| RN02 | Instituições e professores são pré-cadastrados. Professor possui nome, CPF, departamento e instituição. |
| RN03 | Cada professor recebe 1.000 moedas por semestre, acumuladas ao saldo anterior. Reprocessar o mesmo semestre não duplica crédito. |
| RN04 | Transferência exige quantidade inteira positiva, saldo suficiente, aluno ativo e motivo obrigatório. |
| RN05 | Aluno recebe notificação por e-mail ao receber moedas. |
| RN06 | Saldo e extrato são privados. Extrato do aluno contém recebimentos e resgates; do professor, créditos e envios. |
| RN07 | Vantagem pertence a uma empresa, possui descrição, foto e custo inteiro positivo. |
| RN08 | Resgate exige saldo suficiente e debita o custo vigente atomicamente. |
| RN09 | Um código único de cupom é enviado ao aluno e à empresa, com o mesmo conteúdo de conferência. |
| RN10 | Os três perfis autenticam com e-mail e senha para acessar as operações privadas. |
| RN11 | Cadastro inicial e login são públicos. Conta só pode consultar, editar e excluir o próprio cadastro. |
| RN12 | Exclusão é lógica para preservar extratos e cupons. Vantagens de empresa desativada saem do catálogo. |

RN11 (propriedade do cadastro), RN12, restrição de alunos à mesma instituição, senha mínima de 8 caracteres e CPF/CNPJ únicos são decisões deste protótipo, complementares ao enunciado. A foto é uma URL HTTP(S), sem upload de arquivo. CPF/CNPJ são normalizados e validados pelo comprimento; não há validação de dígitos verificadores.

## Backlog e critérios de aceite

| ID / entrega | História | Critério de aceite |
|---|---|---|
| HU01 / S2-S3 | Como aluno, quero me cadastrar para participar do sistema. | Dados obrigatórios válidos criam conta; instituição vem da lista; e-mail/CPF repetidos são recusados; senha é armazenada como hash. |
| HU02 / S2-S3 | Como aluno, quero consultar, alterar e excluir meu cadastro. | Após login, vejo meus dados; alterações persistem; exclusão exige minha senha, encerra o acesso e preserva o histórico. |
| HU03 / S2-S3 | Como empresa, quero cadastrar minha parceria. | Nome, e-mail, CNPJ, endereço e senha válidos criam conta; duplicidade é recusada. |
| HU04 / S2-S3 | Como empresa, quero consultar, atualizar e excluir meu cadastro. | Apenas a própria empresa altera seus dados; desativação retira suas vantagens do catálogo. |
| HU05 / S2-S3 | Como usuário, quero autenticar para acessar minhas operações. | Credenciais corretas abrem a área do perfil; credenciais inválidas mostram erro; aluno não acessa operações de professor ou empresa. |
| HU06 / S3 | Como professor, quero receber o crédito semestral. | Comando institucional adiciona 1.000; saldo anterior é mantido; repetição no mesmo semestre não altera saldo. |
| HU07 / S3 | Como professor, quero reconhecer um aluno enviando moedas. | Aluno da instituição, quantidade positiva e motivo geram débito/crédito e notificação em uma transação; saldo insuficiente não gera efeitos. |
| HU08 / S3 | Como aluno ou professor, quero consultar saldo e extrato. | Saldo corresponde aos lançamentos; extrato identifica tipo, data UTC, quantidade e motivo/cupom quando aplicável. |
| HU09 / S3 | Como empresa, quero cadastrar e gerenciar vantagens. | Descrição, URL da foto e custo são obrigatórios; somente a proprietária edita/desativa; catálogo reflete alterações. |
| HU10 / S3 | Como aluno, quero consultar vantagens disponíveis. | Catálogo mostra foto, descrição, empresa e custo apenas para vantagens/empresas ativas. |
| HU11 / S3 | Como aluno, quero resgatar uma vantagem. | Saldo suficiente gera débito, registro com preço histórico e cupom único; saldo insuficiente não altera dados. |
| HU12 / S3 | Como aluno e empresa, quero receber o cupom para conferência presencial. | Duas notificações contêm o mesmo código; sem SMTP ficam pendentes e visíveis; com SMTP são processadas pelo comando de envio. |

## Requisitos não funcionais

- RNF01: arquitetura MVC, com controladores separados de templates, serviços e DAO.
- RNF02: persistência SQLite com chaves estrangeiras, consultas parametrizadas e transações.
- RNF03: hash de senha, autorização por perfil/proprietário e proteção CSRF em formulários POST.
- RNF04: interface em português, formulários rotulados, layout adaptável a celular e navegação por teclado.
- RNF05: execução reproduzível, comandos documentados e testes automatizados independentes do banco de demonstração.
- RNF06: alterações de modelos preservam os originais; escopo, evidências e limitações são documentados.

## Definição de pronto

Artefato presente, coerente com modelo/código, testável segundo o critério de aceite e acompanhado das instruções de execução. Apresentação em aula, validação SMTP externa e publicação remota são atividades distintas, não presumidas por esta documentação.
