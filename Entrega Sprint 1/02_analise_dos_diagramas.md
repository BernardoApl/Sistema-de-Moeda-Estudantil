# Análise e revisão dos diagramas

## Casos de uso

O original identifica corretamente aluno, professor, empresa e serviço de e-mail; já relaciona resgate à geração de cupom e envio à notificação. A autenticação e a consulta de extrato aparecem duplicadas para atores diferentes, embora representem funcionalidades compartilhadas.

A revisão unifica esses casos, acrescenta consultar/atualizar/excluir cadastro (exigidos pelos CRUDs das sprints 2 e 3), crédito semestral e operação institucional de preparação dos dados. O envio de cupom passa a explicitar os dois destinatários. Autenticação é precondição das operações privadas, não um `include` que exigiria novo login a cada ação. Cadastro inicial e login continuam públicos.

## Classes

O original contém as entidades centrais e cardinalidades adequadas entre instituição, aluno, professor, transferência, empresa, vantagem e resgate. Faltam identificadores, crédito semestral, preço histórico do resgate, estado da conta/vantagem e registro das notificações. Atributo `senha: String` poderia sugerir armazenamento de senha legível.

A revisão usa `senhaHash`, identificadores, `ativo`, `CreditoSemestral`, `Notificacao` e `valor` no resgate. `foto: Arquivo` passa a `fotoUrl: String`, refletindo a implementação por URL. O e-mail é o identificador de login; o professor também possui e-mail para autenticar. O modelo distingue o domínio conceitual e a realização em código: Python utiliza registros SQLite, `ContaDAO`, `VantagemDAO` e funções de serviço, sem fingir que há classes Python Aluno/Professor/Empresa. Os subtipos conceituais são persistidos em tabela única, discriminada por `perfil`.

## Componentes

O original já propõe MVC e separa persistência e e-mail. A revisão nomeia os módulos reais: templates e CSS (View), `controllers.py` (Controller), `services.py` (regras), `models.py` (DAO), `schema.sql` (modelo relacional), SQLite e `commands.py` (operação/SMTP). O serviço grava a notificação na mesma transação da movimentação. O comando SMTP processa a caixa de saída posteriormente, para que uma falha de rede não desfaça um resgate concluído.

## Decisões e limites

| Tema | Decisão e consequência |
|---|---|
| Herança de contas | Tabela única com `perfil`; reduz joins e mantém unicidade global de e-mail/documento. Campos de subtipos não aplicáveis ficam vazios. |
| Remoção de cadastro | Exclusão lógica; mantém as referências dos extratos e cupons. Cadastro não pode reutilizar documento/e-mail de conta desativada. |
| Alunos elegíveis | Mesma instituição do professor; enunciado não fornece uma matrícula professor-turma-aluno. Não se afirma verificar vínculo de turma. |
| Semestre | Operador informa `AAAA-1` ou `AAAA-2`; chave única impede duplicação. Não há agendador automático. |
| Cupom | Token aleatório de 24 caracteres hexadecimais, com unicidade no banco. Conferência presencial por código; não há baixa/validação de uso único na aplicação. |
| Foto | URL pública HTTP(S); disponibilidade depende do servidor da imagem. |
| SMTP | Adaptador com STARTTLS e caixa de saída persistida. Sem credenciais reais, o teste é simulado. Um worker por vez; falha após envio e antes da marcação pode causar reenvio. |
| Datas | Banco registra UTC e interface identifica explicitamente esse fuso. |
| Segurança | Adequado à demonstração local. Não inclui recuperação de senha, limitação de tentativas ou implantação HTTPS. |

## Rastreabilidade dos artefatos

Originais: `originais/`. Revisões: `diagramas/*.puml` e `*.svg`. ER: `../Entrega Sprint 2/diagramas/04_modelo_er.*`. Arquitetura e correspondência entre modelo e código: `../Entrega Sprint 3/01_arquitetura_e_persistencia.md`.
