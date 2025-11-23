"""Floating window base class for draggable UI components"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFrame)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QMouseEvent


class FloatingWindow(QFrame):
    """Base class for floating, draggable windows"""
    
    closed = pyqtSignal()
    minimized = pyqtSignal()
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.dragging = False
        self.drag_position = QPoint()
        self.is_minimized = False
        
        self.setup_ui()
        self.setup_style()
    
    def setup_ui(self):
        """Setup the UI layout"""
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title bar
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(30)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 5, 0)
        
        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-weight: bold; color: white;")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # Minimize button
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setFixedSize(25, 25)
        self.minimize_btn.clicked.connect(self.toggle_minimize)
        title_layout.addWidget(self.minimize_btn)
        
        # Close button
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(25, 25)
        self.close_btn.clicked.connect(self.close_window)
        title_layout.addWidget(self.close_btn)
        
        layout.addWidget(self.title_bar)
        
        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.content_widget)
    
    def setup_style(self):
        """Setup window styling"""
        self.setStyleSheet("""
            FloatingWindow {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 8px;
            }
            QWidget#title_bar {
                background-color: #3498db;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 3px;
                color: white;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        self.title_bar.setObjectName("title_bar")
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if click is in title bar
            if self.title_bar.geometry().contains(event.pos()):
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for dragging"""
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()
    
    def toggle_minimize(self):
        """Toggle minimized state"""
        if self.is_minimized:
            self.content_widget.show()
            self.minimize_btn.setText("−")
            self.is_minimized = False
        else:
            self.content_widget.hide()
            self.minimize_btn.setText("+")
            self.is_minimized = True
        self.adjustSize()
        self.minimized.emit()
    
    def close_window(self):
        """Close the window"""
        self.hide()
        self.closed.emit()
    
    def set_content(self, widget: QWidget):
        """Set the content widget"""
        # Clear existing content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add new content
        self.content_layout.addWidget(widget)

