from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QHBoxLayout,
                            QVBoxLayout, QPushButton, QLabel, QSizePolicy,
                             QStackedLayout, QCheckBox, QLineEdit)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize, Qt
from pathlib import Path

import sys

from widgets.app_header import AppHeader

# TODO un-hardcode this
CURRENT_USER = "Mish"

ASSETS_DIR = Path("assets") / "todo_list"
DB_DIR = Path("src") / "screens" / "todo_list"

# takes the array of parts as input
# outputs percentage of subtasks completed (2dp) multiplied by 100 (always integer)
def completion(task):
    count = 0
    for amountOfLoops in range(len(task)):
        if task[amountOfLoops] == 1:
            count += 1
    return (count * 100) // len(task)

# takes number in set {0, 33, 50, 66, 100} input
# outputs correct QPixmap
def findProgressBar(percentage):
    match percentage:
        case 100:
            return QPixmap(str(ASSETS_DIR / "full_progress_bar.png"))
        case 66:
            return QPixmap(str(ASSETS_DIR / "two_third_progress_bar.png"))
        case 50:
            return QPixmap(str(ASSETS_DIR / "half_progress_bar.png"))
        case 33:
            return QPixmap(str(ASSETS_DIR / "one_third_progress_bar.png"))
        case _:
            return QPixmap(str(ASSETS_DIR / "empty_progress_bar.png"))

#destroys the window and restarts it
def restartWindow(self):
    self.close()
    self.deleteLater()

    self.window = MainWindow(self.current_user)
    self.window.show()


def startup():
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        STYLE_SHEET_PATH = Path(__file__).parent / "stylesheet.qss"
        app.setStyleSheet(STYLE_SHEET_PATH.read_text())

        window = MainWindow()
        window.show()

        app.exec()

class MainWindow(QMainWindow):
    def __init__(self, user: str = CURRENT_USER):
        super().__init__()

        self.current_user = user
        self.setWindowTitle("To-Do List")
        self.setFixedSize(QSize(1450, 800))
        self.pageNumber = 1
        with open(DB_DIR / "db_Current Page.txt", "r") as database:
            self.pageNumber = int(database.readline())
        # keeps track of the subtasks completed per task
        self.subtasks = []
        with open(DB_DIR / "db_Subtasks.txt", "r") as database:
            for line in database:
                self.subtasks.append(line.strip("\n").split(","))
        for task in range(len(self.subtasks)):
            for subtask in range(len(self.subtasks[task])):
                self.subtasks[task][subtask] = int(self.subtasks[task][subtask])
        # keeps track of task names
        self.taskText = []
        with open(DB_DIR / "db_Task Names.txt", "r") as database:
            self.taskText = database.readline().split(",")
        # keeps track of subtask names
        self.subtaskText = []
        with open(DB_DIR / "db_Subtask Names.txt", "r") as database:
            for line in database:
                self.subtaskText.append(line.strip("\n").split(","))
        # keeps track of the checkboxes
        self.checkboxes = []
        # keeps track of the progress bars and their progress text
        self.progressBars = []
        # keeps track of the form inputs
        self.formInputs = []

        self.taskToDelete = 0
        self.maxPageAmount = (len(self.subtasks) // 2) + (len(self.subtasks) % 2)
        if(self.maxPageAmount <= 0):
            self.maxPageAmount = 1
        self.pageAmount = QLabel(f"Page {self.pageNumber}/{self.maxPageAmount}")
        self.pageAmount.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        self.pageAmount.setContentsMargins(200,0,0,0)
        self.pageAmount.setObjectName("pageNumber")
        self.deleteConfirmText = QLabel()
        self.deleteConfirmText.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        self.deleteConfirmText.setWordWrap(True)
        self.listTabs = QStackedLayout(self)
    
        
        #says to ignore sizing guidelines
        unrestricted = QSizePolicy()
        unrestricted.setHorizontalPolicy(QSizePolicy.Policy.Ignored)
        unrestricted.setVerticalPolicy(QSizePolicy.Policy.Ignored)

        #page layout
        ladder = QVBoxLayout()
        ladder.setContentsMargins(16, 16, 16, 16)
        ladder.setSpacing(0)
        
        #header
        self.header = AppHeader("To-Do List", user=user, back_to_calendar=True)
        self.header.back_requested.connect(self.exitWindow)
        ladder.addWidget(self.header)
        
        #to-do list
        middleContainer = QWidget()
        containerWidgets = QVBoxLayout()
        
        movementArrows = QHBoxLayout()
        movementArrows.setSpacing(1200)
        if self.pageNumber > 1:
            #previous page button
            backwardButton = QPushButton(
                icon = QIcon(str(ASSETS_DIR / "page_arrow_backward.png")),
                text = "",
                parent = self
            )
            backwardButton.setSizePolicy(unrestricted)
            backwardButton.setFixedSize(101,85)
            backwardButton.setIconSize(QSize(101,101))
            backwardButton.clicked.connect(self.previousPage)
            movementArrows.addWidget(backwardButton)
        else:
            backReplacement = QWidget()
            backReplacement.setFixedSize(101,85)
            movementArrows.addWidget(backReplacement)
        if self.maxPageAmount > self.pageNumber:
            #next page button
            forwardButton = QPushButton(
                icon = QIcon(str(ASSETS_DIR / "page_arrow_forward.png")),
                text = "",
                parent = self
            )
            forwardButton.setSizePolicy(unrestricted)
            forwardButton.setFixedSize(101,85)
            forwardButton.setIconSize(QSize(101,101))
            forwardButton.clicked.connect(self.nextPage)
            movementArrows.addWidget(forwardButton)
        else:
            forwardReplacement = QWidget()
            forwardReplacement.setFixedSize(101,85)
            movementArrows.addWidget(forwardReplacement)
        containerWidgets.addLayout(movementArrows)

        #task lists
        taskLists = QHBoxLayout()
        taskLists.setContentsMargins(200,0,200,0)
        taskLists.setSpacing(300)
        #how many tasks are to be shown on this page
        taskCount = 1
        if self.pageNumber < self.maxPageAmount or len(self.subtasks) % 2 == 0:
            taskCount = 2

        if len(self.subtasks) > 0 and self.pageNumber <= self.maxPageAmount:
            #stops the task from taking the whole screen if it is on it's own
            antiSpread = False
            if taskCount == 1:
                antiSpread = True
            
            for loopCount in range(taskCount):
                firstTask = QWidget()
                firstTask.setMinimumHeight(400)
                firstTask.setObjectName("taskWindow")
                firstContents = QVBoxLayout()
                taskText = self.taskText[self.pageNumber * 2 - 2 + loopCount]
                taskName = QLabel(taskText)
                taskName.setAlignment(
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
                )
                taskName.setObjectName("task")
                taskName.setWordWrap(True)
                firstContents.addWidget(taskName)
                firstSubtasks = QWidget()
                firstSubtasks.setMinimumHeight(300)
                subtaskHolder = QVBoxLayout()
                for subtaskNumber in range(len(self.subtasks[loopCount + (2 * (self.pageNumber - 1))])):
                    currentSubtask = QHBoxLayout()
                    if(len(self.subtasks[loopCount + (2 * (self.pageNumber - 1))]) >= subtaskNumber):
                        currentSubtaskName = QLabel(self.subtaskText[loopCount + (2 * (self.pageNumber - 1))][subtaskNumber])
                    currentSubtaskName.setWordWrap(True)
                    currentSubtaskName.setAlignment(
                        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
                    )
                    currentSubtaskName.setMinimumWidth(325)
                    currentSubtaskName.setObjectName("subtask")
                    currentSubtask.addWidget(currentSubtaskName)
                    self.checkboxes.append(QCheckBox())
                    self.checkboxes[len(self.checkboxes) - 1].stateChanged.connect(self.updateProgress)
                    if(self.subtasks[loopCount + (2 * (self.pageNumber - 1))][subtaskNumber] == 1):
                        self.checkboxes[len(self.checkboxes) - 1].setChecked(True)
                    currentSubtask.addWidget(self.checkboxes[len(self.checkboxes) - 1])
                    subtaskHolder.addLayout(currentSubtask)


                progressBarHolder = QVBoxLayout()
                progressLabel = QLabel(str(completion(self.subtasks[(self.pageNumber * 2) - 2 + loopCount])) + "%")
                progressLabel.setAlignment(
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
                )
                progressLabel.setMaximumHeight(20)
                progressBar = QLabel()
                progressBar.setPixmap(findProgressBar(completion(self.subtasks[(self.pageNumber * 2) - 2 + loopCount])))
                self.progressBars.append([progressLabel, progressBar])
                progressBar.setMaximumHeight(20)
                progressBar.setContentsMargins(25,0,0,0)
                progressBarHolder.addWidget(progressLabel)
                progressBarHolder.addWidget(progressBar)
                subtaskHolder.addLayout(progressBarHolder)
                deletionButton = QPushButton(
                    icon = QIcon(str(ASSETS_DIR / "delete_icon.png")),
                    text = "",
                    parent = self
                )
                deletionButton.setObjectName("delete")
                deletionButton.setSizePolicy(unrestricted)
                deletionButton.setFixedSize(20,20)
                deletionButton.setIconSize(QSize(20,20))
                if(loopCount == 0):
                    deletionButton.clicked.connect(self.deleteFirst)
                elif(loopCount == 1):
                    deletionButton.clicked.connect(self.deleteSecond)   
                subtaskHolder.addWidget(deletionButton)

                firstSubtasks.setLayout(subtaskHolder)
                firstContents.addWidget(firstSubtasks)
                firstContents.setContentsMargins(0,0,0,0)
                firstTask.setLayout(firstContents)
                taskLists.addWidget(firstTask)
            if antiSpread == True:
                taskLists.addWidget(QWidget())
        
        containerWidgets.addLayout(taskLists)

        #bottom row
        bottomRow = QHBoxLayout()
        bottomRow.setContentsMargins(250,0,0,0)
        #add page button
        addListButton = QPushButton(
            icon = QIcon(str(ASSETS_DIR / "add_item.png")),
            text = "",
            parent = self
        )
        addListButton.setSizePolicy(unrestricted)
        addListButton.setFixedSize(101,101)
        addListButton.setIconSize(QSize(101,101))
        addListButton.clicked.connect(self.addTask)
        bottomRow.addWidget(addListButton)
        bottomRow.addWidget(self.pageAmount)
        bottomRow.addWidget(QWidget())
        containerWidgets.addLayout(bottomRow)
        
        middleContainer.setLayout(containerWidgets)

        self.listTabs.addWidget(middleContainer)

        #add new task form
        taskWindow = QWidget()
        taskContainer = QWidget()
        taskContainer.setMaximumWidth(350)
        taskContainer.setObjectName("taskWindow")
        centraliser = QHBoxLayout()
        centraliser.addWidget(QWidget())
        centraliser.addWidget(taskContainer)
        centraliser.addWidget(QWidget())
        formLayout = QVBoxLayout()
        formInput = QLineEdit()
        taskTextHolder = QLabel("Task Name")
        taskTextHolder.setMaximumHeight(50)
        taskTextHolder.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
        )
        formLayout.addWidget(taskTextHolder)
        self.formInputs.append(formInput)
        formLayout.addWidget(formInput)
        subtaskTextHolder = QLabel("Subtask Names (may leave blank)")
        subtaskTextHolder.setMaximumHeight(50)
        subtaskTextHolder.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom
        )
        formLayout.addWidget(subtaskTextHolder)
        for inputBox in range(3):
            newestInputBox = QLineEdit()
            self.formInputs.append(newestInputBox)
            formLayout.addWidget(newestInputBox)
        finishCreation = QPushButton(
            icon = QIcon(str(ASSETS_DIR / "page_arrow_forward.png")),
            text = "",
            parent = self
        )
        finishCreation.setFixedSize(101,85)
        finishCreation.setIconSize(QSize(101,101))
        finishCreation.clicked.connect(self.createTask)
        finishCentraliser = QHBoxLayout()
        finishCentraliser.addWidget(QWidget())
        finishCentraliser.addWidget(finishCreation)
        finishCentraliser.addWidget(QWidget())
        formLayout.addLayout(finishCentraliser)
        taskContainer.setLayout(formLayout)
        taskWindow.setLayout(centraliser)
        self.listTabs.addWidget(taskWindow)

        #deletion confirmation
        deleteConfirmation = QWidget()
        deleteContainer = QWidget()
        deleteContainer.setMaximumWidth(350)
        deleteContainer.setObjectName("taskWindow")
        deleteCentraliser = QHBoxLayout()
        deleteCentraliser.addWidget(QWidget())
        deleteCentraliser.addWidget(deleteContainer)
        deleteCentraliser.addWidget(QWidget())
        deleteConfirmation.setLayout(deleteCentraliser)
        deleteConfirmHolder = QVBoxLayout()
        deleteConfirmText = self.deleteConfirmText
        deleteConfirmHolder.addWidget(deleteConfirmText)
        confirmDelete = QPushButton(
            icon = QIcon(str(ASSETS_DIR / "delete_icon.png")),
            text = "",
            parent = self
        )
        confirmDelete.setObjectName("delete")
        confirmDelete.setSizePolicy(unrestricted)
        confirmDelete.setFixedSize(101,101)
        confirmDelete.setIconSize(QSize(101,101))
        confirmDelete.clicked.connect(self.deleteTask)
        deleteConfirmHolder.addWidget(confirmDelete)
        deleteContainer.setLayout(deleteConfirmHolder)
        
        self.listTabs.addWidget(deleteConfirmation)
        
        ladder.addLayout(self.listTabs)

        #setup
        main = QWidget()
        main.setLayout(ladder)
        self.setCentralWidget(main)
        
    def set_user(self, user):
        self.current_user = user
        self.header.set_user(user)

    def exitWindow(self):
        if(self.listTabs.currentIndex() != 0):
            self.listTabs.setCurrentIndex(0)
        else:
            #needs to connect to the previous window opened. Charles.
            self.close()
    
    def previousPage(self):
        if(self.pageNumber > 1):
            self.pageNumber -= 1
            with open(DB_DIR / "db_Current Page.txt", "w") as database:
                database.write(str(self.pageNumber))
        restartWindow(self)
        
    def nextPage(self):
        if(self.pageNumber < self.maxPageAmount):
            self.pageNumber += 1
            with open(DB_DIR / "db_Current Page.txt", "w") as database:
                database.write(str(self.pageNumber))
        restartWindow(self)

    def deleteFirst(self):
        #confirms if sure
        self.taskToDelete = (self.pageNumber * 2) - 2
        self.deleteConfirmText.setText("Are you sure that you want to delete " + self.taskText[self.taskToDelete] + "?")
        print(self.taskToDelete)
        self.listTabs.setCurrentIndex(2)

    def deleteSecond(self):
        #confirms if sure
        self.taskToDelete = (self.pageNumber * 2) - 1
        self.deleteConfirmText.setText("Are you sure that you want to delete " + self.taskText[self.taskToDelete] + "?")
        self.listTabs.setCurrentIndex(2)
        
    def addTask(self):
        self.listTabs.setCurrentIndex(1)

    def deleteTask(self):
        if(self.pageNumber == self.maxPageAmount and len(self.subtasks) % 2 == 1):
            with open(DB_DIR / "db_Current Page.txt", "w") as database:
                self.pageNumber -= 1
                database.write(str(self.pageNumber))
        with open(DB_DIR / "db_Task Names.txt", "w") as database:
            finalTasks = ""
            foundTask = False
            for task in range(len(self.taskText)):
                if(task != self.taskToDelete):
                    finalTasks += self.taskText[task]
                    if(task != len(self.taskText) - 1 and (task != len(self.taskText) - 2 and foundTask == False)):
                        finalTasks += ","
                else:
                    foundTask = True
            database.write(finalTasks)
        with open(DB_DIR / "db_Subtasks.txt", "w") as database:
            finalTasks = ""
            for task in range(len(self.subtasks)):
                if(task != self.taskToDelete):
                    for subtask in range(len(self.subtasks[task])):
                        finalTasks += str(self.subtasks[task][subtask])
                        if(subtask != len(self.subtasks[task]) - 1):
                            finalTasks += ","
                        
                    finalTasks += "\n"
            database.write(finalTasks)
        with open(DB_DIR / "db_Subtask Names.txt", "w") as database:
            finalTasks = ""
            for task in range(len(self.subtaskText)):
                if(task != self.taskToDelete):
                    for subtask in range(len(self.subtaskText[task])):
                        finalTasks += self.subtaskText[task][subtask]
                        if(subtask != len(self.subtaskText[task]) - 1):
                            finalTasks += ","
                    finalTasks += "\n"
            database.write(finalTasks)
        restartWindow(self)
        
    def createTask(self):
        #if the task doesn't have a name, does nothing
        if self.formInputs[0].text() != "":
            newSubtaskNames = []
            success = False
            skipFirst = True
            for subtaskInput in self.formInputs:
                #if no subtasks are filled in, does nothing
                if(skipFirst == True):
                    skipFirst = False
                elif(subtaskInput.text() != ""):
                    success = True
                    newSubtaskNames.append(subtaskInput.text())
            if success == True:
                with open(DB_DIR / "db_Subtask Names.txt", "a") as database:
                    subtaskEdit = ""
                    for newSubtasks in range(len(newSubtaskNames)):
                        subtaskEdit += newSubtaskNames[newSubtasks]
                        if(newSubtasks != len(newSubtaskNames) - 1):
                            subtaskEdit += ","
                    subtaskEdit += "\n"
                    database.write(subtaskEdit)
                with open(DB_DIR / "db_Subtasks.txt", "a") as database:
                    subtaskEdit = ""
                    for newSubtasks in range(len(newSubtaskNames)):
                        subtaskEdit += "0"
                        if(newSubtasks != len(newSubtaskNames) - 1):
                            subtaskEdit += ","
                    subtaskEdit += "\n"
                    database.write(subtaskEdit)
                with open(DB_DIR / "db_Task Names.txt", "a") as database:
                    database.write("," + self.formInputs[0].text())
                restartWindow(self)
           
    def updateProgress(self):
        count = 1
        firstTask = self.subtasks[(self.pageNumber * 2) - 2]
        secondTask = []
        if(self.pageNumber != self.maxPageAmount or len(self.subtasks) % 2 == 0):
            secondTask = self.subtasks[self.pageNumber * 2 - 1]
        for checkbox in self.checkboxes:
            checkboxValue = 0
            if checkbox.checkState() == Qt.CheckState.Checked:
                checkboxValue = 1
            #updates the correct list that the checkbox currently checked is in
            if len(firstTask) >= count:
                firstTask[count - 1] = checkboxValue
            else:
                secondTask[count - len(firstTask) - 1] = checkboxValue
            count += 1
        open(DB_DIR / "db_Subtasks.txt", "w").close()
        with open(DB_DIR / "db_Subtasks.txt", "a") as database:
            for subtaskValues in self.subtasks:
                databaseAppend = ""
                first = True
                for subtaskValue in subtaskValues:
                    if(first == False):
                        databaseAppend += ","
                    first = False
                    databaseAppend += str(subtaskValue)
                databaseAppend += "\n"
                database.write(databaseAppend)
        for progressBar in range(len(self.progressBars)):
            self.progressBars[progressBar][0].setText(str(completion(self.subtasks[(self.pageNumber * 2) - 2 + progressBar])) + "%")
            self.progressBars[progressBar][1].setPixmap(findProgressBar(completion(self.subtasks[(self.pageNumber * 2) - 2 + progressBar])))

startup()
