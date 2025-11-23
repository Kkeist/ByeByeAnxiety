"""Sortable task container for drag-and-drop reordering"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent


class SortableTaskContainer(QWidget):
    """Container widget that supports drag-and-drop reordering of tasks"""
    
    task_reordered = pyqtSignal(str, str)  # dragged_task_id, target_task_id
    
    def __init__(self, task_id: str, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        """Handle drag enter"""
        if event.mimeData().hasFormat("application/x-task"):
            event.acceptProposedAction()
            self.setStyleSheet("background-color: #e3f2fd; border: 2px dashed #3498db; border-radius: 5px;")
    
    def dragMoveEvent(self, event):
        """Handle drag move"""
        if event.mimeData().hasFormat("application/x-task"):
            event.acceptProposedAction()
    
    def dragLeaveEvent(self, event):
        """Handle drag leave"""
        self.setStyleSheet("")
    
    def dropEvent(self, event):
        """Handle drop"""
        if event.mimeData().hasFormat("application/x-task"):
            dragged_task_id = event.mimeData().data("application/x-task").data().decode()
            target_task_id = self.task_id
            
            if dragged_task_id != target_task_id:
                self.task_reordered.emit(dragged_task_id, target_task_id)
            
            event.acceptProposedAction()
        
        self.setStyleSheet("")
