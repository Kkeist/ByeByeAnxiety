"""Calendar widget for task scheduling"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget,
                             QLabel, QListWidget, QListWidgetItem, QPushButton,
                             QDialog, QDialogButtonBox, QDateEdit, QTextEdit,
                             QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QLocale
from PyQt6.QtGui import QTextCharFormat, QColor
from datetime import datetime, timedelta

from src.models import Task


class TaskScheduleDialog(QDialog):
    """Dialog for scheduling task start and due dates"""
    
    def __init__(self, task=None, parent=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Schedule Task" if task else "New Scheduled Task")
        self.setMinimumWidth(400)
        self.setup_ui()
        
        if task:
            self.load_task_data()
    
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QFormLayout(self)
        
        # Task title
        self.title_edit = QTextEdit()
        self.title_edit.setMaximumHeight(60)
        layout.addRow("Task Title:", self.title_edit)
        
        # Start date
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.start_date.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        layout.addRow("Start Date:", self.start_date)
        
        # Due date
        self.due_date = QDateEdit()
        self.due_date.setDate(QDate.currentDate().addDays(1))
        self.due_date.setCalendarPopup(True)
        self.due_date.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        layout.addRow("Due Date:", self.due_date)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        layout.addRow("Description:", self.description_edit)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def load_task_data(self):
        """Load task data into form"""
        if not self.task:
            return
        
        self.title_edit.setPlainText(self.task.title)
        self.description_edit.setPlainText(self.task.description or "")
        
        if self.task.start_date:
            start_date = QDate.fromString(self.task.start_date, "yyyy-MM-dd")
            self.start_date.setDate(start_date)
        
        if self.task.due_date:
            due_date = QDate.fromString(self.task.due_date, "yyyy-MM-dd")
            self.due_date.setDate(due_date)
    
    def get_task_data(self):
        """Get task data from form"""
        return {
            "title": self.title_edit.toPlainText().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "start_date": self.start_date.date().toString("yyyy-MM-dd"),
            "due_date": self.due_date.date().toString("yyyy-MM-dd")
        }


class CalendarWidget(QWidget):
    """Calendar widget for viewing and scheduling tasks"""
    
    task_scheduled = pyqtSignal(str)  # task_id
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        
        self.setup_ui()
        self.load_tasks()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("<h3>📅 Task Calendar</h3>")
        title.setStyleSheet("color: #2c3e50;")
        header.addWidget(title)
        header.addStretch()
        
        schedule_btn = QPushButton("+ Schedule Task")
        schedule_btn.clicked.connect(self.schedule_new_task)
        schedule_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        header.addWidget(schedule_btn)
        layout.addLayout(header)
        
        # Main content
        content = QHBoxLayout()
        
        # Calendar
        self.calendar = QCalendarWidget()
        self.calendar.setMinimumWidth(350)
        # Set locale to English to force weekday names in English
        self.calendar.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.calendar.clicked.connect(self.date_selected)
        content.addWidget(self.calendar, 2)
        
        # Task list for selected date
        task_panel = QVBoxLayout()
        
        self.selected_date_label = QLabel("Select a date to view tasks")
        self.selected_date_label.setStyleSheet("font-weight: bold; color: #2c3e50; padding: 10px;")
        task_panel.addWidget(self.selected_date_label)
        
        self.task_list = QListWidget()
        self.task_list.setMaximumWidth(300)
        self.task_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e9ecef;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
        """)
        task_panel.addWidget(self.task_list)
        
        content.addLayout(task_panel, 1)
        layout.addLayout(content)
        
        # Info
        info = QLabel("💡 Tasks are color-coded: 🔵 Start dates, 🔴 Due dates, 🟢 Completed")
        info.setWordWrap(True)
        info.setStyleSheet("""
            background-color: #e8f4fd;
            color: #1565c0;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #bbdefb;
            margin: 10px 0;
        """)
        layout.addWidget(info)
    
    def load_tasks(self):
        """Load all tasks and highlight dates on calendar"""
        # Clear existing highlights
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # Get all tasks
        all_tasks = []
        for category in ["today_must", "future_date", "long_term", "someday_maybe"]:
            tasks = self.data_manager.get_tasks_by_category(category)
            all_tasks.extend(tasks)
        
        # Highlight dates with tasks
        for task in all_tasks:
            # Highlight start date
            if task.start_date:
                start_date = QDate.fromString(task.start_date, "yyyy-MM-dd")
                if start_date.isValid():
                    format = QTextCharFormat()
                    if task.completed:
                        format.setBackground(QColor("#4caf50"))  # Green for completed
                    else:
                        format.setBackground(QColor("#2196f3"))  # Blue for start dates
                    format.setForeground(QColor("white"))
                    self.calendar.setDateTextFormat(start_date, format)
            
            # Highlight due date
            if task.due_date:
                due_date = QDate.fromString(task.due_date, "yyyy-MM-dd")
                if due_date.isValid():
                    format = QTextCharFormat()
                    if task.completed:
                        format.setBackground(QColor("#4caf50"))  # Green for completed
                    else:
                        format.setBackground(QColor("#f44336"))  # Red for due dates
                    format.setForeground(QColor("white"))
                    self.calendar.setDateTextFormat(due_date, format)
    
    def date_selected(self, date: QDate):
        """Handle date selection"""
        date_str = date.toString("yyyy-MM-dd")
        self.selected_date_label.setText(f"Tasks for {date.toString('dddd, MMMM d, yyyy')}")
        
        # Clear task list
        self.task_list.clear()
        
        # Get all tasks
        all_tasks = []
        for category in ["today_must", "future_date", "long_term", "someday_maybe"]:
            tasks = self.data_manager.get_tasks_by_category(category)
            all_tasks.extend(tasks)
        
        # Find tasks for this date
        tasks_for_date = []
        for task in all_tasks:
            if task.start_date == date_str or task.due_date == date_str:
                tasks_for_date.append(task)
        
        if not tasks_for_date:
            item = QListWidgetItem("No tasks scheduled for this date")
            item.setFlags(Qt.ItemFlag.NoItemFlags)  # Make it non-selectable
            self.task_list.addItem(item)
        else:
            for task in tasks_for_date:
                # Determine task type for this date
                task_type = ""
                if task.start_date == date_str:
                    task_type += "🔵 Start "
                if task.due_date == date_str:
                    task_type += "🔴 Due "
                
                status = "✅" if task.completed else "⏳"
                
                item_text = f"{status} {task_type}- {task.title}"
                if task.description:
                    item_text += f"\n   {task.description[:50]}{'...' if len(task.description) > 50 else ''}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, task)
                
                # Style based on completion
                if task.completed:
                    item.setBackground(QColor("#e8f5e8"))
                
                self.task_list.addItem(item)
    
    def schedule_new_task(self):
        """Schedule a new task"""
        dialog = TaskScheduleDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_task_data()
            
            if not data["title"]:
                QMessageBox.warning(self, "Invalid Input", "Task title cannot be empty.")
                return
            
            # Create new task
            task = Task(
                id=datetime.now().strftime("%Y%m%d%H%M%S%f"),
                title=data["title"],
                description=data["description"],
                category="future_date",  # Scheduled tasks go to future_date
                start_date=data["start_date"],
                due_date=data["due_date"]
            )
            
            # Save task
            self.data_manager.save_task(task)
            
            # Refresh calendar
            self.load_tasks()
            
            # Emit signal
            self.task_scheduled.emit(task.id)
            
            QMessageBox.information(self, "Task Scheduled", 
                                  f"Task '{task.title}' scheduled successfully!")
    
    def refresh_calendar(self):
        """Refresh the calendar display"""
        self.load_tasks()
        # Refresh current date selection if any
        current_date = self.calendar.selectedDate()
        self.date_selected(current_date)
