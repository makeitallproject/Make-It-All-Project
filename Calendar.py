import sys
from datetime import date

# QDate is used for Qt widgets and calendar calculations; date is used as a
# simple dictionary key for storing tasks independently of the UI.
from PyQt6.QtCore import QDate, Qt, QPoint
from PyQt6.QtGui import QFont, QPainter, QColor
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
)

is_manager = False

task_list = [{"date" : QDate(2026, 11, 30), "tasks": [{"name" : "Finish Team Project", "completed": False},{"name" : "Team networking event", "completed": True}]},
             {"date" : QDate(2026, 11, 22), "tasks": [{"name" : "Finish Team Project", "completed": False}]},]

class CalendarApp(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simple Calendar")
        #self.setGeometry(300,300,400,300)

        #create calendar widget
        self.calendar = SpecialCalendar()
        #connect signal for date selection
        self.calendar.selectionChanged.connect(self.on_date_selected)
        #set todays date as selected
        self.calendar.setSelectedDate(QDate.currentDate())

        #also create all tasks button
        self.all_tasks_btn = QPushButton("View All Tasks")
        self.all_tasks_btn_pressed = False
        self.all_tasks_btn.clicked.connect(self.clicked_all_tasks_btn)

        #add task button
        self.add_task_btn = QPushButton("Add Task")
        self.add_task_btn_pressed = False
        self.add_task_btn.clicked.connect(self.clicked_add_task_btn)
        self.add_task_window = AddTask(self.calendar)

        #show tasks on selected date
        self.show_tasks = QLabel()


        #create layout and add calendar
        layout = QVBoxLayout()
        layout.addWidget(self.add_task_btn)
        layout.addWidget(self.calendar)
        layout.addWidget(self.all_tasks_btn)
        layout.addWidget(self.show_tasks)
        self.setLayout(layout)

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
                    task_txt += f"{task["name"]}, {"Completed" if task["completed"] == True else "Incomplete"} \n"

                self.show_tasks.setText(task_txt)
                return

        #otherwise, say there are no tasks due on this date
        self.show_tasks.setText("There are no tasks due on this date")

    def clicked_all_tasks_btn(self):
        """
        if self.all_tasks_button_pressed:
            self.all_tasks.setText("")

        else:
            task_txt = ""
            for task in task_list:
                task_txt += f"{task["task"]}, {"Completed" if task["completed"] == True else "Incomplete"}, Finish Date: {task["date"].strftime("%d/%m/%Y")} \n" 

            self.all_tasks.setText(task_txt)
        """
        # clicking on the "all tasks" button will take the user to the to-do list
        return

    def clicked_add_task_btn(self):
        self.add_task_window.show()



class SpecialCalendar(QCalendarWidget):
    def __init__(self):
        super().__init__()

    def paintCell(self, painter: QPainter, rect, date: QDate):
            """
            draw red dots on calendar to show there are tasks due on that date
            """
            #let Qt draw the normal cell (number, selection, etc.) first
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

            self.calendar = calendar

            #enter name of task
            self.name_input = QLineEdit(self)

            #enter date of task ending
            self.calendar = SpecialCalendar()

            #add "submit" button
            self.submit_btn = QPushButton("Submit")
            self.submit_btn.clicked.connect(self.clicked_submit_btn)

            #add confirmation text
            self.confirm_submit = QLabel()


            #create layout and add calendar
            layout = QVBoxLayout()
            layout.addWidget(self.name_input)
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