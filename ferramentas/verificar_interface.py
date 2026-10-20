"""QA opcional: pip install playwright; usa Chrome instalado e banco temporário."""
import sys
import tempfile
import threading
from pathlib import Path
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Entrega Sprint 3/sistema'))
from app import create_app
from services import creditar_semestre

out = ROOT/'tmp/qa'
out.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory() as temporary:
    app = create_app({'DATABASE':str(Path(temporary)/'qa.sqlite3'),'SECRET_KEY':'qa-local'})
    app.test_cli_runner().invoke(args=['seed-demo'])
    with app.app_context(): creditar_semestre('2026-2')
    server = make_server('127.0.0.1',5059,app,threaded=True)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel='chrome',headless=True)
            page = browser.new_page(viewport={'width':1366,'height':900})
            errors=[]
            page.on('pageerror',lambda error: errors.append(str(error)))
            page.goto('http://127.0.0.1:5059')
            page.screenshot(path=str(out/'login.png'),full_page=True)
            def login(perfil):
                page.goto('http://127.0.0.1:5059/login')
                page.get_by_label('E-mail',exact=True).fill(perfil+'@demo.local')
                page.get_by_label('Senha',exact=True).fill('Demo12345!')
                page.get_by_role('button',name='Entrar',exact=True).click()
            def sair(): page.get_by_role('button',name='Sair',exact=True).click()
            login('empresa')
            page.get_by_role('link',name='Cadastrar vantagem',exact=True).click()
            page.get_by_label('Descrição').fill('Desconto no lanche da cantina')
            page.get_by_label('URL da foto').fill('http://127.0.0.1:5059/static/demo-lanche.svg')
            page.get_by_label('Custo em moedas').fill('50')
            page.get_by_role('button',name='Salvar vantagem').click()
            sair()
            login('professor')
            page.locator('select[name="aluno_id"]').select_option(label='Aluno Demo')
            page.get_by_label('Quantidade',exact=True).fill('100')
            page.get_by_label('Motivo do reconhecimento').fill('Participação na atividade')
            page.get_by_role('button',name='Enviar moedas',exact=True).click()
            assert '900' in page.locator('.saldo').inner_text()
            page.screenshot(path=str(out/'professor.png'),full_page=True)
            sair()
            login('aluno')
            assert '100' in page.locator('.saldo').inner_text()
            page.get_by_role('button',name='Resgatar vantagem',exact=True).click()
            assert '50' in page.locator('.saldo').inner_text()
            assert 'Cupom:' in page.locator('table').inner_text()
            page.screenshot(path=str(out/'aluno.png'),full_page=True)
            page.set_viewport_size({'width':390,'height':844})
            page.screenshot(path=str(out/'aluno-mobile.png'),full_page=True)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            page.get_by_role('link',name='Meu cadastro').click()
            page.get_by_label('Nome *',exact=True).fill('Aluno Demo Atualizado')
            page.get_by_role('button',name='Salvar alterações').click()
            assert page.get_by_label('Nome *',exact=True).input_value()=='Aluno Demo Atualizado'
            page.screenshot(path=str(out/'cadastro-mobile.png'),full_page=True)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            sair()
            login('empresa')
            page.get_by_role('link',name='Notificações').click()
            assert 'Conferência de resgate' in page.locator('main').inner_text()
            page.screenshot(path=str(out/'notificacao.png'),full_page=True)
            page.set_viewport_size({'width':1280,'height':820})
            page.goto((ROOT/'Entrega Sprint 3/apresentacao.html').as_uri())
            for i in range(12):
                page.screenshot(path=str(out/f'slide-{i+1:02}.png'),full_page=True)
                if i<11: page.get_by_role('button',name='Próximo',exact=True).click()
            assert not errors,errors
            browser.close()
    finally:
        server.shutdown()
print('QA visual: fluxo empresa > professor > aluno > empresa, edição de cadastro, 390px, 12 slides e zero erros JS: OK.')
