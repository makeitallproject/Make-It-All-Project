"""Kanban board screen. Columns hold task cards with optional subtasks."""

import signal
import sys
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import state
from widgets.app_header import AppHeader
from widgets.avatar import Avatar
from widgets.empty_state import EmptyState
from widgets.truncation import EllipsisLabel

CARD_GAP = 8
COLUMN_MIN_WIDTH = 260
COLUMN_MAX_WIDTH = 420
BOARD_GAP = 10
COLUMNS = ["To Do", "In Progress", "Done"]

# Matches the type scale used by the forum screen: 12 meta, 13 UI, 14 card
# title, 16 column title, 20 screen title.
STYLESHEET = """
QWidget {
    font-size: 13px;
}
QLabel#columnTitle {
    font-size: 16px;
    font-weight: 600;
}
QLabel#countBadge {
    font-size: 12px;
    font-weight: 600;
    color: palette(text);
    background-color: palette(light);
    border-radius: 10px;
    padding: 0 7px;
}
QFrame#panel {
    border: 1px solid palette(mid);
    border-radius: 8px;
}
QFrame#card {
    background-color: palette(base);
    border: 1px solid palette(mid);
    border-radius: 8px;
}
QLabel#cardTitle {
    font-size: 14px;
    font-weight: 600;
}
QLabel#cardAuthor {
    font-size: 12px;
    font-weight: 600;
}
QLabel#cardMeta {
    font-size: 12px;
    color: palette(placeholder-text);
}
QLabel#cardOverdue {
    font-size: 12px;
    font-weight: 600;
    color: palette(text);
}
QProgressBar#subtaskProgress {
    border: none;
    background-color: palette(midlight);
    border-radius: 2px;
}
QProgressBar#subtaskProgress::chunk {
    background-color: palette(highlight);
    border-radius: 2px;
}
QPushButton#cardFooter {
    background-color: transparent;
    border: 1px solid transparent;
    border-top: 1px solid palette(mid);
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
    padding: 7px 12px;
    text-align: left;
    font-size: 12px;
    color: palette(placeholder-text);
}
QPushButton#cardFooter:hover {
    background-color: palette(light);
    color: palette(text);
}
QPushButton#cardFooter:pressed {
    background-color: palette(midlight);
}
QPushButton#cardFooter:focus {
    border: 1px solid palette(highlight);
}
QScrollArea#columnScroll {
    border: none;
    background: transparent;
}
QScrollArea#boardScroll {
    border: none;
    background: transparent;
}
"""


def format_date(day: datetime) -> str:
    """Short day and month, e.g. 4 Nov."""
    return f"{day.day} {day.strftime('%b')}"


def format_datetime(day: datetime) -> str:
    """Full date and time, e.g. 4 Nov 2026, 17:00."""
    return f"{day.day} {day.strftime('%b %Y, %H:%M')}"


def card_meta_text(task: dict) -> str:
    """Due or finished date, or an empty string when neither is set."""
    finished = task.get("finished")
    if finished is not None:
        return f"Done {format_date(finished)}"

    due = task.get("due")
    if due is None:
        return ""
    if is_overdue(task):
        return f"Overdue · {format_date(due)}"
    return f"Due {format_date(due)}"


def is_overdue(task: dict) -> bool:
    due = task.get("due")
    return (
        due is not None
        and task.get("finished") is None
        and due < datetime.now()
    )


def card_meta_tooltip(task: dict) -> str:
    finished = task.get("finished")
    if finished is not None:
        return f"Finished {format_datetime(finished)}"

    due = task.get("due")
    if due is None:
        return ""
    if is_overdue(task):
        return f"Was due {format_datetime(due)}"
    return f"Due {format_datetime(due)}"


def subtask_word(count: int) -> str:
    return "subtask" if count == 1 else "subtasks"


class TaskCard(QFrame):
    """One task. Collapsed by default, with a footer to reveal subtasks."""

    def __init__(self, task: dict, parent=None):
        super().__init__(parent)
        self.task = task
        self.subtasks = task.get("subtasks", [])
        self.done_count = sum(
            1 for subtask in self.subtasks if subtask["completed"]
        )
        self.expanded = False
        self.expand_button = None
        self.subtask_area = None

        self.setObjectName("card")
        self.setAccessibleName(f"Task: {task['name']}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.build_content())

        if self.subtasks:
            self.expand_button = self.build_expand_button()
            self.subtask_area = self.build_subtask_area()
            self.subtask_area.hide()
            layout.addWidget(self.subtask_area)
            layout.addWidget(self.expand_button)

    def build_content(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        title = QLabel(self.task["name"])
        title.setObjectName("cardTitle")
        title.setWordWrap(True)
        layout.addWidget(title)
        layout.addLayout(self.build_meta_row())

        if self.subtasks:
            layout.addWidget(self.build_progress())
        return content

    def build_meta_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(6)

        assignee = self.task.get("assignee")
        row.addWidget(Avatar(assignee or "?", 20))

        name = EllipsisLabel(assignee or "Unassigned")
        name.setObjectName("cardAuthor")
        row.addWidget(name, 1)

        meta_text = card_meta_text(self.task)
        if meta_text:
            meta = QLabel(meta_text)
            meta.setObjectName(
                "cardOverdue" if is_overdue(self.task) else "cardMeta"
            )
            meta.setToolTip(card_meta_tooltip(self.task))
            row.addWidget(meta)
        return row

    def build_progress(self) -> QWidget:
        total = len(self.subtasks)
        progress = QWidget()
        layout = QVBoxLayout(progress)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        label = QLabel(
            f"{self.done_count} of {total} {subtask_word(total)} done"
        )
        label.setObjectName("cardMeta")
        layout.addWidget(label)

        bar = QProgressBar()
        bar.setObjectName("subtaskProgress")
        bar.setRange(0, total)
        bar.setValue(self.done_count)
        bar.setTextVisible(False)
        bar.setFixedHeight(4)
        bar.setAccessibleName(f"{self.done_count} of {total} done")
        layout.addWidget(bar)
        return progress

    def build_subtask_area(self) -> QWidget:
        area = QWidget()
        layout = QVBoxLayout(area)
        layout.setContentsMargins(12, 0, 12, 10)
        layout.setSpacing(4)

        for subtask in self.subtasks:
            check = QCheckBox(subtask["name"])
            check.setChecked(subtask["completed"])
            check.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(check)
        return area

    def build_expand_button(self) -> QPushButton:
        button = QPushButton(self.expand_text())
        button.setObjectName("cardFooter")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setAccessibleName(
            f"{self.expand_text()} for {self.task['name']}"
        )
        button.clicked.connect(self.toggle_subtasks)
        return button

    def expand_text(self) -> str:
        verb = "Hide" if self.expanded else "Show"
        count = len(self.subtasks)
        return f"{verb} {count} {subtask_word(count)}"

    def toggle_subtasks(self) -> None:
        self.expanded = not self.expanded
        self.subtask_area.setVisible(self.expanded)
        self.expand_button.setText(self.expand_text())
        self.expand_button.setAccessibleName(
            f"{self.expand_text()} for {self.task['name']}"
        )
        if self.expanded:
            self.link_subtask_tab_order()

    def link_subtask_tab_order(self) -> None:
        """Send Tab from the toggle through the subtasks it just revealed."""
        previous = self.expand_button
        for check in self.subtask_area.findChildren(QCheckBox):
            QWidget.setTabOrder(previous, check)
            previous = check


class ColumnWidget(QFrame):
    """One board column with a header and a scrollable stack of cards."""

    def __init__(self, column: dict, parent=None):
        super().__init__(parent)
        tasks = column["tasks"]
        name = column["column"]

        self.setObjectName("panel")
        self.setMinimumWidth(COLUMN_MIN_WIDTH)
        self.setMaximumWidth(COLUMN_MAX_WIDTH)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.setAccessibleName(f"{name} column")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addLayout(self.build_header(name, len(tasks)))

        self.scroll = QScrollArea()
        self.scroll.setObjectName("columnScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(CARD_GAP)

        if tasks:
            for task in tasks:
                body_layout.addWidget(TaskCard(task))
            body_layout.addStretch()
        else:
            body_layout.addWidget(EmptyState(f"No tasks in {name}"), 1)

        self.scroll.setWidget(body)
        layout.addWidget(self.scroll, 1)

    def build_header(self, name: str, count: int) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(8)

        title = QLabel(name)
        title.setObjectName("columnTitle")
        header.addWidget(title)

        badge = QLabel(str(count))
        badge.setObjectName("countBadge")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedHeight(20)
        badge.setAccessibleName(f"{count} tasks")
        header.addWidget(badge)
        header.addStretch()
        return header


class KanbanScreen(QWidget):
    def __init__(self, user: str = ""):
        super().__init__()

        self.current_user = user or state.get_user()
        self.setWindowTitle("Make-It-All Tasks Board")
        self.setMinimumSize(500, 200)
        self.resize(1100, 780)
        self.setStyleSheet(STYLESHEET)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)
        self.header = AppHeader(
            "Tasks Board", user=self.current_user, back_to_calendar=True
        )
        root.addWidget(self.header)

        board_max_width = (
            len(COLUMNS) * COLUMN_MAX_WIDTH + (len(COLUMNS) - 1) * BOARD_GAP
        )
        self.board = QWidget()
        self.board.setAccessibleName("Task board")
        self.board.setMaximumWidth(board_max_width)
        self.board.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.board_layout = QHBoxLayout(self.board)
        self.board_layout.setContentsMargins(0, 0, 0, 0)
        self.board_layout.setSpacing(BOARD_GAP)

        board_scroll = QScrollArea()
        board_scroll.setObjectName("boardScroll")
        board_scroll.setAccessibleName("Task board")
        board_scroll.setWidgetResizable(True)
        board_scroll.setFrameShape(QFrame.Shape.NoFrame)
        board_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        board_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        board_scroll.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        board_scroll.setWidget(self.board)
        root.addWidget(board_scroll, 1)

        self.refresh()
        state.subscribe(self.refresh)

    def refresh(self) -> None:
        """Rebuild the columns from the shared task store."""
        while self.board_layout.count():
            item = self.board_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for column_name in COLUMNS:
            column_tasks = [
                task
                for task in state.tasks
                if task.get("column") == column_name
            ]
            column = {"column": column_name, "tasks": column_tasks}
            self.board_layout.addWidget(ColumnWidget(column), 1)

    def set_user(self, user: str) -> None:
        """Update the signed-in user shown in the header."""
        self.current_user = user or state.get_user()
        self.header.set_user(self.current_user)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Make Ctrl+C work
    app = QApplication(sys.argv)
    window = KanbanScreen()
    window.show()
    sys.exit(app.exec())
