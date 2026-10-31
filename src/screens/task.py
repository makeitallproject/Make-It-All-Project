"""Create-task form."""

import signal
import sys

from PyQt6.QtCore import QDate, Qt, QTime
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from widgets.app_header import AppHeader


class MainWindow(QMainWindow):
    def __init__(self, user: str = "Mish"):
        super().__init__()

        self.current_user = user
        self.setWindowTitle("New task")
        self.resize(600, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        self.header = AppHeader(
            "New task",
            user=user,
        )
        main_layout.addWidget(self.header)

        form_layout = QFormLayout()
        form_layout.setSpacing(20)

        self.title_input = QLineEdit()
        self.title_input.setMinimumHeight(35)

        self.notes_input = QTextEdit()
        self.notes_input.setMinimumHeight(80)

        self.people_input = QComboBox()
        self.people_input.addItems(
            [
                "Unassigned",
                "Evan",
                "Mish",
                "Charles",
                "Tobi",
                "Kipras",
                "Louis",
            ]
        )
        self.people_input.setMinimumHeight(35)

        self.due_input = QDateEdit()
        self.due_input.setCalendarPopup(True)
        self.due_input.setDate(QDate.currentDate())
        self.due_input.setDisplayFormat("dd/MM/yyyy")
        self.due_input.setMinimumHeight(35)

        self.docs_container = QWidget()
        docs_layout = QHBoxLayout(self.docs_container)
        docs_layout.setContentsMargins(0, 0, 0, 0)

        self.docs_input = QLineEdit()
        self.docs_input.setPlaceholderText("No file selected...")
        self.docs_input.setReadOnly(True)
        self.docs_input.setMinimumHeight(35)

        self.docs_btn = QPushButton("Browse...")
        self.docs_btn.setMinimumHeight(35)
        self.docs_btn.clicked.connect(self.browse_for_document)

        docs_layout.addWidget(self.docs_input)
        docs_layout.addWidget(self.docs_btn)

        form_layout.addRow("Task title", self.title_input)
        form_layout.addRow("Task notes", self.notes_input)
        form_layout.addRow("Assign to", self.people_input)
        form_layout.addRow("Due date", self.due_input)
        form_layout.addRow("Documents", self.docs_container)

        main_layout.addLayout(form_layout)

        self.reminders_checkbox = QCheckBox(
            "Section below expands if this is checked"
        )
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.addRow("Reminders?", self.reminders_checkbox)

        self.reminders_container = QWidget()
        reminders_layout = QFormLayout(self.reminders_container)
        reminders_layout.setContentsMargins(0, 10, 0, 0)
        reminders_layout.setSpacing(20)

        self.dates_input = QDateEdit()
        self.dates_input.setCalendarPopup(True)
        self.dates_input.setDate(QDate.currentDate())
        self.dates_input.setDisplayFormat("dd/MM/yyyy")
        self.dates_input.setMinimumHeight(35)

        self.times_input = QTimeEdit()
        self.times_input.setTime(QTime.currentTime())
        self.times_input.setDisplayFormat("HH:mm")
        self.times_input.setMinimumHeight(35)

        reminders_layout.addRow("Reminder date", self.dates_input)
        reminders_layout.addRow("Reminder time", self.times_input)

        self.reminders_container.setVisible(False)
        main_layout.addWidget(self.reminders_container)

        self.reminders_checkbox.toggled.connect(self.toggle_reminders)

        main_layout.addStretch()

        bottom_layout = QHBoxLayout()

        back_btn = QPushButton("Back")
        back_btn.setFixedSize(100, 45)
        back_btn.clicked.connect(self.clicked_back_btn)

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setFixedSize(120, 45)
        self.submit_btn.setEnabled(False)

        bottom_layout.addWidget(back_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.submit_btn)

        main_layout.addLayout(bottom_layout)

        self.title_input.textChanged.connect(self.validate_form)

    def set_user(self, user: str) -> None:
        self.current_user = user
        self.header.set_user(user)

    def toggle_reminders(self, checked: bool) -> None:
        self.reminders_container.setVisible(checked)

    def validate_form(self) -> None:
        self.submit_btn.setEnabled(bool(self.title_input.text().strip()))

    def browse_for_document(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Document", "", "All Files (*)"
        )
        if file_path:
            self.docs_input.setText(file_path)

    def clicked_back_btn(self) -> None:
        self.hide()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Make Ctrl+C work
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
