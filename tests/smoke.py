"""Recorridos funcionales: requiere servidor en el puerto 8000, Playwright y Chromium."""
import json
import os
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

BASE = os.environ.get('DERMA_TEST_URL', 'http://127.0.0.1:8000')
ROOT = Path(__file__).resolve().parents[1]

with sync_playwright() as p:
    executable = os.environ.get('DERMA_CHROMIUM') or shutil.which('chromium')
    browser = p.chromium.launch(headless=True, **({'executable_path': executable} if executable else {}))
    context = browser.new_context(viewport={'width':1440, 'height':1000}, accept_downloads=True)
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(BASE)
    expect(page.locator('#nav a')).to_have_count(2)
    assert page.title() == 'Derma · Tu espacio de estudio'
    page.goto(BASE + '/#temario')
    expect(page.locator('.topic-card')).to_have_count(14)
    page.locator('#topic-search').fill('melanogenesis')
    expect(page.locator('.topic-card')).to_have_count(2)
    page.locator('.topic-card').filter(has=page.get_by_role('heading', name='La melanogénesis', exact=True)).click()
    expect(page.locator('h1')).to_have_text('La melanogénesis')
    page.locator('#complete').click()
    page.reload()
    expect(page.locator('#complete')).to_have_text('✓ Tema completado')
    page.goto(BASE+'/#tema/epidermis')
    page.locator('[data-layer="2"]').click()
    expect(page.locator('.layer-info h3')).to_have_text('Hipodermis')
    page.goto(BASE+'/#tarjetas/epidermis')
    page.locator('#reveal-card').click()
    page.locator('#known-card').click()
    assert page.evaluate("Object.values(JSON.parse(localStorage.getItem('derma-estudio-v1')).cards).includes('known')")
    print('PASS: temario, búsqueda, capas, progreso persistente y tarjetas')

    page.goto(BASE+'/#practica/epidermis')
    page.locator('#start-quiz').click()
    count = 0
    while page.locator('[data-answer]').count():
        question = page.locator('.quiz-card h2').inner_text()
        answer = page.evaluate('(text) => COURSE.questions.find(q=>q.q===text).a', question)
        options = page.locator('.option')
        if count == 0:
            choice = next(b for b in options.all() if b.locator('span').nth(1).inner_text() != answer)
            choice.click()
            expect(page.locator('.feedback')).to_have_class('feedback wrong')
        else:
            choice = next(b for b in options.all() if b.locator('span').nth(1).inner_text() == answer)
            choice.click()
            expect(page.locator('.feedback')).to_have_class('feedback ')
        page.locator('#next-question').click()
        count += 1
    assert count == 6
    expect(page.locator('.result-score')).to_have_text('5/6')
    saved = page.evaluate("JSON.parse(localStorage.getItem('derma-estudio-v1'))")
    assert len(saved['mistakes'])==1 and saved['history'][0]['total']==6
    page.goto(BASE+'/#practica')
    for i in range(6):
        page.locator(f'[data-left="{i}"]').click()
        page.locator(f'[data-right="{i}"]').click()
    expect(page.locator('#match-status')).to_have_text('¡Todas las parejas correctas!')
    print('PASS: ronda de 6 preguntas, resultado, errores y mini-reto')

    page.goto(BASE+'/#examen')
    page.locator('#submit-exam').click()
    expect(page.locator('#exam-warning')).to_contain_text('Quedan 14 temas')
    test_text = 'La piel es un órgano vivo. <img src=x onerror="window.INJECTED=true">'
    page.locator('#essay-answer').fill(test_text)
    page.reload()
    expect(page.locator('#essay-answer')).to_have_value(test_text)
    ids = page.evaluate('COURSE.lessons.map(l=>l.id)')
    for i, topic in enumerate(ids):
        page.locator(f'[data-essay="{i}"]').click()
        page.locator('#essay-answer').fill(test_text if i == 0 else f'Respuesta personal del tema {i+1}: conceptos, relaciones y ejemplos.')
    expect(page.locator('#exam-count')).to_have_text('14 / 14')
    page.locator('#submit-exam').click()
    expect(page.locator('.essay-review')).to_have_count(14)
    assert not page.evaluate('Boolean(window.INJECTED)')
    expect(page.locator('.written-answer').first).to_have_text(test_text)
    assert len(page.locator('[data-rubric]').all()) == 79
    page.locator('[data-rubric]').first.check()
    page.reload()
    expect(page.locator('[data-rubric]').first).to_be_checked()
    with page.expect_download() as download_info:
        page.locator('#download-exam').click()
    text = Path(download_info.value.path()).read_text()
    assert 'TEMA 14.' in text and test_text in text and 'GUÍA BASADA EN LOS PDF' in text
    # Forzar la ruta alternativa de copia manual, también necesaria en file://.
    page.evaluate("Object.defineProperty(navigator,'clipboard',{configurable:true,value:undefined})")
    page.locator('#copy-prompt').click()
    expect(page.locator('#clipboard-fallback')).to_be_visible()
    prompt = page.locator('#prompt-text').input_value()
    assert 'TEMA 14.' in prompt and 'Actúa como tutor' in prompt
    page.locator('#edit-exam').click()
    expect(page.locator('#essay-answer')).to_be_visible()
    assert page.evaluate("Object.keys(JSON.parse(localStorage.getItem('derma-estudio-v1')).exam.checks).length") == 0
    print('PASS: examen completo, autoguardado, bloqueo de temas vacíos, guía, exportación, copia y edición')

    page.goto(BASE+'/#biblioteca')
    page.locator('#slide-select').select_option('35')
    expect(page.locator('#slide-counter')).to_have_text('35 / 35')
    expect(page.locator('#next-slide')).to_be_disabled()
    page.locator('#doc-search').fill('melanina')
    assert page.locator('.search-result').count()>0
    for file in ['apuntes','diapositivas']:
        r=context.request.get(BASE+f'/assets/docs/{file}.pdf')
        assert r.ok and r.body().startswith(b'%PDF')
    for i in range(1,36):
        assert context.request.get(BASE+f'/assets/slides/{i}.webp').ok
    print('PASS: documentos originales, 35 imágenes y búsqueda documental')

    page.goto(BASE+'/#progreso')
    with page.expect_download() as info:
        page.locator('#export-progress').click()
    backup=Path(info.value.path()).read_bytes()
    page.locator('#reset').click()
    page.locator('#cancel-reset').click()
    assert page.evaluate("JSON.parse(localStorage.getItem('derma-estudio-v1')).completed.length") == 1
    page.locator('#reset').click()
    page.locator('#confirm-reset').click()
    assert page.evaluate("JSON.parse(localStorage.getItem('derma-estudio-v1')).completed.length") == 0
    page.locator('#import-progress').set_input_files({'name':'backup.json','mimeType':'application/json','buffer':backup})
    expect(page.locator('#import-dialog')).to_be_visible()
    page.locator('#confirm-import').click()
    assert page.evaluate("JSON.parse(localStorage.getItem('derma-estudio-v1')).completed.length") == 1
    invalid=json.loads(backup)
    invalid['history'][0]['correct']='<img src=x onerror=alert(1)>'
    page.locator('#import-progress').set_input_files({'name':'invalid.json','mimeType':'application/json','buffer':json.dumps(invalid).encode()})
    expect(page.locator('#toast')).to_contain_text('no es válida')
    assert not page.locator('#import-dialog').is_visible()
    print('PASS: copia/restauración validada y confirmación al borrar')

    for width in [390,768,1440]:
        page.set_viewport_size({'width':width,'height':844})
        for route in ['estudio','temario','tema/estratos','tarjetas','practica','examen','progreso','biblioteca']:
            page.goto(BASE+'/#'+route)
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'), f'Overflow {width} {route}'
    page.set_viewport_size({'width':1440,'height':1000})
    page.goto(BASE+'/#estudio')
    page.screenshot(path='/workspace/artifacts/derma-escritorio.png',full_page=True)
    page.goto(BASE+'/#examen')
    page.screenshot(path='/workspace/artifacts/derma-examen.png',full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    page.screenshot(path='/workspace/artifacts/derma-movil.png',full_page=True)
    assert not errors, errors
    # Validar los recursos sin red: servirlos desde disco mediante rutas interceptadas.
    # file:// no está permitido por la política del Chromium de este entorno.
    offline = browser.new_context(offline=True)
    def local_route(route):
        from urllib.parse import urlparse, unquote
        path = unquote(urlparse(route.request.url).path).lstrip('/') or 'index.html'
        file = (ROOT/path).resolve()
        if file.is_relative_to(ROOT) and file.is_file():
            route.fulfill(path=str(file))
        else:
            route.abort()
    offline.route('**/*', local_route)
    local = offline.new_page()
    local.goto(BASE)
    expect(local.locator('h1')).to_contain_text('Aprender')
    local.locator('a[href="#temario"]').first.click()
    expect(local.locator('.topic-card')).to_have_count(14)
    local.goto(BASE+'/#examen')
    local.locator('#essay-answer').fill('Respuesta sin conexión.')
    local.reload()
    expect(local.locator('#essay-answer')).to_have_value('Respuesta sin conexión.')
    browser.close()
    print('PASS: 24 vistas responsive, cero errores JavaScript y recursos locales sin red')
    print('NO EJECUTADO: apertura file://, bloqueada por la política del navegador del entorno')
