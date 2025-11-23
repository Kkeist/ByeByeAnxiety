"""Settings dialog"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QComboBox, QPushButton,
                             QDialogButtonBox, QTabWidget, QWidget, QMessageBox)
from PyQt6.QtCore import Qt


class SettingsDialog(QDialog):
    """Settings configuration dialog"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 500)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        
        # Tab widget
        tabs = QTabWidget()
        
        # API Settings tab
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        
        api_layout.addWidget(QLabel("<h3>API Configuration</h3>"))
        
        # Provider selection
        api_layout.addWidget(QLabel("AI Provider:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Gemini (Google)", "Claude (Anthropic)"])
        self.provider_combo.currentTextChanged.connect(self.provider_changed)
        api_layout.addWidget(self.provider_combo)
        
        # Gemini API key
        api_layout.addWidget(QLabel("Gemini API Key:"))
        self.gemini_key_input = QLineEdit()
        self.gemini_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_key_input.setPlaceholderText("Enter your Google Gemini API key")
        api_layout.addWidget(self.gemini_key_input)
        
        gemini_info = QLabel(
            '<small>Get your API key from: '
            '<a href="https://makersuite.google.com/app/apikey">Google AI Studio</a></small>'
        )
        gemini_info.setOpenExternalLinks(True)
        gemini_info.setStyleSheet("color: #7f8c8d;")
        api_layout.addWidget(gemini_info)
        
        # Anthropic API key
        api_layout.addWidget(QLabel("Anthropic API Key:"))
        self.anthropic_key_input = QLineEdit()
        self.anthropic_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.anthropic_key_input.setPlaceholderText("Enter your Anthropic API key")
        api_layout.addWidget(self.anthropic_key_input)
        
        anthropic_info = QLabel(
            '<small>Get your API key from: '
            '<a href="https://console.anthropic.com/">Anthropic Console</a></small>'
        )
        anthropic_info.setOpenExternalLinks(True)
        anthropic_info.setStyleSheet("color: #7f8c8d;")
        api_layout.addWidget(anthropic_info)
        
        api_layout.addStretch()
        tabs.addTab(api_tab, "API Keys")
        
        # User Preferences tab
        prefs_tab = QWidget()
        prefs_layout = QVBoxLayout(prefs_tab)
        
        prefs_layout.addWidget(QLabel("<h3>User Preferences</h3>"))
        
        prefs_info = QLabel(
            "These preferences will be shared with the AI agents to personalize their responses. "
            "You can include information about your work style, preferences, or anything else "
            "you'd like the AI to remember."
        )
        prefs_info.setWordWrap(True)
        prefs_info.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        prefs_layout.addWidget(prefs_info)
        
        self.preferences_input = QTextEdit()
        self.preferences_input.setPlaceholderText(
            "Example:\n"
            "- I prefer short, concise responses\n"
            "- I work best in the morning\n"
            "- I'm a visual learner\n"
            "- Please use simple language"
        )
        prefs_layout.addWidget(self.preferences_input)
        
        tabs.addTab(prefs_tab, "Preferences")
        
        # Ask Me Instructions tab
        askme_tab = QWidget()
        askme_layout = QVBoxLayout(askme_tab)
        
        askme_layout.addWidget(QLabel("<h3>Ask Me Custom Instructions</h3>"))
        
        askme_info = QLabel(
            "Customize how the Ask Me learning assistant responds to your questions. "
            "These instructions will be added to the default ADHD-friendly teaching style."
        )
        askme_info.setWordWrap(True)
        askme_info.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        askme_layout.addWidget(askme_info)
        
        self.askme_instructions_input = QTextEdit()
        self.askme_instructions_input.setPlaceholderText(
            "Example:\n"
            "- Always include practical examples\n"
            "- Use analogies when explaining complex topics\n"
            "- Focus on the 'why' before the 'how'"
        )
        askme_layout.addWidget(self.askme_instructions_input)
        
        tabs.addTab(askme_tab, "Ask Me")
        
        # Data Management tab
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        
        data_layout.addWidget(QLabel("<h3>Data Management</h3>"))
        
        data_info = QLabel(
            "⚠️ Warning: Clearing all data will permanently delete all your tasks, "
            "diary entries, social contacts, focus sessions, and chat history. "
            "This action cannot be undone!"
        )
        data_info.setWordWrap(True)
        data_info.setStyleSheet("""
            color: #d32f2f;
            font-weight: bold;
            padding: 15px;
            background-color: #ffebee;
            border: 1px solid #ef5350;
            border-radius: 5px;
            margin-bottom: 20px;
        """)
        data_layout.addWidget(data_info)
        
        clear_all_btn = QPushButton("🗑️ Clear All Data")
        clear_all_btn.clicked.connect(self.clear_all_data)
        clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        data_layout.addWidget(clear_all_btn)
        
        data_layout.addStretch()
        tabs.addTab(data_tab, "Data Management")
        
        layout.addWidget(tabs)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def provider_changed(self, provider_text: str):
        """Handle provider change"""
        # Just for visual feedback - actual provider is determined by which key is used
        pass
    
    def load_settings(self):
        """Load settings from database"""
        # Load API keys
        gemini_key = self.data_manager.get_setting("gemini_api_key", "")
        anthropic_key = self.data_manager.get_setting("anthropic_api_key", "")
        active_provider = self.data_manager.get_setting("active_ai_provider", "gemini")
        
        self.gemini_key_input.setText(gemini_key)
        self.anthropic_key_input.setText(anthropic_key)
        
        if active_provider == "anthropic":
            self.provider_combo.setCurrentIndex(1)
        else:
            self.provider_combo.setCurrentIndex(0)
        
        # Load preferences
        preferences = self.data_manager.get_setting("user_preferences", "")
        self.preferences_input.setPlainText(preferences)
        
        # Load Ask Me instructions
        askme_instructions = self.data_manager.get_setting("askme_instructions", "")
        self.askme_instructions_input.setPlainText(askme_instructions)
    
    def save_and_accept(self):
        """Save settings and close dialog"""
        # Save API keys
        self.data_manager.save_setting("gemini_api_key", self.gemini_key_input.text())
        self.data_manager.save_setting("anthropic_api_key", self.anthropic_key_input.text())
        
        # Determine active provider based on which key is filled
        if self.provider_combo.currentIndex() == 1 and self.anthropic_key_input.text():
            self.data_manager.save_setting("active_ai_provider", "anthropic")
        else:
            self.data_manager.save_setting("active_ai_provider", "gemini")
        
        # Save preferences
        self.data_manager.save_setting("user_preferences", self.preferences_input.toPlainText())
        self.data_manager.save_setting("askme_instructions", self.askme_instructions_input.toPlainText())
        
        self.accept()
    
    def get_settings(self):
        """Get current settings"""
        provider = "anthropic" if self.provider_combo.currentIndex() == 1 else "gemini"
        api_key = self.anthropic_key_input.text() if provider == "anthropic" else self.gemini_key_input.text()
        
        return {
            "provider": provider,
            "api_key": api_key,
            "gemini_key": self.gemini_key_input.text(),
            "anthropic_key": self.anthropic_key_input.text(),
            "preferences": self.preferences_input.toPlainText(),
            "askme_instructions": self.askme_instructions_input.toPlainText()
        }
    
    def clear_all_data(self):
        """Clear all application data"""
        reply = QMessageBox.question(
            self,
            "Clear All Data",
            "⚠️ WARNING: This will permanently delete ALL your data:\n\n"
            "• All tasks\n"
            "• All diary entries\n"
            "• All social contacts\n"
            "• All focus sessions\n"
            "• All chat history\n"
            "• All todo lists\n\n"
            "This action CANNOT be undone!\n\n"
            "Are you absolutely sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Second confirmation
            reply2 = QMessageBox.question(
                self,
                "Final Confirmation",
                "This is your last chance to cancel.\n\n"
                "Clicking Yes will DELETE EVERYTHING.\n\n"
                "Are you 100% sure?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply2 == QMessageBox.StandardButton.Yes:
                # Clear all data
                self.data_manager.clear_all_data()
                
                QMessageBox.information(
                    self,
                    "Data Cleared",
                    "All data has been cleared successfully.\n\n"
                    "The application will need to be restarted for changes to take full effect."
                )

