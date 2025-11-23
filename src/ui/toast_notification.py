"""Toast notification widget that fades in/out"""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty
from PyQt6.QtGui import QPainter, QColor


class ToastNotification(QLabel):
    """A toast notification that fades in, displays, and fades out"""
    
    def __init__(self, message: str, parent=None, duration: int = 3000):
        super().__init__(parent)
        self.message = message
        self.duration = duration
        self._opacity = 1.0
        
        self.setup_ui()
        self.show_animation()
    
    def setup_ui(self):
        """Setup the notification UI"""
        self.setText(self.message)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            ToastNotification {
                background-color: rgba(44, 62, 80, 240);
                color: white;
                border-radius: 10px;
                padding: 15px 25px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        # Make it a window that stays on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Adjust size
        self.adjustSize()
    
    def show_animation(self):
        """Show with fade-in animation"""
        # Position in center of parent or screen
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + 100
        else:
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            y = 100
        
        self.move(x, y)
        
        # Fade in
        self.fade_animation = QPropertyAnimation(self, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_animation.start()
        
        # Schedule fade out
        QTimer.singleShot(self.duration, self.fade_out)
    
    def fade_out(self):
        """Fade out and close"""
        self.fade_animation = QPropertyAnimation(self, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_animation.finished.connect(self.close)
        self.fade_animation.start()
    
    def get_opacity(self):
        """Get opacity value"""
        return self._opacity
    
    def set_opacity(self, value):
        """Set opacity value"""
        self._opacity = value
        self.update()
    
    opacity = pyqtProperty(float, get_opacity, set_opacity)
    
    def paintEvent(self, event):
        """Custom paint to support opacity"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background with opacity
        bg_color = QColor(44, 62, 80, int(240 * self._opacity))
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)
        
        # Draw text with opacity
        text_color = QColor(255, 255, 255, int(255 * self._opacity))
        painter.setPen(text_color)
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.message)
