"""Header shared by the main screens: title, current user, and logo."""

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .avatar import Avatar

ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"


class AppHeader(QWidget):
    """Screen title on the left, signed-in user and company logo on the right."""

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        user: str = "",
        parent=None,
    ):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        titles = QVBoxLayout()
        titles.setSpacing(0)

        title_label = QLabel(title)
        title_label.setObjectName("screenTitle")
        titles.addWidget(title_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("muted")
            titles.addWidget(subtitle_label)

        layout.addLayout(titles)
        layout.addStretch()

        if user:
            user_row = QHBoxLayout()
            user_row.setSpacing(6)
            user_row.addWidget(Avatar(user, 28))
            user_name = QLabel(user)
            user_name.setObjectName("headerUser")
            user_row.addWidget(user_name)
            layout.addLayout(user_row)

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
