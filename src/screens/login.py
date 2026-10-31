# src > screens > login.py
# @toblobs // last updated 27.10.26

import signal
import sys

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget

from widgets.app_header import AppHeader

# login window form
class LoginWindow(QWidget):

    login_requested = pyqtSignal(str, str)

    def __init__(self):
        
        super().__init__()

        self.setWindowTitle("Make-It-All Login Screen")
        self.resize(700, 560)
        self.setMinimumSize(700, 560)

        self.setObjectName("loginWindow")

        self.setStyleSheet(
            """
            QLabel#instruction {
                border: 1px solid palette(mid);
                background-color: palette(base);
                color: palette(text);
                font-size: 12px;
            }

            QLineEdit {
                border: 1px solid palette(mid);
                background-color: palette(base);
                color: palette(text);
                padding: 0 8px;
                font-size: 12px;
            }

            QLineEdit:focus {
                border: 2px solid palette(highlight);
            }

            QPushButton#enterButton {
                border: 1px solid palette(mid);
                background-color: palette(button);
                color: palette(button-text);
                font-size: 12px;
            }

            QPushButton#enterButton:hover {
                background-color: palette(light);
            }

            QPushButton#enterButton:pressed {
                background-color: palette(midlight);
            }
            """)

        # vertical layout for a rounded button
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        main_layout.addWidget(AppHeader("Make-It-All System"))
        
        # form area
        form_area = QWidget()
        form_layout = QVBoxLayout(form_area)
        form_layout.setContentsMargins(45, 39, 45, 0)
        form_layout.setSpacing(0)

        # instruction heading
        instruction_row = QHBoxLayout()
        
        instruction = QLabel("Enter Username/password")
        instruction.setObjectName("instruction")
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setFixedSize(174, 22)
        
        instruction_row.addStretch()
        instruction_row.addWidget(instruction)
        instruction_row.addStretch()
        
        form_layout.addLayout(instruction_row)
        form_layout.addSpacing(19)
        
        # username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Email (user/manager)")
        self.username_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.username_input.setFixedHeight(42)
        self.username_input.setAccessibleName("Username or email")
        self.username_input.returnPressed.connect(self._focus_password)
        
        form_layout.addWidget(self.username_input)
        form_layout.addSpacing(18)

        # password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password_input.setFixedHeight(42)
        self.password_input.setAccessibleName("Password")
        self.password_input.returnPressed.connect(self.submit)
        
        form_layout.addWidget(self.password_input)
        form_layout.addSpacing(8)

        # enter button
        button_row = QHBoxLayout()

        self.enter_button = QPushButton("Enter")
        self.enter_button.setObjectName("enterButton")
        self.enter_button.setFixedSize(121, 32)
        self.enter_button.clicked.connect(self.submit)
        
        button_row.addStretch()
        button_row.addWidget(self.enter_button)
        
        form_layout.addLayout(button_row)
        form_layout.addStretch()

        main_layout.addWidget(form_area, 1)
        
        self.username_input.setFocus()

    def _focus_password(self):
        self.password_input.setFocus()
        
    def submit(self):
        
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Missing information", "Please enter username/email and password.")
            return

        # here, connect to authenticator
        self.login_requested.emit(username, password)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Make Ctrl+C work
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
