"""Focus timer widget (Pomodoro-style)"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSpinBox, QProgressBar, QGridLayout,
                             QScrollArea, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QFont
from datetime import datetime
import os
import random

from src.models import FocusSession


class FocusWidget(QWidget):
    """Pomodoro-style focus timer"""
    
    session_completed = pyqtSignal(int)  # points earned
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.is_running = False
        self.elapsed_seconds = 0
        self.target_seconds = 0
        self.current_session = None
        
        self.setup_ui()
        self.load_stats()
        self.update_points_display()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        
        # Header
        layout.addWidget(QLabel("<h3>Focus Timer</h3>"))
        
        # Stats display
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Total: 0 sessions | 0 minutes")
        self.stats_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        
        self.points_label = QLabel("Points: 0")
        self.points_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        stats_layout.addWidget(self.points_label)
        layout.addLayout(stats_layout)
        
        # Timer display
        self.time_display = QLabel("25:00")
        self.time_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_display.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: #2c3e50;
            padding: 20px;
            background-color: #ecf0f1;
            border-radius: 10px;
            margin: 10px 0;
        """)
        layout.addWidget(self.time_display)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: #ecf0f1;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Duration selector
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration (minutes):"))
        
        self.duration_spin = QSpinBox()
        self.duration_spin.setMinimum(1)
        self.duration_spin.setMaximum(120)
        self.duration_spin.setValue(25)
        self.duration_spin.valueChanged.connect(self.update_display)
        duration_layout.addWidget(self.duration_spin)
        duration_layout.addStretch()
        layout.addLayout(duration_layout)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_timer)
        self.start_btn.setMinimumHeight(40)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_timer)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
        
        # Sticker collection section
        sticker_section = self.create_sticker_section()
        layout.addWidget(sticker_section)
        
        # Info
        info = QLabel("💡 Stay focused and earn points! Every minute = 1 point. Use 10 points to draw stickers!")
        info.setWordWrap(True)
        info.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 10px;")
        layout.addWidget(info)
        
        layout.addStretch()
    
    def load_stats(self):
        """Load focus statistics"""
        stats = self.data_manager.get_focus_stats()
        self.stats_label.setText(
            f"Total: {stats.total_sessions} sessions | {stats.total_minutes} minutes"
        )
        # Use unified points system
        points = self.get_user_points()
        self.points_label.setText(f"Points: {points}")
    
    def update_display(self):
        """Update time display"""
        if not self.is_running:
            minutes = self.duration_spin.value()
            self.time_display.setText(f"{minutes:02d}:00")
    
    def start_timer(self):
        """Start the focus timer"""
        self.is_running = True
        self.elapsed_seconds = 0
        self.target_seconds = self.duration_spin.value() * 60
        
        # Create session
        self.current_session = FocusSession(
            id=datetime.now().strftime("%Y%m%d%H%M%S%f"),
            start_time=datetime.now().isoformat(),
            duration_minutes=self.duration_spin.value()
        )
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.duration_spin.setEnabled(False)
        
        # Start timer (update every second)
        self.timer.start(1000)
    
    def update_timer(self):
        """Update timer display"""
        self.elapsed_seconds += 1
        
        # Calculate remaining time
        remaining = max(0, self.target_seconds - self.elapsed_seconds)
        minutes = remaining // 60
        seconds = remaining % 60
        
        self.time_display.setText(f"{minutes:02d}:{seconds:02d}")
        
        # Update progress
        progress = int((self.elapsed_seconds / self.target_seconds) * 100)
        self.progress_bar.setValue(min(progress, 100))
        
        # Check if completed
        if remaining == 0:
            self.complete_session()
    
    def stop_timer(self):
        """Stop the timer"""
        self.timer.stop()
        
        if self.current_session:
            self.complete_session()
    
    def complete_session(self):
        """Complete the current session"""
        self.timer.stop()
        self.is_running = False
        
        if self.current_session:
            # Complete session
            self.current_session.complete(self.elapsed_seconds)
            self.data_manager.save_focus_session(self.current_session)
            
            # Calculate minutes completed (even if 0)
            minutes_completed = self.elapsed_seconds // 60
            
            # Add points (1 point per minute)
            points_earned = self.current_session.points_earned
            total_points = self.add_points(points_earned)
            
            # Show toast notification with minutes completed
            from src.ui.toast_notification import ToastNotification
            toast = ToastNotification(
                f"⏱️ {minutes_completed} minutes completed! Earned {points_earned} points",
                parent=self,
                duration=3000
            )
            toast.show()
            
            # Emit signal with points
            self.session_completed.emit(points_earned)
            
            # Update stats
            self.load_stats()
            self.update_points_display()
            
            self.current_session = None
        
        # Reset UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.duration_spin.setEnabled(True)
        self.progress_bar.setValue(0)
        self.update_display()
    
    def create_sticker_section(self):
        """Create the sticker collection and lottery section"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 10px 0;
            }
        """)
        layout = QVBoxLayout(section)
        
        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("<b>🎁 Sticker Collection</b>"))
        header.addStretch()
        
        # Points display
        self.points_display = QLabel("Points: 0")
        self.points_display.setStyleSheet("color: #f39c12; font-weight: bold;")
        header.addWidget(self.points_display)
        
        # Draw button
        self.draw_btn = QPushButton("🎲 Draw Stickers (10 points)")
        self.draw_btn.clicked.connect(self.draw_stickers)
        self.draw_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        header.addWidget(self.draw_btn)
        layout.addLayout(header)
        
        # Sticker collection display
        scroll = QScrollArea()
        scroll.setMaximumHeight(120)
        scroll.setWidgetResizable(True)
        
        self.sticker_container = QWidget()
        self.sticker_layout = QGridLayout(self.sticker_container)
        self.sticker_layout.setSpacing(5)
        
        scroll.setWidget(self.sticker_container)
        layout.addWidget(scroll)
        
        self.update_sticker_display()
        return section
    
    def get_available_stickers(self):
        """Get list of available sticker files"""
        sticker_dir = "img/stickers"
        if os.path.exists(sticker_dir):
            return [f for f in os.listdir(sticker_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        return []
    
    def get_user_points(self):
        """Get user's current points"""
        return self.data_manager.get_setting("user_points", 0)
    
    def add_points(self, points):
        """Add points to user's total"""
        current = self.get_user_points()
        new_total = current + points
        self.data_manager.save_setting("user_points", new_total)
        self.update_points_display()
        return new_total
    
    def spend_points(self, points):
        """Spend points (returns True if successful)"""
        current = self.get_user_points()
        if current >= points:
            new_total = current - points
            self.data_manager.save_setting("user_points", new_total)
            self.update_points_display()
            return True
        return False
    
    def update_points_display(self):
        """Update points display"""
        points = self.get_user_points()
        self.points_display.setText(f"Points: {points}")
        self.points_label.setText(f"Points: {points}")  # Also update the top label
        self.draw_btn.setEnabled(points >= 10)
    
    def get_user_stickers(self):
        """Get user's collected stickers"""
        return self.data_manager.get_setting("user_stickers", {})
    
    def add_sticker(self, sticker_name, count=1):
        """Add sticker(s) to user's collection"""
        stickers = self.get_user_stickers()
        stickers[sticker_name] = stickers.get(sticker_name, 0) + count
        self.data_manager.save_setting("user_stickers", stickers)
        self.update_sticker_display()
    
    def draw_stickers(self):
        """Draw random stickers"""
        if not self.spend_points(10):
            QMessageBox.warning(self, "Not Enough Points", "You need 10 points to draw stickers!")
            return
        
        available_stickers = self.get_available_stickers()
        if not available_stickers:
            QMessageBox.warning(self, "No Stickers", "No sticker files found in img/stickers/")
            return
        
        # Random number of stickers (1, 2, 3, 5, or 10)
        sticker_counts = [1, 2, 3, 5, 10]
        weights = [40, 30, 20, 8, 2]  # Probability weights
        num_stickers = random.choices(sticker_counts, weights=weights)[0]
        
        # Draw random stickers
        drawn_stickers = []
        for _ in range(num_stickers):
            sticker = random.choice(available_stickers)
            drawn_stickers.append(sticker)
            self.add_sticker(sticker)
        
        # Show result with images
        self.show_sticker_result(drawn_stickers)
    
    def show_sticker_result(self, drawn_stickers):
        """Show sticker result with images"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("🎉 Got stickers!")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Title
        title_label = QLabel(f"🎉 Got {len(drawn_stickers)} stickers!")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Sticker images grid
        images_layout = QHBoxLayout()
        images_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        for sticker in drawn_stickers:
            # Handle both with and without extension
            sticker_path = None
            if os.path.exists(f"img/stickers/{sticker}"):
                sticker_path = f"img/stickers/{sticker}"
            elif os.path.exists(f"img/stickers/{sticker}.JPG"):
                sticker_path = f"img/stickers/{sticker}.JPG"
            elif os.path.exists(f"img/stickers/{sticker}.jpg"):
                sticker_path = f"img/stickers/{sticker}.jpg"
            elif os.path.exists(f"img/stickers/{sticker}.png"):
                sticker_path = f"img/stickers/{sticker}.png"
            
            if sticker_path and os.path.exists(sticker_path):
                pixmap = QPixmap(sticker_path)
                if not pixmap.isNull():
                    # Scale to 80x80
                    scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    image_label = QLabel()
                    image_label.setPixmap(scaled_pixmap)
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    images_layout.addWidget(image_label)
        
        layout.addLayout(images_layout)
        
        # OK button
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dialog.accept)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(ok_btn)
        
        dialog.exec()
    
    def update_sticker_display(self):
        """Update the sticker collection display"""
        # Clear existing items
        while self.sticker_layout.count():
            item = self.sticker_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        stickers = self.get_user_stickers()
        row, col = 0, 0
        
        for sticker_name, count in stickers.items():
            # Create sticker item - square widget without layout for absolute positioning
            sticker_widget = QWidget()  # Use QWidget instead of QFrame for simpler absolute positioning
            sticker_widget.setFixedSize(70, 70)  # Square widget
            sticker_widget.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                }
            """)
            
            # Find sticker image file
            sticker_path = None
            if os.path.exists(f"img/stickers/{sticker_name}"):
                sticker_path = f"img/stickers/{sticker_name}"
            elif os.path.exists(f"img/stickers/{sticker_name}.JPG"):
                sticker_path = f"img/stickers/{sticker_name}.JPG"
            elif os.path.exists(f"img/stickers/{sticker_name}.jpg"):
                sticker_path = f"img/stickers/{sticker_name}.jpg"
            elif os.path.exists(f"img/stickers/{sticker_name}.png"):
                sticker_path = f"img/stickers/{sticker_name}.png"
            
            # Display sticker image - square, centered
            if sticker_path and os.path.exists(sticker_path):
                pixmap = QPixmap(sticker_path)
                if not pixmap.isNull():
                    # Scale to square (60x60) maintaining aspect ratio
                    scaled_pixmap = pixmap.scaled(
                        60, 60, 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    
                    # Create image label with parent
                    image_label = QLabel(sticker_widget)
                    image_label.setPixmap(scaled_pixmap)
                    # Position in center: (70-60)/2 = 5px margin on all sides
                    image_label.setGeometry(0, 0, 70, 70)
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    image_label.setScaledContents(False)
                    image_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            
            # Count badge - red circle with white number in top-right corner
            count_label = QLabel(str(count), sticker_widget)
            count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Calculate badge size for perfect circle
            # Minimum 20px, add 4px per digit
            badge_size = max(20, 16 + len(str(count)) * 4)
            radius = badge_size // 2  # Half for perfect circle
            
            count_label.setStyleSheet(f"""
                QLabel {{
                    background-color: #e74c3c;
                    color: white;
                    border-radius: {radius}px;
                    font-size: 11px;
                    font-weight: bold;
                    min-width: {badge_size}px;
                    min-height: {badge_size}px;
                }}
            """)
            
            # Position in top-right corner: widget is 70x70, badge is badge_size x badge_size
            # Position: x = 70 - badge_size - 2 (2px margin), y = 2
            count_label.setGeometry(70 - badge_size - 2, 2, badge_size, badge_size)
            count_label.raise_()  # Ensure it's on top of image
            count_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            
            self.sticker_layout.addWidget(sticker_widget, row, col)
            
            col += 1
            if col >= 8:  # 8 stickers per row
                col = 0
                row += 1

