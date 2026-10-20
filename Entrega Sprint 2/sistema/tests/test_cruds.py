import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app import create_app
from models import db, ContaDAO
from services import salvar_conta, transferir, resgatar, creditar_semestre, salvar_vantagem, excluir_conta


class SistemaTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app({'TESTING':True,'SECRET_KEY':'test','DATABASE':str(Path(self.temp.name)/'test.sqlite3')})
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

    def test_crud_aluno_via_http(self):
        dados = {'nome':'Novo Aluno','email':'novo@demo.local','documento':'12345678901','rg':'123','endereco':'Rua A','curso':'Software','instituicao_id':'1','senha':'Teste12345!'}
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
        dados = {'nome':'Loja Nova','email':'nova@demo.local','documento':'12345678901234','endereco':'Rua B','telefone':'31999999999','senha':'Teste12345!'}
        self.assertIn('Cadastro concluído',self.post('/cadastro/empresa',dados).text)
        self.post('/login',{'email':dados['email'],'senha':dados['senha']})
        self.assertIn('Loja Nova',self.client.get('/perfil').text)
        self.assertIn('Loja Atualizada',self.post('/perfil',{**dados,'nome':'Loja Atualizada','senha':''}).text)
        self.post('/perfil/excluir',{'senha':'Teste12345!'})
        self.assertIsNone(ContaDAO.por_email(dados['email']))

    def test_csrf(self):
        self.assertEqual(self.client.post('/login',data={'email':'a'}).status_code,400)

    def test_login_invalido(self):
        self.assertIn('E-mail ou senha inválidos',self.post('/login',{'email':'aluno@demo.local','senha':'errada'}).text)

    def test_duplicidade_e_senha_hash(self):
        conta = ContaDAO.obter(self.aluno)
        self.assertNotEqual(conta['senha_hash'],'Demo12345!')
        with self.assertRaises(ValueError):
            salvar_conta({'nome':'Teste','email':conta['email'],'documento':'12345678901','rg':'1','endereco':'A','curso':'B','instituicao_id':'1','senha':'Teste12345!'},'aluno')
