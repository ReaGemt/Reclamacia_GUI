# Reclamacia_GUI

## 📦 Установка

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## ⚙️ Настройка окружения
Создайте файл `.env`:

```
APP_URL=https://example.com
APP_LOGIN=your_login
APP_PASSWORD=your_password
```

## 🚀 Запуск

### 1. Инициализация базы данных:
```bash
python init_db.py
```

### 2. Запуск backend-сервера:
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Тестовый запуск selenium вручную:
```bash
python backend/selenium_worker.py
```

## 🧰 Полезные команды

Установка webdriver-manager:
```bash
pip install webdriver-manager
```

Обновление зависимостей:
```bash
pip freeze > requirements.txt
```

## 📝 Заметки
- Логика кнопок в `frontend/main.py`
- Обработка selenium — в `backend/selenium_worker.py`
- REST API — в `backend/routes.py`
- Инициализация БД — `init_db.py`