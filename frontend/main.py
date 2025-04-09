#frontend/main.py
import sys
import requests
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QDialog, QLabel, QLineEdit, QFormLayout,
    QDateEdit, QFileDialog, QComboBox, QAbstractItemView
)
from PySide6.QtCore import QDate, QSettings
from PySide6.QtGui import QColor
from openpyxl import Workbook, load_workbook
import sys

API_URL = "http://127.0.0.1:8000"
current_user = None

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход")
        layout = QFormLayout()

        self.login_combo = QComboBox()
        layout.addRow("Логин:", self.login_combo)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Пароль:", self.password_input)

        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.try_login)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)
        self.success = False

        # Загружаем список логинов динамически
        self.load_logins()

    def load_logins(self):
        try:
            resp = requests.get(f"{API_URL}/users")
            if resp.status_code == 200:
                # Ожидаем, что сервер вернет список логинов в формате JSON, например:
                # ["admin", "user1", "user2"]
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

class RecordDialog(QDialog):
    def __init__(self, parent=None, record=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать запись" if record else "Добавить запись")
        self.record_id = record.get("id") if record else None

        layout = QFormLayout()
        self.inputs = {}

        self.fields = [
            "record_date", "card_number", "last_name", "first_name", "patronymic",
            "organization", "manufacturer", "work_status", "comment"
        ]

        labels = {
            "record_date": "Дата",
            "card_number": "№ карты",
            "last_name": "Фамилия",
            "first_name": "Имя",
            "patronymic": "Отчество",
            "organization": "Организация",
            "manufacturer": "Производитель",
            "work_status": "Статус работы",
            "comment": "Комментарий"
        }

        for field in self.fields:
            if field == "record_date":
                date_edit = QDateEdit()
                date_edit.setCalendarPopup(True)
                if record:
                    date = QDate.fromString(record.get(field, ""), "yyyy-MM-dd")
                    date_edit.setDate(date if date.isValid() else QDate.currentDate())
                else:
                    date_edit.setDate(QDate.currentDate())
                layout.addRow(QLabel(labels.get(field, field)), date_edit)
                self.inputs[field] = date_edit

            elif field == "manufacturer":
                combo = QComboBox()
                combo.addItem("")
                combo.addItems([
                    "ООО \"ИКЦ Транспортные Технологии\"",
                    "АО НТЦ \"Спецпроект\""
                ])
                if record:
                    idx = combo.findText(record.get(field, ""))
                    if idx >= 0:
                        combo.setCurrentIndex(idx)
                layout.addRow(QLabel(labels.get(field, field)), combo)
                self.inputs[field] = combo

            elif field == "work_status":
                combo = QComboBox()
                combo.addItems(["Новый", "В работе", "Ожидает", "Закрыт"])
                if record:
                    idx = combo.findText(record.get(field, ""))
                    if idx >= 0:
                        combo.setCurrentIndex(idx)
                layout.addRow(QLabel(labels.get(field, field)), combo)
                self.inputs[field] = combo

            else:
                line = QLineEdit()
                if record:
                    line.setText(str(record.get(field, "")))
                layout.addRow(QLabel(labels.get(field, field)), line)
                self.inputs[field] = line

        self.submit_btn = QPushButton("Сохранить")
        self.submit_btn.clicked.connect(self.submit)
        layout.addWidget(self.submit_btn)

        self.setLayout(layout)

    def submit(self):
        data = {}
        for k, widget in self.inputs.items():
            if isinstance(widget, QDateEdit):
                data[k] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QComboBox):
                data[k] = widget.currentText().strip()
            else:
                data[k] = widget.text().strip()

        if len(data.get("card_number", "")) != 16:
            QMessageBox.critical(self, "Ошибка", "Номер карты должен содержать ровно 16 символов.")
            return

        required_fields = [
            "record_date", "card_number", "last_name", "first_name", "patronymic",
            "organization", "manufacturer", "work_status"
        ]
        for field in required_fields:
            if not data.get(field):
                QMessageBox.critical(self, "Ошибка", f"Поле '{field}' обязательно для заполнения.")
                return

        if not self.record_id:
            if not current_user:
                QMessageBox.critical(self, "Ошибка", "Пользователь не авторизован.")
                return
            data["created_by"] = current_user
            data["status"] = "Создано"
        else:
            data["status"] = "Изменено"

        try:
            if self.record_id:
                response = requests.put(f"{API_URL}/records/{self.record_id}", json=data)
            else:
                response = requests.post(f"{API_URL}/records", json=data)
            if response.status_code in (200, 201):
                self.accept()
            else:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении:\n{response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reclamacia GUI")
        self.setMinimumSize(1000, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # --- Панель фильтрации ---
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        filter_layout.addWidget(QLabel("Поиск:"))
        filter_layout.addWidget(self.search_input)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate(2000, 1, 1))
        filter_layout.addWidget(QLabel("с"))
        filter_layout.addWidget(self.date_from)

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        filter_layout.addWidget(QLabel("по"))
        filter_layout.addWidget(self.date_to)

        self.status_filter = QComboBox()
        self.status_filter.addItem("[Все]")
        self.status_filter.setMinimumWidth(120)
        filter_layout.addWidget(QLabel("Статус:"))
        filter_layout.addWidget(self.status_filter)

        self.search_btn = QPushButton("Фильтровать")
        self.search_btn.clicked.connect(self.search_records)
        filter_layout.addWidget(self.search_btn)

        self.reset_btn = QPushButton("Сброс")
        self.reset_btn.clicked.connect(self.load_data)
        filter_layout.addWidget(self.reset_btn)

        layout.addLayout(filter_layout)

        # --- Таблица ---
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "ID",  # col 0 → id
            "Дата",  # col 1 → record_date
            "№ Карты",  # col 2 → card_number
            "Фамилия",  # col 3 → last_name
            "Имя",  # col 4 → first_name
            "Отчество",  # col 5 → patronymic
            "Организация",  # col 6 → organization
            "Производитель",  # col 7 → manufacturer
            "Статус работы",  # col 8 → work_status
            "Комментарий",  # col 9 → comment
            "Статус",  # col 10 → status
            "Кем создано"  # col 11 → created_by
        ])

        # Настраиваем режим выделения
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        layout.addWidget(self.table)

        # --- Кнопки ---
        btn_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.load_data)
        btn_layout.addWidget(self.refresh_btn)

        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.open_add_dialog)
        btn_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("Редактировать")
        self.edit_btn.clicked.connect(self.open_edit_dialog)
        btn_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_selected)
        btn_layout.addWidget(self.delete_btn)

        self.export_btn = QPushButton("Экспорт в Excel")
        self.export_btn.clicked.connect(self.export_to_excel)
        btn_layout.addWidget(self.export_btn)

        self.import_btn = QPushButton("Импорт из Excel")
        self.import_btn.clicked.connect(self.import_from_excel)
        btn_layout.addWidget(self.import_btn)

        self.selenium_btn = QPushButton("Обновить статус в системе")
        self.selenium_btn.clicked.connect(self.run_selenium)
        btn_layout.addWidget(self.selenium_btn)

        layout.addLayout(btn_layout)
        self.load_data()

    def load_data(self):
        try:
            response = requests.get(f"{API_URL}/records")
            self.all_records = response.json()
            statuses = sorted(set(r["work_status"] for r in self.all_records if r.get("work_status")))
            self.status_filter.blockSignals(True)
            self.status_filter.clear()
            self.status_filter.addItem("[Все]")
            self.status_filter.addItems(statuses)
            self.status_filter.blockSignals(False)
            self.apply_filters(self.all_records)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def search_records(self):
        self.apply_filters(self.all_records)

    def apply_filters(self, records):
        query = self.search_input.text().strip().lower()
        date_from = self.date_from.date().toPython()
        date_to = self.date_to.date().toPython()
        status_selected = self.status_filter.currentText()

        filtered = []
        for record in records:
            try:
                rec_date = QDate.fromString(record["record_date"], "yyyy-MM-dd").toPython()
            except:
                rec_date = None
            if rec_date and not (date_from <= rec_date <= date_to):
                continue
            if status_selected != "[Все]" and record.get("work_status") != status_selected:
                continue
            if query and not any(query in str(v).lower() for v in record.values()):
                continue
            filtered.append(record)

        # Список ключей в нужном порядке
        display_keys = [
            "id",  # col 0
            "record_date",  # col 1
            "card_number",  # col 2
            "last_name",  # col 3
            "first_name",  # col 4
            "patronymic",  # col 5
            "organization",  # col 6
            "manufacturer",  # col 7
            "work_status",  # col 8
            "comment",  # col 9
            "status",  # col 10
            "created_by"  # col 11
        ]

        self.table.setRowCount(len(filtered))
        for row_idx, record in enumerate(filtered):
            row_color = status_colors.get(record.get("work_status", ""))
            for col_idx, key in enumerate(display_keys):
                value = record.get(key, "")
                # Если нужно добавить иконку для work_status
                if key == "work_status":
                    icon = status_icons.get(value, "")
                    value = f"{icon} {value}"
                item = QTableWidgetItem(str(value))
                if row_color:
                    item.setBackground(row_color)
                self.table.setItem(row_idx, col_idx, item)

    def open_add_dialog(self):
        dialog = RecordDialog(self)
        if dialog.exec():
            self.load_data()

    def open_edit_dialog(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Нет выбора", "Выберите строку.")
            return

        # Считываем ID из столбца 0
        record = {"id": int(self.table.item(selected, 0).text())}

        # Для столбцов 1 - 11 используем следующий список ключей:
        keys = [
            "record_date",  # col 1
            "card_number",  # col 2
            "last_name",  # col 3
            "first_name",  # col 4
            "patronymic",  # col 5
            "organization",  # col 6
            "manufacturer",  # col 7
            "work_status",  # col 8
            "comment",  # col 9
            "status",  # col 10
            "created_by"  # col 11
        ]
        for i, field in enumerate(keys, start=1):
            record[field] = self.table.item(selected, i).text()

        dialog = RecordDialog(self, record=record)
        if dialog.exec():
            self.load_data()

    def delete_selected(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Нет выбора", "Выберите строку для удаления.")
            return
        record_id = self.table.item(selected, 0).text()
        confirm = QMessageBox.question(self, "Удаление", f"Удалить запись ID {record_id}?")
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                requests.delete(f"{API_URL}/records/{record_id}")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить запись:\n{e}")

    def export_to_excel(self):
        try:
            path, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "export.xlsx", "Excel (*.xlsx)")
            if not path:
                return
            wb = Workbook()
            ws = wb.active
            ws.title = "Records"
            headers = list(self.all_records[0].keys())
            ws.append(headers)
            for record in self.all_records:
                ws.append([record.get(k, "") for k in headers])
            wb.save(path)
            QMessageBox.information(self, "Успех", f"Экспортировано: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать:\n{e}")

    def import_from_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите Excel файл", "", "Excel (*.xlsx *.xls)")
        if not path:
            return
        try:
            wb = load_workbook(path)
            sheet = wb.active
            headers = [cell.value for cell in sheet[1]]
            expected = [
                "record_date", "last_name", "first_name", "patronymic", "status",
                "comment", "card_number", "organization", "manufacturer", "work_status"
            ]
            for field in expected:
                if field not in headers:
                    QMessageBox.warning(self, "Ошибка", f"Не хватает поля: {field}")
                    return
            col_idx = {name: idx for idx, name in enumerate(headers)}
            count = 0
            for row in sheet.iter_rows(min_row=2, values_only=True):
                data = {field: row[col_idx[field]] for field in expected}
                data["created_by"] = current_user
                r = requests.post(f"{API_URL}/records", json=data)
                if r.status_code == 200:
                    count += 1
            QMessageBox.information(self, "Импорт завершён", f"Добавлено записей: {count}")
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось импортировать:\n{e}")

    def run_selenium(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Нет выбора", "Выберите запись.")
            return

        card_number = self.table.item(selected, 6).text()
        work_status = self.table.item(selected, 9).text()

        try:
            response = requests.post(f"{API_URL}/selenium", json={
                "card_number": card_number,
                "new_status": work_status
            })
            if response.status_code == 200:
                QMessageBox.information(self, "Готово", "Статус обновлён в системе.")
            else:
                QMessageBox.warning(self, "Ошибка", response.text)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_dialog = LoginDialog()
    if login_dialog.exec() != QDialog.DialogCode.Accepted or not login_dialog.success:
        sys.exit()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
