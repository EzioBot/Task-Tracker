import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QCalendarWidget, QLineEdit, QListWidget, QListWidgetItem, QLabel, QInputDialog,
    QFrame
)
from PyQt5.QtCore import QTimer, QTime, Qt, QDate
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtGui import QIcon 

class TaskTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nodepad")
        self.setWindowIcon(QIcon("logo.png"))
        self.setGeometry(100, 100, 600, 700)
        self.init_ui()
        self.load_tasks()

    def init_ui(self):
        self.setStyleSheet("background-color: #fdf5d1;")

        layout = QVBoxLayout()
        font = QFont("Courier", 12)

        # Clock
        self.clock_label = QLabel()
        self.clock_label.setFont(QFont("Courier", 16, QFont.Bold))
        self.clock_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.clock_label)

        # Clock update timer
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
        self.update_clock()

        # Compact Calendar
        calendar_frame = QFrame()
        calendar_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        calendar_frame.setStyleSheet("""
            QFrame {
                background-color: #fffbe6;
                border: 2px solid #d4c9a8;
                border-radius: 5px;
            }
            QFrame:hover {
                background-color: #f0e6cc;
                cursor: pointer;
            }
        """)
        calendar_layout = QVBoxLayout(calendar_frame)
        
        # Date display label
        self.date_label = QLabel()
        self.date_label.setFont(QFont("Courier", 14, QFont.Bold))
        self.date_label.setAlignment(Qt.AlignCenter)
        self.update_date_display()
        calendar_layout.addWidget(self.date_label)
        
        # Calendar widget (initially hidden)
        self.calendar = QCalendarWidget()
        self.calendar.setVisible(False)
        calendar_layout.addWidget(self.calendar)
        
        # Make the frame clickable
        calendar_frame.mousePressEvent = self.toggle_calendar
        layout.addWidget(calendar_frame)

        # Task Input
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setFont(font)
        self.task_input.setPlaceholderText("Enter a task...")
        input_layout.addWidget(self.task_input)

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_task)
        input_layout.addWidget(add_button)

        layout.addLayout(input_layout)

        # Task List
        self.task_list = QListWidget()
        self.task_list.setFont(font)
        self.task_list.setStyleSheet("background-color: #fffbe6;")
        layout.addWidget(self.task_list)

        # Edit/Delete buttons
        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit")
        delete_btn = QPushButton("Delete")
        edit_btn.clicked.connect(self.edit_task)
        delete_btn.clicked.connect(self.delete_task)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def update_clock(self):
        self.clock_label.setText(QTime.currentTime().toString("hh:mm:ss AP"))

    def add_task(self):
        task_text = self.task_input.text().strip()
        if task_text:
            self.task_list.addItem(task_text)
            self.task_input.clear()
            self.save_tasks()

    def edit_task(self):
        current_item = self.task_list.currentItem()
        if current_item:
            new_text, ok = QInputDialog.getText(self, "Edit Task", "Update task:", text=current_item.text())
            if ok and new_text.strip():
                current_item.setText(new_text.strip())
                self.save_tasks()

    def delete_task(self):
        row = self.task_list.currentRow()
        if row >= 0:
            self.task_list.takeItem(row)
            self.save_tasks()

    def save_tasks(self):
        tasks = [self.task_list.item(i).text() for i in range(self.task_list.count())]
        with open("tasks.json", "w") as f:
            json.dump(tasks, f)

    def load_tasks(self):
        try:
            with open("tasks.json", "r") as f:
                tasks = json.load(f)
                for task in tasks:
                    self.task_list.addItem(task)
        except FileNotFoundError:
            pass

    def update_date_display(self):
        current_date = QDate.currentDate()
        self.date_label.setText(current_date.toString("MMMM d, yyyy"))

    def toggle_calendar(self, event):
        self.calendar.setVisible(not self.calendar.isVisible())
        if self.calendar.isVisible():
            self.calendar.setSelectedDate(QDate.currentDate())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tracker = TaskTracker()
    tracker.show()
    sys.exit(app.exec_())
