"""Gera documentação visual e snapshot S2. Não altera arquivos originais."""
from pathlib import Path
import shutil
import html

ROOT = Path(__file__).resolve().parents[1]


def write(path, text):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.strip()+'\n', encoding='utf-8')


prefix = '''@startuml
!pragma layout smetana
skinparam backgroundColor white
skinparam defaultFontName Arial
skinparam defaultFontSize 14
skinparam shadowing false
skinparam classAttributeIconSize 0
skinparam ArrowColor #21655F
skinparam packageStyle rectangle
'''

write('Entrega Sprint 1/diagramas/01_casos_de_uso.puml', prefix+r'''
left to right direction
title Sistema de Moeda Estudantil - Casos de uso revisados
actor Aluno
actor Professor
actor "Empresa parceira" as Empresa
actor "Operador institucional" as Operador
actor "Servidor SMTP" as SMTP
rectangle "Sistema de Moeda Estudantil" {
 usecase "Autenticar usuário" as Login
 usecase "Cadastrar aluno" as CA
 usecase "Consultar, alterar e\nexcluir próprio cadastro" as CRUD
 usecase "Cadastrar empresa" as CE
 usecase "Consultar saldo e extrato" as Extrato
 usecase "Enviar moedas\ncom motivo" as Envio
 usecase "Registrar notificação\nde recebimento" as NReceb
 usecase "Consultar vantagens" as Catalogo
 usecase "Gerenciar próprias\nvantagens" as GV
 usecase "Resgatar vantagem" as Resgate
 usecase "Gerar código de cupom" as Cupom
 usecase "Registrar cupom para\naluno e empresa" as NCupom
 usecase "Consultar notificações" as CN
 usecase "Pré-cadastrar instituição\ne professor (carga local)" as Carga
 usecase "Creditar 1.000 moedas\npor semestre" as Credito
 usecase "Processar caixa de saída" as Emails
}
Aluno --> Login
Professor --> Login
Empresa --> Login
Aluno --> CA
Aluno --> CRUD
Empresa --> CE
Empresa --> CRUD
Aluno --> Extrato
Professor --> Extrato
Professor --> Envio
Envio ..> NReceb : <<include>>
Aluno --> Catalogo
Empresa --> GV
Aluno --> Resgate
Resgate ..> Cupom : <<include>>
Resgate ..> NCupom : <<include>>
Aluno --> CN
Empresa --> CN
Professor --> CN
Operador --> Carga
Operador --> Credito
Operador --> Emails
SMTP --> Emails
note bottom of Login
Autenticação é precondição das operações privadas.
Cadastro inicial e login são públicos.
end note
note bottom of Emails
Envio assíncrono por comando local.
Sem SMTP, mensagens permanecem pendentes.
end note
@enduml''')

write('Entrega Sprint 1/diagramas/02_classes.puml',prefix+r'''
title Modelo conceitual de domínio e correspondência de implementação
abstract class ContaAcesso {
 id: Integer
 nome: String
 email: String {único, login}
 senhaHash: String
 documento: String {único}
 endereco: String
 ativo: Boolean
}
class Aluno {
 rg: String
 curso: String
 saldo: Integer
}
class Professor {
 departamento: String
 saldo: Integer
}
class EmpresaParceira {
 telefone: String
}
class InstituicaoEnsino {
 id: Integer
 nome: String
}
class TransferenciaMoedas {
 id: Integer
 valor: Integer
 motivo: String
 dataHora: DateTime
}
class CreditoSemestral {
 id: Integer
 semestre: String
 valor: Integer = 1000
 dataHora: DateTime
}
class Vantagem {
 id: Integer
 descricao: String
 fotoUrl: String
 custo: Integer
 ativo: Boolean
}
class Resgate {
 id: Integer
 valor: Integer {histórico}
 codigo: String {único}
 dataHora: DateTime
}
class Notificacao {
 id: Integer
 destinatario: String
 assunto: String
 mensagem: String
 enviado: Boolean
 dataHora: DateTime
}
ContaAcesso <|-- Aluno
ContaAcesso <|-- Professor
ContaAcesso <|-- EmpresaParceira
InstituicaoEnsino "1" -- "0..*" Aluno
InstituicaoEnsino "1" -- "0..*" Professor
Professor "1" -- "0..*" TransferenciaMoedas : envia
Aluno "1" -- "0..*" TransferenciaMoedas : recebe
Professor "1" -- "0..*" CreditoSemestral
EmpresaParceira "1" -- "0..*" Vantagem : oferece
Aluno "1" -- "0..*" Resgate
Vantagem "1" -- "0..*" Resgate
ContaAcesso "1" -- "0..*" Notificacao
note bottom of CreditoSemestral
Único por professor e semestre.
Adiciona ao saldo anterior.
end note
note top of ContaAcesso
Subtipos persistidos em contas.perfil.
Python usa registros SQLite + ContaDAO.
Operações em services.py; não há
classes Python para cada entidade.
end note
@enduml''')

write('Entrega Sprint 1/diagramas/03_componentes.puml',prefix+r'''
title Arquitetura MVC implementada
actor Usuário
component "View\ntemplates/*.html\nstatic/style.css" as View
component "Controller\ncontrollers.py\nrotas, sessão, CSRF, autorização" as Controller
component "Model / Serviços\nservices.py\nregras e transações" as Services
component "Model / DAO\nmodels.py\nContaDAO, VantagemDAO, extrato" as DAO
component "Operação local\ncommands.py\ncarga, crédito, envio SMTP" as CLI
component "Composição\napp.py\ncreate_app()" as App
database "SQLite\nschema.sql\ncontas, histórico, caixa de saída" as DB
cloud "SMTP externo\nSTARTTLS" as SMTP
Usuário --> View
View --> Controller : HTTP GET/POST
Controller --> View : render_template
Controller --> Services
Controller --> DAO : consultas
Services --> DAO : conexão / consultas
DAO --> DB : SQL parametrizado
CLI --> Services : crédito semestral
CLI --> DAO : carga / pendências
CLI --> SMTP : e-mails após commit
App ..> Controller : registra Blueprint
App ..> CLI : registra comandos
note bottom of Services
Débito, crédito, histórico e notificações
confirmados na mesma transação.
end note
@enduml''')

write('Entrega Sprint 2/diagramas/04_modelo_er.puml',prefix+r'''
title Modelo ER físico - SQLite
entity instituicoes {
 * id : INTEGER <<PK>>
 --
 * nome : TEXT <<UNIQUE>>
}
entity contas {
 * id : INTEGER <<PK>>
 --
 * perfil : TEXT
 * nome : TEXT
 * email : TEXT <<UNIQUE>>
 * senha_hash : TEXT
 * documento : TEXT <<UNIQUE>>
 * rg : TEXT
 * endereco : TEXT
 * curso : TEXT
 * departamento : TEXT
 * telefone : TEXT
 instituicao_id : INTEGER <<FK>>
 * saldo : INTEGER
 * ativo : INTEGER
}
entity vantagens {
 * id : INTEGER <<PK>>
 --
 * empresa_id : INTEGER <<FK>>
 * descricao : TEXT
 * foto : TEXT
 * custo : INTEGER
 * ativo : INTEGER
}
entity transferencias {
 * id : INTEGER <<PK>>
 --
 * professor_id : INTEGER <<FK>>
 * aluno_id : INTEGER <<FK>>
 * valor : INTEGER
 * motivo : TEXT
 * data_hora : TEXT
}
entity creditos {
 * id : INTEGER <<PK>>
 --
 * professor_id : INTEGER <<FK>>
 * semestre : TEXT
 * valor : INTEGER
 * data_hora : TEXT
}
entity resgates {
 * id : INTEGER <<PK>>
 --
 * aluno_id : INTEGER <<FK>>
 * vantagem_id : INTEGER <<FK>>
 * valor : INTEGER
 * codigo : TEXT <<UNIQUE>>
 * data_hora : TEXT
}
entity notificacoes {
 * id : INTEGER <<PK>>
 --
 * conta_id : INTEGER <<FK>>
 * destinatario : TEXT
 * assunto : TEXT
 * mensagem : TEXT
 * enviado : INTEGER
 * data_hora : TEXT
}
instituicoes |o--o{ contas
contas ||--o{ vantagens : empresa
contas ||--o{ transferencias : professor
contas ||--o{ transferencias : aluno
contas ||--o{ creditos
contas ||--o{ resgates
vantagens ||--o{ resgates
contas ||--o{ notificacoes
note bottom of contas
Instituição obrigatória para aluno/professor.
Perfil restringe os subtipos na aplicação.
CHECK saldo >= 0.
end note
note bottom of creditos
UNIQUE(professor_id, semestre)
CHECK valor = 1000
end note
@enduml''')

# Snapshot inicial: reutiliza infraestrutura; expõe apenas autenticação e CRUDs.
source = ROOT/'Entrega Sprint 3/sistema'
target = ROOT/'Entrega Sprint 2/sistema'
target.mkdir(parents=True,exist_ok=True)
for name in ['app.py','models.py','services.py','schema.sql','requirements.txt','commands.py']:
    shutil.copy2(source/name,target/name)
for folder, names in [('templates',['base.html','login.html','perfil.html']),('static',['style.css'])]:
    (target/folder).mkdir(parents=True,exist_ok=True)
    for name in names:
        shutil.copy2(source/folder/name,target/folder/name)
controller = (source/'controllers.py').read_text(encoding='utf-8')
controller = controller[:controller.index("@routes.get('/')")]+'''@routes.get('/')
@acesso()
def index():
    if g.conta['perfil'] in ('aluno','empresa'):
        return redirect(url_for('web.perfil'))
    return render_template('inicial.html')
'''
write('Entrega Sprint 2/sistema/controllers.py',controller)
base = (target/'templates/base.html').read_text(encoding='utf-8')
base = base.replace('<a href="{{ url_for(\'web.notificacoes\') }}">Notificações</a>','')
write('Entrega Sprint 2/sistema/templates/base.html',base)
write('Entrega Sprint 2/sistema/templates/inicial.html',"{% extends 'base.html' %}{% block content %}<h1>Versão inicial dos CRUDs</h1><p>Acesse como aluno ou empresa para gerenciar seu cadastro. As funcionalidades de moedas são expostas na sprint 3.</p>{% endblock %}")
tests = (source/'tests/test_sistema.py').read_text(encoding='utf-8')
# Mesmos testes reais de CRUD e login, com fixture compartilhada.
methods = ['test_crud_aluno_via_http','test_crud_empresa_via_http','test_csrf','test_login_invalido','test_duplicidade_e_senha_hash']
head = tests[:tests.index('    def preparar_resgate')]
for method in methods:
    start = tests.index('    def '+method)
    end = tests.find('\n    def ',start+5)
    head += tests[start:end if end!=-1 else tests.index("\n\nif __name__")]+'\n'
write('Entrega Sprint 2/sistema/tests/test_cruds.py',head)

slides = [
 ('Sistema de Moeda Estudantil','Laboratório 3 · Projeto de Software · PUC Minas', ['Bernardo Augusto Pereira · Bruno Kenji Fantucci','João Gabriel · Murilo Duarte Moura','Modelagem, persistência e protótipo MVC'], 'Apresente o grupo e a proposta. 1 minuto.'),
 ('Reconhecimento que vira vantagem','O ciclo principal', ['Professor envia moedas com uma justificativa.','Aluno acompanha saldo e troca moedas por vantagens.','Empresa recebe o código do cupom para conferência.'], 'Explique o ciclo em 1 minuto.'),
 ('Entregas das três sprints','Do modelo à execução', ['Sprint 1: casos de uso, histórias, classes e componentes.','Sprint 2: ER, DAO e CRUDs iniciais com persistência.','Sprint 3: CRUDs finais, fluxos de moedas e apresentação.'], 'Mostre as três pastas. 1 minuto.'),
 ('Casos de uso revisados','Operações privadas exigem autenticação', ['CRUDs de aluno e empresa foram explicitados.','Crédito semestral entra como operação institucional.','Cupom gera notificações para aluno e empresa.'], 'Abra 01_casos_de_uso.svg para os detalhes. 1 minuto.'),
 ('Modelo e código','Correspondência explícita', ['ContaAcesso e subtipos → tabela contas e campo perfil.','Transferência, crédito e resgate → tabelas de histórico.','Notificação → caixa de saída persistida na transação.'], 'Abra 02_classes.svg. Explique que classes são conceituais e Python usa registros/DAO. 1 minuto.'),
 ('Arquitetura MVC','Responsabilidades separadas', ['View: templates Jinja e CSS.','Controller: rotas, sessão e autorização.','Model: serviços, DAO e banco SQLite.'], 'Abra 03_componentes.svg e localize os arquivos. 1,5 minuto.'),
 ('Persistência com DAO','SQLite e SQL parametrizado', ['Chaves estrangeiras mantêm as referências.','E-mail, documento e código têm unicidade.','Exclusão lógica preserva transações e cupons.'], 'Abra 04_modelo_er.svg e schema.sql. 1,5 minuto.'),
 ('Tutorial: requisição ao banco','Um cadastro completo', ['GET renderiza o formulário Jinja.','POST valida CSRF, dados e regras de negócio.','Serviço grava; controlador redireciona para a consulta.'], 'Mostre cadastro em controllers.py, salvar_conta e perfil.html. 2 minutos.'),
 ('Tutorial: transações de moedas','Consistência em caso de falha', ['BEGIN IMMEDIATE protege a verificação do saldo.','Saldo, histórico e notificações confirmam juntos.','SMTP processa pendências depois do commit.'], 'Mostre transferir e resgatar em services.py. 2 minutos.'),
 ('Demonstração dos CRUDs','Aluno e empresa', ['Criar uma conta fictícia e entrar.','Consultar e alterar o próprio cadastro.','Excluir uma conta descartável confirmando a senha.'], 'Demonstre os dois perfis. 2 minutos.'),
 ('Demonstração do ciclo completo','Professor → aluno → empresa', ['Professor envia 100 moedas com motivo.','Aluno resgata vantagem de 50 e recebe o cupom.','Empresa confere o mesmo código nas notificações.'], 'Use banco novo e vantagem de teste. Mostre extratos. 3 minutos.'),
 ('Testes e próximos passos','Evidências e limites', ['Testes cobrem CRUD, saldo, autorização e rollback.','Repetir o crédito do semestre não duplica moedas.','SMTP externo exige configuração; apresentação e publicação são etapas do grupo.'], 'Execute testes. Mencione ausência de validação de uso único do cupom. 2 minutos.')
]
sections = []
for i,(title,sub,items,note) in enumerate(slides,1):
    sections.append(f'<section class="slide" id="s{i}"><p class="numero">LAB 03 / {i:02d}</p><h1>{html.escape(title)}</h1><h2>{html.escape(sub)}</h2><ul>'+''.join('<li>'+html.escape(x)+'</li>' for x in items)+f'</ul><details><summary>Notas de apresentação</summary><p>{html.escape(note)}</p></details><footer>Moeda Estudantil <span>{i} / {len(slides)}</span></footer></section>')
write('Entrega Sprint 3/apresentacao.html','''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apresentação — Moeda Estudantil</title><style>
*{box-sizing:border-box}body{margin:0;background:#e4ecec;font-family:Arial,sans-serif;color:#123e3c}.slide{display:none;max-width:1200px;min-height:675px;margin:30px auto;background:#fff;padding:54px 70px;position:relative;border-top:12px solid #096b62}.slide.active,body.all .slide{display:block}.numero{font-size:14px;letter-spacing:2px;color:#53676f}h1{font-size:46px;line-height:1.15;max-width:1000px;margin:30px 0 14px}h2{font-size:24px;color:#53676f;font-weight:400;margin-bottom:42px}ul{padding-left:26px;font-size:25px;line-height:1.5}li{margin:20px 0}footer{margin-top:48px;border-top:1px solid #d9e4e7;padding-top:15px;color:#53676f;font-size:14px}footer span{float:right}details{font-size:15px;color:#53676f}nav{text-align:center;padding:10px 10px 24px}button{font:inherit;padding:12px 22px;background:#096b62;color:white;border:0;border-radius:6px;margin:5px;cursor:pointer}button:focus-visible{outline:3px solid #df9e28}@media(max-width:700px){.slide{margin:10px;min-height:75vh;padding:24px}h1{font-size:32px}h2{font-size:20px}ul{font-size:20px}}@media print{body{background:white}.slide{display:block;margin:0;border:0;min-height:0;height:180mm;break-after:page;padding:12mm}nav,details{display:none}@page{size:A4 landscape;margin:10mm}}
</style></head><body>'''+''.join(sections)+'''<nav><button id="prev">Anterior</button><button id="next">Próximo</button><button id="all">Mostrar todos</button></nav><script>let current=0;const slides=[...document.querySelectorAll('.slide')];function show(n){current=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,i)=>s.classList.toggle('active',i===current));document.getElementById('prev').disabled=current===0;document.getElementById('next').disabled=current===slides.length-1;}document.getElementById('prev').onclick=()=>show(current-1);document.getElementById('next').onclick=()=>show(current+1);document.getElementById('all').onclick=()=>document.body.classList.toggle('all');document.addEventListener('keydown',e=>{if(e.key==='ArrowRight')show(current+1);if(e.key==='ArrowLeft')show(current-1)});show(0);</script></body></html>''')

print('Diagramas editáveis, snapshot S2 e apresentação HTML preparados.')
