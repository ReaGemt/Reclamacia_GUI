import sys
import hashlib
from getpass import getpass
#from database import get_connection
#from .database import get_connection #Пишем так для ручного создания нового пользователя
from backend.database import get_connection

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(login: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (login, password_hash) VALUES (?, ?)",
                       (login, hash_password(password)))
        conn.commit()
        print(f"[+] Пользователь '{login}' успешно добавлен.")
    except Exception as e:
        print(f"[!] Ошибка: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        login = sys.argv[1]
        password = getpass("Введите пароль: ")
        confirm = getpass("Повторите пароль: ")
        if password != confirm:
            print("[!] Пароли не совпадают.")
            sys.exit(1)
        create_user(login, password)
    else:
        print("Использование: python cli_add_user.py <login>")
