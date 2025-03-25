# ... предшествующий код ...
        self.selenium_btn = QPushButton("Обновить статус в системе")
        self.selenium_btn.clicked.connect(self.run_selenium)
        btn_layout.addWidget(self.selenium_btn)

# ... ниже, внутри MainWindow ...
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