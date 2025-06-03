#backend/selenium_worker.py
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
import time
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("APP_URL")
LOGIN = os.getenv("APP_LOGIN")
PASSWORD = os.getenv("APP_PASSWORD")

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def update_status(card_number: str, new_status: str):
    try:
        log("Шаг 1: Инициализация браузера")
        options = Options()
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 15)

        log("Шаг 2: Открываю страницу логина")
        driver.get(f"{BASE_URL}/private/default/login")
        time.sleep(1)

        log("Шаг 3: Ожидание полей логина")
        username_input = wait.until(EC.presence_of_element_located((By.ID, "loginform-username")))
        password_input = wait.until(EC.presence_of_element_located((By.ID, "loginform-password")))
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))

        log("Шаг 4: Ввожу логин и пароль...")
        username_input.send_keys(LOGIN)
        password_input.send_keys(PASSWORD)
        submit_button.click()
        time.sleep(1)

        log("Шаг 5: Проверяю появление модального окна (если есть)")
        try:
            modal_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-default.btn-blue"))
            )
            log("→ Модальное окно появилось. Подтверждаю вход...")
            modal_button.click()
            time.sleep(1)
        except TimeoutException:
            log("→ Модального окна не появилось — продолжаем.")

        log("Шаг 6: Проверка, что загрузилась основная панель")
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Основная панель')]")))
        log("→ Основная панель загружена")
        time.sleep(1)

        log("Шаг 7: Переход в раздел 'Заявления' — сначала через execute_script")
        try:
            driver.execute_script(f"window.location.href = '{BASE_URL}/private/cards/list?form=30'")
            time.sleep(3)
            wait.until(EC.presence_of_element_located((By.ID, "cardinfoforproducer-card_number")))
            log("→ Переход сработал через execute_script")
        except Exception as e:
            log(f"⚠ Не удалось через execute_script: {e}")
            log("→ Пробуем через клик по меню...")
            try:
                menu_link = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Заявление на карту водителя')]"))
                )
                menu_link.click()
                time.sleep(3)
                wait.until(EC.presence_of_element_located((By.ID, "cardinfoforproducer-card_number")))
                log("→ Переход по клику выполнен успешно")
            except Exception as e2:
                raise Exception(f"❌ Не удалось открыть раздел ни одним способом: {e2}")

        log("Шаг 8: Ввод номера карты")
        input_field = driver.find_element(By.ID, "cardinfoforproducer-card_number")
        input_field.clear()
        input_field.send_keys(card_number + Keys.ENTER)
        log(f"→ Номер карты введён: {card_number}")

        wait.until(EC.presence_of_element_located((By.XPATH, f"//table//td[contains(text(), '{card_number}')]")))
        time.sleep(1)

        log("Шаг 9: Проверка статуса из таблицы (td[2])")
        status_cell = wait.until(
            EC.presence_of_element_located((By.XPATH, "//table//tbody/tr[1]/td[2]"))
        )
        current_status = status_cell.text.strip()
        log(f"→ Статус карты: {current_status}")

        log("Шаг 10: Проверка соответствия статусу")
        if current_status.lower() != "активна":
            raise Exception("Карта не выдана — статус не 'Активна'")

        log("→ Статус 'Активна'. Переходим к изменению...")

        log("Шаг 11: Кликаю на кнопку 'Set defective'")
        edit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.set-defective-btn")))
        edit_button.click()
        time.sleep(1)

        log("Шаг 12: Ввожу 'Гарантия' в модальном окне")
        note_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.form-control.note-block")))
        note_field.clear()
        note_field.send_keys("Гарантия")
        time.sleep(1)

        log("Шаг 13: Нажимаю кнопку 'Изменить'")
        submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Изменить')]")))
        submit_btn.click()
        log("→ Изменение успешно отправлено")

    except Exception as e:
        log(f"❌ Ошибка: {e}")

    finally:
        time.sleep(1)
        driver.quit()
        log("✅ Браузер закрыт.")

if __name__ == "__main__":
    test_card = "RUD0000259991000"
    test_status = "Гарантия"
    update_status(test_card, test_status)