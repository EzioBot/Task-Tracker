import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QCalendarWidget, QLineEdit, QListWidget, QLabel, QInputDialog,
    QFrame, QTimeEdit, QDialog, QDialogButtonBox, QListWidgetItem,
    QListView, QSizePolicy, QRadioButton, QButtonGroup, QSpinBox, QFormLayout,
    QGroupBox
)
from PyQt5.QtCore import QTimer, QTime, Qt, QDate, QPoint, QRect, QDateTime
from PyQt5.QtGui import QFont, QIcon


class TaskItemWidget(QFrame):
    def __init__(self, parent_tracker, description: str, created: str, due: str, priority: str):
        super().__init__()
        self._tracker = parent_tracker
        self.description = description
        self.created = created
        self.due = due
        self.priority = priority or "low"

        bg = self._background_for_priority(self.priority)
        self.setStyleSheet(
            f"""
            QFrame {{
                background: {bg};
                border-radius: 10px;
            }}
            QLabel {{ color: #333; }}
            QPushButton {{
                margin-left: 8px;
                background-color: #2d3436;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: #000000;
            }}
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)

        self.desc_label = QLabel(self.description)
        # Make task title more readable and bold
        title_font = QFont("Courier", 13)
        title_font.setBold(True)
        self.desc_label.setFont(title_font)

        priority_label = self.priority.capitalize()
        # Removed created date/time from display; show priority and due only
        self.meta_label = QLabel((f"[{priority_label}]   " if priority_label else "") + (f"[Due: {self.due}]" if self.due else ""))
        meta_font = QFont("Courier", 10)
        self.meta_label.setFont(meta_font)

        layout.addWidget(self.desc_label)
        layout.addStretch()
        layout.addWidget(self.meta_label)

        self.edit_btn = QPushButton("Edit")
        btn_font = QFont("Courier", 11)
        btn_font.setBold(True)
        self.edit_btn.setFont(btn_font)
        self.edit_btn.clicked.connect(self.edit_task)
        layout.addWidget(self.edit_btn)

        self.setMinimumHeight(48)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def _background_for_priority(self, priority: str) -> str:
        p = (priority or "").lower()
        if p == "urgent":
            return "#f8a3a0"  # vibrant soft red
        if p == "high":
            return "#ffe066"  # vibrant soft yellow
        # low
        return "#aecdff"      # vibrant soft blue

    def edit_task(self):
        new_text, ok = QInputDialog.getText(self, "Edit Task", "Update task:", text=self.description)
        if ok and new_text.strip():
            self.description = new_text.strip()
            self.desc_label.setText(self.description)
            # Persist changes
            self._tracker.save_tasks()
            # Ensure the list recalculates the item's size
            self._tracker.rehint_for_widget(self)


class DueDateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Due Date")
        layout = QVBoxLayout(self)
        self.calendar = QCalendarWidget()
        self.calendar.setSelectedDate(QDate.currentDate())
        layout.addWidget(self.calendar)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selectedDate(self) -> QDate:
        return self.calendar.selectedDate()


class DueTimeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Due Time or Timer")
        main_layout = QVBoxLayout(self)

        # Choice: exact time or timer
        self.radio_exact = QRadioButton("Pick exact time")
        self.radio_timer = QRadioButton("Use timer (duration)")
        self.radio_exact.setChecked(True)
        main_layout.addWidget(self.radio_exact)
        main_layout.addWidget(self.radio_timer)

        # Exact time controls
        exact_layout = QHBoxLayout()
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTime(QTime.currentTime())
        exact_layout.addWidget(QLabel("Time:"))
        exact_layout.addWidget(self.time_edit)
        main_layout.addLayout(exact_layout)

        # Timer controls
        form = QFormLayout()
        self.spin_hours = QSpinBox()
        self.spin_hours.setRange(0, 168)
        self.spin_hours.setValue(0)
        self.spin_minutes = QSpinBox()
        self.spin_minutes.setRange(0, 59)
        self.spin_minutes.setValue(30)
        form.addRow("Hours:", self.spin_hours)
        form.addRow("Minutes:", self.spin_minutes)
        main_layout.addLayout(form)

        # Enable/disable sections based on radio
        def update_enabled():
            exact_enabled = self.radio_exact.isChecked()
            self.time_edit.setEnabled(exact_enabled)
            self.spin_hours.setEnabled(not exact_enabled)
            self.spin_minutes.setEnabled(not exact_enabled)
        self.radio_exact.toggled.connect(update_enabled)
        update_enabled()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

    def resultDateTime(self, base_date: QDate) -> QDateTime:
        if self.radio_exact.isChecked():
            return QDateTime(base_date, self.time_edit.time())
        # Timer mode: compute now + duration
        now_dt = QDateTime.currentDateTime()
        minutes_total = self.spin_hours.value() * 60 + self.spin_minutes.value()
        return now_dt.addSecs(minutes_total * 60)


class PriorityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Priority")
        layout = QVBoxLayout(self)

        group_box = QGroupBox("Priority")
        g_layout = QVBoxLayout(group_box)
        self.radio_urgent = QRadioButton("Urgent")
        self.radio_high = QRadioButton("High")
        self.radio_low = QRadioButton("Low")
        self.radio_low.setChecked(True)
        g_layout.addWidget(self.radio_urgent)
        g_layout.addWidget(self.radio_high)
        g_layout.addWidget(self.radio_low)
        layout.addWidget(group_box)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selectedPriority(self) -> str:
        if self.radio_urgent.isChecked():
            return "urgent"
        if self.radio_high.isChecked():
            return "high"
        return "low"


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

        # Removed global Edit button; per-task Edit buttons are provided in the list

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_task)
        input_layout.addWidget(delete_button)

        main_layout.addLayout(input_layout)

        # --- Task list ---
        self.task_list = QListWidget()
        self.task_list.setSpacing(8)
        font = QFont("Courier", 12)
        self.task_list.setFont(font)
        # Keep background only; card styles come from TaskItemWidget
        self.task_list.setStyleSheet(
            """
            QListWidget { background-color: #fffbe6; border: none; }
            """
        )
        # Enforce vertical, non-wrapping list behavior
        self.task_list.setViewMode(QListView.ListMode)
        self.task_list.setMovement(QListView.Static)
        self.task_list.setWrapping(False)
        self.task_list.setFlow(QListView.TopToBottom)
        self.task_list.setResizeMode(QListView.Adjust)
        self.task_list.setUniformItemSizes(False)
        self.task_list.setSortingEnabled(False)
        main_layout.addWidget(self.task_list)

        self.setLayout(main_layout)

    def update_clock(self):
        # FIX: Use correct time format
        self.clock_label.setText(QTime.currentTime().toString("hh:mm:ss AP"))

    def add_task(self):
        task_text = self.task_input.text().strip()
        if not task_text:
            return

        # --- Ask for due date with calendar ---
        date_dialog = DueDateDialog(self)
        if date_dialog.exec_() != QDialog.Accepted:
            return
        selected_date = date_dialog.selectedDate()

        # --- Ask for due time or timer ---
        time_dialog = DueTimeDialog(self)
        if time_dialog.exec_() != QDialog.Accepted:
            return
        result_dt = time_dialog.resultDateTime(selected_date)
        due_qdate = result_dt.date()
        due_qtime = result_dt.time()

        # --- Ask for priority ---
        prio_dialog = PriorityDialog(self)
        if prio_dialog.exec_() != QDialog.Accepted:
            return
        priority = prio_dialog.selectedPriority()

        due_date_str = due_qdate.toString("yyyy-MM-dd")
        due_time_str = due_qtime.toString("HH:mm")
        due = f"{due_date_str} {due_time_str}"

        item = QListWidgetItem()
        widget = TaskItemWidget(self, task_text, "", due, priority)
        item.setSizeHint(widget.sizeHint())
        self.task_list.addItem(item)
        self.task_list.setItemWidget(item, widget)
        self.task_input.clear()
        self.save_tasks()

    def edit_task(self):
        # Deprecated: global edit removed in favor of per-task Edit buttons
        pass

    def delete_task(self):
        row = self.task_list.currentRow()
        if row >= 0:
            self.task_list.takeItem(row)
            self.save_tasks()

    def save_tasks(self):
        tasks = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            widget = self.task_list.itemWidget(item)
            if isinstance(widget, TaskItemWidget):
                tasks.append({
                    "description": widget.description,
                    "due": widget.due,
                    "priority": widget.priority
                })
            else:
                # Fallback for plain text items (legacy)
                item_text = item.text()
                try:
                    desc = item_text
                    created = ""
                    due = ""
                    priority = "low"
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
                        "due": due,
                        "priority": priority
                    })
                except Exception:
                    tasks.append({"description": item_text, "priority": "low"})
        with open("tasks.json", "w") as f:
            json.dump(tasks, f)

    def load_tasks(self):
        try:
            with open("tasks.json", "r") as f:
                tasks = json.load(f)
                for task in tasks:
                    if isinstance(task, dict):
                        desc = task.get("description", "")
                        due = task.get("due", "")
                        priority = task.get("priority", "low")
                    elif isinstance(task, str):
                        desc = task
                        created = ""
                        due = ""
                        priority = "low"
                    else:
                        continue

                    item = QListWidgetItem()
                    widget = TaskItemWidget(self, desc, "", due, priority)
                    item.setSizeHint(widget.sizeHint())
                    self.task_list.addItem(item)
                    self.task_list.setItemWidget(item, widget)
        except FileNotFoundError:
            pass

    def rehint_for_widget(self, widget: QWidget):
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            if self.task_list.itemWidget(item) is widget:
                item.setSizeHint(widget.sizeHint())
                break


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
