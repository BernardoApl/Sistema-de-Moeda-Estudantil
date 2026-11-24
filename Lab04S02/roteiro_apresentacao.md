# Roteiro de apresentação — Release 2

## 1. Objetivo e perfis

Apresentar o reconhecimento do mérito por meio de moedas. Professores as distribuem; alunos consultam saldo e resgatam vantagens; empresas oferecem vantagens e conferem cupons.

## 2. Evolução dos modelos

- Release 1: casos de uso, histórias, classes, componentes e modelo ER; CRUDs de aluno e empresa.
- Release 2: [sequências e visão geral de interação](../Lab04S01/README.md), além do [diagrama de implantação](implantacao.svg).
- Comparar o modelo conceitual de contas e perfis com a tabela `contas`, diferenciada pelo campo `perfil`; os serviços implementam regras e os DAOs consultam os dados.
- Explicar que professor é cadastrado por comando institucional; crédito semestral e envio SMTP são operações executadas por comando. A aplicação web usa Flask, Jinja e MVC; não há API REST separada.
- Mostrar a evolução para validação de CPF/CNPJ e registro de utilização de cupom. A implantação prevista adiciona PostgreSQL e um adaptador, mantendo SQLite para uso local.

## 3. Demonstração local

Siga o [guia de execução](../Entrega%20Sprint%203/README.md), use somente dados fictícios e credite o semestre antes da demonstração.

1. Entre como empresa e cadastre uma vantagem com descrição, foto por URL e custo.
2. Entre como professor e envie moedas ao aluno da mesma instituição, informando o motivo; mostre saldo e extrato.
3. Entre como aluno, confira o recebimento, resgate a vantagem e mostre o cupom e o extrato.
4. Entre como empresa, confira o mesmo código e marque o cupom como utilizado.
5. Mostre as notificações pendentes e explique que o envio externo requer SMTP configurado e execução do comando `enviar-emails`.

## 4. Validação e limites

Apresente o resultado atualizado da suíte automatizada, distinguindo SQLite local de PostgreSQL em nuvem. A configuração e o diagrama de implantação não são evidência de publicação: demonstre a URL e os fluxos somente depois de verificá-los. O envio SMTP real também requer verificação com provedor configurado.

## 5. Avaliação de outro grupo

A [avaliação da Lab04S03](../Lab04S03/relatorio.md) examina o projeto indicado, documenta três refatorações GRASP e registra os impedimentos para publicar o pull request.
