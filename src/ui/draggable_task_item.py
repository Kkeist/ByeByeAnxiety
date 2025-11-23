"""Draggable task item widget"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QDrag, QPainter, QPixmap

from src.models import Task


class DraggableTaskItem(QWidget):
    """A draggable task item widget"""
    
    task_completed = pyqtSignal(str)  # task_id
    task_uncompleted = pyqtSignal(str)  # task_id
    task_clicked = pyqtSignal(str)    # task_id
    
    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.task = task
        self.drag_start_position = None
        
        self.setup_ui()
        self.setAcceptDrops(False)  # This item is draggable, not a drop target
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.task.completed)
        self.checkbox.stateChanged.connect(self.on_checkbox_changed)
        layout.addWidget(self.checkbox)
        
        # Task info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)  # Reduce spacing between items
        
        # Title
        self.title_label = QLabel(f"<b>{self.task.title}</b>")
        self.title_label.setWordWrap(True)  # Allow title to wrap
        if self.task.completed:
            self.title_label.setStyleSheet("text-decoration: line-through; color: #95a5a6;")
        else:
            self.title_label.setStyleSheet("color: #2c3e50;")
        info_layout.addWidget(self.title_label)
        
        # Add spacer to push description and date down
        info_layout.addSpacing(2)
        
        # Description (if exists) - limit height
        if self.task.description:
            desc_text = self.task.description[:50] + "..." if len(self.task.description) > 50 else self.task.description
            desc_label = QLabel(desc_text)
            desc_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
            desc_label.setMaximumHeight(15)  # Limit height
            info_layout.addWidget(desc_label)
        
        # Due date
        if self.task.due_date:
            due_label = QLabel(f"📅 {self.task.due_date}")
            due_label.setStyleSheet("color: #e67e22; font-size: 10px;")
            info_layout.addWidget(due_label)
        
        layout.addLayout(info_layout, 1)
        
        # Drag handle
        drag_handle = QLabel("⋮⋮")
        drag_handle.setStyleSheet("""
            color: #bdc3c7;
            font-size: 16px;
            padding: 5px;
        """)
        drag_handle.setToolTip("Drag to move task")
        layout.addWidget(drag_handle)
        
        # Style the widget
        self.setStyleSheet("""
            DraggableTaskItem {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                margin: 2px 0;
            }
            DraggableTaskItem:hover {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)
        self.setMinimumHeight(60)  # Increase minimum height to give title more space
    
    def on_checkbox_changed(self, state):
        """Handle checkbox state change"""
        self.task.completed = (state == Qt.CheckState.Checked.value)
        
        # Update visual style
        was_completed = self.task.completed
        if self.task.completed:
            self.title_label.setStyleSheet("text-decoration: line-through; color: #95a5a6;")
        else:
            self.title_label.setStyleSheet("color: #2c3e50;")
        
        # Emit appropriate signal
        if self.task.completed:
            self.task_completed.emit(self.task.id)
        else:
            self.task_uncompleted.emit(self.task.id)
    
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
        if ((event.position().toPoint() - self.drag_start_position).manhattanLength() < 
            10):  # Minimum distance to start drag
            return
        
        # Start drag operation
        self.start_drag()
    
    def start_drag(self):
        """Start the drag operation"""
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # Set the task ID as drag data
        mime_data.setText(self.task.id)
        mime_data.setData("application/x-task", self.task.id.encode())
        
        # Create drag pixmap (screenshot of this widget)
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
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click to edit task"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.task_clicked.emit(self.task.id)
