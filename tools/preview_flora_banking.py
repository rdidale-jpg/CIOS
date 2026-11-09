"""Optional local browser acceptance and screenshots for the Banking Explorer.

Requires Playwright and Chromium; targets a running *local* FLORA instance.
Not a production probe and not a replacement for the standard CI gate.
"""
import argparse
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8765')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--chromium', default='/usr/bin/chromium')
    args = parser.parse_args()
    target = urlsplit(args.url)
    if target.scheme != 'http' or target.hostname not in {'127.0.0.1', 'localhost'}:
        parser.error('Preview must target a local HTTP instance')
    args.output.mkdir(parents=True, exist_ok=True)
    root = '/flora/banking/explorer'
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=args.chromium, headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(args.url)
        page.get_by_role('link', name='Banking Explorer', exact=False).first.click()
        page.get_by_role('heading', name='Banking.').wait_for()
        page.get_by_role('link', name='Lloyds Banking Group', exact=False).first.click()
        page.get_by_role('heading', name='Lloyds Banking Group', exact=True).wait_for()
        page.locator('svg a').first.click()
        page.get_by_role('heading', name='Make the reasoning inspectable.').wait_for()
        page.get_by_text('What would validate or change this insight?', exact=True).first.click()
        assert page.get_by_role('heading', name='Disconfirming signals').first.is_visible()
        for viewport, width, height in [('desktop', 1440, 1000), ('mobile', 390, 844)]:
            page.set_viewport_size({'width': width, 'height': height})
            for name, path in [('industry', root), ('enterprise', root+'/lloyds'),
                               ('insights', root+'/lloyds/insights')]:
                page.goto(args.url + path)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), name
                page.screenshot(path=str(args.output/f'{name}-{viewport}.png'), full_page=True)
        page.goto(args.url + root+'/lloyds')
        page.locator('.ex-map-mobile').get_by_role('link', name='Customer & service', exact=False).click()
        page.get_by_role('heading', name='Make the reasoning inspectable.').wait_for()
        page.goto(args.url + root)
        # Skip link must work for keyboard users, not just pointer interaction.
        for _ in range(20):
            page.keyboard.press('Tab')
            if page.locator('.ex-skip').evaluate('(node) => node === document.activeElement'):
                break
        else:
            raise AssertionError('Explorer skip link is not keyboard reachable')
        page.keyboard.press('Enter')
        assert page.url.endswith('#explorer-content')
        assert not errors, errors
        browser.close()
    print('PASS: desktop/mobile journey, SVG/mobile links, disclosure, keyboard skip, no overflow or JS errors; six previews.')


if __name__ == '__main__':
    main()
