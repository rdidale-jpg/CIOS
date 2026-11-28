"""Exercise the native financial views on an isolated local Flora server."""
from argparse import ArgumentParser
from pathlib import Path
from shutil import which
import os
import sys
from tempfile import TemporaryDirectory
from threading import Thread
from http.server import ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import expect, sync_playwright

sys.path.insert(0, str(Path.cwd()))
from cios.applications.flora.web.app import FloraWebHandler


ENTERPRISE = '/enterprises/lloyds'
TOP_LEVEL = {
    'opening': '',
    'economics': '?focus=economics',
    'retail': '?focus=retail',
    'commercial': '?focus=commercial',
    'insurance': '?focus=retirement',
    'operating': '?stream=inside&focus=operations',
    'organisation': '?stream=inside&focus=people&detail=leadership',
    'technology': '?stream=inside&focus=applications',
    'agenda': '?stream=forces&focus=markets',
    'strategy': '?stream=forces&focus=strategy&detail=goals',
    'competition': '?stream=forces&focus=competition',
    'swot': '?stream=forces&focus=analysis',
}


def capture_top_level(page, output, phase):
    for name, query in TOP_LEVEL.items():
        assert page.goto(ENTERPRISE + query).status == 200
        page.evaluate('document.fonts.ready')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2')
        page.screenshot(path=output / f'{phase}-desktop-{name}.jpg', quality=82)


def check_executive_story(page, output, device):
    assert page.goto(ENTERPRISE).status == 200
    main = page.locator('main')
    opening = main.locator('.gold-executive-opening')
    for text in ('households, businesses and long-term savers', 'cash, trade and payments',
                 '£6.625bn', '+1,947m', '+851m', 'Below 45% cost/income', 'About £2bn gross savings'):
        expect(opening).to_contain_text(text)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2')
    page.screenshot(path=output / f'after-{device}-opening.jpg', quality=82)
    opening.get_by_role('link', name='Where earnings came from', exact=True).click()
    expect(main).to_contain_text('2,332')
    expect(main).to_contain_text('single-quarter comparisons')
    expect(main).to_contain_text('+64m')
    expect(main).to_contain_text('separate nine-month bridge')

    for business, label, first, follow, check in (
        ('retail', 'Retail mortgages', 'Lending & credit', 'Verify income and underwrite', 'Vertex AI'),
        ('commercial', 'Commercial transaction banking', 'Payments', 'Manage cash, trade and payments', 'Natasha Condon'),
        ('retirement', 'Insurance, pensions and wealth', 'Insurance, pensions & wealth',
         'Administer policies and investments', '84,000'),
    ):
        page.goto(ENTERPRISE + TOP_LEVEL['operating'])
        main.get_by_role('link', name=first, exact=True).click()
        rail = main.get_by_role('navigation', name=label, exact=True)
        expect(rail).to_be_visible()
        rail.get_by_role('link', name=follow, exact=True).click()
        assert parse_qs(urlsplit(page.url).query)['subject'] == [business]
        expect(main).to_contain_text(check)
        page.reload()
        expect(main).to_contain_text(check)
        page.go_back()
        expect(rail).to_be_visible()

    page.goto(ENTERPRISE + TOP_LEVEL['agenda'])
    main.get_by_role('link', name='Prepare for the executive decision', exact=True).click()
    for label in ('CFO · Sustainable earnings and capital', 'COO · Deliver change while protecting service',
                  'CEO · Grow customer activity and earn the investment'):
        expect(main.get_by_role('link', name=label, exact=True)).to_be_visible()
    main.get_by_role('link', name='COO · Deliver change while protecting service', exact=True).click()
    expect(main).to_contain_text('end-to-end completion')


def check_integration(page, output, device):
    assert page.goto(ENTERPRISE).status == 200
    main = page.locator('main')
    opening = main.locator('.gold-executive-opening')
    for amount in ('3,926', '+289', '−34', '+112', '4,293', '2,332', '6,625',
                   '+1,262', '+851', '−70', '−312', '−35', '+251'):
        expect(opening).to_contain_text(amount.replace('−', '-'))
    for route, numbers in (
        ('retail', ('27,574', 'income verification')),
        ('commercial', ('7,955', 'digitally')),
        ('retirement', ('6,025', '84,000')),
    ):
        assert page.goto(ENTERPRISE + '?focus=' + route).status == 200
        connection = main.locator('.gold-evidence-paths')
        for text in numbers:
            expect(connection).to_contain_text(text)
        connection.get_by_role('link', name='Operating detail').click()
        assert parse_qs(urlsplit(page.url).query)['subject'] == [route]
        expect(main.locator('.gold-evidence-paths')).to_be_visible()
        page.reload()
        expect(main.locator('.gold-evidence-paths')).to_be_visible()
        page.go_back()
        expect(main.locator('.gold-evidence-paths')).to_contain_text(numbers[0])
    assert page.goto(ENTERPRISE).status == 200
    opening.get_by_role('link', name='Strategy and reported progress').click()
    assert parse_qs(urlsplit(page.url).query)['detail'] == ['goals']
    expect(main.locator('.gold-evidence-paths')).to_contain_text('Cost efficiency and investment')
    expect(main.locator('.gold-evidence-paths')).to_contain_text('Payments growth and customer use')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2')
    page.screenshot(path=output / f'after-{device}-strategy.jpg', quality=82)
    assert page.goto(ENTERPRISE + TOP_LEVEL['swot']).status == 200
    expect(main).to_contain_text('Business SWOT in evidence')
    expect(main).to_contain_text('Payment competition and substitutes')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2')
    page.screenshot(path=output / f'after-{device}-swot.jpg', quality=82)
    assert page.goto(ENTERPRISE + TOP_LEVEL['competition']).status == 200
    peer = main.get_by_role('heading', name='Customer service across named UK banks').locator('..')
    for count in ('118,762', '90,678', '79,323', '92,548'):
        expect(peer).to_contain_text(count)
    peer.get_by_role('link', name='Inspect the UK Banking evidence').click()
    assert urlsplit(page.url).path == '/industries/banking'
    expect(page.locator('main')).to_contain_text('90,678')
    page.go_back()
    expect(peer).to_contain_text('118,762')


def check(base_url, output, browser, phase):
    for name, width, height in (('desktop', 1440, 1000), ('ipad-landscape', 1366, 1024),
                                ('ipad-portrait', 1024, 1366), ('mobile', 390, 844)):
        page = browser.new_page(base_url=base_url, viewport={'width': width, 'height': height},
                                has_touch=name != 'desktop')
        if name == 'desktop':
            capture_top_level(page, output, phase)
        if phase == 'before':
            for view in ('opening', 'strategy', 'swot'):
                assert page.goto(ENTERPRISE + TOP_LEVEL[view]).status == 200
                page.evaluate('document.fonts.ready')
                page.screenshot(path=output / f'before-{name}-{view}.jpg', quality=82)
            page.close()
            continue
        check_executive_story(page, output, name)
        check_integration(page, output, name)
        income = '/enterprises/lloyds?focus=economics&detail=income'
        assert page.goto(income).status == 200
        expect(page.locator('main')).to_contain_text('1,947')
        expect(page.locator('main h3').get_by_text('Income to statutory profit')).to_be_visible()
        page.evaluate('document.fonts.ready')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=output / (name + '.jpg'), quality=82)
        target = page.get_by_role('link', name='Income to statutory profit', exact=False)
        if name == 'desktop':
            target.focus()
            page.keyboard.press('Enter')
        else:
            target.tap()
        expect(page.locator('#financial-evidence')).to_be_visible()
        assert 'detail=sources' in page.url
        page.reload()
        expect(page.locator('#financial-evidence')).to_contain_text('EDGAR')
        page.go_back()
        expect(page.locator('main')).to_contain_text('1,947')
        assert page.goto('/enterprises/lloyds?focus=economics&detail=divisions').status == 200
        expect(page.locator('main')).to_contain_text('4,293')
        assert page.goto('/enterprises/lloyds?focus=commercial').status == 200
        expect(page.locator('main')).to_contain_text('1,425')
        assert page.goto('/enterprises/lloyds?stream=forces&focus=strategy&detail=objective-efficiency').status == 200
        expect(page.locator('main')).to_contain_text('FY2026 guidance')
        expect(page.locator('main')).to_contain_text('49.3%')
        expect(page.locator('main')).to_contain_text('17.9%')
        expect(page.locator('main')).to_contain_text('nine-month actuals are a checkpoint only')
        for route in ('/industries/banking', '/industries/aviation', '/enterprises/easyjet',
                      '/enterprises/lloyds/legacy', '/enterprises/lloyds/preview'):
            assert page.goto(route).status == 200
        page.close()
        print(name, 'passed', flush=True)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('output', type=Path)
    parser.add_argument('--before', action='store_true')
    args = parser.parse_args()
    captures = args.output
    captures.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix='flora-financial-browser-') as runtime, sync_playwright() as playwright:
        os.environ.update(FLORA_DATA_DIR=runtime, FLORA_ENVIRONMENT='development',
                          FLORA_AUTH_PROVIDER='local', FLORA_TRUST_PROXY_HEADERS='0')
        os.environ.pop('OPENAI_API_KEY', None)
        with ThreadingHTTPServer(('127.0.0.1', 0), FloraWebHandler) as server:
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                browser = playwright.chromium.launch(executable_path=which('chromium'))
                check(f'http://127.0.0.1:{server.server_port}', captures, browser, 'before' if args.before else 'after')
                browser.close()
            finally:
                server.shutdown()
                thread.join()
