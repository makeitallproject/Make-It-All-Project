"""Forum (knowledge sharing) screen. Contains topics and posts."""

import re
import signal
import sys
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QPalette, QPixmap, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

# TODO: Fix this nonsense vvv
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from widgets.avatar import Avatar
from widgets.empty_state import EmptyState
from widgets.forum.growing_text_edit import GrowingTextEdit
from widgets.forum.post_card import PostCard
from widgets.forum.topic_row import TopicRow

# TODO un-hardcode these
ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"
CURRENT_USER = "Mish"

# Keep the line width comfortable on wide screens
# TODO this should be dynamic based on font size
READING_MEASURE = 700

TOPICS = [
    {
        "id": "software-development",
        "name": "Software Development",
    },
    {
        "id": "software-issues",
        "name": "Software Issues",
    },
    {
        "id": "printing",
        "name": "Printing",
    },
]

POSTS = [
    {
        "id": 1,
        "topic_id": "software-development",
        "title": "Put shared widgets in src/widgets",
        "body": (
            "Now that the calendar, kanban, and forum screens exist, we are "
            "starting to duplicate small pieces like initials bubbles and empty "
            "states. Anything the screens share belongs in src/widgets so we fix "
            "it once. Screen-specific code stays in src/screens."
        ),
        "author": "Mish",
        "created": datetime(2026, 10, 30, 9, 12),
    },
    {
        "id": 2,
        "topic_id": "software-development",
        "title": "Use uv instead of hand-made virtualenvs",
        "body": (
            "uv run handles the environment for you, so nobody commits a broken "
            "venv again. If a command needs a new package, add it to "
            "pyproject.toml with uv add and commit the lock file with it."
        ),
        "author": "Tobi",
        "created": datetime(2026, 10, 29, 16, 40),
    },
    {
        "id": 3,
        "topic_id": "software-development",
        "title": "Name branches after the work, not the person",
        "body": (
            "Our contributing guide suggests branches like add-calendar-screen. "
            "It keeps the pull request list readable when several of us are "
            "working at the same time."
        ),
        "author": "Kipras",
        "created": datetime(2026, 10, 28, 11, 5),
    },
    {
        "id": 4,
        "topic_id": "software-issues",
        "title": "Calendar logo gets cut off on narrow windows",
        "body": (
            "Resizing the calendar below about 900px cuts the right edge of the "
            "logo because the header row has a fixed spacer width. Replacing the "
            "spacer with a stretch factor keeps the logo aligned at any size."
        ),
        "author": "Evan",
        "created": datetime(2026, 10, 30, 8, 3),
    },
    {
        "id": 5,
        "topic_id": "software-issues",
        "title": "Ctrl+C does not stop a screen",
        "body": (
            "Running a screen with uv run swallows Ctrl+C because Qt keeps the "
            "Python signal handler busy. Calling signal.signal(signal.SIGINT, "
            "signal.SIG_DFL) fixes it, as used at the bottom of calendar.py."
        ),
        "author": "Charles",
        "created": datetime(2026, 10, 27, 15, 22),
    },
    {
        "id": 6,
        "topic_id": "printing",
        "title": "Queue stuck on Paused after a failed job",
        "body": (
            "The office printer pauses itself after a paper jam and never "
            "resumes. Open the queue, cancel the failed job, then resume the "
            "printer. If the job stays at the top, restart the print spooler."
        ),
        "author": "Louis",
        "created": datetime(2026, 10, 29, 10, 15),
    },
    {
        "id": 7,
        "topic_id": "printing",
        "title": "Which driver should we use for the office printer?",
        "body": (
            "The generic driver prints, but double-sided printing only works "
            "with the model-specific driver from the manufacturer. Use the "
            "specific one for anything longer than a couple of pages."
        ),
        "author": "Mish",
        "created": datetime(2026, 10, 26, 13, 48),
    },
]

# Current type scale in px: 13 secondary, 14 UI, 15 reading, 16 section, 18 pane title, 20 screen title, 24 post title.
STYLESHEET = """
QWidget {
    font-size: 13px;
}
QFrame#panel {
    border: 1px solid palette(mid);
    border-radius: 8px;
}
QFrame#composer {
    background-color: palette(alternate-base);
    border: 1px solid palette(mid);
    border-radius: 8px;
}
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
QLabel#sectionTitle {
    font-size: 16px;
    font-weight: 600;
}
QLabel#fieldLabel {
    font-size: 13px;
    font-weight: 600;
}
QLabel#dialogTitle {
    font-size: 18px;
    font-weight: 600;
}
QLabel#errorLabel {
    font-size: 13px;
    font-weight: 600;
}
QLabel#topicTitle {
    font-size: 18px;
    font-weight: 600;
}
QLabel#postTitle {
    font-size: 24px;
    font-weight: 600;
}
QLabel#readerAuthor {
    font-size: 13px;
    font-weight: 600;
}
QLabel#readerBody {
    font-size: 15px;
}
QLineEdit, QPlainTextEdit {
    background-color: palette(base);
    border: 1px solid palette(mid);
    border-radius: 6px;
    padding: 4px 6px;
    font-size: 14px;
    selection-background-color: palette(highlight);
    selection-color: palette(highlighted-text);
}
QLineEdit:focus, QPlainTextEdit:focus {
    border: 2px solid palette(highlight);
}
QPushButton {
    border: 1px solid palette(mid);
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 14px;
}
QPushButton:hover {
    background-color: palette(light);
}
QPushButton:pressed {
    background-color: palette(midlight);
}
QPushButton:focus {
    border: 2px solid palette(highlight);
}
QPushButton#primaryButton {
    background-color: palette(highlight);
    color: palette(highlighted-text);
    border: 1px solid palette(highlight);
    font-weight: 600;
}
QPushButton#primaryButton:hover {
    border: 1px solid palette(dark);
}
QPushButton#primaryButton:disabled {
    background-color: palette(base);
    color: palette(placeholder-text);
    border: 1px solid palette(midlight);
    font-weight: normal;
}
QPushButton#primaryButton:focus {
    border: 2px solid palette(highlighted-text);
}
QListWidget#topicList {
    border: none;
    background: transparent;
    outline: 0;
}
QListWidget#topicList::item {
    border-radius: 6px;
    margin-bottom: 2px;
}
QListWidget#topicList::item:hover {
    background-color: palette(light);
}
QListWidget#topicList::item:selected {
    background-color: palette(midlight);
}
QScrollArea {
    border: none;
    background: transparent;
}
"""


def posts_for(topic_id: str) -> list[dict]:
    """Posts in a topic, newest first."""
    matching = [post for post in POSTS if post["topic_id"] == topic_id]
    return sorted(matching, key=lambda post: post["created"], reverse=True)


def post_by_id(post_id: int) -> dict | None:
    return next((post for post in POSTS if post["id"] == post_id), None)


def topic_by_id(topic_id: str) -> dict | None:
    return next((topic for topic in TOPICS if topic["id"] == topic_id), None)


def next_post_id() -> int:
    return max((post["id"] for post in POSTS), default=0) + 1


def make_topic_id(name: str) -> str:
    """Turn a topic name into a unique, readable id."""
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "topic"
    candidate = base
    suffix = 2
    existing = {topic["id"] for topic in TOPICS}
    while candidate in existing:
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def format_created(created: datetime) -> str:
    return created.strftime("%d %b %Y, %H:%M")


def format_created_full(created: datetime) -> str:
    """Full timestamp with seconds and timezone, used for tooltips."""
    local = created.astimezone()
    return local.strftime("%d %b %Y, %H:%M:%S %Z (%z)")


def primary_button_shades(widget: QWidget) -> str:
    """Derive hover and pressed shades from the theme's highlight colour."""
    highlight = widget.palette().color(QPalette.ColorRole.Highlight)
    return f"""
QPushButton#primaryButton:hover {{
    background-color: {highlight.darker(115).name()};
}}
QPushButton#primaryButton:pressed {{
    background-color: {highlight.darker(135).name()};
}}
"""


class TopicDialog(QDialog):
    """Form for creating a topic. Call exec() and check the result."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New topic")
        self.setMinimumWidth(420)
        self.setStyleSheet(STYLESHEET + primary_button_shades(self))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        heading = QLabel("Create a topic")
        heading.setObjectName("dialogTitle")
        layout.addWidget(heading)

        form = QFormLayout()
        form.setSpacing(8)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Printing")
        self.name_input.setAccessibleName("Topic name")

        form.addRow("Name", self.name_input)
        layout.addLayout(form)

        self.error_label = QLabel()
        self.error_label.setObjectName("errorLabel")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        layout.addWidget(self.error_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self.create_button = QPushButton("Create topic")
        self.create_button.setObjectName("primaryButton")
        self.create_button.setEnabled(False)
        buttons.addButton(
            self.create_button, QDialogButtonBox.ButtonRole.AcceptRole
        )
        buttons.accepted.connect(self.submit)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.name_input.textChanged.connect(self.update_state)
        self.name_input.returnPressed.connect(self.submit)
        for button in self.findChildren(QPushButton):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_state()
        self.name_input.setFocus()

    def update_state(self) -> None:
        self.error_label.hide()
        enabled = bool(self.name_input.text().strip())
        self.create_button.setEnabled(enabled)
        self.create_button.setCursor(
            Qt.CursorShape.PointingHandCursor
            if enabled
            else Qt.CursorShape.ArrowCursor
        )

    def submit(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            return
        if any(topic["name"].lower() == name.lower() for topic in TOPICS):
            self.error_label.setText(
                f'A topic called "{name}" already exists. Choose another name.'
            )
            self.error_label.show()
            self.name_input.setFocus()
            return
        self.accept()

    def topic_name(self) -> str:
        return self.name_input.text().strip()


class ForumScreen(QWidget):
    """The 3-pane forum screen"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Make-It-All Forum")
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(STYLESHEET + primary_button_shades(self))

        self.selected_topic_id = TOPICS[0]["id"]
        self.selected_post_id = None

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)
        root.addLayout(self.build_header())

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(10)
        self.splitter.addWidget(self.build_topic_panel())
        self.splitter.addWidget(self.build_feed_panel())
        self.splitter.addWidget(self.build_reader_panel())
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 1)
        self.splitter.setSizes([250, 460, 460])
        root.addWidget(self.splitter, 1)

        self.refresh_topic_list()
        self.select_topic(self.selected_topic_id)
        for button in self.findChildren(QPushButton):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_publish_state()
        self.topic_list.setFocus()


    def build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(12)

        titles = QVBoxLayout()
        titles.setSpacing(0)

        title = QLabel("Make-It-All Forum")
        title.setObjectName("screenTitle")
        titles.addWidget(title)

        header.addLayout(titles)
        header.addStretch()

        user_row = QHBoxLayout()
        user_row.setSpacing(6)
        user_row.addWidget(Avatar(CURRENT_USER, 28))
        user_name = QLabel(CURRENT_USER)
        user_name.setObjectName("headerUser")
        user_row.addWidget(user_name)
        header.addLayout(user_row)

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
        logo.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        header.addWidget(logo)

        return header

    def build_topic_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setMinimumWidth(210)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("Topics")
        title.setObjectName("sectionTitle")
        new_topic_button = QPushButton("New topic")
        new_topic_button.clicked.connect(self.open_topic_dialog)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(new_topic_button)

        self.topic_list = QListWidget()
        self.topic_list.setObjectName("topicList")
        self.topic_list.setCursor(Qt.CursorShape.PointingHandCursor)
        self.topic_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.topic_list.currentItemChanged.connect(self.on_topic_changed)

        layout.addLayout(header)
        layout.addWidget(self.topic_list, 1)
        return panel

    def build_feed_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setMinimumWidth(320)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.feed_title = QLabel()
        self.feed_title.setObjectName("topicTitle")
        self.feed_title.setWordWrap(True)
        layout.addWidget(self.feed_title)
        layout.addWidget(self.build_composer())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.feed_container = QWidget()
        self.feed_layout = QVBoxLayout(self.feed_container)
        self.feed_layout.setContentsMargins(0, 0, 0, 0)
        self.feed_layout.setSpacing(8)
        scroll.setWidget(self.feed_container)

        layout.addWidget(scroll, 1)
        return panel

    def build_composer(self) -> QWidget:
        composer = QFrame()
        composer.setObjectName("composer")

        layout = QVBoxLayout(composer)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(6)

        heading = QHBoxLayout()
        heading_label = QLabel("Write a post")
        heading_label.setObjectName("sectionTitle")
        heading.addWidget(heading_label)
        heading.addStretch()
        layout.addLayout(heading)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_label = QLabel("Title")
        title_label.setObjectName("fieldLabel")
        title_label.setFixedWidth(38)
        self.post_title_input = QLineEdit()
        self.post_title_input.setPlaceholderText("Give your post a title")
        self.post_title_input.setAccessibleName("Post title")
        self.post_title_input.textChanged.connect(self.update_publish_state)
        title_row.addWidget(title_label)
        title_row.addWidget(self.post_title_input, 1)
        layout.addLayout(title_row)

        body_row = QHBoxLayout()
        body_row.setSpacing(8)
        body_label = QLabel("Body")
        body_label.setObjectName("fieldLabel")
        body_label.setFixedWidth(38)
        self.post_body_input = GrowingTextEdit()
        self.post_body_input.setPlaceholderText("What do you want to share?")
        self.post_body_input.setAccessibleName("Post body")
        self.post_body_input.textChanged.connect(self.update_publish_state)
        body_row.addWidget(body_label, 0, Qt.AlignmentFlag.AlignTop)
        body_row.addWidget(self.post_body_input, 1)
        layout.addLayout(body_row)

        footer = QHBoxLayout()
        footer.addStretch()
        self.publish_button = QPushButton("Publish post")
        self.publish_button.setObjectName("primaryButton")
        self.publish_button.setEnabled(False)
        self.publish_button.setToolTip("Publish post (Ctrl+Enter)")
        self.publish_button.clicked.connect(self.publish_post)
        footer.addWidget(self.publish_button)
        layout.addLayout(footer)

        # Ctrl+Enter publishes while focus is anywhere in the composer.
        self._publish_shortcuts = []
        for sequence in ("Ctrl+Return", "Ctrl+Enter"):
            shortcut = QShortcut(QKeySequence(sequence), composer)
            shortcut.setContext(
                Qt.ShortcutContext.WidgetWithChildrenShortcut
            )
            shortcut.activated.connect(self.publish_post)
            self._publish_shortcuts.append(shortcut)

        return composer

    def build_reader_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setMinimumWidth(320)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        self.reader_stack = QStackedWidget()
        self.reader_empty = EmptyState(
            "No post selected",
            "Pick a post from the feed to read it here.",
        )
        self.reader_stack.addWidget(self.reader_empty)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(18, 18, 18, 18)
        content_layout.setSpacing(8)

        self.reader_title = QLabel()
        self.reader_title.setObjectName("postTitle")
        self.reader_title.setWordWrap(True)
        self.reader_title.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        meta = QHBoxLayout()
        meta.setSpacing(8)
        self.reader_avatar = Avatar("", 28)

        names = QVBoxLayout()
        names.setSpacing(0)
        self.reader_author = QLabel()
        self.reader_author.setObjectName("readerAuthor")
        self.reader_date = QLabel()
        self.reader_date.setObjectName("muted")
        names.addWidget(self.reader_author)
        names.addWidget(self.reader_date)

        meta.addWidget(self.reader_avatar)
        meta.addLayout(names)
        meta.addStretch()

        self.reader_body = QLabel()
        self.reader_body.setObjectName("readerBody")
        self.reader_body.setWordWrap(True)
        self.reader_body.setMaximumWidth(READING_MEASURE)
        self.reader_body.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self.reader_body.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.reader_body.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        content_layout.addWidget(self.reader_title)
        content_layout.addLayout(meta)
        content_layout.addSpacing(4)
        content_layout.addWidget(self.reader_body)
        content_layout.addStretch()

        scroll.setWidget(content)
        self.reader_scroll = scroll
        self.reader_stack.addWidget(scroll)

        layout.addWidget(self.reader_stack, 1)
        return panel


    def on_topic_changed(self, current, _previous) -> None:
        if current is None:
            return
        self.select_topic(current.data(Qt.ItemDataRole.UserRole))

    def select_topic(self, topic_id: str) -> None:
        topic = topic_by_id(topic_id)
        if topic is None:
            return

        self.selected_topic_id = topic_id

        # Keep the rail in step when the topic is chosen in code rather than
        # by clicking a row (for example right after creating a topic).
        self.topic_list.blockSignals(True)
        for row in range(self.topic_list.count()):
            item = self.topic_list.item(row)
            if item is not None and item.data(
                Qt.ItemDataRole.UserRole
            ) == topic_id:
                self.topic_list.setCurrentRow(row)
                break
        self.topic_list.blockSignals(False)

        self.feed_title.setText(topic["name"])
        self.refresh_feed()

        posts = posts_for(topic_id)
        if posts:
            self.select_post(posts[0]["id"])
        else:
            self.selected_post_id = None
            self.reader_stack.setCurrentWidget(self.reader_empty)

    def select_post(self, post_id: int) -> None:
        post = post_by_id(post_id)
        if post is None:
            return

        self.selected_post_id = post_id
        for card in self.feed_container.findChildren(PostCard):
            card.setChecked(card.post_id == post_id)

        self.reader_title.setText(post["title"])
        self.reader_avatar.set_name(post["author"])
        self.reader_author.setText(post["author"])
        self.reader_date.setText(format_created(post["created"]))
        self.reader_date.setToolTip(format_created_full(post["created"]))
        self.reader_body.setText(post["body"])
        scroll_bar = self.reader_scroll.verticalScrollBar()
        if scroll_bar is not None:
            scroll_bar.setValue(0)
        self.reader_stack.setCurrentWidget(self.reader_scroll)

    def refresh_feed(self) -> None:
        """Rebuild the post cards for the selected topic."""
        while self.feed_layout.count():
            item = self.feed_layout.takeAt(0)
            if item is None:
                break
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        posts = posts_for(self.selected_topic_id)

        if not posts:
            self.feed_layout.addWidget(
                EmptyState(
                    "No posts yet",
                    "Write the first post for this topic above.",
                )
            )
            self.feed_layout.addStretch()
            return

        for post in posts:
            card = PostCard(post)
            card.opened.connect(self.select_post)
            self.feed_layout.addWidget(card)
        self.feed_layout.addStretch()

    def refresh_topic_list(self) -> None:
        """Rebuild the rail, keeping the current topic selected."""
        self.topic_list.blockSignals(True)
        self.topic_list.clear()

        current_row = 0
        for row_index, topic in enumerate(TOPICS):
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, topic["id"])
            item.setData(
                Qt.ItemDataRole.AccessibleTextRole,
                f"{topic['name']}, {len(posts_for(topic['id']))} posts",
            )

            row = TopicRow(topic, len(posts_for(topic["id"])))
            item.setSizeHint(row.sizeHint())

            self.topic_list.addItem(item)
            self.topic_list.setItemWidget(item, row)

            if topic["id"] == self.selected_topic_id:
                current_row = row_index

        self.topic_list.setCurrentRow(current_row)
        self.topic_list.blockSignals(False)

    def update_publish_state(self) -> None:
        has_title = bool(self.post_title_input.text().strip())
        has_body = bool(self.post_body_input.toPlainText().strip())
        enabled = has_title and has_body
        self.publish_button.setEnabled(enabled)
        self.publish_button.setCursor(
            Qt.CursorShape.PointingHandCursor
            if enabled
            else Qt.CursorShape.ArrowCursor
        )

    def publish_post(self) -> None:
        title = self.post_title_input.text().strip()
        body = self.post_body_input.toPlainText().strip()
        if not title or not body:
            return

        post = {
            "id": next_post_id(),
            "topic_id": self.selected_topic_id,
            "title": title,
            "body": body,
            "author": CURRENT_USER,
            "created": datetime.now(),
        }
        POSTS.append(post)

        self.post_title_input.clear()
        self.post_body_input.clear()
        self.refresh_topic_list()
        self.refresh_feed()
        self.select_post(post["id"])
        self.post_title_input.setFocus()

    def open_topic_dialog(self) -> None:
        dialog = TopicDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        name = dialog.topic_name()
        topic = {
            "id": make_topic_id(name),
            "name": name,
        }
        TOPICS.append(topic)

        self.selected_topic_id = topic["id"]
        self.refresh_topic_list()
        self.select_topic(topic["id"])

    def resizeEvent(self, event):  # type: ignore
        super().resizeEvent(event)
        # The body editor's maximum height follows the window height.
        body = getattr(self, "post_body_input", None)
        if body is not None:
            body.refresh_height()


if __name__ == "__main__":
    # Make Ctrl+C work
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    window = ForumScreen()
    window.resize(1280, 820)
    window.show()
    sys.exit(app.exec())
