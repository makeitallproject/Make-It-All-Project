"""Kanban board screen. Columns hold task cards with optional subtasks."""

import signal
import sys

from PyQt6.QtCore import Qt, pyqtSignal
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
from screens import task as task_screen
from widgets import task_meta
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
QCheckBox {
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

        meta_text = task_meta.meta_text(self.task)
        if meta_text:
            meta = QLabel(meta_text)
            meta.setObjectName(
                "cardOverdue"
                if task_meta.is_overdue(self.task)
                else "cardMeta"
            )
            meta.setToolTip(task_meta.meta_tooltip(self.task))
            row.addWidget(meta)
        return row

    def build_progress(self) -> QWidget:
        total = len(self.subtasks)
        progress = QWidget()
        layout = QVBoxLayout(progress)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        label = QLabel(task_meta.progress_text(self.done_count, total))
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
            check.setSizePolicy(
                QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
            )
            check.setToolTip(subtask["name"])
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
        return f"{verb} {count} {task_meta.subtask_word(count)}"

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
    todo_requested = pyqtSignal()

    def __init__(self, user: str = ""):
        super().__init__()

        self.current_user = user or state.get_user()
        self.add_task_window = None
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

        controls = QHBoxLayout()
        self.create_task_btn = QPushButton("Create a task")
        self.create_task_btn.clicked.connect(self.open_add_task)
        self.todo_btn = QPushButton("Switch to To-Do List")
        self.todo_btn.clicked.connect(lambda: self.todo_requested.emit())
        controls.addWidget(self.create_task_btn)
        controls.addWidget(self.todo_btn)
        controls.addStretch()
        root.addLayout(controls)

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

    def open_add_task(self) -> None:
        if self.add_task_window is None:
            self.add_task_window = task_screen.MainWindow(
                user=self.current_user
            )
        self.add_task_window.show()
        self.add_task_window.raise_()
        self.add_task_window.activateWindow()

    def set_user(self, user: str) -> None:
        """Update the signed-in user shown in the header."""
        self.current_user = user or state.get_user()
        self.header.set_user(self.current_user)
        if self.add_task_window is not None:
            self.add_task_window.set_user(self.current_user)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Make Ctrl+C work
    app = QApplication(sys.argv)

    from screens.todo_list import todo_list

    window = KanbanScreen()
    todo = todo_list.TodoListScreen()
    window.todo_requested.connect(lambda: (window.hide(), todo.show()))
    todo.kanban_requested.connect(lambda: (todo.hide(), window.show()))
    todo.header.back_requested.connect(lambda: (todo.hide(), window.show()))
    window.show()
    sys.exit(app.exec())
