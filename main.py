import json
import sys
import ctypes
from pathlib import Path

from PyQt5.QtCore import QDate, QDateTime, QTime, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QGraphicsDropShadowEffect,
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QTimeEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


APP_DIR = Path(__file__).resolve().parent
TASKS_FILE = APP_DIR / "tasks.json"
WINDOWS_APP_ID = "Sagar.TaskTracker.Desktop.1"

PRIORITY_STYLES = {
    "urgent": {"label": "Urgent", "bg": "#fee2e2", "fg": "#991b1b", "rank": 0},
    "high": {"label": "High", "bg": "#fef3c7", "fg": "#92400e", "rank": 1},
    "low": {"label": "Low", "bg": "#dcfce7", "fg": "#166534", "rank": 2},
}

THEMES = {
    "light": {
        "name": "light",
        "text": "#111827",
        "text_soft": "#374151",
        "muted": "#64748b",
        "shell_bg": "#f8fafc",
        "shell_border": "#d5dde8",
        "surface": "#ffffff",
        "surface_alt": "#f1f5f9",
        "surface_hover": "#e2e8f0",
        "input_bg": "#ffffff",
        "input_border": "#cbd5e1",
        "primary": "#0f766e",
        "primary_hover": "#0d9488",
        "primary_soft": "#f0fdfa",
        "primary_soft_border": "#99f6e4",
        "primary_contrast": "#ffffff",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "secondary": "#e2e8f0",
        "secondary_hover": "#cbd5e1",
        "danger": "#ef4444",
        "danger_hover": "#dc2626",
        "danger_soft": "#fee2e2",
        "danger_soft_hover": "#fecaca",
        "danger_text": "#991b1b",
        "edit_soft": "#eef2ff",
        "edit_hover": "#dbeafe",
        "edit_text": "#1d4ed8",
        "check_border": "#9ca3af",
        "check_bg": "#ffffff",
        "check_checked": "#22c55e",
        "shadow": QColor(15, 23, 42, 48),
        "dialog_shadow": QColor(15, 23, 42, 44),
        "priority": {
            "urgent": {"bg": "#fee2e2", "fg": "#991b1b"},
            "high": {"bg": "#fef3c7", "fg": "#92400e"},
            "low": {"bg": "#dcfce7", "fg": "#166534"},
        },
    },
    "dark": {
        "name": "dark",
        "text": "#e5e7eb",
        "text_soft": "#cbd5e1",
        "muted": "#94a3b8",
        "shell_bg": "#0f172a",
        "shell_border": "#263244",
        "surface": "#172033",
        "surface_alt": "#1e293b",
        "surface_hover": "#334155",
        "input_bg": "#111827",
        "input_border": "#334155",
        "primary": "#2dd4bf",
        "primary_hover": "#14b8a6",
        "primary_soft": "#123c3a",
        "primary_soft_border": "#0f766e",
        "primary_contrast": "#042f2e",
        "accent": "#60a5fa",
        "accent_hover": "#3b82f6",
        "secondary": "#273449",
        "secondary_hover": "#334155",
        "danger": "#f87171",
        "danger_hover": "#ef4444",
        "danger_soft": "#431b22",
        "danger_soft_hover": "#5b222b",
        "danger_text": "#fecaca",
        "edit_soft": "#1e2f55",
        "edit_hover": "#25406d",
        "edit_text": "#93c5fd",
        "check_border": "#64748b",
        "check_bg": "#0f172a",
        "check_checked": "#2dd4bf",
        "shadow": QColor(0, 0, 0, 92),
        "dialog_shadow": QColor(0, 0, 0, 86),
        "priority": {
            "urgent": {"bg": "#4c1d24", "fg": "#fecaca"},
            "high": {"bg": "#453217", "fg": "#fde68a"},
            "low": {"bg": "#123c2d", "fg": "#bbf7d0"},
        },
    },
}


def configure_windows_taskbar_icon():
    if sys.platform != "win32":
        return

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(WINDOWS_APP_ID)
    except AttributeError:
        pass


def create_brand_pixmap(size=96):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    padding = max(4, size // 14)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor("#0f766e"))
    painter.drawRoundedRect(padding, padding, size - padding * 2, size - padding * 2, size // 5, size // 5)

    painter.setBrush(QColor("#f59e0b"))
    painter.drawEllipse(size - padding * 5, padding * 3, padding * 3, padding * 3)

    pen = QPen(QColor("#ffffff"), max(4, size // 14), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)
    painter.drawLine(int(size * 0.28), int(size * 0.53), int(size * 0.42), int(size * 0.67))
    painter.drawLine(int(size * 0.42), int(size * 0.67), int(size * 0.73), int(size * 0.35))

    line_pen = QPen(QColor("#ccfbf1"), max(2, size // 28), Qt.SolidLine, Qt.RoundCap)
    painter.setPen(line_pen)
    painter.drawLine(int(size * 0.28), int(size * 0.78), int(size * 0.72), int(size * 0.78))
    painter.end()
    return pixmap


def create_brand_icon():
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 96, 128, 256):
        icon.addPixmap(create_brand_pixmap(size))
    return icon


def create_line_icon(name, color="#334155", size=24):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    pen = QPen(QColor(color), max(2, size // 12), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)

    center = size // 2
    if name == "add":
        painter.drawLine(center, int(size * 0.25), center, int(size * 0.75))
        painter.drawLine(int(size * 0.25), center, int(size * 0.75), center)
    elif name == "search":
        painter.drawEllipse(int(size * 0.2), int(size * 0.2), int(size * 0.42), int(size * 0.42))
        painter.drawLine(int(size * 0.58), int(size * 0.58), int(size * 0.78), int(size * 0.78))
    elif name == "minimize":
        painter.drawLine(int(size * 0.25), int(size * 0.62), int(size * 0.75), int(size * 0.62))
    elif name == "close":
        painter.drawLine(int(size * 0.28), int(size * 0.28), int(size * 0.72), int(size * 0.72))
        painter.drawLine(int(size * 0.72), int(size * 0.28), int(size * 0.28), int(size * 0.72))
    elif name == "clear":
        painter.drawLine(int(size * 0.3), int(size * 0.3), int(size * 0.7), int(size * 0.3))
        painter.drawLine(int(size * 0.37), int(size * 0.42), int(size * 0.63), int(size * 0.42))
        painter.drawLine(int(size * 0.42), int(size * 0.55), int(size * 0.58), int(size * 0.55))
    elif name == "edit":
        painter.drawLine(int(size * 0.28), int(size * 0.72), int(size * 0.68), int(size * 0.32))
        painter.drawLine(int(size * 0.62), int(size * 0.26), int(size * 0.74), int(size * 0.38))
        painter.drawLine(int(size * 0.24), int(size * 0.76), int(size * 0.36), int(size * 0.72))
    elif name == "delete":
        painter.drawLine(int(size * 0.31), int(size * 0.36), int(size * 0.69), int(size * 0.36))
        painter.drawLine(int(size * 0.38), int(size * 0.36), int(size * 0.42), int(size * 0.78))
        painter.drawLine(int(size * 0.62), int(size * 0.36), int(size * 0.58), int(size * 0.78))
        painter.drawLine(int(size * 0.42), int(size * 0.24), int(size * 0.58), int(size * 0.24))
    elif name == "moon":
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(color))
        painter.drawEllipse(int(size * 0.28), int(size * 0.18), int(size * 0.48), int(size * 0.64))
        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.drawEllipse(int(size * 0.43), int(size * 0.14), int(size * 0.46), int(size * 0.64))
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
    elif name == "sun":
        painter.drawEllipse(int(size * 0.35), int(size * 0.35), int(size * 0.3), int(size * 0.3))
        for x1, y1, x2, y2 in (
            (0.50, 0.15, 0.50, 0.25),
            (0.50, 0.75, 0.50, 0.85),
            (0.15, 0.50, 0.25, 0.50),
            (0.75, 0.50, 0.85, 0.50),
            (0.25, 0.25, 0.32, 0.32),
            (0.68, 0.68, 0.75, 0.75),
            (0.75, 0.25, 0.68, 0.32),
            (0.32, 0.68, 0.25, 0.75),
        ):
            painter.drawLine(int(size * x1), int(size * y1), int(size * x2), int(size * y2))

    painter.end()
    return QIcon(pixmap)


class TaskDialog(QDialog):
    def __init__(self, parent=None, task=None, prefill=""):
        super().__init__(parent)
        self.task = task or {}
        self._drag_position = None
        self.setWindowTitle("Edit Task" if task else "New Task")
        if parent and hasattr(parent, "app_icon"):
            self.setWindowIcon(parent.app_icon)
        self.theme_name = getattr(parent, "theme_name", "light")
        self.theme = THEMES[self.theme_name]
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMinimumWidth(340)
        self.setObjectName("TaskDialog")
        self.apply_theme()

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(10, 10, 10, 10)
        self.root_layout.setSpacing(0)

        self.dialog_shell = QFrame()
        self.dialog_shell.setObjectName("TaskDialogShell")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(26)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(15, 23, 42, 44))
        self.dialog_shell.setGraphicsEffect(shadow)
        self.root_layout.addWidget(self.dialog_shell)

        layout = QVBoxLayout(self.dialog_shell)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.dialog_header = QFrame()
        self.dialog_header.setObjectName("DialogHeader")
        header_layout = QHBoxLayout(self.dialog_header)
        header_layout.setContentsMargins(10, 8, 8, 8)
        header_layout.setSpacing(8)

        icon_label = QLabel()
        icon = parent.app_icon if parent and hasattr(parent, "app_icon") else create_brand_icon()
        icon_label.setPixmap(icon.pixmap(32, 32))
        icon_label.setFixedSize(36, 36)
        icon_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(icon_label)

        title_stack = QVBoxLayout()
        title_stack.setSpacing(0)
        title_label = QLabel("Edit Task" if task else "New Task")
        title_label.setObjectName("DialogTitle")
        subtitle_label = QLabel("Set details, date, and time")
        subtitle_label.setObjectName("DialogSubtitle")
        title_stack.addWidget(title_label)
        title_stack.addWidget(subtitle_label)
        header_layout.addLayout(title_stack, 1)

        self.close_button = QToolButton()
        self.close_button.setIcon(create_line_icon("close", self.theme["text_soft"]))
        self.close_button.setIconSize(QPixmap(20, 20).size())
        self.close_button.setFixedSize(34, 34)
        self.close_button.setToolTip("Close")
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.clicked.connect(self.reject)
        header_layout.addWidget(self.close_button)
        layout.addWidget(self.dialog_header)

        self.error_label = QLabel("")
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Task name")
        self.title_input.setText(self.task.get("description", prefill))
        task_label = QLabel("Task")
        task_label.setObjectName("FieldLabel")
        layout.addWidget(task_label)
        layout.addWidget(self.title_input)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notes")
        self.notes_input.setFixedHeight(76)
        self.notes_input.setText(self.task.get("notes", ""))
        notes_label = QLabel("Notes")
        notes_label.setObjectName("FieldLabel")
        layout.addWidget(notes_label)
        layout.addWidget(self.notes_input)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "High", "Urgent"])
        current_priority = self.task.get("priority", "low").lower()
        if current_priority in PRIORITY_STYLES:
            self.priority_combo.setCurrentText(PRIORITY_STYLES[current_priority]["label"])
        priority_label = QLabel("Priority")
        priority_label.setObjectName("FieldLabel")
        layout.addWidget(priority_label)
        layout.addWidget(self.priority_combo)

        self.due_mode = QComboBox()
        self.due_mode.addItems(["Exact date and time", "Timer from now", "No due date"])
        due_label = QLabel("Due")
        due_label.setObjectName("FieldLabel")
        layout.addWidget(due_label)
        layout.addWidget(self.due_mode)

        self.date_edit = QDateEdit()
        self.date_edit.setObjectName("DatePicker")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("ddd, MMM d, yyyy")
        self.style_calendar()

        self.time_edit = QTimeEdit()
        self.time_edit.setObjectName("TimePicker")
        self.time_edit.setDisplayFormat("hh:mm AP")
        self.time_edit.setAccelerated(True)

        due_dt = TaskTracker.parse_due(self.task.get("due", ""))
        if due_dt.isValid():
            self.date_edit.setDate(due_dt.date())
            self.time_edit.setTime(due_dt.time())
        else:
            self.date_edit.setDate(QDate.currentDate())
            self.time_edit.setTime(QTime.currentTime().addSecs(3600))
            if task:
                self.due_mode.setCurrentText("No due date")

        exact_layout = QHBoxLayout()
        exact_layout.setSpacing(8)
        exact_layout.addWidget(self.date_edit, 1)
        exact_layout.addWidget(self.time_edit, 1)
        layout.addLayout(exact_layout)

        timer_layout = QHBoxLayout()
        timer_layout.setSpacing(8)
        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(0, 168)
        self.hours_spin.setSuffix(" h")
        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 59)
        self.minutes_spin.setSuffix(" min")
        self.minutes_spin.setValue(30)
        timer_layout.addWidget(self.hours_spin)
        timer_layout.addWidget(self.minutes_spin)
        layout.addLayout(timer_layout)

        self.completed_check = QCheckBox("Completed")
        self.completed_check.setChecked(bool(self.task.get("completed", False)))
        layout.addWidget(self.completed_check)

        self.due_mode.currentIndexChanged.connect(self.update_due_controls)
        self.update_due_controls()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Save")
        buttons.button(QDialogButtonBox.Ok).setObjectName("PrimaryDialogButton")
        buttons.button(QDialogButtonBox.Cancel).setObjectName("CancelButton")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.apply_theme()
        if parent:
            dialog_width = min(max(parent.width() - 36, 340), 520)
            self.resize(dialog_width, self.sizeHint().height())

    def apply_theme(self):
        t = self.theme
        self.setStyleSheet(
            f"""
            QDialog#TaskDialog {{
                background: transparent;
                color: {t["text"]};
            }}
            QFrame#TaskDialogShell {{
                background: {t["shell_bg"]};
                border: 1px solid {t["shell_border"]};
                border-radius: 18px;
            }}
            QFrame#DialogHeader {{
                background: {t["surface"]};
                border: 1px solid {t["input_border"]};
                border-radius: 14px;
            }}
            QLabel {{
                color: {t["text_soft"]};
                font-weight: 600;
            }}
            QLabel#DialogTitle {{
                color: {t["text"]};
                font-size: 16px;
                font-weight: 900;
            }}
            QLabel#DialogSubtitle {{
                color: {t["muted"]};
                font-size: 11px;
                font-weight: 700;
            }}
            QLabel#FieldLabel {{
                color: {t["muted"]};
                font-size: 12px;
                font-weight: 800;
            }}
            QLabel#ErrorLabel {{
                color: {t["danger_text"]};
                font-weight: 800;
            }}
            QLineEdit, QTextEdit, QDateEdit, QTimeEdit, QSpinBox, QComboBox {{
                background: {t["input_bg"]};
                border: 1px solid {t["input_border"]};
                border-radius: 8px;
                padding: 9px;
                color: {t["text"]};
                selection-background-color: {t["primary"]};
                selection-color: {t["primary_contrast"]};
            }}
            QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QTimeEdit:focus, QSpinBox:focus, QComboBox:focus {{
                border-color: {t["primary"]};
            }}
            QDateEdit#DatePicker, QTimeEdit#TimePicker {{
                background: {t["primary_soft"]};
                border-color: {t["primary_soft_border"]};
                font-weight: 800;
            }}
            QDateEdit::drop-down, QTimeEdit::up-button, QTimeEdit::down-button,
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 22px;
                border: none;
                background: {t["surface_alt"]};
                border-radius: 6px;
                margin: 3px;
            }}
            QPushButton#PrimaryDialogButton {{
                background: {t["primary"]};
                color: {t["primary_contrast"]};
                border: none;
                border-radius: 9px;
                padding: 11px 16px;
                font-weight: 900;
            }}
            QPushButton#PrimaryDialogButton:hover {{
                background: {t["primary_hover"]};
            }}
            QPushButton#CancelButton {{
                background: {t["secondary"]};
                color: {t["text_soft"]};
                border: none;
                border-radius: 9px;
                padding: 11px 16px;
                font-weight: 800;
            }}
            QPushButton#CancelButton:hover {{
                background: {t["secondary_hover"]};
            }}
            QToolButton {{
                background: {t["surface_alt"]};
                border: none;
                border-radius: 10px;
                padding: 7px;
            }}
            QToolButton:hover {{
                background: {t["surface_hover"]};
            }}
            """
        )
        if hasattr(self, "dialog_shell") and self.dialog_shell.graphicsEffect():
            self.dialog_shell.graphicsEffect().setColor(t["dialog_shadow"])
        if hasattr(self, "close_button"):
            self.close_button.setIcon(create_line_icon("close", t["text_soft"]))
        if hasattr(self, "date_edit"):
            self.style_calendar()

    def style_calendar(self):
        t = self.theme
        calendar = self.date_edit.calendarWidget()
        calendar.setGridVisible(False)
        calendar.setFirstDayOfWeek(Qt.Monday)
        calendar.setVerticalHeaderFormat(calendar.NoVerticalHeader)
        calendar.setStyleSheet(
            f"""
            QCalendarWidget {{
                background: {t["surface"]};
                border: 1px solid {t["input_border"]};
                border-radius: 12px;
            }}
            QCalendarWidget QWidget {{
                background: {t["surface"]};
                color: {t["text"]};
                alternate-background-color: {t["surface_alt"]};
            }}
            QCalendarWidget QToolButton {{
                background: {t["surface_alt"]};
                color: {t["text"]};
                border: none;
                border-radius: 8px;
                margin: 3px;
                padding: 6px;
                font-weight: 800;
            }}
            QCalendarWidget QToolButton:hover {{
                background: {t["primary_soft"]};
                color: {t["primary"]};
            }}
            QCalendarWidget QMenu {{
                background: {t["surface"]};
                border: 1px solid {t["input_border"]};
                color: {t["text"]};
            }}
            QCalendarWidget QSpinBox {{
                background: {t["input_bg"]};
                border: 1px solid {t["input_border"]};
                border-radius: 8px;
                padding: 4px;
                color: {t["text"]};
            }}
            QCalendarWidget QAbstractItemView {{
                background: {t["surface"]};
                color: {t["text"]};
                selection-background-color: {t["primary"]};
                selection-color: {t["primary_contrast"]};
                border: none;
                outline: 0;
                font-weight: 700;
            }}
            """
        )

    def update_due_controls(self):
        mode = self.due_mode.currentText()
        exact_enabled = mode == "Exact date and time"
        timer_enabled = mode == "Timer from now"
        self.date_edit.setEnabled(exact_enabled)
        self.time_edit.setEnabled(exact_enabled)
        self.hours_spin.setEnabled(timer_enabled)
        self.minutes_spin.setEnabled(timer_enabled)

    def accept(self):
        self.error_label.setVisible(False)
        if not self.title_input.text().strip():
            self.error_label.setText("Add a task name first.")
            self.error_label.setVisible(True)
            self.title_input.setFocus()
            return

        if self.due_mode.currentText() == "Timer from now":
            minutes = self.hours_spin.value() * 60 + self.minutes_spin.value()
            if minutes <= 0:
                self.error_label.setText("Timer must be at least 1 minute.")
                self.error_label.setVisible(True)
                return

        super().accept()

    def task_data(self):
        due = ""
        mode = self.due_mode.currentText()
        if mode == "Exact date and time":
            due = QDateTime(self.date_edit.date(), self.time_edit.time()).toString("yyyy-MM-dd HH:mm")
        elif mode == "Timer from now":
            minutes = self.hours_spin.value() * 60 + self.minutes_spin.value()
            due = QDateTime.currentDateTime().addSecs(minutes * 60).toString("yyyy-MM-dd HH:mm")

        return {
            "description": self.title_input.text().strip(),
            "notes": self.notes_input.toPlainText().strip(),
            "due": due,
            "priority": self.priority_combo.currentText().lower(),
            "completed": self.completed_check.isChecked(),
        }

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_header_drag_area(event.pos()):
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_position is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_position)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_position = None
        super().mouseReleaseEvent(event)

    def is_header_drag_area(self, position):
        if isinstance(self.childAt(position), QToolButton):
            return False
        return self.dialog_header.rect().contains(self.dialog_header.mapFrom(self, position))


class TaskItemWidget(QFrame):
    def __init__(self, tracker, task):
        super().__init__()
        self.tracker = tracker
        self.task = task
        self.task_id = task["id"]
        theme = tracker.theme
        self.setObjectName("TaskCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(
            f"""
            QFrame#TaskCard {{
                background: {theme["surface"]};
                border: 1px solid {theme["input_border"]};
                border-radius: 8px;
            }}
            QLabel {{
                background: transparent;
            }}
            QToolButton {{
                background: {theme["edit_soft"]};
                color: {theme["edit_text"]};
                border: none;
                border-radius: 8px;
                padding: 6px;
            }}
            QToolButton:hover {{
                background: {theme["edit_hover"]};
            }}
            QToolButton#DangerButton {{
                background: {theme["danger_soft"]};
                color: {theme["danger_text"]};
            }}
            QToolButton#DangerButton:hover {{
                background: {theme["danger_soft_hover"]};
            }}
            """
        )

        card_layout = QVBoxLayout(self)
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self.done_check = QCheckBox()
        self.done_check.setChecked(bool(task.get("completed", False)))
        self.done_check.toggled.connect(
            lambda checked: self.tracker.set_task_completed(self.task_id, checked)
        )
        top_row.addWidget(self.done_check, 0, Qt.AlignTop)

        text_stack = QVBoxLayout()
        text_stack.setSpacing(4)

        title = QLabel(task.get("description", "Untitled task"))
        title.setWordWrap(True)
        title_font = QFont("Segoe UI", 12, QFont.Bold)
        title_font.setStrikeOut(bool(task.get("completed", False)))
        title.setFont(title_font)
        title.setStyleSheet(
            f"color: {theme['muted']};" if task.get("completed", False) else f"color: {theme['text']};"
        )
        text_stack.addWidget(title)

        notes = task.get("notes", "").strip()
        if notes:
            notes_label = QLabel(notes)
            notes_label.setWordWrap(True)
            notes_label.setStyleSheet(f"color: {theme['muted']}; font-size: 12px;")
            text_stack.addWidget(notes_label)

        top_row.addLayout(text_stack, 1)

        actions = QVBoxLayout()
        actions.setSpacing(6)
        edit_button = QToolButton()
        edit_button.setIcon(create_line_icon("edit", theme["edit_text"]))
        edit_button.setIconSize(QPixmap(20, 20).size())
        edit_button.setToolTip("Edit task")
        edit_button.setFixedSize(34, 34)
        edit_button.setCursor(Qt.PointingHandCursor)
        edit_button.clicked.connect(lambda: self.tracker.edit_task(self.task_id))
        delete_button = QToolButton()
        delete_button.setObjectName("DangerButton")
        delete_button.setIcon(create_line_icon("delete", theme["danger_text"]))
        delete_button.setIconSize(QPixmap(20, 20).size())
        delete_button.setToolTip("Delete task")
        delete_button.setFixedSize(34, 34)
        delete_button.setCursor(Qt.PointingHandCursor)
        delete_button.clicked.connect(lambda: self.tracker.delete_task(self.task_id))
        actions.addWidget(edit_button)
        actions.addWidget(delete_button)
        top_row.addLayout(actions)

        card_layout.addLayout(top_row)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)

        priority = task.get("priority", "low").lower()
        priority_style = PRIORITY_STYLES.get(priority, PRIORITY_STYLES["low"])
        themed_priority = theme["priority"].get(priority, theme["priority"]["low"])
        priority_label = QLabel(priority_style["label"])
        priority_label.setStyleSheet(
            f"""
            color: {themed_priority["fg"]};
            background: {themed_priority["bg"]};
            border-radius: 8px;
            padding: 4px 8px;
            font-weight: 800;
            """
        )
        meta_row.addWidget(priority_label, 0)

        due_label = QLabel(self.tracker.format_due(task))
        due_label.setStyleSheet(self.tracker.due_label_style(task))
        meta_row.addWidget(due_label, 1)
        card_layout.addLayout(meta_row)


class TaskTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.tasks = []
        self.current_filter = "all"
        self._drag_position = None
        self.theme_name = "light"
        self.theme = THEMES[self.theme_name]
        self.icon_buttons = []
        self.app_icon = create_brand_icon()

        self.setWindowTitle("Task Tracker")
        self.setWindowIcon(self.app_icon)
        self.setWindowFlags(
            Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(410, 760)
        self.setMinimumSize(340, 560)
        self.setObjectName("Root")

        self.init_ui()
        self.load_tasks()
        self.refresh_tasks()

    def init_ui(self):
        self.setStyleSheet(
            """
            QWidget#Root {
                background: transparent;
                color: #111827;
            }
            QFrame#AppShell {
                background: #f8fafc;
                border: 1px solid #d5dde8;
                border-radius: 18px;
            }
            QFrame#AppToolbar {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
            }
            QLineEdit {
                background: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 10px 12px;
                color: #111827;
                selection-background-color: #2563eb;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
            QPushButton {
                background: #111827;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #1f2937;
            }
            QPushButton#SecondaryButton {
                background: #e5e7eb;
                color: #111827;
            }
            QPushButton#SecondaryButton:hover {
                background: #d1d5db;
            }
            QPushButton#FilterButton {
                background: #ffffff;
                color: #4b5563;
                border: 1px solid #d1d5db;
                padding: 8px 9px;
            }
            QPushButton#FilterButton:checked {
                background: #2563eb;
                color: #ffffff;
                border-color: #2563eb;
            }
            QToolButton {
                border: none;
                border-radius: 10px;
                padding: 7px;
            }
            QToolButton#ToolbarButton {
                background: #f1f5f9;
            }
            QToolButton#ToolbarButton:hover {
                background: #e2e8f0;
            }
            QToolButton#InlineAddButton {
                background: #0f766e;
            }
            QToolButton#InlineAddButton:hover {
                background: #0d9488;
            }
            QToolButton#WindowButton {
                background: #f8fafc;
            }
            QToolButton#WindowButton:hover {
                background: #e2e8f0;
            }
            QToolButton#CloseWindowButton {
                background: #ef4444;
            }
            QToolButton#CloseWindowButton:hover {
                background: #dc2626;
            }
            QFrame#StatsBar {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
            QListWidget {
                background: transparent;
                border: none;
                outline: 0;
            }
            QListWidget::item {
                border: none;
                padding: 0;
                margin: 0;
            }
            QCheckBox {
                color: #374151;
                font-weight: 700;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border-radius: 11px;
                border: 2px solid #9ca3af;
                background: #ffffff;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #22c55e;
                background: #22c55e;
            }
            """
        )

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(10, 10, 10, 10)
        self.root_layout.setSpacing(0)

        self.app_shell = QFrame()
        self.app_shell.setObjectName("AppShell")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(15, 23, 42, 48))
        self.app_shell.setGraphicsEffect(shadow)
        self.root_layout.addWidget(self.app_shell)

        self.main_layout = QVBoxLayout(self.app_shell)
        self.main_layout.setContentsMargins(14, 14, 14, 12)
        self.main_layout.setSpacing(12)

        self.toolbar = QFrame()
        self.toolbar.setObjectName("AppToolbar")
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(10, 8, 8, 8)
        toolbar_layout.setSpacing(8)

        self.brand_icon_label = QLabel()
        self.brand_icon_label.setPixmap(self.app_icon.pixmap(34, 34))
        self.brand_icon_label.setFixedSize(38, 38)
        self.brand_icon_label.setAlignment(Qt.AlignCenter)
        toolbar_layout.addWidget(self.brand_icon_label)

        title_stack = QVBoxLayout()
        title_stack.setSpacing(0)
        self.title_label = QLabel("Task Tracker")
        self.title_label.setObjectName("AppTitle")
        self.title_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.subtitle_label = QLabel("Mobile daily planner")
        self.subtitle_label.setObjectName("AppSubtitle")
        title_stack.addWidget(self.title_label)
        title_stack.addWidget(self.subtitle_label)
        toolbar_layout.addLayout(title_stack, 1)

        search_button = self.create_icon_button("search", "Search tasks", self.focus_search)
        toolbar_layout.addWidget(search_button)

        add_top_button = self.create_icon_button("add", "Add task", self.add_task)
        toolbar_layout.addWidget(add_top_button)

        self.theme_button = self.create_icon_button("moon", "Switch to dark mode", self.toggle_theme)
        toolbar_layout.addWidget(self.theme_button)

        minimize_button = self.create_icon_button(
            "minimize", "Minimize", self.showMinimized, "WindowButton"
        )
        toolbar_layout.addWidget(minimize_button)

        close_button = self.create_icon_button(
            "close", "Close", self.close, "CloseWindowButton", "#ffffff"
        )
        toolbar_layout.addWidget(close_button)

        self.main_layout.addWidget(self.toolbar)

        self.clock_label = QLabel()
        self.clock_label.setObjectName("ClockLabel")
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.clock_label)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()

        stats_bar = QFrame()
        stats_bar.setObjectName("StatsBar")
        stats_layout = QHBoxLayout(stats_bar)
        stats_layout.setContentsMargins(12, 10, 12, 10)
        stats_layout.setSpacing(8)

        self.total_stat = self.create_stat(stats_layout, "All")
        self.active_stat = self.create_stat(stats_layout, "Active")
        self.done_stat = self.create_stat(stats_layout, "Done")
        self.late_stat = self.create_stat(stats_layout, "Late")
        self.main_layout.addWidget(stats_bar)

        add_row = QHBoxLayout()
        add_row.setSpacing(8)
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("What needs to get done?")
        self.task_input.returnPressed.connect(self.add_task)
        add_row.addWidget(self.task_input, 1)

        add_button = self.create_icon_button(
            "add", "Add task", self.add_task, "InlineAddButton", "#ffffff", 40
        )
        add_row.addWidget(add_button)
        self.main_layout.addLayout(add_row)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tasks")
        self.search_input.textChanged.connect(self.refresh_tasks)
        self.main_layout.addWidget(self.search_input)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(6)
        self.filter_group = QButtonGroup(self)
        self.filter_group.setExclusive(True)
        self.filter_buttons = {}
        for key, label in [
            ("all", "All"),
            ("active", "Active"),
            ("today", "Today"),
            ("overdue", "Late"),
            ("completed", "Done"),
        ]:
            button = QPushButton(label)
            button.setObjectName("FilterButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked, selected=key: self.set_filter(selected))
            self.filter_group.addButton(button)
            self.filter_buttons[key] = button
            filter_row.addWidget(button)
        self.filter_buttons["all"].setChecked(True)
        self.main_layout.addLayout(filter_row)

        self.task_list = QListWidget()
        self.task_list.setSpacing(8)
        self.task_list.setViewMode(QListView.ListMode)
        self.task_list.setMovement(QListView.Static)
        self.task_list.setResizeMode(QListView.Adjust)
        self.task_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.task_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.task_list.setUniformItemSizes(False)
        self.task_list.setSortingEnabled(False)
        self.main_layout.addWidget(self.task_list, 1)

        self.empty_label = QLabel()
        self.empty_label.setObjectName("EmptyState")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setWordWrap(True)
        self.main_layout.addWidget(self.empty_label, 1)

        clear_button = QPushButton("Clear Done")
        clear_button.setObjectName("SecondaryButton")
        clear_button.clicked.connect(self.clear_completed)
        self.main_layout.addWidget(clear_button)
        self.apply_theme()
        self.apply_responsive_layout()

    def create_icon_button(self, icon_name, tooltip, handler, object_name="ToolbarButton", color=None, size=36):
        button = QToolButton()
        icon_color = color or self.theme["text_soft"]
        button.setObjectName(object_name)
        button.setIcon(create_line_icon(icon_name, icon_color))
        button.setIconSize(QPixmap(22, 22).size())
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedSize(size, size)
        button.clicked.connect(handler)
        button.setProperty("icon_name", icon_name)
        button.setProperty("fixed_icon_color", color or "")
        button.setProperty("base_size", size)
        self.icon_buttons.append(button)
        return button

    def apply_theme(self):
        t = self.theme
        self.setStyleSheet(
            f"""
            QWidget#Root {{
                background: transparent;
                color: {t["text"]};
            }}
            QFrame#AppShell {{
                background: {t["shell_bg"]};
                border: 1px solid {t["shell_border"]};
                border-radius: 18px;
            }}
            QFrame#AppToolbar {{
                background: {t["surface"]};
                border: 1px solid {t["input_border"]};
                border-radius: 14px;
            }}
            QLabel#AppTitle {{
                color: {t["text"]};
            }}
            QLabel#AppSubtitle, QLabel#ClockLabel {{
                color: {t["muted"]};
                font-weight: 800;
            }}
            QLabel#StatNumber {{
                color: {t["text"]};
                font-size: 20px;
                font-weight: 900;
            }}
            QLabel#StatCaption {{
                color: {t["muted"]};
                font-size: 11px;
                font-weight: 700;
            }}
            QLabel#EmptyState {{
                background: {t["surface"]};
                border: 1px solid {t["input_border"]};
                border-radius: 8px;
                color: {t["muted"]};
                padding: 24px;
                font-weight: 700;
            }}
            QLineEdit {{
                background: {t["input_bg"]};
                border: 1px solid {t["input_border"]};
                border-radius: 8px;
                padding: 10px 12px;
                color: {t["text"]};
                selection-background-color: {t["primary"]};
                selection-color: {t["primary_contrast"]};
            }}
            QLineEdit:focus {{
                border-color: {t["primary"]};
            }}
            QPushButton {{
                background: {t["surface_alt"]};
                color: {t["text"]};
                border: none;
                border-radius: 8px;
                padding: 10px 12px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                background: {t["surface_hover"]};
            }}
            QPushButton#SecondaryButton {{
                background: {t["secondary"]};
                color: {t["text_soft"]};
            }}
            QPushButton#SecondaryButton:hover {{
                background: {t["secondary_hover"]};
            }}
            QPushButton#FilterButton {{
                background: {t["surface"]};
                color: {t["muted"]};
                border: 1px solid {t["input_border"]};
                padding: 8px 9px;
            }}
            QPushButton#FilterButton:checked {{
                background: {t["accent"]};
                color: #ffffff;
                border-color: {t["accent"]};
            }}
            QPushButton#FilterButton:hover {{
                background: {t["surface_hover"]};
                color: {t["text"]};
            }}
            QPushButton#FilterButton:checked:hover {{
                background: {t["accent_hover"]};
                color: #ffffff;
            }}
            QToolButton {{
                border: none;
                border-radius: 10px;
                padding: 7px;
            }}
            QToolButton#ToolbarButton {{
                background: {t["surface_alt"]};
            }}
            QToolButton#ToolbarButton:hover {{
                background: {t["surface_hover"]};
            }}
            QToolButton#InlineAddButton {{
                background: {t["primary"]};
            }}
            QToolButton#InlineAddButton:hover {{
                background: {t["primary_hover"]};
            }}
            QToolButton#WindowButton {{
                background: {t["surface_alt"]};
            }}
            QToolButton#WindowButton:hover {{
                background: {t["surface_hover"]};
            }}
            QToolButton#CloseWindowButton {{
                background: {t["danger"]};
            }}
            QToolButton#CloseWindowButton:hover {{
                background: {t["danger_hover"]};
            }}
            QFrame#StatsBar {{
                background: {t["surface"]};
                border: 1px solid {t["input_border"]};
                border-radius: 8px;
            }}
            QListWidget {{
                background: transparent;
                border: none;
                outline: 0;
            }}
            QListWidget::item {{
                border: none;
                padding: 0;
                margin: 0;
            }}
            QCheckBox {{
                color: {t["text_soft"]};
                font-weight: 700;
            }}
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border-radius: 11px;
                border: 2px solid {t["check_border"]};
                background: {t["check_bg"]};
            }}
            QCheckBox::indicator:checked {{
                border: 2px solid {t["check_checked"]};
                background: {t["check_checked"]};
            }}
            """
        )
        if hasattr(self, "app_shell") and self.app_shell.graphicsEffect():
            self.app_shell.graphicsEffect().setColor(t["shadow"])
        self.update_theme_button()
        self.update_icon_buttons()

    def update_icon_buttons(self):
        for button in self.icon_buttons:
            icon_name = button.property("icon_name")
            fixed_color = button.property("fixed_icon_color")
            icon_color = fixed_color or self.theme["text_soft"]
            button.setIcon(create_line_icon(icon_name, icon_color))

    def update_theme_button(self):
        if not hasattr(self, "theme_button"):
            return
        is_dark = self.theme_name == "dark"
        self.theme_button.setProperty("icon_name", "sun" if is_dark else "moon")
        self.theme_button.setToolTip("Switch to light mode" if is_dark else "Switch to dark mode")

    def toggle_theme(self):
        self.theme_name = "dark" if self.theme_name == "light" else "light"
        self.theme = THEMES[self.theme_name]
        self.apply_theme()
        self.refresh_tasks()

    def apply_responsive_layout(self):
        if not hasattr(self, "toolbar"):
            return
        compact = self.width() < 390
        outer_margin = 8 if compact else 10
        inner_margin = 10 if compact else 14
        button_delta = -2 if compact else 0
        icon_size = 20 if compact else 22

        self.root_layout.setContentsMargins(outer_margin, outer_margin, outer_margin, outer_margin)
        self.main_layout.setContentsMargins(inner_margin, inner_margin, inner_margin, 12)
        self.main_layout.setSpacing(10 if compact else 12)
        self.toolbar.layout().setSpacing(6 if compact else 8)

        title_font = QFont("Segoe UI", 12 if compact else 13, QFont.Bold)
        self.title_label.setFont(title_font)
        self.subtitle_label.setVisible(self.width() >= 370)
        self.clock_label.setFont(QFont("Segoe UI", 9 if compact else 10, QFont.Bold))

        brand_box = 34 if compact else 38
        brand_pixmap = 30 if compact else 34
        self.brand_icon_label.setFixedSize(brand_box, brand_box)
        self.brand_icon_label.setPixmap(self.app_icon.pixmap(brand_pixmap, brand_pixmap))

        for button in self.icon_buttons:
            base_size = int(button.property("base_size") or 36)
            size = max(32, base_size + button_delta)
            button.setFixedSize(size, size)
            button.setIconSize(QPixmap(icon_size, icon_size).size())

        self.task_list.setSpacing(6 if compact else 8)

    def focus_search(self):
        self.search_input.setFocus()
        self.search_input.selectAll()

    def create_stat(self, parent_layout, label):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        number = QLabel("0")
        number.setObjectName("StatNumber")
        number.setAlignment(Qt.AlignCenter)

        caption = QLabel(label)
        caption.setObjectName("StatCaption")
        caption.setAlignment(Qt.AlignCenter)

        layout.addWidget(number)
        layout.addWidget(caption)
        parent_layout.addWidget(container, 1)
        return number

    def update_clock(self):
        self.clock_label.setText(QDateTime.currentDateTime().toString("ddd, MMM d  -  h:mm AP"))

    def add_task(self):
        dialog = TaskDialog(self, prefill=self.task_input.text().strip())
        if dialog.exec_() != QDialog.Accepted:
            return

        task = {
            "id": self.new_task_id(),
            "created": QDateTime.currentDateTime().toString(Qt.ISODate),
            **dialog.task_data(),
        }
        self.tasks.append(task)
        self.task_input.clear()
        self.save_tasks()
        self.refresh_tasks()

    def edit_task(self, task_id):
        task = self.find_task(task_id)
        if not task:
            return

        dialog = TaskDialog(self, task=task)
        if dialog.exec_() != QDialog.Accepted:
            return

        task.update(dialog.task_data())
        self.save_tasks()
        self.refresh_tasks()

    def delete_task(self, task_id=None):
        if task_id is None:
            item = self.task_list.currentItem()
            if item is None:
                return
            task_id = item.data(Qt.UserRole)

        task = self.find_task(task_id)
        if not task:
            return

        reply = QMessageBox.question(
            self,
            "Delete Task",
            f'Delete "{task.get("description", "this task")}"?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self.tasks = [existing for existing in self.tasks if existing.get("id") != task_id]
        self.save_tasks()
        self.refresh_tasks()

    def clear_completed(self):
        completed = [task for task in self.tasks if task.get("completed", False)]
        if not completed:
            return

        reply = QMessageBox.question(
            self,
            "Clear Done",
            f"Remove {len(completed)} completed task(s)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self.tasks = [task for task in self.tasks if not task.get("completed", False)]
        self.save_tasks()
        self.refresh_tasks()

    def set_task_completed(self, task_id, completed):
        task = self.find_task(task_id)
        if not task:
            return
        task["completed"] = completed
        self.save_tasks()
        self.refresh_tasks()

    def set_filter(self, selected):
        self.current_filter = selected
        self.refresh_tasks()

    def refresh_tasks(self):
        self.update_stats()
        visible_tasks = self.filtered_tasks()
        self.task_list.clear()

        for task in visible_tasks:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, task["id"])
            widget = TaskItemWidget(self, task)
            widget.adjustSize()
            item.setSizeHint(widget.sizeHint())
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, widget)

        has_visible_tasks = bool(visible_tasks)
        self.task_list.setVisible(has_visible_tasks)
        self.empty_label.setVisible(not has_visible_tasks)
        if not has_visible_tasks:
            self.empty_label.setText(self.empty_message())

    def update_stats(self):
        total = len(self.tasks)
        done = sum(1 for task in self.tasks if task.get("completed", False))
        active = total - done
        late = sum(1 for task in self.tasks if self.is_overdue(task))
        self.total_stat.setText(str(total))
        self.active_stat.setText(str(active))
        self.done_stat.setText(str(done))
        self.late_stat.setText(str(late))

    def filtered_tasks(self):
        query = self.search_input.text().strip().lower()
        tasks = []

        for task in self.tasks:
            description = task.get("description", "").lower()
            notes = task.get("notes", "").lower()
            if query and query not in description and query not in notes:
                continue

            completed = task.get("completed", False)
            if self.current_filter == "active" and completed:
                continue
            if self.current_filter == "completed" and not completed:
                continue
            if self.current_filter == "today" and not self.is_due_today(task):
                continue
            if self.current_filter == "overdue" and not self.is_overdue(task):
                continue

            tasks.append(task)

        return sorted(tasks, key=self.task_sort_key)

    def task_sort_key(self, task):
        due_dt = self.parse_due(task.get("due", ""))
        due_rank = due_dt.toSecsSinceEpoch() if due_dt.isValid() else 9_999_999_999
        priority = task.get("priority", "low").lower()
        priority_rank = PRIORITY_STYLES.get(priority, PRIORITY_STYLES["low"])["rank"]
        completed_rank = 1 if task.get("completed", False) else 0
        return (completed_rank, due_rank, priority_rank, task.get("created", ""))

    def empty_message(self):
        query = self.search_input.text().strip()
        if query:
            return "No matching tasks."
        if not self.tasks:
            return "No tasks yet. Add your first one."
        if self.current_filter == "completed":
            return "No completed tasks yet."
        if self.current_filter == "today":
            return "Nothing due today."
        if self.current_filter == "overdue":
            return "Nothing is late."
        return "No tasks in this view."

    def save_tasks(self):
        with TASKS_FILE.open("w", encoding="utf-8") as file:
            json.dump(self.tasks, file, indent=2)

    def load_tasks(self):
        try:
            with TASKS_FILE.open("r", encoding="utf-8") as file:
                raw_tasks = json.load(file)
        except FileNotFoundError:
            raw_tasks = []
        except json.JSONDecodeError:
            raw_tasks = []

        if not isinstance(raw_tasks, list):
            raw_tasks = []

        self.tasks = []
        for index, raw_task in enumerate(raw_tasks):
            task = self.normalize_task(raw_task, index)
            if task:
                self.tasks.append(task)

    def normalize_task(self, raw_task, index):
        if isinstance(raw_task, str):
            description = raw_task.strip()
            due = ""
            priority = "low"
            completed = False
            notes = ""
            created = QDateTime.currentDateTime().toString(Qt.ISODate)
            task_id = self.legacy_task_id(description, due, index)
        elif isinstance(raw_task, dict):
            description = str(raw_task.get("description", "")).strip()
            due = str(raw_task.get("due", "")).strip()
            priority = str(raw_task.get("priority", "low")).lower()
            completed = bool(raw_task.get("completed", False))
            notes = str(raw_task.get("notes", "")).strip()
            created = str(raw_task.get("created", "")).strip()
            task_id = str(raw_task.get("id", "")).strip()
            if not created:
                created = QDateTime.currentDateTime().toString(Qt.ISODate)
            if not task_id:
                task_id = self.legacy_task_id(description, due, index)
        else:
            return None

        if not description:
            return None
        if priority not in PRIORITY_STYLES:
            priority = "low"

        return {
            "id": task_id,
            "description": description,
            "notes": notes,
            "due": due,
            "priority": priority,
            "completed": completed,
            "created": created,
        }

    def find_task(self, task_id):
        for task in self.tasks:
            if task.get("id") == task_id:
                return task
        return None

    def new_task_id(self):
        stamp = QDateTime.currentDateTime().toMSecsSinceEpoch()
        return f"task-{stamp}-{len(self.tasks)}"

    def legacy_task_id(self, description, due, index):
        checksum = sum(ord(char) for char in f"{description}{due}")
        return f"legacy-{index}-{checksum}"

    @staticmethod
    def parse_due(due):
        if not due:
            return QDateTime()
        for date_format in ("yyyy-MM-dd HH:mm", "yyyy-MM-dd h:mm AP", Qt.ISODate):
            parsed = QDateTime.fromString(due, date_format)
            if parsed.isValid():
                return parsed
        parsed_date = QDate.fromString(due, "yyyy-MM-dd")
        if parsed_date.isValid():
            return QDateTime(parsed_date, QTime(23, 59))
        return QDateTime()

    def is_due_today(self, task):
        due_dt = self.parse_due(task.get("due", ""))
        return due_dt.isValid() and due_dt.date() == QDate.currentDate()

    def is_overdue(self, task):
        if task.get("completed", False):
            return False
        due_dt = self.parse_due(task.get("due", ""))
        if not due_dt.isValid():
            return False
        return due_dt.toSecsSinceEpoch() < QDateTime.currentDateTime().toSecsSinceEpoch()

    def format_due(self, task):
        due_dt = self.parse_due(task.get("due", ""))
        if not due_dt.isValid():
            return "No due date"

        due_date = due_dt.date()
        today = QDate.currentDate()
        time_text = due_dt.time().toString("h:mm AP")

        if due_date == today:
            day_text = "Today"
        elif due_date == today.addDays(1):
            day_text = "Tomorrow"
        elif due_date == today.addDays(-1):
            day_text = "Yesterday"
        else:
            day_text = due_date.toString("MMM d")

        if self.is_overdue(task):
            return f"Late - {day_text}, {time_text}"
        return f"{day_text}, {time_text}"

    def due_label_style(self, task):
        t = self.theme
        if task.get("completed", False):
            return f"color: {t['muted']}; font-weight: 700;"
        if self.is_overdue(task):
            return f"color: {t['danger_text']}; font-weight: 800;"
        if self.is_due_today(task):
            return f"color: {t['accent']}; font-weight: 800;"
        return f"color: {t['muted']}; font-weight: 700;"

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_responsive_layout()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_toolbar_drag_area(event.pos()):
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_position is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_position)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_position = None
        super().mouseReleaseEvent(event)

    def is_toolbar_drag_area(self, position):
        if not hasattr(self, "toolbar"):
            return False
        if isinstance(self.childAt(position), QToolButton):
            return False
        return self.toolbar.rect().contains(self.toolbar.mapFrom(self, position))


if __name__ == "__main__":
    configure_windows_taskbar_icon()
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setWindowIcon(create_brand_icon())
    app.setFont(QFont("Segoe UI", 10))
    tracker = TaskTracker()
    tracker.show()
    sys.exit(app.exec_())
