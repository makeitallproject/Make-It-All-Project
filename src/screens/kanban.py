"""Kanban board screen. Columns hold task cards with optional subtasks."""

import signal
import sys
from datetime import date

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
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from widgets.app_header import AppHeader
from widgets.avatar import Avatar
from widgets.empty_state import EmptyState
from widgets.truncation import EllipsisLabel

# TODO un-hardcode these
CURRENT_USER = "Mish"
CARD_GAP = 8

TASKS = [
    {
        "column": "To Do",
        "empty_hint": "Work that has not started will show up here.",
        "tasks": [
            {
                "name": "Set up CI pipeline",
                "assignee": "Tobi",
                "due": date(2026, 11, 4),
                "subtasks": [
                    {"name": "Install GitHub Actions", "completed": False},
                    {"name": "Add lint step", "completed": False},
                ],
            },
            {
                "name": "Write project README",
                "assignee": "Mish",
                "due": date(2026, 11, 2),
                "subtasks": [],
            },
            {
                "name": (
                    "Audit keyboard navigation across the calendar and "
                    "forum screens"
                ),
                "assignee": "Charles",
                "due": date(2026, 11, 7),
                "subtasks": [
                    {
                        "name": "List screens that need testing",
                        "completed": True,
                    },
                    {"name": "Document focus order", "completed": False},
                    {"name": "Test with keyboard only", "completed": False},
                ],
            },
            {
                "name": "Collect requirements from each team",
                "assignee": None,
                "due": date(2026, 11, 10),
                "subtasks": [],
            },
            {
                "name": "Document the printer setup for new starters",
                "assignee": "Louis",
                "due": date(2026, 11, 12),
                "subtasks": [
                    {"name": "Photograph the printer panel", "completed": False},
                    {"name": "Add paper refill steps", "completed": False},
                ],
            },
        ],
    },
    {
        "column": "In Progress",
        "empty_hint": "Work someone is actively doing will show up here.",
        "tasks": [
            {
                "name": "Design database schema",
                "assignee": "Kipras",
                "due": date(2026, 10, 30),
                "subtasks": [
                    {"name": "Draft ER diagram", "completed": True},
                    {"name": "Normalize tables", "completed": False},
                ],
            },
            {
                "name": "Polish the forum reader pane",
                "assignee": "Mish",
                "due": date(2026, 11, 1),
                "subtasks": [
                    {"name": "Fix long post titles", "completed": True},
                    {
                        "name": "Keep the reading measure at 700px",
                        "completed": True,
                    },
                    {"name": "Add paragraph spacing", "completed": False},
                ],
            },
            {
                "name": "Wire up the task creation form",
                "assignee": "Evan",
                "due": date(2026, 11, 3),
                "subtasks": [],
            },
            {
                "name": "Replace hardcoded colours in the calendar stylesheet",
                "assignee": "Kipras",
                "due": date(2026, 11, 5),
                "subtasks": [
                    {
                        "name": "Audit hardcoded colours",
                        "completed": False,
                    },
                    {"name": "Use palette roles", "completed": False},
                ],
            },
        ],
    },
    {
        "column": "Review",
        "empty_hint": (
            "Tasks waiting for a second pair of eyes will show up here."
        ),
        "tasks": [],
    },
    {
        "column": "Done",
        "empty_hint": "Finished work will show up here.",
        "tasks": [
            {
                "name": "Scaffold repository",
                "assignee": "Tobi",
                "finished": date(2026, 10, 20),
                "subtasks": [
                    {"name": "Init git repo", "completed": True},
                    {"name": "Add pyproject.toml", "completed": True},
                ],
            },
            {
                "name": "Build the forum screen",
                "assignee": "Mish",
                "finished": date(2026, 10, 29),
                "subtasks": [
                    {"name": "Topic rail", "completed": True},
                    {"name": "Post feed", "completed": True},
                    {"name": "Reader pane", "completed": True},
                ],
            },
            {
                "name": "Add the shared avatar widget",
                "assignee": "Kipras",
                "finished": date(2026, 10, 27),
                "subtasks": [],
            },
            {
                "name": "Move shared widgets into src/widgets",
                "assignee": "Mish",
                "finished": date(2026, 10, 28),
                "subtasks": [
                    {"name": "Create widgets package", "completed": True},
                ],
            },
        ],
    },
]

# Matches the type scale used by the forum screen: 12 meta, 13 UI, 14 card
# title, 16 column title, 20 screen title.
STYLESHEET = """
QWidget {
    font-size: 13px;
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
"""


def format_date(day: date) -> str:
    """Short day and month, e.g. 4 Nov."""
    return f"{day.day} {day.strftime('%b')}"


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
        and due < date.today()
    )


def card_meta_tooltip(task: dict) -> str:
    finished = task.get("finished")
    if finished is not None:
        return f"Finished {finished.strftime('%d %b %Y')}"

    due = task.get("due")
    if due is None:
        return ""
    if due < date.today():
        return f"Was due {due.strftime('%d %b %Y')}"
    return f"Due {due.strftime('%d %b %Y')}"


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
        self.setMinimumWidth(240)
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
            body_layout.addWidget(
                EmptyState(f"No tasks in {name}", column["empty_hint"]), 1
            )

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
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Make-It-All Board")
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(STYLESHEET)

        task_count = sum(len(column["tasks"]) for column in TASKS)
        stage_word = "stage" if len(TASKS) == 1 else "stages"

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)
        root.addWidget(
            AppHeader(
                "Make-It-All Board",
                subtitle=f"{task_count} tasks across {len(TASKS)} {stage_word}",
                user=CURRENT_USER,
            )
        )

        board = QSplitter(Qt.Orientation.Horizontal)
        board.setAccessibleName("Task board")
        board.setChildrenCollapsible(False)
        board.setHandleWidth(10)

        for index, column in enumerate(TASKS):
            board.addWidget(ColumnWidget(column))
            board.setStretchFactor(index, 1)

        board.setSizes([300] * len(TASKS))
        root.addWidget(board, 1)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Make Ctrl+C work
    app = QApplication(sys.argv)
    window = KanbanScreen()
    window.resize(1280, 820)
    window.show()
    sys.exit(app.exec())
