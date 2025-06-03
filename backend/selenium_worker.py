from xvfbwrapper import Xvfb
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def update_status(card_number, new_status):
    with Xvfb():
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get("http://10.78.78.251/private/default/login")
            # Здесь следует разместить остальной код логики авторизации и обновления статуса

        finally:
            driver.quit()