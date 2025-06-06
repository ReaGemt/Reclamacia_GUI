## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Пример .env файла

```env
APP_URL=https://example.com
APP_LOGIN=admin
APP_PASSWORD=password
```

## Импорт данных из Excel

Перед первым запуском выполните инициализацию базы данных:

```bash
python init_db.py
```

## Запуск Backend

```bash
uvicorn backend.main:app --port 8000
```

## Запуск GUI

```bash
python frontend/main.py
```

## Пример вызова selenium из API

```bash
curl -X POST "http://127.0.0.1:8000/selenium" -H "Content-Type: application/json" -d '{"card_number": "RUD0000000000000", "new_status": "Гарантия"}'
```

## 🗂 Структура проекта

```
├── backend/              # Backend: FastAPI, SQLAlchemy, Selenium
│   ├── main.py           # Точка входа для backend-приложения
│   ├── routes.py         # Определения REST API маршрутов
│   ├── admin.py          # Интерфейс администратора (sqladmin)
│   └── selenium_worker.py  # Автоматизация через браузер
│
├── frontend/             # GUI: PySide6
│   └── main.py           # Основная логика интерфейса
│
├── init_db.py            # Скрипт инициализации базы данных
├── requirements.txt      # Зависимости проекта
├── README.md             # Инструкции и документация
└── .env                  # Конфигурация (не включается в git)
```