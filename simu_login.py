import os, time, json

from playwright.sync_api import sync_playwright

PROXY = 'http://127.0.0.1:1081'

LOGIN_URL = r'https://accounts.pixiv.net/login?return_to=https%3A%2F%2Fwww.pixiv.net%2F&lang=zh&source=pc&view_type=page'

def login_for_cookies() -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(proxy={'server': PROXY})
        page = context.new_page()

        page.goto(LOGIN_URL)
        username_e = page.get_by_placeholder('邮箱地址或pixiv ID')
        password_e = page.get_by_placeholder('密码')
        button_e = page.get_by_role('button', name='登录')

        username_e.hover()
        username_e.click()
        time.sleep(1)
        username_e.fill(os.environ['GMAIL_ADDRESS'])
        password_e.fill(os.environ['DEFAULT_PW'])
        time.sleep(2)
        button_e.click()

        page.wait_for_selector('#root')
        cookies = {}
        for cookie in context.cookies():
            cookies[cookie['name']] = cookie['value']
        
        context.close()
        browser.close()
        return cookies
    
def save_and_return_cookies() -> dict:
    cookies: dict = login_for_cookies()
    with open('cookies.json', 'w') as f:
        json.dump(cookies, f)
    return cookies

if __name__ == '__main__':
    save_and_return_cookies()