# Sistema de Moeda Estudantil

Projeto acadêmico de reconhecimento do mérito estudantil — Laboratório 3 de Projeto de Software, segundo semestre de 2026.

## Integrantes

- Bernardo Augusto Pereira
- Bruno Kenji Fantucci
- João Gabriel
- Murilo Duarte Moura

## Entregas

| Pasta | Material |
|---|---|
| [Entrega Sprint 1](<Entrega Sprint 1/README.md>) | Requisitos, histórias com critérios de aceite, análise e diagramas UML revisados; originais preservados. |
| [Entrega Sprint 2](<Entrega Sprint 2/README.md>) | Modelo ER, estratégia DAO e versão inicial executável dos CRUDs de aluno e empresa. |
| [Entrega Sprint 3](<Entrega Sprint 3/README.md>) | Sistema final MVC, testes, arquitetura, tutorial e slides HTML para apresentação de 20 minutos. |
| [Referência](referencias/enunciado_laboratorio_3.pdf) | Cópia do enunciado fornecido. |
| [Ferramentas](ferramentas/README.md) | Scripts opcionais de geração de artefatos e verificação visual. |

**Comece pela [Sprint 3](<Entrega Sprint 3/README.md>) para executar o sistema final.** A aplicação usa Python, Flask, Jinja e SQLite.

## Funcionalidades

CRUDs da própria conta de aluno/empresa; autenticação dos três perfis; crédito semestral acumulável e idempotente; envio de moedas com motivo; saldo e extrato; gerenciamento de vantagens; resgate com cupom; caixa de saída e adaptador SMTP.

Os modelos possuem fontes `.puml` e imagens `.svg`/`.png`. Abra [apresentacao.html](<Entrega Sprint 3/apresentacao.html>) no navegador: são 12 slides com notas e navegação por setas.

## Validação e limites

Foram aprovados **5 testes na sprint 2 e 25 testes na sprint 3**, além do fluxo no Chrome em desktop e celular. Consulte o [relatório](<Entrega Sprint 3/03_validacao.md>).

O envio real de e-mails requer configuração SMTP; foi validado com simulação, sem envio externo. Os arquivos estão preparados localmente; publicação no GitHub, submissão à disciplina e apresentação em aula não foram realizadas. As versões foram organizadas em 20/10/2026, sem atribuir datas fictícias de entregas anteriores.
