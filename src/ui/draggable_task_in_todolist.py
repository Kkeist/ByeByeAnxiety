"""Draggable task item for todolist display"""
from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDrag, QPainter


class DraggableTaskInTodolist(QLabel):
    """A task item in todolist that can be dragged back to other todolists"""
    
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.drag_start_position = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI"""
        self.setText(f"• {self.task.title[:40]}{'...' if len(self.task.title) > 40 else ''}")
        self.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 10px;
                margin-left: 10px;
                padding: 3px;
                border-radius: 3px;
            }
            QLabel:hover {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        self.setToolTip(f"Drag to move '{self.task.title}' to another list")
    
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
    
    def start_drag(self):
        """Start the drag operation"""
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # Set the task ID as drag data
        mime_data.setText(self.task.id)
        mime_data.setData("application/x-task", self.task.id.encode())
        
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
