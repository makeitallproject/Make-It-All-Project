"""A clickable summary of a forum post, shown in the feed."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .avatar import Avatar
from .truncation import EllipsisLabel


class PostCard(QFrame):
    """One row of the feed. Emits the post id when clicked or activated."""

    clicked = pyqtSignal(int)

    def __init__(self, post: dict, parent=None):
        super().__init__(parent)
        self.post_id = post["id"]

        self.setObjectName("postCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(f"Post: {post['title']}")
        self.setProperty("selected", False)
        self.setStyleSheet(
            """
            QFrame#postCard {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 8px;
            }
            QFrame#postCard:hover {
                background-color: palette(light);
            }
            QFrame#postCard[selected="true"] {
                background-color: palette(light);
                border: 2px solid palette(highlight);
            }
            QFrame#postCard:focus {
                border: 2px solid palette(highlight);
            }
            QLabel#cardTitle {
                font-size: 13px;
                font-weight: 600;
            }
            QLabel#cardSnippet {
                font-size: 12px;
                color: palette(placeholder-text);
            }
            QLabel#cardAuthor {
                font-size: 11px;
                font-weight: 600;
            }
            QLabel#cardMeta {
                font-size: 11px;
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

    def set_selected(self, selected: bool) -> None:
        """Repaint the card when the reader switches to another post."""
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setFocus()
            self.clicked.emit(self.post_id)
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        # Space, Enter and Return activate the card so it works without a mouse.
        if event.key() in (
            Qt.Key.Key_Space,
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
        ):
            self.clicked.emit(self.post_id)
            return
        super().keyPressEvent(event)
