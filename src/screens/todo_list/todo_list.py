"""To-do list screen backed by the shared in-memory task store."""

import math
import signal
import sys
from pathlib import Path

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import state
from screens import task as task_screen
from widgets.app_header import AppHeader
from widgets.empty_state import EmptyState

ASSETS_DIR = Path("assets") / "todo_list"
SCREEN_DIR = Path("src") / "screens" / "todo_list"
STYLESHEET_PATH = SCREEN_DIR / "stylesheet.qss"

TASKS_PER_PAGE = 2


def completion_percent(task: dict) -> int:
    """Percentage of a task's subtasks that are complete."""
    subtasks = task.get("subtasks", [])
    if not subtasks:
        return 100 if state.is_completed(task) else 0
    done = sum(1 for subtask in subtasks if subtask["completed"])
    return done * 100 // len(subtasks)


def progress_bar_path(percent: int) -> Path:
    """Pick the progress image closest to the given percentage."""
    if percent >= 100:
        file_name = "full_progress_bar.png"
    elif percent >= 66:
        file_name = "two_third_progress_bar.png"
    elif percent >= 50:
        file_name = "half_progress_bar.png"
    elif percent >= 33:
        file_name = "one_third_progress_bar.png"
    else:
        file_name = "empty_progress_bar.png"
    return ASSETS_DIR / file_name


class MainWindow(QMainWindow):
    kanban_requested = pyqtSignal()

    def __init__(self, user: str = ""):
        super().__init__()

        self.current_user = user or state.get_user()
        self.page_number = 1
        self.task_to_delete = None
        self.add_task_window = None

        self.setWindowTitle("To-Do List")
        self.resize(1100, 780)
        self.setMinimumSize(640, 480)

        self.header = AppHeader(
            "To-Do List", user=self.current_user, back_to_calendar=True
        )
        self.header.back_requested.connect(self.exit_window)

        self.stack = QStackedWidget()

        self.list_page = QWidget()
        self.list_layout = QVBoxLayout(self.list_page)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(0)
        self.stack.addWidget(self.list_page)

        self.delete_confirm_text = QLabel()
        self.delete_confirm_text.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        self.delete_confirm_text.setWordWrap(True)
        self.stack.addWidget(self.build_delete_page())

        controls = QHBoxLayout()
        self.create_task_btn = QPushButton("Create a task")
        self.create_task_btn.clicked.connect(self.open_add_task)
        self.kanban_btn = QPushButton("Switch to Kanban Board")
        self.kanban_btn.clicked.connect(
            lambda: self.kanban_requested.emit()
        )
        controls.addWidget(self.create_task_btn)
        controls.addWidget(self.kanban_btn)
        controls.addStretch()

        ladder = QVBoxLayout()
        ladder.setContentsMargins(16, 16, 16, 16)
        ladder.setSpacing(12)
        ladder.addWidget(self.header)
        ladder.addLayout(controls)
        ladder.addWidget(self.stack, 1)

        container = QWidget()
        container.setLayout(ladder)
        self.setCentralWidget(container)

        self.refresh()
        state.subscribe(self.refresh)

    def build_delete_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addStretch()
        layout.addWidget(self.delete_confirm_text)

        confirm_button = QPushButton(
            icon=QIcon(str(ASSETS_DIR / "delete_icon.png")), text=""
        )
        confirm_button.setObjectName("delete")
        confirm_button.setFixedSize(101, 101)
        confirm_button.setIconSize(QSize(101, 101))
        confirm_button.clicked.connect(self.delete_task)

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(confirm_button)
        button_row.addStretch()
        layout.addLayout(button_row)
        layout.addStretch()
        return page

    def refresh(self) -> None:
        """Rebuild the visible page from the shared task store."""
        page_count = max(1, math.ceil(len(state.tasks) / TASKS_PER_PAGE))
        self.page_number = min(max(self.page_number, 1), page_count)
        self.build_list(page_count)

    def build_list(self, page_count: int) -> None:
        self.clear_layout(self.list_layout)

        arrows = QHBoxLayout()
        arrows.addWidget(
            self.build_page_button(
                "page_arrow_backward.png",
                self.previous_page,
                self.page_number > 1,
            )
        )
        arrows.addStretch()
        arrows.addWidget(
            self.build_page_button(
                "page_arrow_forward.png",
                self.next_page,
                self.page_number < page_count,
            )
        )
        self.list_layout.addLayout(arrows)

        start = (self.page_number - 1) * TASKS_PER_PAGE
        page_tasks = state.tasks[start : start + TASKS_PER_PAGE]

        task_row = QHBoxLayout()
        task_row.setSpacing(24)
        if page_tasks:
            task_row.addStretch()
            for task in page_tasks:
                task_row.addWidget(self.build_task(task), 1)
            task_row.addStretch()
        else:
            task_row.addWidget(
                EmptyState("No tasks yet", "Create a task to get started."), 1
            )
        self.list_layout.addLayout(task_row, 1)

        add_button = QPushButton(
            icon=QIcon(str(ASSETS_DIR / "add_item.png")), text=""
        )
        add_button.setFixedSize(101, 101)
        add_button.setIconSize(QSize(101, 101))
        add_button.clicked.connect(self.open_add_task)

        page_label = QLabel(f"Page {self.page_number}/{page_count}")
        page_label.setObjectName("pageNumber")
        page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        bottom_row = QHBoxLayout()
        bottom_row.addWidget(add_button)
        bottom_row.addWidget(page_label, 1)
        bottom_row.addSpacing(101)
        self.list_layout.addLayout(bottom_row)

    def build_page_button(self, icon_name, slot, visible: bool) -> QPushButton:
        button = QPushButton(icon=QIcon(str(ASSETS_DIR / icon_name)), text="")
        button.setFixedSize(101, 85)
        button.setIconSize(QSize(101, 101))
        button.clicked.connect(slot)
        button.setVisible(visible)
        return button

    def build_task(self, task: dict) -> QWidget:
        panel = QWidget()
        panel.setObjectName("taskWindow")
        panel.setMinimumHeight(400)
        panel.setMaximumWidth(500)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        name = QLabel(task["name"])
        name.setObjectName("task")
        name.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        name.setWordWrap(True)
        layout.addWidget(name)

        subtasks = task.get("subtasks", [])
        if subtasks:
            for index, subtask in enumerate(subtasks):
                layout.addLayout(self.build_subtask_row(task, index, subtask))
            layout.addWidget(self.build_progress(task))
        else:
            checkbox = QCheckBox("Mark as complete")
            checkbox.setChecked(state.is_completed(task))
            checkbox.stateChanged.connect(
                lambda _state, current=task, box=checkbox: (
                    self.set_task_completed(current, box.isChecked())
                )
            )
            layout.addWidget(checkbox)

        delete_button = QPushButton(
            icon=QIcon(str(ASSETS_DIR / "delete_icon.png")), text=""
        )
        delete_button.setObjectName("delete")
        delete_button.setFixedSize(20, 20)
        delete_button.setIconSize(QSize(20, 20))
        delete_button.clicked.connect(
            lambda _checked=False, current=task: self.confirm_delete(current)
        )
        layout.addWidget(
            delete_button, 0, Qt.AlignmentFlag.AlignRight
        )
        return panel

    def build_subtask_row(self, task: dict, index: int, subtask: dict):
        row = QHBoxLayout()
        label = QLabel(subtask["name"])
        label.setObjectName("subtask")
        label.setWordWrap(True)
        label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        row.addWidget(label, 1)

        checkbox = QCheckBox()
        checkbox.setChecked(subtask["completed"])
        checkbox.stateChanged.connect(
            lambda _state, current=task, position=index, box=checkbox: (
                self.set_subtask_completed(current, position, box.isChecked())
            )
        )
        row.addWidget(checkbox)
        return row

    def build_progress(self, task: dict) -> QWidget:
        percent = completion_percent(task)
        holder = QWidget()
        layout = QVBoxLayout(holder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        label = QLabel(f"{percent}%")
        label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
        )
        label.setMaximumHeight(20)

        bar = QLabel()
        bar.setPixmap(QPixmap(str(progress_bar_path(percent))))
        bar.setMaximumHeight(20)
        bar.setContentsMargins(25, 0, 0, 0)

        layout.addWidget(label)
        layout.addWidget(bar)
        return holder

    def clear_layout(self, layout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                continue
            child_layout = item.layout()
            if child_layout is not None:
                self.clear_layout(child_layout)

    def set_task_completed(self, task: dict, completed: bool) -> None:
        task["completed"] = completed
        if completed:
            task["column"] = "Done"
        elif task["column"] == "Done":
            task["column"] = "To Do"
        state.notify_changed()

    def set_subtask_completed(
        self, task: dict, index: int, completed: bool
    ) -> None:
        task["subtasks"][index]["completed"] = completed
        state.notify_changed()

    def confirm_delete(self, task: dict) -> None:
        self.task_to_delete = task
        self.delete_confirm_text.setText(
            f"Are you sure that you want to delete {task['name']}?"
        )
        self.stack.setCurrentIndex(1)

    def delete_task(self) -> None:
        if self.task_to_delete is not None:
            state.remove_task(self.task_to_delete)
            self.task_to_delete = None
        self.stack.setCurrentIndex(0)

    def open_add_task(self) -> None:
        if self.add_task_window is None:
            self.add_task_window = task_screen.MainWindow(
                user=self.current_user
            )
        self.add_task_window.show()
        self.add_task_window.raise_()
        self.add_task_window.activateWindow()

    def previous_page(self) -> None:
        if self.page_number > 1:
            self.page_number -= 1
            self.refresh()

    def next_page(self) -> None:
        self.page_number += 1
        self.refresh()

    def set_user(self, user: str) -> None:
        self.current_user = user or state.get_user()
        self.header.set_user(self.current_user)
        if self.add_task_window is not None:
            self.add_task_window.set_user(self.current_user)

    def exit_window(self) -> None:
        if self.stack.currentIndex() != 0:
            self.stack.setCurrentIndex(0)
        else:
            self.close()


def startup() -> None:
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    if STYLESHEET_PATH.exists():
        app.setStyleSheet(STYLESHEET_PATH.read_text())

    from screens import kanban

    window = MainWindow()
    board = kanban.KanbanScreen()
    window.kanban_requested.connect(lambda: (window.hide(), board.show()))
    board.todo_requested.connect(lambda: (board.hide(), window.show()))
    board.header.back_requested.connect(
        lambda: (board.hide(), window.show())
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    startup()
