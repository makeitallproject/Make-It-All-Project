import sys
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
)

is_manager = True

task_list = [{"date" : QDate(2026, 10, 30), "tasks": [{"name" : "Finish Team Project", "completed": False},{"name" : "Team networking event", "completed": True}]},
             {"date" : QDate(2026, 10, 18), "tasks": [{"name" : "Finish Team Project", "completed": False}]},]

class CalendarApp(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Calendar")
        self.setMinimumSize(700, 560)
        self.setStyleSheet(
            """
            QPushButton {
                border: 1px solid;
                padding: 8px 12px;
                font-size: 13px;
            """
        )

        #create calendar
        self.calendar = SpecialCalendar()
        self.calendar.selectionChanged.connect(self.on_date_selected)
        self.calendar.setSelectedDate(QDate.currentDate())

        #create view tasks button
        self.all_tasks_btn = QPushButton("View Tasks")
        self.all_tasks_btn_pressed = False
        self.all_tasks_btn.clicked.connect(self.clicked_all_tasks_btn)

        #create add task button
        if is_manager:
            self.add_task_btn = QPushButton("Add a task")
            self.add_task_btn.clicked.connect(self.clicked_add_task_btn)
            self.add_task_window = AddTask(self.calendar)
            self.add_task_btn.setMinimumSize(70, 60)

        #create logo
        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.logo.setMinimumSize(200, 60)
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
        logo_row.addWidget(self.logo)

        #add logo row to header
        header_layout.addLayout(logo_row)
        header_layout.addStretch()

        #create row for buttons
        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(10)
        self.all_tasks_btn.setMinimumSize(70, 60)
        button_row.addWidget(self.all_tasks_btn)
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
        clicking on the "all tasks" button will take the user to the to-do list (WIP)
        """
        return

    def clicked_add_task_btn(self):
        """
        show new window for adding tasks
        """
        self.add_task_window.show()



class SpecialCalendar(QCalendarWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            /* top navigation bar (month/year buttons) */
            QCalendarWidget QToolButton {
                font-size: 14px;
            }
        """)

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


class AddTask(QWidget):
    def __init__(self,calendar):
            super().__init__()
    
            self.setWindowTitle("Add Task")
            self.setGeometry(300,300,400,300)
            self.setStyleSheet(
                """
                QPushButton {
                    border: 1px solid;
                    padding: 8px 12px;
                    font-size: 13px;
                }
                """
            )

            self.calendar = calendar



            #enter name of task
            self.name_title = QLabel()
            self.name_title.setText("Task Name:")
            self.name_input = QLineEdit(self)

            #enter date of task ending
            self.date_title = QLabel()
            self.date_title.setText("\nTask Due Date: ")
            self.calendar = SpecialCalendar()

            #add "submit" button
            self.submit_btn = QPushButton("Submit")
            self.submit_btn.clicked.connect(self.clicked_submit_btn)

            #add confirmation text
            self.confirm_submit = QLabel()


            #create layout and add calendar
            layout = QVBoxLayout()
            layout.addWidget(self.name_title)
            layout.addWidget(self.name_input)
            layout.addWidget(self.date_title)
            layout.addWidget(self.calendar)
            layout.addWidget(self.submit_btn)
            layout.addWidget(self.confirm_submit)
            self.setLayout(layout)

    def clicked_submit_btn(self):
        """
        No need to implement adding tasks at first prototype stage, so success and fail messages are toggled
        """
        
        success = "Task added successfully!"
        fail = "Unable to add task."

        if self.confirm_submit.text() == fail or self.confirm_submit.text() == "":
            self.confirm_submit.setText(success)

        elif self.confirm_submit.text() == success:
            self.confirm_submit.setText(fail)

        self.calendar.updateCells()

if __name__ == "__main__":
    # This guard allows Calendar.py to be imported for testing without opening
    # a window, while still supporting direct execution from the command line.
    app = QApplication(sys.argv)
    window = CalendarApp()
    window.show()
    sys.exit(app.exec())