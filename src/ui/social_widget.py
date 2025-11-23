"""Social book widget"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QListWidgetItem, QLabel, QDialog,
                             QLineEdit, QTextEdit, QDateEdit, QCheckBox,
                             QDialogButtonBox, QMessageBox, QSplitter)
from PyQt6.QtCore import Qt, QDate, QLocale
from datetime import datetime

from src.models import Person


class PersonDialog(QDialog):
    """Dialog for creating/editing person"""
    
    def __init__(self, person=None, parent=None):
        super().__init__(parent)
        self.person = person
        self.setWindowTitle("Edit Person" if person else "New Person")
        self.setMinimumWidth(400)
        self.setup_ui()
        
        if person:
            self.load_person()
    
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        
        # Name
        layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        # Personal info
        layout.addWidget(QLabel("Personal Info:"))
        self.info_input = QTextEdit()
        self.info_input.setMaximumHeight(80)
        layout.addWidget(self.info_input)
        
        # Birthday
        birthday_layout = QHBoxLayout()
        self.birthday_check = QCheckBox("Birthday:")
        birthday_layout.addWidget(self.birthday_check)
        
        self.birthday_date = QDateEdit()
        self.birthday_date.setCalendarPopup(True)
        self.birthday_date.setDate(QDate.currentDate())
        self.birthday_date.setEnabled(False)
        self.birthday_date.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        self.birthday_check.stateChanged.connect(
            lambda state: self.birthday_date.setEnabled(state == Qt.CheckState.Checked.value)
        )
        birthday_layout.addWidget(self.birthday_date)
        
        self.reminder_check = QCheckBox("Reminder")
        birthday_layout.addWidget(self.reminder_check)
        birthday_layout.addStretch()
        layout.addLayout(birthday_layout)
        
        # Preferences
        layout.addWidget(QLabel("Preferences/Likes:"))
        self.preferences_input = QTextEdit()
        self.preferences_input.setMaximumHeight(80)
        layout.addWidget(self.preferences_input)
        
        # Notes
        layout.addWidget(QLabel("Notes:"))
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        layout.addWidget(self.notes_input)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_person(self):
        """Load person data into form"""
        self.name_input.setText(self.person.name)
        self.info_input.setPlainText(self.person.personal_info)
        self.preferences_input.setPlainText(self.person.preferences)
        self.notes_input.setPlainText(self.person.notes)
        
        if self.person.birthday:
            self.birthday_check.setChecked(True)
            date = QDate.fromString(self.person.birthday, "yyyy-MM-dd")
            self.birthday_date.setDate(date)
        
        self.reminder_check.setChecked(self.person.birthday_reminder)
    
    def get_person_data(self):
        """Get person data from form"""
        return {
            "name": self.name_input.text(),
            "personal_info": self.info_input.toPlainText(),
            "preferences": self.preferences_input.toPlainText(),
            "notes": self.notes_input.toPlainText(),
            "birthday": self.birthday_date.date().toString("yyyy-MM-dd") if self.birthday_check.isChecked() else None,
            "birthday_reminder": self.reminder_check.isChecked()
        }


class SocialWidget(QWidget):
    """Social book management widget"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.current_person = None
        
        self.setup_ui()
        self.load_people()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QHBoxLayout(self)
        
        # Splitter for list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: People list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        header = QHBoxLayout()
        header.addWidget(QLabel("<h3>Social Book</h3>"))
        header.addStretch()
        
        add_btn = QPushButton("+ Add Person")
        add_btn.clicked.connect(self.add_person)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        header.addWidget(add_btn)
        left_layout.addLayout(header)
        
        self.people_list = QListWidget()
        self.people_list.itemClicked.connect(self.load_person_details)
        self.people_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #e9ecef;
            }
            QListWidget::item:selected {
                background-color: #9b59b6;
                color: white;
            }
        """)
        left_layout.addWidget(self.people_list)
        
        splitter.addWidget(left_panel)
        
        # Right: Person details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.details_widget = QWidget()
        details_layout = QVBoxLayout(self.details_widget)
        
        self.name_label = QLabel()
        self.name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        details_layout.addWidget(self.name_label)
        
        details_layout.addWidget(QLabel("<b>Personal Info:</b>"))
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.setMaximumHeight(100)
        details_layout.addWidget(self.info_display)
        
        details_layout.addWidget(QLabel("<b>Birthday:</b>"))
        self.birthday_label = QLabel()
        details_layout.addWidget(self.birthday_label)
        
        details_layout.addWidget(QLabel("<b>Preferences:</b>"))
        self.preferences_display = QTextEdit()
        self.preferences_display.setReadOnly(True)
        self.preferences_display.setMaximumHeight(100)
        details_layout.addWidget(self.preferences_display)
        
        details_layout.addWidget(QLabel("<b>Notes:</b>"))
        self.notes_display = QTextEdit()
        self.notes_display.setReadOnly(True)
        details_layout.addWidget(self.notes_display)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.clicked.connect(self.edit_person)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.clicked.connect(self.delete_person)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        
        details_layout.addLayout(btn_layout)
        details_layout.addStretch()
        
        self.details_widget.hide()  # Hide until a person is selected
        right_layout.addWidget(self.details_widget)
        
        # Placeholder
        self.placeholder = QLabel("Select a person to view details")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color: #95a5a6; font-size: 14px;")
        right_layout.addWidget(self.placeholder)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([250, 550])
        
        layout.addWidget(splitter)
    
    def load_people(self):
        """Load people list"""
        self.people_list.clear()
        people = self.data_manager.get_all_people()
        
        for person in people:
            item = QListWidgetItem(person.name)
            item.setData(Qt.ItemDataRole.UserRole, person.id)
            self.people_list.addItem(item)
    
    def load_person_details(self, item: QListWidgetItem):
        """Load person details"""
        person_id = item.data(Qt.ItemDataRole.UserRole)
        person = self.data_manager.get_person(person_id)
        
        if person:
            self.current_person = person
            self.name_label.setText(f"👤 {person.name}")
            self.info_display.setPlainText(person.personal_info)
            self.preferences_display.setPlainText(person.preferences)
            self.notes_display.setPlainText(person.notes)
            
            if person.birthday:
                reminder_text = " (Reminder ON)" if person.birthday_reminder else ""
                self.birthday_label.setText(f"🎂 {person.birthday}{reminder_text}")
            else:
                self.birthday_label.setText("Not set")
            
            self.placeholder.hide()
            self.details_widget.show()
    
    def add_person(self):
        """Add a new person"""
        dialog = PersonDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_person_data()
            person = Person(
                id=datetime.now().strftime("%Y%m%d%H%M%S%f"),
                name=data["name"],
                personal_info=data["personal_info"],
                preferences=data["preferences"],
                notes=data["notes"],
                birthday=data["birthday"],
                birthday_reminder=data["birthday_reminder"]
            )
            self.data_manager.save_person(person)
            self.load_people()
    
    def edit_person(self):
        """Edit current person"""
        if not self.current_person:
            return
        
        dialog = PersonDialog(person=self.current_person, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_person_data()
            self.current_person.name = data["name"]
            self.current_person.personal_info = data["personal_info"]
            self.current_person.preferences = data["preferences"]
            self.current_person.notes = data["notes"]
            self.current_person.birthday = data["birthday"]
            self.current_person.birthday_reminder = data["birthday_reminder"]
            self.data_manager.save_person(self.current_person)
            self.load_people()
            
            # Reload details
            for i in range(self.people_list.count()):
                item = self.people_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == self.current_person.id:
                    self.load_person_details(item)
                    break
    
    def delete_person(self):
        """Delete current person"""
        if not self.current_person:
            return
        
        reply = QMessageBox.question(
            self, "Delete Person",
            f"Are you sure you want to delete {self.current_person.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.delete_person(self.current_person.id)
            self.current_person = None
            self.details_widget.hide()
            self.placeholder.show()
            self.load_people()

