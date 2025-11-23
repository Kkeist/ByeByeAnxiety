"""Diary widget"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTextEdit, QCalendarWidget, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCharFormat, QColor
from datetime import datetime

from src.models import DiaryEntry


class DiaryWidget(QWidget):
    """Diary management widget"""
    
    ai_summary_requested = pyqtSignal(str, str)  # date, content
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.current_entry = None
        
        self.setup_ui()
        self.load_entry(self.current_date)
        self.highlight_dates_with_entries()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QHBoxLayout(self)
        
        # Left: Calendar
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("<h3>Diary</h3>"))
        
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.date_selected)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
            }
        """)
        left_layout.addWidget(self.calendar)
        
        layout.addWidget(left_panel)
        
        # Right: Entry editor
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Date display
        self.date_label = QLabel()
        self.date_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        right_layout.addWidget(self.date_label)
        
        # Entry editor
        self.entry_editor = QTextEdit()
        self.entry_editor.setPlaceholderText("Write about your day...")
        self.entry_editor.textChanged.connect(self.auto_save)
        self.entry_editor.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-size: 13px;
                background-color: #fffef7;
            }
        """)
        right_layout.addWidget(self.entry_editor)
        
        # AI Summary section
        right_layout.addWidget(QLabel("<b>AI Summary:</b>"))
        self.summary_display = QTextEdit()
        self.summary_display.setReadOnly(True)
        self.summary_display.setMaximumHeight(150)
        self.summary_display.setPlaceholderText("AI-generated summary will appear here...")
        self.summary_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
                background-color: #e8f5e9;
            }
        """)
        right_layout.addWidget(self.summary_display)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_entry)
        save_btn.setStyleSheet("""
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
        btn_layout.addWidget(save_btn)
        
        self.summarize_btn = QPushButton("🤖 AI Summary")
        self.summarize_btn.clicked.connect(self.request_ai_summary)
        self.summarize_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_layout.addWidget(self.summarize_btn)
        
        btn_layout.addStretch()
        right_layout.addLayout(btn_layout)
        
        layout.addWidget(right_panel, 1)
    
    def date_selected(self, date):
        """Handle date selection"""
        date_str = date.toString("yyyy-MM-dd")
        self.load_entry(date_str)
    
    def load_entry(self, date_str: str):
        """Load diary entry for a date"""
        self.current_date = date_str
        self.date_label.setText(f"📅 {date_str}")
        
        # Load entry from database
        entry = self.data_manager.get_diary_entry(date_str)
        
        if entry:
            self.current_entry = entry
            self.entry_editor.setPlainText(entry.content)
            self.summary_display.setPlainText(entry.ai_summary)
        else:
            self.current_entry = DiaryEntry(date=date_str)
            self.entry_editor.clear()
            self.summary_display.clear()
    
    def auto_save(self):
        """Auto-save entry on text change"""
        # Simple debouncing - save after 2 seconds of no typing
        # For simplicity, we'll save immediately
        pass
    
    def save_entry(self):
        """Save current entry"""
        if self.current_entry:
            self.current_entry.update_content(self.entry_editor.toPlainText())
            self.data_manager.save_diary_entry(self.current_entry)
            self.highlight_dates_with_entries()
    
    def highlight_dates_with_entries(self):
        """Highlight dates that have diary entries"""
        entries = self.data_manager.get_all_diary_entries()
        
        # Create format for dates with entries
        format_with_entry = QTextCharFormat()
        format_with_entry.setBackground(QColor("#c8e6c9"))
        
        for entry in entries:
            if entry.content:  # Only highlight if there's content
                date_parts = entry.date.split("-")
                year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
                from PyQt6.QtCore import QDate
                date = QDate(year, month, day)
                self.calendar.setDateTextFormat(date, format_with_entry)
    
    def request_ai_summary(self):
        """Request AI summary for current entry - summarizes chats and tasks, not user content"""
        # Save current entry first (even if empty)
        self.save_entry()
        
        # Emit signal to request AI summary (content is not used, but kept for compatibility)
        content = self.entry_editor.toPlainText().strip()
        self.ai_summary_requested.emit(self.current_date, content)
        
        # Update button state
        self.summarize_btn.setEnabled(False)
        self.summarize_btn.setText("🤖 Generating...")
    
    def set_summary(self, summary: str):
        """Set AI-generated summary"""
        if self.current_entry:
            self.current_entry.set_summary(summary)
            self.summary_display.setPlainText(summary)
            self.data_manager.save_diary_entry(self.current_entry)
            
            # Reset button state
            self.summarize_btn.setEnabled(True)
            self.summarize_btn.setText("🤖 AI Summary")

