from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def update_status(card_number: str, new_status: str):
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=options)

        driver.get("http://10.78.78.251/private/default/login")
        time.sleep(1)

        # --- Логин ---
        driver.find_element(By.ID, "loginform-username").send_keys("your_login")
        driver.find_element(By.ID, "loginform-password").send_keys("your_password")
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # TODO: дальнейшие шаги по переходу, поиску, изменению статуса
        time.sleep(2)

    except Exception as e:
        print(f"[Selenium Error] {e}")

    finally:
        driver.quit()