"""Calendar screen with a day summary and links to the other screens."""

import signal
import sys

from PyQt6.QtCore import QDate, QPoint, Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QApplication,
    QCalendarWidget,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from screens import kanban, login, task
from widgets.app_header import AppHeader

IS_MANAGER = True
CURRENT_USER = "Mish"

task_list = [
    {
        "date": QDate(2026, 10, 30),
        "tasks": [
            {"name": "Finish Team Project", "completed": False},
            {"name": "Team networking event", "completed": True},
        ],
    },
    {
        "date": QDate(2026, 10, 18),
        "tasks": [{"name": "Finish Team Project", "completed": False}],
    },
]


class CalendarApp(QWidget):
    def __init__(self, login_window):
        super().__init__()

        self.setWindowTitle("Make-It-All Calendar")
        self.setMinimumSize(700, 560)

        self.login_window = login_window
        self.current_user = CURRENT_USER

        self.calendar = SpecialCalendar()
        self.calendar.selectionChanged.connect(self.on_date_selected)
        self.calendar.setSelectedDate(QDate.currentDate())

        self.all_tasks_btn = QPushButton("View tasks")
        self.all_tasks_btn.clicked.connect(self.clicked_all_tasks_btn)
        self.all_tasks_window = kanban.KanbanScreen()

        self.knowledge_btn = QPushButton("View knowledge")
        self.knowledge_btn.clicked.connect(self.clicked_knowledge_btn)

        self.logout_btn = QPushButton("Log out")
        self.logout_btn.clicked.connect(self.clicked_logout_btn)

        if IS_MANAGER:
            self.add_task_btn = QPushButton("Add task")
            self.add_task_btn.clicked.connect(self.clicked_add_task_btn)
            self.add_task_window = task.MainWindow()

        for button in self.action_buttons():
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.show_tasks = QLabel("Select a day to view its tasks")
        self.show_tasks.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.show_tasks.setMinimumHeight(58)
        self.show_tasks.setStyleSheet(
            "border: 4px; font-size: 20px; padding: 8px;"
        )

        self.header = AppHeader(
            "Make-It-All Calendar",
            subtitle="Team calendar",
            user=self.current_user,
        )

        calendar_frame = QFrame()
        calendar_frame.setFrameShape(QFrame.Shape.Box)
        calendar_frame.setLineWidth(4)
        calendar_layout = QVBoxLayout(calendar_frame)
        calendar_layout.setContentsMargins(16, 14, 16, 14)
        calendar_layout.addWidget(self.calendar)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)
        root.addWidget(self.header)
        root.addLayout(self.build_action_row())
        root.addWidget(calendar_frame, 1)
        root.addWidget(self.show_tasks)

        self.on_date_selected()

    def action_buttons(self) -> list[QPushButton]:
        buttons = [self.all_tasks_btn, self.knowledge_btn, self.logout_btn]
        if IS_MANAGER:
            buttons.append(self.add_task_btn)
        return buttons

    def build_action_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(self.all_tasks_btn)
        row.addWidget(self.knowledge_btn)
        if IS_MANAGER:
            row.addWidget(self.add_task_btn)
        row.addStretch()
        row.addWidget(self.logout_btn)
        return row

    def on_date_selected(self) -> None:
        """Show the tasks due on the selected day."""
        selected_date = self.calendar.selectedDate()

        for day in task_list:
            if day["date"] != selected_date:
                continue

            lines = [f"Tasks due on {selected_date.toString()}:"]
            for task in day["tasks"]:
                status = "Completed" if task["completed"] else "Incomplete"
                lines.append(f"{task['name']}, {status}")
            self.show_tasks.setText("\n".join(lines))
            return

        self.show_tasks.setText("There are no tasks due on this date")

    def clicked_all_tasks_btn(self) -> None:
        """Show the Kanban board."""
        self.all_tasks_window.show()

    def clicked_knowledge_btn(self) -> None:
        """Show the knowledge-sharing screen."""
        # self.knowledge_window.show()

    def clicked_logout_btn(self) -> None:
        """Return to the login screen."""
        self.login_window.password_input.setText("")
        self.login_window.username_input.setText("")
        self.login_window.showMaximized()
        self.hide()

    def clicked_add_task_btn(self) -> None:
        """Show the create-task form."""
        self.add_task_window.show()


class SpecialCalendar(QCalendarWidget):
    def paintCell(self, painter: QPainter, rect, date: QDate) -> None:
        """Draw red dots under days that have tasks."""
        super().paintCell(painter, rect, date)

        count = 0
        for day in task_list:
            if day["date"] == date:
                count = len(day["tasks"])
                break

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#e74c3c"))

        # Draw up to 10 small dots along the bottom of the cell.
        dots = min(count, 10)
        radius, gap = 3, 4
        total_width = dots * (2 * radius) + (dots - 1) * gap
        x = rect.center().x() - total_width // 2 + radius
        y = rect.bottom() - radius - 3
        for index in range(dots):
            painter.drawEllipse(
                QPoint(x + index * (2 * radius + gap), y), radius, radius
            )

        painter.restore()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Make Ctrl+C work
    app = QApplication(sys.argv)
    login_window = login.LoginWindow()
    window = CalendarApp(login_window)
    window.show()
    sys.exit(app.exec())
