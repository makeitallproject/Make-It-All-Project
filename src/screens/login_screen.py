# src > screens > login.py
# @toblobs // last updated 27.10.26

import sys
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QPalette, QPen
from PyQt6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget

# logo panel
class LogoPanel(QWidget):
    
    def __init__(self, parent = None):
        
        super().__init__(parent)
        self.setFixedHeight(250)
        
        logo_path = Path(__file__).resolve().parent.parent.parent / "assets" / "company_logo.png"
        self.logo = QPixmap(str(logo_path)) if logo_path else QPixmap()
        
    def paintEvent(self, event): # type: ignore
        
        # make a painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        bounds = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        outline = QPainterPath()
        outline.addRoundedRect(bounds, 35, 35)

        painter.save()
        painter.setClipPath(outline)

        # paint logo
        if not self.logo.isNull(): painter.drawPixmap(bounds, self.logo, QRectF(self.logo.rect()))
        else: painter.fillPath(outline, self.palette().color(QPalette.ColorRole.Base))
        
        painter.setPen(self.palette().color(QPalette.ColorRole.Text))
        # painter.drawText(bounds, Qt.AlignmentFlag.AlignCenter, "Make-It-All")

        # cleanup
        painter.restore()

        painter.setPen(QPen(self.palette().color(QPalette.ColorRole.Mid), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(outline)
        
        painter.end()

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
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # logo label
        self.logo_panel = LogoPanel()
        main_layout.addWidget(self.logo_panel)        
        
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

def main():
    
    app = QApplication(sys.argv)
    window = LoginWindow()

    # previewing with a default password
    def preview_login(_username: str, _password: str):
        
        QMessageBox.information(window, "Login prototype", f"Form submitted.")
        print(_username)
        print(_password)

    window.login_requested.connect(preview_login)
    
    window.show()
    return app.exec()

if __name__ == "__main__": main()