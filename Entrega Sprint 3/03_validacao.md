# Relatório de validação — 20/10/2026

## Ambiente e resultados

Python 3.12, Flask 3.1.3, SQLite e Windows. Testes funcionais usam banco temporário por teste. Verificação visual usa Playwright com Chrome instalado, servidor local na porta 5059 e dados fictícios. O navegador integrado não estava disponível (inventário vazio), por isso foi usado Chrome headless.

| Verificação | Resultado observado |
|---|---|
| Sprint 2: `python -m unittest discover -s tests -v` | 5 testes, OK, 9,397 segundos. |
| Sprint 3: mesmo comando | 22 testes, OK, 22,335 segundos. |
| Chrome: empresa cadastra vantagem de 50 | Operação concluída e imagem local carregada. |
| Chrome: professor envia 100 com motivo | Saldo passou de 1.000 para 900; extrato exibiu envio. |
| Chrome: aluno resgata vantagem | Saldo passou de 100 para 50; cupom e extrato exibidos. |
| Chrome: empresa consulta notificações | Mensagem de conferência do resgate exibida. |
| Chrome: aluno altera cadastro | Nome atualizado persistiu após redirecionamento. |
| Responsividade: 390 × 844 | Cadastro e painel do aluno sem transbordamento horizontal do documento. |
| JavaScript: fluxo e 12 slides | Nenhum erro de página capturado. |
| Diagramas | Quatro fontes PlantUML renderizadas sem erro e imagens inspecionadas. |
| Slides | 12 páginas capturadas; títulos, conteúdo e navegação conferidos. |

## Cobertura da suíte final

1. Crédito acumulável e idempotente.
2. Rejeição de semestre inválido.
3. Transferência com atualização dos dois saldos e notificação.
4. Transferência sem saldo não grava histórico.
5. Rejeição de zero, negativo, decimal, texto e valor excessivo.
6. Motivo obrigatório.
7. Aluno de outra instituição é recusado.
8. Resgate gera o mesmo código nas duas notificações.
9. Alteração de custo não muda o valor histórico do resgate.
10. Resgate sem saldo não grava operação.
11. Falha na notificação causa rollback do resgate e saldo.
12. CRUD completo de aluno via HTTP.
13. CRUD completo de empresa via HTTP.
14. Duplicidade recusada e senha armazenada como hash.
15. POST sem CSRF é recusado.
16. Perfil aluno não acessa envio nem cadastro de vantagem.
17. Login inválido é recusado.
18. Empresa não lê notificação privada do aluno.
19. Exclusão da empresa preserva resgate e impede novos resgates.
20. Empresa não edita vantagem que não lhe pertence.
21. Telas principais renderizam para os três perfis.
22. Adaptador SMTP envia e marca pendência em teste com mock.

A suíte da sprint 2 repete CRUD de aluno, CRUD de empresa, CSRF, login inválido e duplicidade/hash, sobre a versão inicial.

## Evidências visuais

- `evidencias/login.png`: entrada e links de cadastro.
- `evidencias/professor.png`: transferência e saldo 900.
- `evidencias/aluno.png`: resgate e saldo 50.
- `evidencias/aluno-mobile.png`: painel em 390 px.
- `evidencias/cadastro-mobile.png`: cadastro atualizado em 390 px.
- `evidencias/notificacao.png`: cupom da empresa.
- `evidencias/slides-contato.png`: visão geral dos slides.

São capturas de execução com dados fictícios, não telas estáticas usadas para simular funcionamento. A imagem da vantagem é um recurso de teste identificado como demonstração.

## Rastreabilidade de aceite

HU01–HU05: testes de CRUD/login/autorização. HU06: crédito idempotente. HU07: transferência/saldo/motivo/instituição. HU08: fluxo no navegador e consultas de extrato. HU09–HU10: cadastro de vantagem e catálogo no navegador, teste de propriedade. HU11: resgate/rollback/preço histórico. HU12: código compartilhado, privacidade e adaptador SMTP simulado.

## Limitações observadas em 20/10/2026

- SMTP real não foi exercitado; requer provedor e credenciais. Nenhum envio externo foi realizado.
- Não foi executado ensaio de carga/concorrência; transações de escrita usam bloqueio SQLite.
- CPF/CNPJ: comprimento, normalização e unicidade; sem dígitos verificadores.
- Cupom sem baixa de utilização presencial ou expiração.
- CRUD consulta a própria conta; não há painel administrativo global.
- Foto por URL HTTP(S), sem upload.
- Snapshot S2 compartilha esquema e infraestrutura previstos para S3, mas expõe somente autenticação e CRUDs.
- Não há evidência de apresentação semanal, publicação no GitHub ou submissão acadêmica.

## Atualização posterior

A suíte foi ampliada para 25 testes, incluindo pré-cadastro institucional, validação de documentos e marcação de cupons com verificação de propriedade e prevenção de uso repetido. Essas funcionalidades superam as limitações de documentos e baixa de cupom registradas acima. O teste SMTP continua simulado.
