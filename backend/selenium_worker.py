from xvfbwrapper import Xvfb
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from dotenv import load_dotenv
import pickle
import os
import time

load_dotenv()

BASE_URL = os.getenv("APP_URL")
LOGIN = os.getenv("APP_LOGIN")
PASSWORD = os.getenv("APP_PASSWORD")
COOKIE_FILE = "cookies.pkl"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def update_status(card_number: str, new_status: str):
    with Xvfb():
        try:
            log("Шаг 1: Инициализация браузера")
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            wait = WebDriverWait(driver, 15)

            log("Шаг 2: Открываю страницу логина")
            driver.get(f"{BASE_URL}/private/default/login")

            if os.path.exists(COOKIE_FILE):
                with open(COOKIE_FILE, "rb") as f:
                    cookies = pickle.load(f)
                    for cookie in cookies:
                        driver.add_cookie(cookie)
                driver.get(f"{BASE_URL}/private/default/index")

            if "login" in driver.current_url:
                log("→ Не авторизован. Ввожу логин и пароль")
                username_input = wait.until(EC.presence_of_element_located((By.ID, "loginform-username")))
                password_input = wait.until(EC.presence_of_element_located((By.ID, "loginform-password")))
                submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
                username_input.send_keys(LOGIN)
                password_input.send_keys(PASSWORD)
                submit_button.click()
                time.sleep(2)

                with open(COOKIE_FILE, "wb") as f:
                    pickle.dump(driver.get_cookies(), f)

            log("Шаг 3: Переход в раздел 'Заявления'")
            driver.get(f"{BASE_URL}/private/cards/list?form=30")
            wait.until(EC.presence_of_element_located((By.ID, "cardinfoforproducer-card_number")))

            log("Шаг 4: Ввод номера карты")
            input_field = driver.find_element(By.ID, "cardinfoforproducer-card_number")
            input_field.clear()
            input_field.send_keys(card_number + Keys.ENTER)
            log(f"→ Номер карты введён: {card_number}")

            wait.until(EC.presence_of_element_located((By.XPATH, f"//table//td[contains(text(), '{card_number}')]")))

            log("Шаг 5: Проверка статуса")
            status_cell = wait.until(EC.presence_of_element_located((By.XPATH, "//table//tbody/tr[1]/td[2]")))
            current_status = status_cell.text.strip()
            log(f"→ Статус: {current_status}")

            if current_status.lower() != "активна":
                raise Exception("Карта не выдана — статус не 'Активна'")

            log("Шаг 6: Изменение статуса")
            edit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.set-defective-btn")))
            edit_button.click()

            note_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.form-control.note-block")))
            note_field.clear()
            note_field.send_keys(new_status)
            log(f"→ Устанавливаю статус: {new_status}")

            submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Изменить')]")))
            submit_btn.click()
            log("→ Изменение отправлено")

        except Exception as e:
            log(f"❌ Ошибка: {e}")
        finally:
            driver.quit()
            log("✅ Браузер закрыт")