import sys
import requests
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QDialog, QLabel, QLineEdit, QFormLayout,
    QDateEdit, QFileDialog, QComboBox
)
from PySide6.QtCore import QDate
from PySide6.QtGui import QColor
from openpyxl import Workbook, load_workbook

API_URL = "http://127.0.0.1:8000"
current_user = None

status_colors = {
    "Новый": QColor("lightgreen"),
    "В работе": QColor("gold"),
    "Ожидает": QColor("lightblue"),
    "Закрыт": QColor("lightgray")
}

# ... остальной код без изменений до метода apply_filters ...

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
            if status_selected != "[Все]" and record.get("status") != status_selected:
                continue
            if query and not any(query in str(v).lower() for v in record.values()):
                continue
            filtered.append(record)

        self.table.setRowCount(len(filtered))
        for row_idx, record in enumerate(filtered):
            for col_idx, (key, value) in enumerate(record.items()):
                item = QTableWidgetItem(str(value))
                if key == "work_status":
                    color = status_colors.get(value)
                    if color:
                        item.setBackground(color)
                self.table.setItem(row_idx, col_idx, item)