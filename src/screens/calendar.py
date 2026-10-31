import sys
import signal
from screens import forum, login, task, kanban
from pathlib import Path
from datetime import date

# QDate is used for Qt widgets and calendar calculations; date is used as a
# simple dictionary key for storing tasks independently of the UI.
from PyQt6.QtCore import QDate, Qt, QPoint
from PyQt6.QtGui import QFont, QPainter, QColor, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QCalendarWidget,
    QLineEdit,
    QFrame,
    QSpacerItem
)

from widgets.app_header import AppHeader

is_manager = True
CURRENT_USER = "Mish"

task_list = [{"date" : QDate(2026, 10, 30), "tasks": [{"name" : "Finish Team Project", "completed": False},{"name" : "Team networking event", "completed": True}]},
             {"date" : QDate(2026, 10, 18), "tasks": [{"name" : "Finish Team Project", "completed": False}]},]

class CalendarApp(QWidget):

    def __init__(self, login_window):
        super().__init__()

        self.setWindowTitle("Make-It-All System")
        self.setMinimumSize(480, 400)

        self.login_window = login_window
        self.current_user = CURRENT_USER
        self.all_tasks_window = None
        self.knowledge_window = None
        self.add_task_window = None

        #create calendar
        self.calendar = SpecialCalendar()
        self.calendar.selectionChanged.connect(self.on_date_selected)
        self.calendar.setSelectedDate(QDate.currentDate())

        #create view tasks button
        self.all_tasks_btn = QPushButton("View Tasks")
        self.all_tasks_btn_pressed = False
        self.all_tasks_btn.clicked.connect(self.clicked_all_tasks_btn)

        #create knowledge sharing button
        self.knowledge_btn = QPushButton("Open the Forum")
        #self.logout_window = kanban.KanbanScreen()
        self.knowledge_btn.clicked.connect(self.clicked_knowledge_btn)

        #create log out button
        self.logout_btn = QPushButton("Log Out")
        self.logout_window = self.login_window
        self.logout_btn.clicked.connect(self.clicked_logout_btn)

        #create add task button
        if is_manager:
            self.add_task_btn = QPushButton("Create a Task")
            self.add_task_btn.clicked.connect(self.clicked_add_task_btn)

        #create show task button
        self.show_tasks = QLabel("Select a day to view its tasks")
        self.show_tasks.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.show_tasks.setWordWrap(True)
        self.show_tasks.setMinimumHeight(48)
        self.show_tasks.setStyleSheet(
            "border: 4px; font-size: 20px; padding: 8px;"
        )

        #create header
        self.header = AppHeader("Make-It-All System", user=self.current_user)

        #create row for buttons
        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(10)
        button_row.addWidget(self.all_tasks_btn)
        button_row.addWidget(self.knowledge_btn)
        if is_manager:
            button_row.addWidget(self.add_task_btn)
        button_row.addStretch()
        button_row.addWidget(self.logout_btn)

        #create layout for calendar and tasks
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(self.header)
        layout.addLayout(button_row)

        #create frame and box for calendar
        calendar_frame = QFrame()
        calendar_frame.setFrameShape(QFrame.Shape.Box)
        calendar_frame.setLineWidth(4)
        calendar_layout = QVBoxLayout(calendar_frame)
        calendar_layout.setContentsMargins(16, 14, 16, 14)
        calendar_layout.addWidget(self.calendar)
        layout.addWidget(calendar_frame, 1)
        layout.addWidget(self.show_tasks)
        self.setLayout(layout)
        self.on_date_selected()

    def on_date_selected(self):
        """
        display a box with tasks in
        """
        selected_date = self.calendar.selectedDate()

        #if selected date has tasks, show them
        for day in task_list:
             if day["date"] == selected_date:
                task_txt = f"Tasks due on {selected_date.toString()}:\n"
                for task in day["tasks"]:
                    status = "Completed" if task["completed"] else "Incomplete"
                    task_txt += f"{task['name']}, {status}\n"

                self.show_tasks.setText(task_txt)
                return

        #otherwise, say there are no tasks due on this date
        self.show_tasks.setText("There are no tasks due on this date")

    def clicked_all_tasks_btn(self):
        """
        show Mish's Kanban board window
        """
        if self.all_tasks_window is None:
            self.all_tasks_window = kanban.KanbanScreen(user=self.current_user)
            # allow the button in the header to re-focus/re-open this window
            self.all_tasks_window.header.back_requested.connect(
                lambda: self.back_to_calendar(self.all_tasks_window)
            )
        self.show_window(self.all_tasks_window)

    def clicked_knowledge_btn(self):
        """
        show Mish's knowledge sharing window
        """
        if self.knowledge_window is None:
            self.knowledge_window = forum.ForumScreen(user=self.current_user)
            self.knowledge_window.header.back_requested.connect(
                lambda: self.back_to_calendar(self.knowledge_window)
            )
            self.show_window(self.knowledge_window, maximized=True)
        else:
            self.show_window(self.knowledge_window)

    def clicked_logout_btn(self):
        """
        show Tobi's log in window
        """
        for window in self.child_windows():
            window.hide()
        self.logout_window.password_input.setText("")
        self.logout_window.username_input.setText("")
        self.logout_window.showNormal()
        self.hide()

    def clicked_add_task_btn(self):
        """
        show Evan's "add tasks" window
        """
        if self.add_task_window is None:
            self.add_task_window = task.MainWindow(user=self.current_user)
        self.show_window(self.add_task_window)

    def set_user(self, user):
        self.current_user = user or CURRENT_USER
        self.header.set_user(self.current_user)
        for window in self.child_windows():
            window.set_user(self.current_user)

    def child_windows(self):
        windows = (
            self.all_tasks_window,
            self.knowledge_window,
            self.add_task_window,
        )
        return [window for window in windows if window is not None]

    def back_to_calendar(self, window):
        """
        close a child screen and focus the calendar
        """
        window.close()
        self.show_window(self)

    def show_window(self, window, maximized=False):
        if maximized:
            window.showMaximized()
        else:
            window.show()
        window.raise_()
        window.activateWindow()




class SpecialCalendar(QCalendarWidget):
    def __init__(self):
        super().__init__()

        

    def paintCell(self, painter: QPainter, rect, date: QDate):
            """
            draw red dots on calendar to show there are tasks due on that date
            """

            super().paintCell(painter, rect, date)
    
            #see if there are tasks on that date
            count = 0
            for day in task_list:
                if day["date"] == date:
                    count = len(day["tasks"])
                    break

     
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#e74c3c"))
     
            #draw up to 10 small dots along the bottom of the cell
            dots = min(count, 10)
            radius, gap = 3, 4
            total_width = dots * (2 * radius) + (dots - 1) * gap
            x = rect.center().x() - total_width // 2 + radius
            y = rect.bottom() - radius - 3
            for i in range(dots):
                painter.drawEllipse(QPoint(x + i * (2 * radius + gap), y), radius, radius)
     
            painter.restore()


if __name__ == "__main__":
    # This guard allows Calendar.py to be imported for testing without opening
    # a window, while still supporting direct execution from the command line.

    signal.signal(signal.SIGINT, signal.SIG_DFL)  # According to Mish, this "Make Ctrl+C work"
    app = QApplication(sys.argv)
    login_window = login.LoginWindow()
    window = CalendarApp(login_window)
    window.showMaximized()
    sys.exit(app.exec())