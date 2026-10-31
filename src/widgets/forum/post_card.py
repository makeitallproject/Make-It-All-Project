from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from ..avatar import Avatar
from ..truncation import EllipsisLabel


class PostCard(QPushButton):
    """A clickable post in the middle pane"""

    opened = pyqtSignal(int)

    def __init__(self, post: dict, parent=None):
        super().__init__("", parent)
        self.post_id = post["id"]

        self.setObjectName("postCard")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.setAccessibleName(f"Post: {post['title']}")
        self.setStyleSheet(
            """
            QPushButton#postCard {
                background-color: palette(base);
                border: 2px solid palette(mid);
                border-radius: 8px;
            }
            QPushButton#postCard:hover {
                background-color: palette(light);
            }
            QPushButton#postCard:pressed {
                background-color: palette(midlight);
            }
            QPushButton#postCard:checked {
                background-color: palette(light);
                border: 2px solid palette(highlight);
            }
            QPushButton#postCard:focus {
                border: 2px solid palette(highlight);
            }
            QLabel#cardTitle {
                font-size: 14px;
                font-weight: 600;
            }
            QLabel#cardSnippet {
                font-size: 13px;
                color: palette(placeholder-text);
            }
            QLabel#cardAuthor {
                font-size: 12px;
                font-weight: 600;
            }
            QLabel#cardMeta {
                font-size: 12px;
                color: palette(placeholder-text);
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        title = QLabel(post["title"])
        title.setObjectName("cardTitle")
        title.setWordWrap(True)

        snippet = EllipsisLabel(post["body"])
        snippet.setObjectName("cardSnippet")

        footer = QHBoxLayout()
        footer.setSpacing(6)
        footer.addWidget(Avatar(post["author"], 20))

        author = QLabel(post["author"])
        author.setObjectName("cardAuthor")
        footer.addWidget(author)

        date = QLabel(post["created"].strftime("%d %b, %H:%M"))
        date.setObjectName("cardMeta")
        footer.addWidget(date)
        footer.addStretch()

        layout.addWidget(title)
        layout.addWidget(snippet)
        layout.addLayout(footer)

        self.clicked.connect(self._emit_opened)

    def _emit_opened(self, _checked: bool = False) -> None:
        """Pass the post id on when the button is activated."""
        self.opened.emit(self.post_id)

    def sizeHint(self) -> QSize:
        # Make the button behave like a frame sizing-wise
        layout = self.layout()
        if layout is not None:
            return layout.sizeHint()
        return super().sizeHint()

    def minimumSizeHint(self) -> QSize:
        layout = self.layout()
        if layout is not None:
            return layout.minimumSize()
        return super().minimumSizeHint()
