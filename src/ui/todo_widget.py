"""Todo list widget"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QListWidgetItem, QCheckBox, QLabel,
                             QDialog, QLineEdit, QTextEdit, QComboBox, QDateEdit,
                             QDialogButtonBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QMimeData
from PyQt6.QtGui import QDrag
from datetime import datetime

from src.models import Task, TaskCategory
from src.ui.draggable_task_item import DraggableTaskItem


class TaskDialog(QDialog):
    """Dialog for creating/editing tasks"""
    
    def __init__(self, task=None, parent=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Edit Task" if task else "New Task")
        self.setMinimumWidth(400)
        self.setup_ui()
        
        if task:
            self.load_task()
    
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        
        # Title
        layout.addWidget(QLabel("Title:"))
        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(100)
        layout.addWidget(self.desc_input)
        
        # Category
        layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        for cat in TaskCategory.all_categories():
            self.category_combo.addItem(TaskCategory.display_name(cat), cat)
        layout.addWidget(self.category_combo)
        
        # Start date (optional)
        start_date_layout = QHBoxLayout()
        self.start_date_check = QCheckBox("Set Start Date (optional):")
        self.start_date_check.stateChanged.connect(self.on_start_date_check_changed)
        start_date_layout.addWidget(self.start_date_check)
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setEnabled(False)  # Disabled by default
        start_date_layout.addWidget(self.start_date)
        layout.addLayout(start_date_layout)
        
        # Due date
        layout.addWidget(QLabel("Due Date:"))
        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDate(QDate.currentDate())
        # When due date changes, update start date to match if they're the same
        self.due_date.dateChanged.connect(self.on_due_date_changed)
        layout.addWidget(self.due_date)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def on_start_date_check_changed(self, state):
        """Enable/disable start date based on checkbox"""
        self.start_date.setEnabled(state == Qt.CheckState.Checked.value)
        if state == Qt.CheckState.Checked.value and not self.start_date.date().isValid():
            # If enabled and no date set, default to due date
            self.start_date.setDate(self.due_date.date())
    
    def on_due_date_changed(self, date):
        """When due date changes, update start date to match if they're currently the same"""
        if self.start_date_check.isChecked() and self.start_date.date() == self.due_date.date():
            # If start date was same as old due date, keep them in sync
            self.start_date.setDate(date)
    
    def load_task(self):
        """Load task data into form"""
        self.title_input.setText(self.task.title)
        self.desc_input.setPlainText(self.task.description)
        
        # Set category
        index = self.category_combo.findData(self.task.category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        
        # Set due date
        if self.task.due_date:
            date = QDate.fromString(self.task.due_date, "yyyy-MM-dd")
            self.due_date.setDate(date)
        else:
            # If no due date, default to today
            self.due_date.setDate(QDate.currentDate())
        
        # Set start date (optional)
        if self.task.start_date:
            date = QDate.fromString(self.task.start_date, "yyyy-MM-dd")
            self.start_date.setDate(date)
            self.start_date_check.setChecked(True)
            self.start_date.setEnabled(True)
        else:
            # No start date - checkbox unchecked
            self.start_date_check.setChecked(False)
            self.start_date.setEnabled(False)
            # Set to due date for display, but won't be saved
            if self.task.due_date:
                date = QDate.fromString(self.task.due_date, "yyyy-MM-dd")
                self.start_date.setDate(date)
            else:
                self.start_date.setDate(QDate.currentDate())
    
    def get_task_data(self):
        """Get task data from form"""
        due_date_str = self.due_date.date().toString("yyyy-MM-dd")
        
        # Start date is optional - only include if checkbox is checked
        start_date_str = None
        if self.start_date_check.isChecked():
            start_date_str = self.start_date.date().toString("yyyy-MM-dd")
        
        return {
            "title": self.title_input.text(),
            "description": self.desc_input.toPlainText(),
            "category": self.category_combo.currentData(),
            "start_date": start_date_str,  # Can be None
            "due_date": due_date_str
        }


class TodoWidget(QWidget):
    """Todo list management widget"""
    
    task_completed = pyqtSignal(str)  # task title
    task_uncompleted = pyqtSignal(str)
    task_deleted = pyqtSignal(str)  # task_id
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.current_category = TaskCategory.TODAY_MUST
        
        self.setup_ui()
        self.load_tasks()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("<h3>Tasks</h3>"))
        header.addStretch()
        
        add_btn = QPushButton("+ Add Task")
        add_btn.clicked.connect(self.add_task)
        add_btn.setStyleSheet("""
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
        header.addWidget(add_btn)
        layout.addLayout(header)
        
        # Category tabs
        cat_layout = QHBoxLayout()
        self.category_buttons = {}
        
        for cat in TaskCategory.all_categories():
            btn = QPushButton(TaskCategory.display_name(cat))
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, c=cat: self.switch_category(c))
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 12px;
                    border: 1px solid #dee2e6;
                    background-color: white;
                }
                QPushButton:checked {
                    background-color: #3498db;
                    color: white;
                    border-color: #3498db;
                }
            """)
            self.category_buttons[cat] = btn
            cat_layout.addWidget(btn)
        
        self.category_buttons[TaskCategory.TODAY_MUST].setChecked(True)
        layout.addLayout(cat_layout)
        
        # Task list (scroll area with draggable items)
        from PyQt6.QtWidgets import QScrollArea
        self.task_scroll = QScrollArea()
        self.task_scroll.setWidgetResizable(True)
        self.task_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """)
        
        self.task_container = QWidget()
        self.task_container.setAcceptDrops(True)
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.task_scroll.setWidget(self.task_container)
        
        layout.addWidget(self.task_scroll)
        
        # Actions
        actions = QHBoxLayout()
        
        delete_completed_btn = QPushButton("Delete Completed")
        delete_completed_btn.clicked.connect(self.delete_completed)
        delete_completed_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        actions.addWidget(delete_completed_btn)
        actions.addStretch()
        
        layout.addLayout(actions)
    
    def switch_category(self, category: str):
        """Switch to a different category"""
        self.current_category = category
        
        # Update button states
        for cat, btn in self.category_buttons.items():
            btn.setChecked(cat == category)
        
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks for current category"""
        # Clear existing task items
        while self.task_layout.count():
            item = self.task_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        tasks = self.data_manager.get_tasks_by_category(self.current_category)
        
        # Sort by order, then by created date
        tasks.sort(key=lambda t: (t.order, t.created_at))
        
        if not tasks:
            # Show empty state
            empty_label = QLabel("No tasks in this category.\nClick 'Add Task' to create one!")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    color: #95a5a6;
                    font-style: italic;
                    padding: 40px;
                    font-size: 14px;
                }
            """)
            self.task_layout.addWidget(empty_label)
        else:
            for task in tasks:
                self.add_task_item(task)
        
        # Add stretch to push tasks to top
        self.task_layout.addStretch()
    
    def add_task_item(self, task: Task, index: int = -1):
        """Add a draggable task item to the layout"""
        task_item = DraggableTaskItem(task)
        task_item.task_completed.connect(self.on_task_completed)
        task_item.task_clicked.connect(self.edit_task_by_id)
        
        # Store task reference for reordering
        task_item.task_id = task.id
        
        # Add action buttons layout
        item_layout = QHBoxLayout()
        item_layout.addWidget(task_item, 1)
        
        # Action buttons
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(2)
        
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(25, 25)
        edit_btn.clicked.connect(lambda: self.edit_task(task))
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        actions_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(25, 25)
        delete_btn.clicked.connect(lambda: self.delete_task(task))
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        actions_layout.addWidget(delete_btn)
        
        item_layout.addLayout(actions_layout)
        
        # Create sortable container widget
        from src.ui.sortable_task_container import SortableTaskContainer
        container = SortableTaskContainer(task.id)
        container.setLayout(item_layout)
        container.task_reordered.connect(self.reorder_tasks)
        
        if index >= 0:
            self.task_layout.insertWidget(index, container)
        else:
            self.task_layout.addWidget(container)
    
    def reorder_tasks(self, dragged_task_id: str, target_task_id: str):
        """Reorder tasks by moving dragged task to target position"""
        # Get all tasks in current category
        tasks = self.data_manager.get_tasks_by_category(self.current_category)
        tasks.sort(key=lambda t: (t.order, t.created_at))
        
        # Find indices
        dragged_index = next((i for i, t in enumerate(tasks) if t.id == dragged_task_id), -1)
        target_index = next((i for i, t in enumerate(tasks) if t.id == target_task_id), -1)
        
        if dragged_index == -1 or target_index == -1 or dragged_index == target_index:
            return
        
        # Remove dragged task and reinsert at target position
        dragged_task = tasks.pop(dragged_index)
        
        # Adjust target index if needed
        if dragged_index < target_index:
            target_index -= 1
        
        tasks.insert(target_index, dragged_task)
        
        # Update order values
        for i, task in enumerate(tasks):
            task.order = i
            self.data_manager.save_task(task)
        
        # Reload display
        self.load_tasks()
    
    def on_task_completed(self, task_id: str):
        """Handle task completion"""
        task = self.data_manager.get_task(task_id)
        if task:
            self.data_manager.save_task(task)
            self.task_completed.emit(task_id)
    
    def edit_task_by_id(self, task_id: str):
        """Edit task by ID"""
        task = self.data_manager.get_task(task_id)
        if task:
            self.edit_task(task)
    
    def add_task(self):
        """Add a new task"""
        dialog = TaskDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_task_data()
            task = Task(
                id=datetime.now().strftime("%Y%m%d%H%M%S%f"),
                title=data["title"],
                description=data["description"],
                category=data["category"],
                start_date=data.get("start_date"),  # Can be None
                due_date=data["due_date"]
            )
            self.data_manager.save_task(task)
            
            # Reload if in same category
            if task.category == self.current_category:
                self.load_tasks()
    
    def edit_task(self, task: Task):
        """Edit a task"""
        dialog = TaskDialog(task=task, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_task_data()
            task.title = data["title"]
            task.description = data["description"]
            task.category = data["category"]
            task.due_date = data["due_date"]
            self.data_manager.save_task(task)
            self.load_tasks()
    
    def delete_task(self, task: Task):
        """Delete a task"""
        reply = QMessageBox.question(
            self, "Delete Task",
            f"Are you sure you want to delete '{task.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.delete_task(task.id)
            self.task_deleted.emit(task.id)
            self.load_tasks()
    
    def toggle_task(self, task: Task, state: int):
        """Toggle task completion"""
        if state == Qt.CheckState.Checked.value:
            task.mark_complete()
            self.task_completed.emit(task.title)
        else:
            task.mark_incomplete()
            self.task_uncompleted.emit(task.title)
        
        self.data_manager.save_task(task)
        self.load_tasks()
    
    def delete_completed(self):
        """Delete all completed tasks"""
        reply = QMessageBox.question(
            self, "Delete Completed Tasks",
            "Are you sure you want to delete all completed tasks?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            tasks = self.data_manager.get_tasks_by_category(self.current_category)
            for task in tasks:
                if task.completed:
                    self.data_manager.delete_task(task.id)
            self.load_tasks()

