"""One row in the topic list: avatar, name, and post count."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .avatar import Avatar

NAME_LIMIT = 26


def shorten(name: str, limit: int = NAME_LIMIT) -> str:
    """Trim a long topic name so the rail does not grow horizontally."""
    if len(name) <= limit:
        return name
    return name[: limit - 1].rstrip() + "…"


def post_count_text(count: int) -> str:
    return f"{count} post" if count == 1 else f"{count} posts"


class TopicRow(QWidget):
    """A row widget placed inside a QListWidgetItem."""

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

        name_label = QLabel(shorten(topic["name"]))
        name_label.setToolTip(topic["name"])
        name_label.setStyleSheet("font-size: 13px; font-weight: 600;")

        count_label = QLabel(post_count_text(post_count))
        count_label.setStyleSheet(
            "font-size: 11px; color: palette(placeholder-text);"
        )

        text_layout.addWidget(name_label)
        text_layout.addWidget(count_label)

        layout.addLayout(text_layout, 1)

        # Let mouse clicks reach the QListWidget underneath, so selecting a
        # topic and moving through the list with the keyboard keep working.
        for child in self.findChildren(QWidget):
            child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
