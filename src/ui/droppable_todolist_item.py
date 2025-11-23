"""Droppable todo list item widget"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPalette


class DroppableTodoListItem(QFrame):
    """A todo list item that can accept dropped tasks"""
    
    task_dropped = pyqtSignal(str, str)  # todolist_id, task_id
    todolist_clicked = pyqtSignal(dict)  # todolist_data
    
    def __init__(self, todolist_data, data_manager, parent=None):
        super().__init__(parent)
        self.todolist_data = todolist_data
        self.data_manager = data_manager
        
        self.setup_ui()
        self.setAcceptDrops(True)
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Title
        title_label = QLabel(f"📝 {self.todolist_data['name']}")
        title_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 13px;")
        layout.addWidget(title_label)
        
        # Task count and preview
        task_count = len(self.todolist_data.get('tasks', []))
        count_label = QLabel(f"{task_count} tasks")
        count_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        layout.addWidget(count_label)
        
        # Show first few task titles if any (as text preview, not draggable widgets to avoid overlap)
        if task_count > 0:
            task_ids = self.todolist_data.get('tasks', [])[:2]  # Show first 2 tasks only
            valid_tasks = []
            for task_id in task_ids:
                task = self.data_manager.get_task(task_id)
                if task:  # Only show tasks that still exist
                    valid_tasks.append(task)
            
            # Show task titles as simple text labels instead of widgets
            for task in valid_tasks:
                task_label = QLabel(f"• {task.title[:30]}{'...' if len(task.title) > 30 else ''}")
                task_label.setStyleSheet("color: #5a6c7d; font-size: 10px; margin-left: 5px;")
                task_label.setWordWrap(False)
                layout.addWidget(task_label)
            
            if task_count > len(valid_tasks):
                more_label = QLabel(f"... and {task_count - len(valid_tasks)} more")
                more_label.setStyleSheet("color: #adb5bd; font-size: 9px; margin-left: 5px;")
                layout.addWidget(more_label)
        
        # Drop zone hint
        drop_hint = QLabel("📋 Drop tasks here")
        drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_hint.setStyleSheet("""
            color: #bdc3c7; 
            font-size: 10px; 
            padding: 5px;
            border: 1px dashed #dee2e6;
            border-radius: 3px;
            margin-top: 5px;
        """)
        layout.addWidget(drop_hint)
        
        # Style the frame
        self.setStyleSheet("""
            DroppableTodoListItem {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                margin: 2px 0;
            }
            DroppableTodoListItem:hover {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)
        self.setMinimumHeight(60)
        self.setMaximumHeight(200)  # Increase max height to prevent overlap
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click to open todolist"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.todolist_clicked.emit(self.todolist_data)
    
    def dragEnterEvent(self, event):
        """Handle drag enter event"""
        if event.mimeData().hasFormat("application/x-task") or event.mimeData().hasText():
            event.acceptProposedAction()
            # Highlight the drop zone
            self.setStyleSheet("""
                DroppableTodoListItem {
                    background-color: #e3f2fd;
                    border: 2px solid #3498db;
                    border-radius: 5px;
                    margin: 2px 0;
                }
            """)
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        """Handle drag move event"""
        if event.mimeData().hasFormat("application/x-task") or event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        # Restore normal styling
        self.setStyleSheet("""
            DroppableTodoListItem {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                margin: 2px 0;
            }
            DroppableTodoListItem:hover {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)
    
    def dropEvent(self, event):
        """Handle drop event"""
        if event.mimeData().hasFormat("application/x-task"):
            task_id = event.mimeData().data("application/x-task").data().decode()
        elif event.mimeData().hasText():
            task_id = event.mimeData().text()
        else:
            event.ignore()
            return
        
        # Emit signal with todolist_id and task_id
        self.task_dropped.emit(self.todolist_data['id'], task_id)
        
        event.acceptProposedAction()
        
        # Restore normal styling
        self.dragLeaveEvent(event)
        
        # Update the display to show the new task count
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the display to show updated task count"""
        # This will be called after a task is dropped
        # The parent will handle the actual data update
        pass
