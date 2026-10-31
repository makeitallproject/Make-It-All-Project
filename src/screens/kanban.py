import signal
import sys

from PyQt6.QtGui import QColor
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

GAP = 8

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


class TaskCard(QFrame):
    def __init__(self, task):
        super().__init__()
        self.expanded = False

        self.setObjectName("card")
        self.setStyleSheet("""
            QFrame#card {
                background-color: palette(base);
                border: 2px solid palette(light);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(GAP)

        # Card title
        title = QLabel(task["name"])
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 10pt; font-weight: semibold;")
        title.setContentsMargins(GAP, GAP, GAP, 0)
        layout.addWidget(title)

        # Subtasks!
        self.subtask_area = QWidget()
        subtask_layout = QVBoxLayout(self.subtask_area)
        subtask_layout.setContentsMargins(GAP, 0, GAP, 0)
        subtask_layout.setSpacing(4)
        for subtask in task.get("subtasks", []):
            check = QCheckBox(subtask["name"])
            check.setChecked(subtask["completed"])
            subtask_layout.addWidget(check)
        self.subtask_area.hide()
        layout.addWidget(self.subtask_area)

        self.expand_btn = QPushButton("Expand") if task.get("subtasks") else None
        if self.expand_btn:
            self.expand_btn.setObjectName("cardFooter")
            self.expand_btn.setStyleSheet("""
                QPushButton#cardFooter {
                  border: 1px solid transparent;
                  border-top: 1px solid palette(light);
                  text-align: center;
                  padding: 6px 0;
                }
                QPushButton#cardFooter:hover { background: palette(light); }
                QPushButton#cardFooter:pressed { background: palette(midlight); }
            """)
            self.expand_btn.clicked.connect(self.toggle_subtasks)
            layout.addWidget(self.expand_btn)
        else:
            layout.addSpacing(GAP)

    def toggle_subtasks(self):
        if not self.expand_btn:
            print("Warning: toggle_subtasks called on a task with no subtasks")
            return
        self.expanded = not self.expanded
        if self.expanded:
            self.subtask_area.show()
            self.expand_btn.setText("Retract")
        else:
            self.subtask_area.hide()
            self.expand_btn.setText("Expand")


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
        title.setStyleSheet("font-size: 12pt; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()

        layout.addLayout(header)

        # The body has the tasks
        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(GAP)
        for task in tasks:
            self.body_layout.addWidget(TaskCard(task))
        self.body_layout.addStretch()
        layout.addWidget(self.body)


class KanbanScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Project tasks (Kanban view)")
        self.setMinimumSize(900, 700)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(*[GAP] * 4)
        layout.setSpacing(GAP)

        for column in TASKS:
            layout.addWidget(ColumnWidget(column["column"], column["tasks"]), 1)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Make Ctrl+C work
    app = QApplication(sys.argv)
    window = KanbanScreen()
    window.show()
    sys.exit(app.exec())
