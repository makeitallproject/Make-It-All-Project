import sys
import signal
import task
import kanban
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

is_manager = True

task_list = [{"date" : QDate(2026, 10, 30), "tasks": [{"name" : "Finish Team Project", "completed": False},{"name" : "Team networking event", "completed": True}]},
             {"date" : QDate(2026, 10, 18), "tasks": [{"name" : "Finish Team Project", "completed": False}]},]

class CalendarApp(QWidget):

    def __init__(self, login_window):
        super().__init__()

        self.setWindowTitle("Calendar")
        self.setMinimumSize(700, 560)


        self.login_window = login_window

        #create calendar
        self.calendar = SpecialCalendar()
        self.calendar.selectionChanged.connect(self.on_date_selected)
        self.calendar.setSelectedDate(QDate.currentDate())

        #create view tasks button
        self.all_tasks_btn = QPushButton("View Tasks")
        self.all_tasks_window = kanban.KanbanScreen()
        self.all_tasks_btn_pressed = False
        self.all_tasks_btn.clicked.connect(self.clicked_all_tasks_btn)
        self.all_tasks_btn.setMinimumSize(70, 60)

        #create knowledge sharing button
        self.knowledge_btn = QPushButton("View Knowledge")
        #self.logout_window = kanban.KanbanScreen()
        self.knowledge_btn.clicked.connect(self.clicked_knowledge_btn)
        self.knowledge_btn.setMinimumSize(70, 60)

        #create log out button
        self.logout_btn = QPushButton("Log Out")
        self.logout_window = self.login_window
        self.logout_btn.clicked.connect(self.clicked_logout_btn)

        #create add task button
        if is_manager:
            self.add_task_btn = QPushButton("Add a task")
            self.add_task_btn.clicked.connect(self.clicked_add_task_btn)
            self.add_task_window = task.MainWindow()
            self.add_task_btn.setMinimumSize(70, 60)


        #create logo
        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.logo.setMaximumSize(280, 78)
        logo_path = Path("assets") / "company_logo.png"
        self.logo.setPixmap(
            QPixmap(str(logo_path)).scaled(
                270,
                70,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

        #create show task button
        self.show_tasks = QLabel("Select a day to view its tasks")
        self.show_tasks.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.show_tasks.setMinimumHeight(58)
        self.show_tasks.setStyleSheet(
            "border: 4px; font-size: 20px; padding: 8px;"
        )

        #create header
        header = QWidget()
        header.setMinimumHeight(185)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 12)
        header_layout.setSpacing(0)

        #create row for logo
        logo_row = QHBoxLayout()
        logo_row.setContentsMargins(0, 0, 0, 0)
        logo_row.addStretch()
        logo_row.addWidget(self.logout_btn)
        logo_row.addSpacerItem(QSpacerItem(1185, 20, QSizePolicy.Policy.Expanding))
        logo_row.addWidget(self.logo)

        #add logo row to header
        header_layout.addLayout(logo_row)
        header_layout.addStretch()

        #create row for buttons
        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(10)
        button_row.addWidget(self.all_tasks_btn)
        button_row.addWidget(self.knowledge_btn)
        if is_manager:
            button_row.addWidget(self.add_task_btn)
        button_row.addStretch()

        #add button row to header
        header_layout.addLayout(button_row)

        #create layout for calendar and tasks
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(header)

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
        self.all_tasks_window.show()

    def clicked_knowledge_btn(self):
        """
        show Mish's knowledge sharing window
        """
        #self.knowledge_window.show()

    def clicked_logout_btn(self):
        """
        show Tobi's log in window
        """
        self.logout_window.password_input.setText("")
        self.logout_window.username_input.setText("")
        self.logout_window.show()
        self.hide()

    def clicked_add_task_btn(self):
        """
        show Evan's "add tasks" window
        """
        self.add_task_window.show()




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
    window = CalendarApp()
    window.show()
    sys.exit(app.exec())