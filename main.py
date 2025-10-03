import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QCalendarWidget, QLineEdit, QListWidget, QLabel, QInputDialog,
    QFrame, QTimeEdit, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import QTimer, QTime, Qt, QDate, QPoint, QRect
from PyQt5.QtGui import QFont, QIcon


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

        # --- Date label (clickable) ---
        self.date_label = QLabel()
        self.date_label.setFont(QFont("Courier", 14, QFont.Bold))
        self.date_label.setAlignment(Qt.AlignCenter)
        self.update_date_display()
        self.date_label.setStyleSheet("padding: 8px; background: #fffbe6; border: 2px solid #d4c9a8; border-radius: 5px;")
        self.date_label.mousePressEvent = self.toggle_calendar
        main_layout.addWidget(self.date_label)

        # --- Calendar (hidden by default) ---
        self.calendar = QCalendarWidget()
        self.calendar.setVisible(False)
        self.calendar.setMaximumHeight(200)
        main_layout.addWidget(self.calendar)

        # --- Input ---
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setFont(QFont("Courier", 12))
        self.task_input.setPlaceholderText("Enter a task...")
        input_layout.addWidget(self.task_input)

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_task)
        input_layout.addWidget(add_button)

        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_task)
        input_layout.addWidget(edit_button)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_task)
        input_layout.addWidget(delete_button)

        main_layout.addLayout(input_layout)

        # --- Task list ---
        self.task_list = QListWidget()
        font = QFont("Courier", 12)
        self.task_list.setFont(font)
        self.task_list.setStyleSheet("""
            QListWidget {
                background-color: #fffbe6;
                border: none;
            }
            QListWidget::item {
                background: #f9eec0;
                border: 1.5px solid #d4c9a8;
                border-radius: 10px;
                margin: 8px 4px;
                padding: 10px 12px;
                color: #333;
            }
            QListWidget::item:selected {
                background: #ffe066;
                border: 2px solid #f1c40f;
                color: #222;
            }
        """)
        main_layout.addWidget(self.task_list)

        self.setLayout(main_layout)

    def update_clock(self):
        # FIX: Use correct time format
        self.clock_label.setText(QTime.currentTime().toString("hh:mm:ss AP"))

    def add_task(self):
        task_text = self.task_input.text().strip()
        if not task_text:
            return

        # --- Ask for due date ---
        due_date, ok = QInputDialog.getText(self, "Due Date", "Enter due date (YYYY-MM-DD) or leave blank for today:", text=QDate.currentDate().toString("yyyy-MM-dd"))
        if not ok:
            return
        if due_date.strip():
            try:
                due_qdate = QDate.fromString(due_date.strip(), "yyyy-MM-dd")
                if not due_qdate.isValid():
                    raise ValueError
            except Exception:
                due_qdate = QDate.currentDate()
        else:
            due_qdate = QDate.currentDate()

        # --- Ask for due time ---
        due_time, ok = QInputDialog.getText(self, "Due Time", "Enter due time (HH:mm) or leave blank for 23:59:", text="23:59")
        if not ok:
            return
        if due_time.strip():
            try:
                due_qtime = QTime.fromString(due_time.strip(), "HH:mm")
                if not due_qtime.isValid():
                    raise ValueError
            except Exception:
                due_qtime = QTime(23, 59)
        else:
            due_qtime = QTime(23, 59)

        now = QDate.currentDate().toString("yyyy-MM-dd")
        time = QTime.currentTime().toString("hh:mm:ss AP")
        due_date_str = due_qdate.toString("yyyy-MM-dd")
        due_time_str = due_qtime.toString("HH:mm")
        display_text = f"{task_text}   [Created: {now} {time}]   [Due: {due_date_str} {due_time_str}]"
        self.task_list.addItem(display_text)
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
        tasks = []
        for i in range(self.task_list.count()):
            item_text = self.task_list.item(i).text()
            # Try to split into text, created, and due
            try:
                desc, created_part, due_part = item_text.split("   [Created: ", 1)[0], "", ""
                if "[Created:" in item_text and "[Due:" in item_text:
                    parts = item_text.split("   [Created: ")
                    desc = parts[0].strip()
                    rest = parts[1]
                    created, due = rest.split("]   [Due: ")
                    created = created.strip()
                    due = due.rstrip("]").strip()
                    tasks.append({
                        "description": desc,
                        "created": created,
                        "due": due
                    })
                else:
                    tasks.append({"description": item_text})
            except Exception:
                tasks.append({"description": item_text})
        with open("tasks.json", "w") as f:
            json.dump(tasks, f)

    def load_tasks(self):
        try:
            with open("tasks.json", "r") as f:
                tasks = json.load(f)
                for task in tasks:
                    if isinstance(task, dict):
                        desc = task.get("description", "")
                        created = task.get("created", "")
                        due = task.get("due", "")
                        if created and due:
                            display_text = f"{desc}   [Created: {created}]   [Due: {due}]"
                        else:
                            display_text = desc
                        self.task_list.addItem(display_text)
                    elif isinstance(task, str):
                        self.task_list.addItem(task)
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

    # --- Mouse events for dragging and resizing ---

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
