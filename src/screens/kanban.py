import signal
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

SPACING = 8

TASKS = [
    {
        "column": "To Do",
        "tasks": [
            {
                "name": "Set up CI pipeline",
                "subtasks": [
                    {"name": "Install GitHub Actions", "completed": False},
                    {"name": "Add lint step", "completed": False},
                ],
            },
            {
                "name": "Write project README",
                "subtasks": [],
            },
        ],
    },
    {
        "column": "In Progress",
        "tasks": [
            {
                "name": "Design database schema",
                "subtasks": [
                    {"name": "Draft ER diagram", "completed": True},
                    {"name": "Normalize tables", "completed": False},
                ],
            },
        ],
    },
    {
        "column": "Done",
        "tasks": [
            {
                "name": "Scaffold repository",
                "subtasks": [
                    {"name": "Init git repo", "completed": True},
                    {"name": "Add pyproject.toml", "completed": True},
                ],
            },
        ],
    },
]


class TaskCard(QWidget):
    def __init__(self, task):
        super().__init__()
        self.expanded = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(*[SPACING] * 4)
        layout.setSpacing(SPACING)

        title = QLabel(task["name"])
        title.setWordWrap(True)
        layout.addWidget(title)

        # Subtasks!
        self.subtask_area = QWidget()
        subtask_layout = QVBoxLayout(self.subtask_area)
        subtask_layout.setContentsMargins(SPACING, 0, 0, SPACING)
        subtask_layout.setSpacing(4)
        for subtask in task.get("subtasks", []):
            check = QCheckBox(subtask["name"])
            check.setChecked(subtask["completed"])
            subtask_layout.addWidget(check)
        self.subtask_area.hide()
        layout.addWidget(self.subtask_area)

        self.toggle_btn = QPushButton("Expand")
        self.toggle_btn.clicked.connect(self.toggle_subtasks)
        layout.addWidget(self.toggle_btn)

    def toggle_subtasks(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.subtask_area.show()
            self.toggle_btn.setText("Retract")
        else:
            self.subtask_area.hide()
            self.toggle_btn.setText("Expand")


class ColumnWidget(QFrame):
    def __init__(self, name, tasks):
        super().__init__()
        self.collapsed = False

        self.setObjectName("column")
        self.setStyleSheet("QFrame#column { border: 1px solid #6e6e79; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel(name)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()

        layout.addLayout(header)

        # The body has the tasks
        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(SPACING)
        for task in tasks:
            self.body_layout.addWidget(TaskCard(task))
        self.body_layout.addStretch()
        layout.addWidget(self.body)


class KanbanScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Project tasks (Kanban view)")

        layout = QHBoxLayout(self)

        layout.setContentsMargins(*[SPACING] * 4)
        layout.setSpacing(SPACING)

        for column in TASKS:
            layout.addWidget(ColumnWidget(column["column"], column["tasks"]), 1)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Make Ctrl+C work
    app = QApplication(sys.argv)
    window = KanbanScreen()
    window.show()
    sys.exit(app.exec())
