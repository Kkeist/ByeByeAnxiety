"""TodoList widget - Stack of paper-like todo lists"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QListWidgetItem, QLabel, QDialog,
                             QLineEdit, QTextEdit, QDialogButtonBox, QMessageBox,
                             QScrollArea, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QDrag, QPainter, QPixmap
from datetime import datetime
import json

from src.models import Task


class TodoListDialog(QDialog):
    """Dialog for creating/editing todo lists"""
    
    def __init__(self, todolist=None, parent=None):
        super().__init__(parent)
        self.todolist = todolist
        self.setWindowTitle("Edit Todo List" if todolist else "New Todo List")
        self.setMinimumWidth(400)
        self.setup_ui()
        
        if todolist:
            self.load_todolist()
    
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        
        # Name
        layout.addWidget(QLabel("Todo List Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(100)
        layout.addWidget(self.desc_input)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_todolist(self):
        """Load todolist data into form"""
        self.name_input.setText(self.todolist.get('name', ''))
        self.desc_input.setPlainText(self.todolist.get('description', ''))
    
    def get_todolist_data(self):
        """Get todolist data from form"""
        return {
            "name": self.name_input.text(),
            "description": self.desc_input.toPlainText()
        }


class TodoListItem(QFrame):
    """A single todo list item that looks like a paper"""
    
    todolist_clicked = pyqtSignal(dict)  # todolist_data
    
    def __init__(self, todolist_data, data_manager=None, parent=None):
        super().__init__(parent)
        self.todolist_data = todolist_data
        self.data_manager = data_manager
        self.drag_start_position = None
        self.setAcceptDrops(False)  # Remove drop functionality
        self.setup_ui()
        self.setup_style()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QHBoxLayout()
        
        name_label = QLabel(f"📝 {self.todolist_data['name']}")
        name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        header.addWidget(name_label)
        
        header.addStretch()
        
        # Task count
        task_count = len(self.todolist_data.get('tasks', []))
        count_label = QLabel(f"{task_count} tasks")
        count_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        header.addWidget(count_label)
        
        layout.addLayout(header)
        
        # Description
        if self.todolist_data.get('description'):
            desc_label = QLabel(self.todolist_data['description'])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #5a6c7d; font-size: 11px; margin: 5px 0;")
            layout.addWidget(desc_label)
        
        # Task preview (first 3 tasks) - show actual task names
        tasks = self.todolist_data.get('tasks', [])
        valid_tasks = []
        if self.data_manager:
            for task_id in tasks[:3]:
                # Get task from data manager
                task = self.data_manager.get_task(task_id)
                if task:  # Only show tasks that still exist
                    valid_tasks.append(task)
        
        for task in valid_tasks:
            task_item = QLabel(f"• {task.title[:35]}{'...' if len(task.title) > 35 else ''}")
            task_item.setStyleSheet("color: #34495e; font-size: 11px; margin-left: 10px;")
            layout.addWidget(task_item)
        
        if len(tasks) > len(valid_tasks):
            more_label = QLabel(f"... and {len(tasks) - len(valid_tasks)} more")
            more_label.setStyleSheet("color: #95a5a6; font-size: 10px; margin-left: 10px;")
            layout.addWidget(more_label)
        
        # Click hint
        click_hint = QLabel("👆 Double-click to view details")
        click_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        click_hint.setStyleSheet("""
            color: #bdc3c7; 
            font-size: 10px; 
            padding: 5px;
            margin-top: 5px;
        """)
        layout.addWidget(click_hint)
    
    def setup_style(self):
        """Setup paper-like styling"""
        self.setStyleSheet("""
            TodoListItem {
                background-color: #fffef7;
                border: 1px solid #e8e5d3;
                border-radius: 8px;
                margin: 5px;
            }
            TodoListItem:hover {
                border-color: #d4c5a9;
                background-color: #fffef0;
            }
        """)
        self.setFixedSize(250, 200)
    
    def mousePressEvent(self, event):
        """Handle mouse press for drag start"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.position().toPoint()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        
        if not self.drag_start_position:
            return
        
        # Check if we've moved far enough to start a drag
        if ((event.position().toPoint() - self.drag_start_position).manhattanLength() < 10):
            return
        
        # Start drag operation
        self.start_drag()
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click to open todolist details"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.todolist_clicked.emit(self.todolist_data)
    
    def start_drag(self):
        """Start the drag operation"""
        from PyQt6.QtGui import QDrag, QPainter
        from PyQt6.QtCore import QMimeData
        
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # Set the todolist ID as drag data
        mime_data.setText(self.todolist_data['id'])
        mime_data.setData("application/x-todolist", self.todolist_data['id'].encode())
        
        # Create drag pixmap
        pixmap = self.grab()
        
        # Make it semi-transparent
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), Qt.GlobalColor.transparent)
        painter.setOpacity(0.7)
        painter.drawPixmap(0, 0, self.grab())
        painter.end()
        
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(self.drag_start_position)
        
        # Execute drag
        drop_action = drag.exec(Qt.DropAction.MoveAction)


class TodoListWidget(QWidget):
    """TodoList management widget - stack of paper-like lists"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        
        self.setup_ui()
        self.load_todolists()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("<h3>📚 Todo Lists</h3>")
        title.setStyleSheet("color: #2c3e50;")
        header.addWidget(title)
        header.addStretch()
        
        add_btn = QPushButton("+ New List")
        add_btn.clicked.connect(self.add_todolist)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        header.addWidget(add_btn)
        layout.addLayout(header)
        
        # Info
        info = QLabel("📝 Create todo lists and drag tasks from the Tasks tab to organize them into lists.")
        info.setWordWrap(True)
        info.setStyleSheet("""
            background-color: #fff3cd;
            color: #856404;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ffeaa7;
            margin-bottom: 10px;
        """)
        layout.addWidget(info)
        
        # Scroll area for todo lists
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.lists_container = QWidget()
        self.lists_container.setAcceptDrops(True)
        self.lists_layout = QVBoxLayout(self.lists_container)
        self.lists_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Add drag/drop handlers for returning todolist from sidebar
        self.lists_container.dragEnterEvent = self.todolist_drag_enter
        self.lists_container.dragMoveEvent = self.todolist_drag_move
        self.lists_container.dropEvent = self.todolist_drop
        
        scroll.setWidget(self.lists_container)
        layout.addWidget(scroll)
    
    def load_todolists(self):
        """Load all todo lists"""
        # Clear existing items
        while self.lists_layout.count():
            item = self.lists_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Load from data manager
        todolists = self.data_manager.get_setting("todolists", [])
        
        # Create grid layout for paper stack effect
        row_layout = None
        for i, todolist in enumerate(todolists):
            if i % 3 == 0:  # 3 lists per row
                row_layout = QHBoxLayout()
                self.lists_layout.addLayout(row_layout)
            
            list_item = TodoListItem(todolist, self.data_manager)
            list_item.todolist_clicked.connect(self.open_todolist_detail)
            row_layout.addWidget(list_item)
        
        # Add stretch to last row if needed
        if row_layout:
            row_layout.addStretch()
    
    def add_todolist(self):
        """Add a new todo list"""
        dialog = TodoListDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_todolist_data()
            
            todolist = {
                "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                "name": data["name"],
                "description": data["description"],
                "tasks": [],
                "created_at": datetime.now().isoformat()
            }
            
            # Save to data manager
            todolists = self.data_manager.get_setting("todolists", [])
            todolists.append(todolist)
            self.data_manager.save_setting("todolists", todolists)
            
            self.load_todolists()
    
    def add_task_to_list(self, todolist_id: str, task_id: str):
        """Add a task to a todo list"""
        todolists = self.data_manager.get_setting("todolists", [])
        
        # Find the todolist
        for todolist in todolists:
            if todolist["id"] == todolist_id:
                if task_id not in todolist["tasks"]:
                    todolist["tasks"].append(task_id)
                    break
        
        # Save updated todolists
        self.data_manager.save_setting("todolists", todolists)
        self.load_todolists()
        
        # Show success message
        QMessageBox.information(self, "Task Added", "Task added to todo list successfully!")
    
    def open_todolist_detail(self, todolist_data):
        """Open todolist detail popup"""
        from src.ui.todolist_detail_popup import TodoListDetailPopup
        
        popup = TodoListDetailPopup(todolist_data, self.data_manager, self)
        popup.todolist_updated.connect(self.load_todolists)
        
        # Position popup
        if self.parent():
            parent_rect = self.parent().geometry()
            popup.move(parent_rect.x() + 50, parent_rect.y() + 50)
        popup.show()
        popup.raise_()
        popup.activateWindow()
    
    def todolist_drag_enter(self, event):
        """Handle drag enter on todolist container"""
        if event.mimeData().hasFormat("application/x-todolist"):
            event.acceptProposedAction()
            self.lists_container.setStyleSheet("background-color: #e3f2fd;")
    
    def todolist_drag_move(self, event):
        """Handle drag move on todolist container"""
        if event.mimeData().hasFormat("application/x-todolist"):
            event.acceptProposedAction()
    
    def todolist_drop(self, event):
        """Handle drop on todolist container - remove from sidebar"""
        if event.mimeData().hasFormat("application/x-todolist"):
            todolist_id = event.mimeData().data("application/x-todolist").data().decode()
            
            # Remove show_in_sidebar flag
            todolists = self.data_manager.get_setting("todolists", [])
            for todolist in todolists:
                if todolist["id"] == todolist_id:
                    # Only remove if it's not a default todolist
                    if todolist.get("is_default") not in ["daily", "longterm"]:
                        todolist["show_in_sidebar"] = False
                    break
            
            self.data_manager.save_setting("todolists", todolists)
            
            # Refresh to update display
            self.load_todolists()
            
            # Also refresh sidebar if we have access to main window
            if hasattr(self.parent(), 'refresh_all_todolists'):
                self.parent().refresh_all_todolists()
            elif hasattr(self.parent().parent(), 'refresh_all_todolists'):
                self.parent().parent().refresh_all_todolists()
            
            event.acceptProposedAction()
        
        self.lists_container.setStyleSheet("")
