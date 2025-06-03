import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QCalendarWidget, QLineEdit, QListWidget, QLabel, QInputDialog,
    QFrame
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

        # Frameless window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)

        # Variables for drag/resize
        self._margin = 8  # resize area margin
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

        # --- Custom title bar ---
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

        # Minimize button
        btn_min = QPushButton("–")
        btn_min.setFixedSize(25, 25)
        btn_min.setStyleSheet(
            "QPushButton {border:none; border-radius:12px; background-color:#f1c40f; color:white; font-weight:bold;}"
            "QPushButton:hover {background-color:black;}"
        )
        btn_min.clicked.connect(self.showMinimized)
        title_layout.addWidget(btn_min)

        # Maximize/Restore button
        btn_max = QPushButton("□")
        btn_max.setFixedSize(25, 25)
        btn_max.setStyleSheet(
            "QPushButton {border:none; border-radius:12px; background-color:#2ecc71; color:white; font-weight:bold;}"
            "QPushButton:hover {background-color:black;}"
        )
        btn_max.clicked.connect(self.toggle_max_restore)
        title_layout.addWidget(btn_max)

        # Close button
        btn_close = QPushButton("×")
        btn_close.setFixedSize(25, 25)
        btn_close.setStyleSheet(
            "QPushButton {border:none; border-radius:12px; background-color:#e74c3c; color:white; font-weight:bold;}"
            "QPushButton:hover {background-color:black;}"
        )
        btn_close.clicked.connect(self.close)
        title_layout.addWidget(btn_close)

        main_layout.addWidget(title_bar)
        self._title_bar = title_bar

        # --- Clock ---
        font = QFont("Courier", 12)
        self.clock_label = QLabel()
        self.clock_label.setFont(QFont("Courier", 16, QFont.Bold))
        self.clock_label.setAlignment(Qt.AlignRight)
        main_layout.addWidget(self.clock_label)

        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
        self.update_clock()

        # --- Calendar frame ---
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

        # --- Task input ---
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setFont(font)
        self.task_input.setPlaceholderText("Enter a task...")
        input_layout.addWidget(self.task_input)

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_task)
        input_layout.addWidget(add_button)
        main_layout.addLayout(input_layout)

        # --- Task list ---
        self.task_list = QListWidget()
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

        # --- Edit/Delete buttons ---
        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit")
        delete_btn = QPushButton("Delete")
        edit_btn.clicked.connect(self.edit_task)
        delete_btn.clicked.connect(self.delete_task)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

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
        self.task_list.clear()
        try:
            with open("tasks.json", "r") as f:
                tasks = json.load(f)
                for task in tasks:
                    if isinstance(task, str):
                        self.task_list.addItem(task)
                    elif isinstance(task, dict):
                        # fallback: show description if present
                        self.task_list.addItem(task.get("description", ""))
        except FileNotFoundError:
            pass

    def update_date_display(self):
        current_date = QDate.currentDate()
        self.date_label.setText(current_date.toString("MMMM d, yyyy"))

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

            # Check edges for resize direction
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
                # Dragging only if click is on title bar
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
                new_left = rect.left() + diff.x()
                if new_left < rect.right() - self.minimumWidth():
                    rect.setLeft(new_left)
            if "right" in self._resize_direction:
                new_right = rect.right() + diff.x()
                if new_right > rect.left() + self.minimumWidth():
                    rect.setRight(new_right)
            if "top" in self._resize_direction:
                new_top = rect.top() + diff.y()
                if new_top < rect.bottom() - self.minimumHeight():
                    rect.setTop(new_top)
            if "bottom" in self._resize_direction:
                new_bottom = rect.bottom() + diff.y()
                if new_bottom > rect.top() + self.minimumHeight():
                    rect.setBottom(new_bottom)

            self.setGeometry(rect)
            self._old_pos = global_pos
            return

        if self._dragging:
            self.move(event.globalPos() - self._drag_pos)
            return

        # Change cursor shape for resize edges
        margin = self._margin
        left = pos.x() <= margin
        right = pos.x() >= geo.width() - margin
        top = pos.y() <= margin
        bottom = pos.y() >= geo.height() - margin

        # If mouse is on the title bar (drag area), show drag cursor
        if self._title_bar.geometry().contains(pos):
            self.setCursor(Qt.SizeAllCursor)
        else:
            if top and left:
                self.setCursor(Qt.SizeFDiagCursor)
            elif top and right:
                self.setCursor(Qt.SizeBDiagCursor)
            elif bottom and left:
                self.setCursor(Qt.SizeBDiagCursor)
            elif bottom and right:
                self.setCursor(Qt.SizeFDiagCursor)
            elif left:
                self.setCursor(Qt.SizeHorCursor)
            elif right:
                self.setCursor(Qt.SizeHorCursor)
            elif top:
                self.setCursor(Qt.SizeVerCursor)
            elif bottom:
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

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
