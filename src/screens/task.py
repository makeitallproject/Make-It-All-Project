import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QPushButton, QLabel, QLineEdit, QCheckBox)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logo_label = QLabel()
        pixmap = QPixmap("assets/company_logo.png")
        logo_label.setPixmap(pixmap.scaled(180, 90, Qt.AspectRatioMode.KeepAspectRatio))
        self.setWindowTitle("Create New Task")
        self.resize(600, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        #top section of the page e.g. company logo
        top_layout = QHBoxLayout()
        
        top_layout.addWidget(logo_label)
        top_layout.addStretch() 
        
        main_layout.addLayout(top_layout)
        main_layout.addSpacing(20) 

        #middle section of the page e.g. the form
        form_layout = QFormLayout()

        form_layout.setSpacing(20)
        
        self.title_input = QLineEdit()
        self.notes_input = QLineEdit()
        self.people_input = QLineEdit()
        self.due_input = QLineEdit()
        self.docs_input = QLineEdit()

        for input_field in [self.title_input, self.notes_input, self.people_input, self.due_input, self.docs_input]:
            input_field.setMinimumHeight(35)
        
        form_layout.addRow("Task Title", self.title_input)
        form_layout.addRow("Task Notes", self.notes_input)
        form_layout.addRow("People to give task to", self.people_input)
        form_layout.addRow("Due", self.due_input)
        form_layout.addRow("Insert documents", self.docs_input)
        
        main_layout.addLayout(form_layout)

        #this is the bottom reminders checkbox section
        self.reminders_checkbox = QCheckBox("Section below expands if this is checked")
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.addRow("Reminders?", self.reminders_checkbox)

        self.reminders_container = QWidget()
        reminders_layout = QFormLayout(self.reminders_container)
        reminders_layout.setContentsMargins(0, 10, 0, 0) 
        reminders_layout.setSpacing(20)
        
        self.dates_input = QLineEdit()
        self.times_input = QLineEdit()
        self.dates_input.setMinimumHeight(35)
        self.times_input.setMinimumHeight(35)
        
        reminders_layout.addRow("Dates", self.dates_input)
        reminders_layout.addRow("Times", self.times_input)

        self.reminders_container.setVisible(False)
        main_layout.addWidget(self.reminders_container)

        self.reminders_checkbox.toggled.connect(self.toggle_reminders)

        main_layout.addStretch() 

        #bottom section e.g. back button and submit button
        bottom_layout = QHBoxLayout()
        
        back_btn = QPushButton("Back")
        back_btn.setFixedSize(100, 45)
        
        submit_btn = QPushButton("Submit")
        submit_btn.setFixedSize(120, 45)
        
        bottom_layout.addWidget(back_btn)
        bottom_layout.addStretch() 
        bottom_layout.addWidget(submit_btn)
        
        main_layout.addLayout(bottom_layout)

    def toggle_reminders(self, checked):
        self.reminders_container.setVisible(checked)


app = QApplication(sys.argv)

window = MainWindow()
window.show()


app.exec()