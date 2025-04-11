import sys
import os
import requests
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QDialog, QLabel, QLineEdit, QFormLayout,
    QDateEdit, QFileDialog, QComboBox, QAbstractItemView
)
from PySide6.QtCore import Qt, QDate, QSettings, QTimer, QSize
from PySide6.QtGui import QColor, QIcon, QPixmap
from openpyxl import Workbook, load_workbook
from PySide6.QtWidgets import QSplashScreen, QHeaderView

os.chdir(os.path.dirname(__file__))

API_URL = "http://127.0.0.1:8000"
current_user = None

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.success = False
        self.setWindowTitle("Вход")
        self.setWindowIcon(QIcon("icon.ico"))
        layout = QVBoxLayout()

        # --- ЛОГОТИП ---
        logo_label = QLabel()
        logo_label = QLabel()
        pixmap = QPixmap(r"logo.png")

        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaledToWidth(300, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        else:
            print("❌ Логотип не загружен. Проверь путь: logo.png")

        # --- ФОРМА ЛОГИНА ---
        form_layout = QFormLayout()
        self.login_combo = QComboBox()
        form_layout.addRow("Логин:", self.login_combo)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Пароль:", self.password_input)

        layout.addLayout(form_layout)

        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.try_login)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

        # Загружаем список логинов динамически
        self.load_logins()

    def load_logins(self):
        try:
            resp = requests.get(f"{API_URL}/users")
            if resp.status_code == 200:
                logins = resp.json()
                print("Status code:", resp.status_code)
                print("Response text:", resp.text)
                self.login_combo.clear()
                self.login_combo.addItems(logins)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить список логинов с сервера")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки логинов: {e}")

    def try_login(self):
        global current_user
        login = self.login_combo.currentText().strip()
        password = self.password_input.text().strip()
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        try:
            resp = requests.post(f"{API_URL}/auth", json={"login": login, "password": password})
            if resp.status_code == 200:
                current_user = login
                self.success = True
                self.accept()
            else:
                QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


status_colors = {
    "Новый": QColor("lightgreen"),
    "В работе": QColor("gold"),
    "Ожидает": QColor("lightblue"),
    "Закрыт": QColor("lightgray")
}

status_icons = {
    "Новый": "🟢",
    "В работе": "🛠",
    "Ожидает": "⏳",
    "Закрыт": "✅"
}

# [...] ОПУЩЕНО ДЛЯ КРАТКОСТИ (без изменений)

    def adjust_table(self):
        header = self.table.horizontalHeader()
        settings = QSettings("MyCompany", "ReclamaciaApp")

        settings.beginGroup(f"column_widths/{current_user}")
        for i in range(self.table.columnCount()):
            width = settings.value(f"col_{i}", type=int)
            if width:
                self.table.setColumnWidth(i, width)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        settings.endGroup()

        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Interactive)

        self.table.setColumnWidth(0, 10)    # ID
        self.table.setColumnWidth(1, 85)    # Дата
        self.table.setColumnWidth(2, 180)   # № Карты
        self.table.setColumnWidth(3, 120)   # Фамилия
        self.table.setColumnWidth(4, 100)   # Имя
        self.table.setColumnWidth(5, 110)   # Отчество
        self.table.setColumnWidth(8, 110)   # Статус работы
        self.table.setColumnWidth(10, 100)  # Статус

        for col in [6, 7, 9, 11]:
            header.setSectionResizeMode(col, QHeaderView.Stretch)

        self.table.resizeRowsToContents()
        self.table.verticalHeader().setDefaultSectionSize(22)  # 👈 добавлено: уменьшение высоты строк