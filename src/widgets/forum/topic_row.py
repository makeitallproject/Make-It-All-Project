from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..avatar import Avatar
from ..truncation import EllipsisLabel


def post_count_text(count: int) -> str:
    return f"{count} post" if count == 1 else f"{count} posts"


class TopicRow(QWidget):
    """A clickable topic item in the left sidebar"""

    def __init__(self, topic: dict, post_count: int, parent=None):
        super().__init__(parent)
        self.topic_id = topic["id"]
        self.setAccessibleName(topic["name"])
        self.setAccessibleDescription(post_count_text(post_count))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)
        layout.addWidget(Avatar(topic["name"], 28))

        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)

        name_label = EllipsisLabel(topic["name"])
        name_label.setStyleSheet("font-size: 13px; font-weight: 600;")

        count_label = QLabel(post_count_text(post_count))
        count_label.setStyleSheet(
            "font-size: 11px; color: palette(placeholder-text);"
        )

        text_layout.addWidget(name_label)
        text_layout.addWidget(count_label)

        layout.addLayout(text_layout, 1)
