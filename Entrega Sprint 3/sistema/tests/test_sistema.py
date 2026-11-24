import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app import create_app
from models import db, ContaDAO
from services import salvar_conta, transferir, resgatar, creditar_semestre, salvar_vantagem, excluir_conta, documento_valido


class SistemaTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app({'TESTING':True,'SECRET_KEY':'test','DATABASE_URL':None,'DATABASE':str(Path(self.temp.name)/'test.sqlite3')})
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.app.test_cli_runner().invoke(args=['seed-demo'])
        self.professor = ContaDAO.por_email('professor@demo.local')['id']
        self.aluno = ContaDAO.por_email('aluno@demo.local')['id']
        self.empresa = ContaDAO.por_email('empresa@demo.local')['id']
        self.client = self.app.test_client()

    def tearDown(self):
        self.ctx.pop()
        self.temp.cleanup()

    def post(self,path,data=None):
        self.client.get('/login')
        with self.client.session_transaction() as session:
            csrf = session['csrf']
        return self.client.post(path,data={**(data or {}),'csrf':csrf},follow_redirects=True)

    def login(self,perfil):
        return self.post('/login',{'email':perfil+'@demo.local','senha':'Demo12345!'})

    def test_login_email_maiusculo(self):
        response = self.post('/login', {'email': '  ALUNO@DEMO.LOCAL  ', 'senha': 'Demo12345!'})
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as session:
            self.assertEqual(session.get('conta_id'), self.aluno)

    def preparar_resgate(self):
        creditar_semestre('2026-2')
        transferir(self.professor,self.aluno,200,'Participação')
        salvar_vantagem(self.empresa,{'descricao':'Lanche','foto':'https://example.com/lanche.jpg','custo':'50'})
        return db().execute('SELECT id FROM vantagens').fetchone()['id']

    def test_credito_acumulavel_idempotente(self):
        self.assertEqual(creditar_semestre('2026-1'),1)
        self.assertEqual(creditar_semestre('2026-1'),0)
        creditar_semestre('2026-2')
        self.assertEqual(ContaDAO.obter(self.professor)['saldo'],2000)

    def test_semestre_invalido(self):
        with self.assertRaises(ValueError): creditar_semestre('2026-3')

    def test_transferencia_e_notificacao(self):
        creditar_semestre('2026-2')
        transferir(self.professor,self.aluno,100,'Bom trabalho')
        self.assertEqual(ContaDAO.obter(self.professor)['saldo'],900)
        self.assertEqual(ContaDAO.obter(self.aluno)['saldo'],100)
        self.assertEqual(db().execute('SELECT count(*) FROM notificacoes').fetchone()[0],1)

    def test_saldo_insuficiente_sem_efeito(self):
        with self.assertRaises(ValueError): transferir(self.professor,self.aluno,1,'Mérito')
        self.assertEqual(db().execute('SELECT count(*) FROM transferencias').fetchone()[0],0)

    def test_valores_invalidos(self):
        for valor in ['0','-1','1.5','abc','1000000001']:
            with self.subTest(valor=valor), self.assertRaises(ValueError): transferir(self.professor,self.aluno,valor,'Mérito')

    def test_motivo_obrigatorio(self):
        with self.assertRaises(ValueError): transferir(self.professor,self.aluno,1,'  ')

    def test_instituicao_diferente(self):
        with db():
            db().execute("INSERT INTO instituicoes VALUES(2,'Outra instituição')")
            db().execute('UPDATE contas SET instituicao_id=2 WHERE id=?',(self.aluno,))
        with self.assertRaises(ValueError): transferir(self.professor,self.aluno,1,'Mérito')

    def test_resgate_codigo_compartilhado(self):
        id = self.preparar_resgate()
        codigo = resgatar(self.aluno,id)
        self.assertEqual(ContaDAO.obter(self.aluno)['saldo'],150)
        mensagens = db().execute("SELECT mensagem FROM notificacoes WHERE assunto LIKE '%resgate%'").fetchall()
        self.assertEqual(len(mensagens),2)
        self.assertTrue(all(codigo in item[0] for item in mensagens))

    def test_resgate_preserva_custo(self):
        id = self.preparar_resgate()
        resgatar(self.aluno,id)
        salvar_vantagem(self.empresa,{'descricao':'Lanche novo','foto':'https://example.com/a.jpg','custo':'80'},id)
        self.assertEqual(db().execute('SELECT valor FROM resgates').fetchone()[0],50)

    def test_documentos_verificadores(self):
        for numero, perfil in [('52998224725', 'aluno'), ('11222333000181', 'empresa')]:
            self.assertTrue(documento_valido(numero, perfil))
            self.assertFalse(documento_valido(numero[:-1] + str((int(numero[-1]) + 1) % 10), perfil))
        self.assertFalse(documento_valido('11111111111', 'professor'))

    def test_cupom_usado_apenas_pela_empresa_dona(self):
        vantagem = self.preparar_resgate()
        codigo = resgatar(self.aluno, vantagem)
        cupom = db().execute('SELECT id FROM resgates WHERE codigo=?', (codigo,)).fetchone()['id']
        self.login('aluno')
        self.assertEqual(self.post(f'/cupons/{cupom}/utilizar').status_code, 403)
        self.post('/sair')
        with db():
            db().execute("INSERT INTO contas(perfil,nome,email,documento,senha_hash) VALUES('empresa','Outra','outra@demo.local','99888777000166',?)", (ContaDAO.obter(self.empresa)['senha_hash'],))
        self.post('/login', {'email': 'outra@demo.local', 'senha': 'Demo12345!'})
        self.assertIn('não encontrado ou já utilizado', self.post(f'/cupons/{cupom}/utilizar').text)
        self.assertIsNone(db().execute('SELECT utilizado_em FROM resgates WHERE id=?', (cupom,)).fetchone()[0])
        self.post('/sair')
        self.login('empresa')
        self.assertIn(codigo, self.client.get('/').text)
        self.assertIn('Cupom marcado como utilizado', self.post(f'/cupons/{cupom}/utilizar').text)
        data = db().execute('SELECT utilizado_em FROM resgates WHERE id=?', (cupom,)).fetchone()[0]
        self.assertIsNotNone(data)
        self.assertIn('não encontrado ou já utilizado', self.post(f'/cupons/{cupom}/utilizar').text)
        self.assertEqual(db().execute('SELECT utilizado_em FROM resgates WHERE id=?', (cupom,)).fetchone()[0], data)

    def test_resgate_sem_saldo(self):
        salvar_vantagem(self.empresa,{'descricao':'Lanche','foto':'https://example.com/a.jpg','custo':'50'})
        with self.assertRaises(ValueError): resgatar(self.aluno,1)
        self.assertEqual(db().execute('SELECT count(*) FROM resgates').fetchone()[0],0)

    def test_atomicidade_falha_notificacao(self):
        id = self.preparar_resgate()
        with patch('services.notificar',side_effect=RuntimeError('Falha simulada')):
            with self.assertRaises(RuntimeError): resgatar(self.aluno,id)
        self.assertEqual(ContaDAO.obter(self.aluno)['saldo'],200)
        self.assertEqual(db().execute('SELECT count(*) FROM resgates').fetchone()[0],0)

    def test_crud_aluno_via_http(self):
        dados = {'nome':'Novo Aluno','email':'novo@demo.local','documento':'52998224725','rg':'123','endereco':'Rua A','curso':'Software','instituicao_id':'1','senha':'Teste12345!'}
        result = self.post('/cadastro/aluno',dados)
        self.assertIn('Cadastro concluído',result.text)
        self.post('/login',{'email':dados['email'],'senha':dados['senha']})
        result = self.client.get('/perfil')
        self.assertIn('Novo Aluno',result.text)
        result = self.post('/perfil',{**dados,'nome':'Nome Atualizado','senha':''})
        self.assertIn('Nome Atualizado',result.text)
        self.post('/perfil/excluir',{'senha':'Teste12345!'})
        self.assertIsNone(ContaDAO.por_email(dados['email']))

    def test_crud_empresa_via_http(self):
        dados = {'nome':'Loja Nova','email':'nova@demo.local','documento':'11222333000181','endereco':'Rua B','telefone':'31999999999','senha':'Teste12345!'}
        self.assertIn('Cadastro concluído',self.post('/cadastro/empresa',dados).text)
        self.post('/login',{'email':dados['email'],'senha':dados['senha']})
        self.assertIn('Loja Nova',self.client.get('/perfil').text)
        self.assertIn('Loja Atualizada',self.post('/perfil',{**dados,'nome':'Loja Atualizada','senha':''}).text)
        self.post('/perfil/excluir',{'senha':'Teste12345!'})
        self.assertIsNone(ContaDAO.por_email(dados['email']))

    def test_duplicidade_e_senha_hash(self):
        conta = ContaDAO.obter(self.aluno)
        self.assertNotEqual(conta['senha_hash'],'Demo12345!')
        with self.assertRaises(ValueError):
            salvar_conta({'nome':'Teste','email':conta['email'],'documento':'52998224725','rg':'1','endereco':'A','curso':'B','instituicao_id':'1','senha':'Teste12345!'},'aluno')

    def test_csrf(self):
        self.assertEqual(self.client.post('/login',data={'email':'a'}).status_code,400)

    def test_permissoes(self):
        self.login('aluno')
        self.assertEqual(self.post('/transferir',{'aluno_id':self.aluno,'valor':'1','motivo':'A'}).status_code,403)
        self.assertEqual(self.client.get('/vantagens/nova').status_code,403)

    def test_login_invalido(self):
        self.assertIn('E-mail ou senha inválidos',self.post('/login',{'email':'aluno@demo.local','senha':'errada'}).text)

    def test_precadastro_institucional_permite_login(self):
        runner = self.app.test_cli_runner()
        dados = 'Maria Silva\nMaria@example.org\n123.456.789-09\nComputação\n'
        senha = 'SenhaInicial123!'
        resultado = runner.invoke(args=['cadastrar-professor'], input=f'{dados}Instituição A\n{senha}\n{senha}\n')
        self.assertEqual(resultado.exit_code, 0, resultado.output)
        professor = ContaDAO.por_email('maria@example.org')
        self.assertEqual(professor['perfil'], 'professor')
        self.assertEqual(professor['documento'], '12345678909')
        self.assertEqual(professor['departamento'], 'Computação')
        self.assertNotEqual(professor['senha_hash'], senha)
        instituicao = db().execute('SELECT nome FROM instituicoes WHERE id=?', (professor['instituicao_id'],)).fetchone()
        self.assertEqual(instituicao['nome'], 'Instituição A')
        login = self.post('/login', {'email': 'maria@example.org', 'senha': senha})
        self.assertIn('Enviar moedas', login.text)

        duplicado = runner.invoke(args=['cadastrar-professor'], input=f'{dados}Instituição B\n{senha}\n{senha}\n')
        self.assertEqual(duplicado.exit_code, 1, duplicado.output)
        self.assertIn('já cadastrado', duplicado.output)
        self.assertIsNone(db().execute('SELECT id FROM instituicoes WHERE nome=?', ('Instituição B',)).fetchone())

    def test_privacidade_notificacoes(self):
        self.preparar_resgate()
        self.login('empresa')
        self.assertNotIn('Você recebeu moedas',self.client.get('/notificacoes').text)

    def test_exclusao_preserva_historico(self):
        id = self.preparar_resgate()
        resgatar(self.aluno,id)
        excluir_conta(self.empresa)
        self.assertEqual(db().execute('SELECT count(*) FROM resgates').fetchone()[0],1)
        with self.assertRaises(ValueError): resgatar(self.aluno,id)

    def test_empresa_nao_edita_vantagem_alheia(self):
        id = self.preparar_resgate()
        with db(): db().execute('UPDATE vantagens SET empresa_id=? WHERE id=?',(self.aluno,id))
        self.login('empresa')
        self.assertEqual(self.client.get(f'/vantagens/{id}/editar').status_code,404)

    def test_telas_principais(self):
        self.preparar_resgate()
        for perfil in ('aluno','empresa','professor'):
            self.login(perfil)
            self.assertEqual(self.client.get('/').status_code,200)
            self.assertEqual(self.client.get('/notificacoes').status_code,200)
            self.post('/sair')

    def test_envio_smtp_mock(self):
        self.preparar_resgate()
        with patch.dict('os.environ',{'SMTP_HOST':'smtp.demo.local','SMTP_USER':'demo','SMTP_PASSWORD':'secret','SMTP_FROM':'demo@demo.local'}), patch('commands.smtplib.SMTP') as smtp:
            result = self.app.test_cli_runner().invoke(args=['enviar-emails'])
            self.assertEqual(result.exit_code,0,result.output)
            smtp.return_value.__enter__.return_value.send_message.assert_called_once()
        self.assertEqual(db().execute('SELECT enviado FROM notificacoes').fetchone()[0],1)


if __name__ == '__main__':
    unittest.main()
