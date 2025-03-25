from PySide6.QtWidgets import QDialog, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox, QDateEdit, QMessageBox
from PySide6.QtCore import QDate
import requests

API_URL = "http://127.0.0.1:8000"
current_user = None

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