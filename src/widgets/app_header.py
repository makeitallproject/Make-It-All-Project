"""Header shared by the app screens: title, current user, and logo."""

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .avatar import Avatar

ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"

STYLESHEET = """
QLabel#screenTitle {
    font-size: 20px;
    font-weight: 600;
}
QLabel#headerUser {
    font-size: 14px;
    font-weight: 600;
}
QLabel#muted {
    font-size: 12px;
    color: palette(placeholder-text);
}
"""


class AppHeader(QWidget):
    """Screen title on the left, signed-in user and company logo on the right."""

    def __init__(
        self,
        title: str,
        user: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.setStyleSheet(STYLESHEET)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        titles = QVBoxLayout()
        titles.setSpacing(0)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("screenTitle")
        titles.addWidget(self.title_label)

        layout.addLayout(titles)
        layout.addStretch()

        user_layout = QHBoxLayout()
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(6)

        self.user_avatar = Avatar(user or "?", 28)
        self.user_name = QLabel(user)
        self.user_name.setObjectName("headerUser")
        user_layout.addWidget(self.user_avatar)
        user_layout.addWidget(self.user_name)

        self.user_widget = QWidget()
        self.user_widget.setLayout(user_layout)
        layout.addWidget(self.user_widget)

        logo = QLabel()
        logo_path = ASSETS_DIR / "company_logo.png"
        if logo_path.exists():
            logo.setPixmap(
                QPixmap(str(logo_path)).scaled(
                    140,
                    44,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        logo.setAccessibleName("Make-It-All logo")
        logo.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(logo)

        self.set_user(user)

    def set_user(self, user: str) -> None:
        """Update, show, or hide the signed-in user badge."""
        self.user = user
        if user:
            self.user_avatar.set_name(user)
            self.user_name.setText(user)
            self.user_widget.show()
        else:
            self.user_avatar.set_name("?")
            self.user_name.clear()
            self.user_widget.hide()
