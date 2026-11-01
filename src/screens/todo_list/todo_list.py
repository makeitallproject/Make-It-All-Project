"""To-do list screen backed by the shared in-memory task store."""

import signal
import sys

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStyle,
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

CONTENT_MAX_WIDTH = 900
LIST_GAP = 10

# Matches the type scale used by the kanban and forum screens: 12 meta,
# 13 UI, 14 card title, 20 screen title.
STYLESHEET = """
QCheckBox {
    font-size: 13px;
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
QFrame#card {
    background-color: palette(base);
    border: 1px solid palette(mid);
    border-radius: 8px;
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
QScrollArea#listScroll {
    border: none;
    background: transparent;
}
"""


class TaskCard(QFrame):
    """One task with its subtasks, completion state, and delete action."""

    delete_requested = pyqtSignal(dict)
    changed = pyqtSignal()

    def __init__(self, task: dict, parent=None):
        super().__init__(parent)
        self.task = task
        self.progress_label = None
        self.progress_bar = None

        self.setObjectName("card")
        self.setAccessibleName(f"Task: {task['name']}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        layout.addLayout(self.build_header())
        layout.addLayout(self.build_meta_row())
        layout.addWidget(self.build_body())

    def build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        title = QLabel(self.task["name"])
        title.setObjectName("cardTitle")
        title.setWordWrap(True)
        row.addWidget(title, 1)

        delete_button = QPushButton("Delete")
        delete_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        )
        delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_button.setAccessibleName(f"Delete {self.task['name']}")
        delete_button.clicked.connect(lambda: self.delete_requested.emit(self.task))
        row.addWidget(delete_button, 0, Qt.AlignmentFlag.AlignTop)
        return row

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
                "cardOverdue" if task_meta.is_overdue(self.task) else "cardMeta"
            )
            meta.setToolTip(task_meta.meta_tooltip(self.task))
            row.addWidget(meta)
        return row

    def build_body(self) -> QWidget:
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        subtasks = self.task.get("subtasks", [])
        if not subtasks:
            complete = QCheckBox("Mark as complete")
            complete.setChecked(state.is_completed(self.task))
            complete.setCursor(Qt.CursorShape.PointingHandCursor)
            complete.toggled.connect(self.set_task_completed)
            layout.addWidget(complete)
            return body

        for index, subtask in enumerate(subtasks):
            check = QCheckBox(subtask["name"])
            check.setChecked(subtask["completed"])
            check.setSizePolicy(
                QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
            )
            check.setToolTip(subtask["name"])
            check.setCursor(Qt.CursorShape.PointingHandCursor)
            check.toggled.connect(
                lambda checked, position=index: self.set_subtask_completed(
                    position, checked
                )
            )
            layout.addWidget(check)

        layout.addWidget(self.build_progress())
        return body

    def build_progress(self) -> QWidget:
        holder = QWidget()
        layout = QVBoxLayout(holder)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(4)

        self.progress_label = QLabel()
        self.progress_label.setObjectName("cardMeta")
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("subtaskProgress")
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        layout.addWidget(self.progress_bar)

        self.update_progress()
        return holder

    def update_progress(self) -> None:
        subtasks = self.task.get("subtasks", [])
        total = len(subtasks)
        done = sum(1 for subtask in subtasks if subtask["completed"])
        text = task_meta.progress_text(done, total)

        self.progress_label.setText(text)
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(done)
        self.progress_bar.setAccessibleName(text)

    def set_task_completed(self, completed: bool) -> None:
        self.task["completed"] = completed
        if completed:
            self.task["column"] = "Done"
        elif self.task["column"] == "Done":
            self.task["column"] = "To Do"
        self.changed.emit()

    def set_subtask_completed(self, index: int, completed: bool) -> None:
        self.task["subtasks"][index]["completed"] = completed
        self.update_progress()
        self.changed.emit()


class TodoListScreen(QWidget):
    kanban_requested = pyqtSignal()

    def __init__(self, user: str = ""):
        super().__init__()

        self.current_user = user or state.get_user()
        self.add_task_window = None
        self.suppress_refresh = False

        self.setWindowTitle("Make-It-All To-Do List")
        self.setMinimumSize(500, 300)
        self.resize(900, 760)
        self.setStyleSheet(STYLESHEET)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        self.header = AppHeader(
            "To-Do List", user=self.current_user, back_to_calendar=True
        )
        root.addWidget(self.header)

        controls = QHBoxLayout()
        self.create_task_btn = QPushButton("Create a task")
        self.create_task_btn.clicked.connect(self.open_add_task)
        self.kanban_btn = QPushButton("Switch to Kanban Board")
        self.kanban_btn.clicked.connect(lambda: self.kanban_requested.emit())
        controls.addWidget(self.create_task_btn)
        controls.addWidget(self.kanban_btn)
        controls.addStretch()

        self.scroll = QScrollArea()
        self.scroll.setObjectName("listScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.list_container = QWidget()
        self.list_container.setAccessibleName("Task list")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(LIST_GAP)
        self.scroll.setWidget(self.list_container)

        content = QWidget()
        content.setMaximumWidth(CONTENT_MAX_WIDTH)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)
        content_layout.addLayout(controls)
        content_layout.addWidget(self.scroll, 1)

        # Grow the column to its maximum width before the side gaps share
        # the remaining space, so the list stays centered on wide screens.
        content_row = QHBoxLayout()
        content_row.addStretch(1)
        content_row.addWidget(content, 100)
        content_row.addStretch(1)
        root.addLayout(content_row, 1)

        self.refresh()
        state.subscribe(self.refresh)

    def refresh(self) -> None:
        """Rebuild the list from the shared task store."""
        if self.suppress_refresh:
            return

        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if not state.tasks:
            self.list_layout.addWidget(
                EmptyState("No tasks yet", "Create a task to get started."), 1
            )
            return

        for task in state.tasks:
            card = TaskCard(task)
            card.delete_requested.connect(self.confirm_delete)
            card.changed.connect(self.on_card_changed)
            self.list_layout.addWidget(card)

        self.list_layout.addStretch()

    def on_card_changed(self) -> None:
        """Tell the other screens without rebuilding this list mid-edit."""
        self.suppress_refresh = True
        try:
            state.notify_changed()
        finally:
            self.suppress_refresh = False

    def confirm_delete(self, task: dict) -> None:
        box = QMessageBox(self)
        box.setWindowTitle("Delete task")
        box.setIcon(QMessageBox.Icon.Warning)
        box.setText(f'Delete "{task["name"]}"?')
        box.setInformativeText("This cannot be undone.")
        cancel_button = box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        delete_button = box.addButton("Delete", QMessageBox.ButtonRole.DestructiveRole)
        box.setDefaultButton(cancel_button)
        box.exec()
        if box.clickedButton() is delete_button:
            state.remove_task(task)

    def open_add_task(self) -> None:
        if self.add_task_window is None:
            self.add_task_window = task_screen.MainWindow(user=self.current_user)
        self.add_task_window.show()
        self.add_task_window.raise_()
        self.add_task_window.activateWindow()

    def set_user(self, user: str) -> None:
        """Update the signed-in user shown in the header."""
        self.current_user = user or state.get_user()
        self.header.set_user(self.current_user)
        if self.add_task_window is not None:
            self.add_task_window.set_user(self.current_user)


def startup() -> None:
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Make Ctrl+C work
    app = QApplication(sys.argv)

    from screens import kanban

    window = TodoListScreen()
    board = kanban.KanbanScreen()
    window.kanban_requested.connect(lambda: (window.hide(), board.show()))
    board.todo_requested.connect(lambda: (board.hide(), window.show()))
    board.header.back_requested.connect(lambda: (board.hide(), window.show()))
    window.header.back_requested.connect(window.close)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    startup()
