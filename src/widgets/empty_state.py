"""A centred placeholder for areas that have nothing to show yet."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class EmptyState(QWidget):
    """Explains an empty area and what would fill it."""

    def __init__(self, title: str, description: str, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(4)
        layout.addStretch()

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("font-size: 13px; font-weight: 600;")

        description_label = QLabel(description)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setWordWrap(True)
        description_label.setStyleSheet(
            "font-size: 12px; color: palette(placeholder-text);"
        )

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addStretch()
