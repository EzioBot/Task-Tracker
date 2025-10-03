import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QCalendarWidget, QLineEdit, QListWidget, QLabel, QInputDialog,
    QFrame, QListWidgetItem
)
from PyQt5.QtCore import QTimer, QTime, Qt, QDate
from PyQt5.QtGui import QFont, QIcon, QFontMetrics, QBrush, QColor


class TaskWidget(QWidget):
    def __init__(self, text, done, parent, item):
        super().__init__()
        self.parent = parent
        self.item = item
        self.text = text
        self.done = done

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(text)
        self.label.setFont(QFont("Courier", 12))
        self.update_style()
        layout.addWidget(self.label)

        btn_done = QPushButton("✔")
        btn_done.setFixedSize(30, 25)
        btn_done.clicked.connect(self.toggle_done)
        layout.addWidget(btn_done)

        btn_edit = QPushButton("✎")
        btn_edit.setFixedSize(30, 25)
        btn_edit.clicked.connect(self.edit_task)
        layout.addWidget(btn_edit)

        btn_delete = QPushButton("🗑")
        btn_delete.setFixedSize(30, 25)
        btn_delete.clicked.connect(self.delete_task)
        layout.addWidget(btn_delete)

        self.setLayout(layout)

    def update_style(self):
        font = self.label.font()
        font.setStrikeOut(self.done)
        self.label.setFont(font)
        color = "#888888" if self.done else "#333333"
        self.label.setStyleSheet(f"color: {color};")

    def toggle_done(self):
        self.done = not self.done
        self.update_style()
        self.parent.save_tasks()

    def edit_task(self):
        new_text, ok = QInputDialog.getText(self, "Edit Task", "Update task:", text=self.text)
        if ok and new_text.strip():
            self.text = new_text.strip()
            self.label.setText(self.text)
            self.parent.save_tasks()

    def delete_task(self):
        self.parent.task_list.takeItem(self.parent.task_list.row(self.item))
        self.parent.save_tasks()


class TaskTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nodepad")
        self.setWindowIcon(QIcon("logo.png"))
        self.setGeometry(100, 100, 600, 700)
        self.setMinimumSize(400, 500)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint)

        self._margin = 8
        self._drag_pos = None
        self._resizing = False
        self._resize_direction = None
        self._dragging = False

        self.init_ui()
        self.load_tasks()

    def init_ui(self):
        self.setStyleSheet("background-color: #fdf5d1;")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Title bar ---
        title_bar = QFrame()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background-color: #e3d7a3;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)

        logo = QLabel()
        logo.setPixmap(QIcon("logo.png").pixmap(24, 24))
        logo.setFixedSize(26, 26)
        title_layout.addWidget(logo)

        title = QLabel("Nodepad")
        title.setFont(QFont("Courier", 14, QFont.Bold))
        title.setStyleSheet("color: #333; padding-left: 5px;")
        title_layout.addWidget(title)
        title_layout.addStretch()

        btn_min = QPushButton("–")
        btn_min.setFixedSize(25, 25)
        btn_min.setStyleSheet(
            "QPushButton {background-color:#f1c40f; color:white; border-radius:12px;}"
            "QPushButton:hover {background-color:black;}"
        )
        btn_min.clicked.connect(self.showMinimized)
        title_layout.addWidget(btn_min)

        btn_max = QPushButton("□")
        btn_max.setFixedSize(25, 25)
        btn_max.setStyleSheet(
            "QPushButton {background-color:#2ecc71; color:white; border-radius:12px;}"
            "QPushButton:hover {background-color:black;}"
        )
        btn_max.clicked.connect(self.toggle_max_restore)
        title_layout.addWidget(btn_max)

        btn_close = QPushButton("×")
        btn_close.setFixedSize(25, 25)
        btn_close.setStyleSheet(
            "QPushButton {background-color:#e74c3c; color:white; border-radius:12px;}"
            "QPushButton:hover {background-color:black;}"
        )
        btn_close.clicked.connect(self.close)
        title_layout.addWidget(btn_close)

        main_layout.addWidget(title_bar)
        self._title_bar = title_bar

        # --- Clock ---
        self.clock_label = QLabel()
        self.clock_label.setFont(QFont("Courier", 16, QFont.Bold))
        self.clock_label.setAlignment(Qt.AlignRight)
        main_layout.addWidget(self.clock_label)

        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
        self.update_clock()

        # --- Calendar ---
        calendar_frame = QFrame()
        calendar_frame.setStyleSheet("""
            QFrame {
                background-color: #fffbe6;
                border: 2px solid #d4c9a8;
                border-radius: 5px;
            }
        """)
        calendar_layout = QVBoxLayout(calendar_frame)

        self.date_label = QLabel()
        self.date_label.setFont(QFont("Courier", 14, QFont.Bold))
        self.date_label.setAlignment(Qt.AlignCenter)
        self.update_date_display()
        calendar_layout.addWidget(self.date_label)

        self.calendar = QCalendarWidget()
        self.calendar.setVisible(False)
        calendar_layout.addWidget(self.calendar)
        calendar_frame.mousePressEvent = self.toggle_calendar
        main_layout.addWidget(calendar_frame)

        # --- Input ---
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setFont(QFont("Courier", 12))
        self.task_input.setPlaceholderText("Enter a task...")
        input_layout.addWidget(self.task_input)

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_task)
        input_layout.addWidget(add_button)
        main_layout.addLayout(input_layout)

        # --- Task list ---
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("QListWidget { background-color: #fffbe6; border: none; }")
        main_layout.addWidget(self.task_list)

        self.setLayout(main_layout)

    def update_clock(self):
        self.clock_label.setText(QTime.currentTime().toString("hh:mm:ss AP"))

    def add_task(self):
        task_text = self.task_input.text().strip()
        if task_text:
            self.create_task_item(task_text, False)
            self.task_input.clear()
            self.save_tasks()

    def create_task_item(self, text, done):
        item = QListWidgetItem()
        widget = TaskWidget(text, done, self, item)
        item.setSizeHint(widget.sizeHint())
        self.task_list.addItem(item)
        self.task_list.setItemWidget(item, widget)

    # def save_tasks(self):
    #     tasks = []
    #     for i in range(self.task_list.count()):
    #         item = self.task_list.item(i)
    #         widget = self.task_list.itemWidget(item)
    #         tasks.append({"text": widget.text, "done": widget.done})
    #     with open("tasks.json", "w") as f:
    #         json.dump(tasks, f)

    def save_tasks(self):
        data = []
        for task_item in self.tasks:
            data.append({
                "text": task_item.text(),
                "done": task_item.is_done()
            })
        with open("tasks.json", "w") as file:
            json.dump(data, file)


    # def load_tasks(self):
    #     self.task_list.clear()
    #     try:
    #         with open("tasks.json", "r") as f:
    #             tasks = json.load(f)
    #             for task in tasks:
    #                 self.create_task_item(task.get("text", ""), task.get("done", False))
    #     except FileNotFoundError:
    #         pass

        
    def load_tasks(self):
        try:
            with open("tasks.json", "r") as file:
                task_data = json.load(file)
                for task in task_data:
                    if isinstance(task, dict):
                        self.create_task_item(task.get("text", ""), task.get("done", False))
                    elif isinstance(task, str):  # fallback if older format
                        self.create_task_item(task, False)
        except FileNotFoundError:
            pass  


    def update_date_display(self):
        self.date_label.setText(QDate.currentDate().toString("MMMM d, yyyy"))

    def toggle_calendar(self, event):
        self.calendar.setVisible(not self.calendar.isVisible())
        if self.calendar.isVisible():
            self.calendar.setSelectedDate(QDate.currentDate())

    def toggle_max_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # --- Mouse events ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            geo = self.rect()
            margin = self._margin

            left = pos.x() <= margin
            right = pos.x() >= geo.width() - margin
            top = pos.y() <= margin
            bottom = pos.y() >= geo.height() - margin

            self._resize_direction = None
            if top and left:
                self._resize_direction = "top_left"
            elif top and right:
                self._resize_direction = "top_right"
            elif bottom and left:
                self._resize_direction = "bottom_left"
            elif bottom and right:
                self._resize_direction = "bottom_right"
            elif left:
                self._resize_direction = "left"
            elif right:
                self._resize_direction = "right"
            elif top:
                self._resize_direction = "top"
            elif bottom:
                self._resize_direction = "bottom"

            if self._resize_direction:
                self._resizing = True
            else:
                if self._title_bar.geometry().contains(pos):
                    self._dragging = True
                    self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

            self._old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        geo = self.rect()
        global_pos = event.globalPos()

        if self._resizing:
            diff = global_pos - self._old_pos
            rect = self.geometry()

            if "left" in self._resize_direction:
                rect.setLeft(rect.left() + diff.x())
            if "right" in self._resize_direction:
                rect.setRight(rect.right() + diff.x())
            if "top" in self._resize_direction:
                rect.setTop(rect.top() + diff.y())
            if "bottom" in self._resize_direction:
                rect.setBottom(rect.bottom() + diff.y())

            self.setGeometry(rect)
            self._old_pos = global_pos
            return

        if self._dragging:
            self.move(global_pos - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._resizing = False
        self._dragging = False
        self._resize_direction = None
        self.setCursor(Qt.ArrowCursor)

    def leaveEvent(self, event):
        if not self._resizing and not self._dragging:
            self.setCursor(Qt.ArrowCursor)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tracker = TaskTracker()
    tracker.show()
    sys.exit(app.exec_())
