"""Smart input widget with @ mention support"""
from PyQt6.QtWidgets import (QTextEdit, QCompleter, QListWidget, QListWidgetItem, 
                             QVBoxLayout, QWidget, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel
from PyQt6.QtGui import QTextCursor, QFont
import re


class SmartInputWidget(QTextEdit):
    """Text input widget with @ mention support for tasks, todolists, and dates"""
    
    message_ready = pyqtSignal(str, dict)  # message, mentions
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.mentions = {}  # Store mentioned items
        
        self.setup_ui()
        self.setup_completer()
    
    def setup_ui(self):
        """Setup the UI"""
        self.setPlaceholderText("Type your message... Use @ to mention tasks, lists, or dates")
        self.setMaximumHeight(100)
        self.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        
        # Set font
        font = QFont()
        font.setPointSize(11)
        self.setFont(font)
    
    def setup_completer(self):
        """Setup auto-completion for @ mentions"""
        self.completer = None
        self.completion_list = QListWidget()
        self.completion_list.setWindowFlags(Qt.WindowType.Popup)
        self.completion_list.setMaximumHeight(150)
        self.completion_list.itemClicked.connect(self.insert_completion)
        self.completion_list.hide()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        # Handle keyboard navigation in completion list
        if self.completion_list.isVisible():
            if event.key() == Qt.Key.Key_Up:
                # Move selection up
                current_row = self.completion_list.currentRow()
                if current_row > 0:
                    self.completion_list.setCurrentRow(current_row - 1)
                return
            elif event.key() == Qt.Key.Key_Down:
                # Move selection down
                current_row = self.completion_list.currentRow()
                if current_row < self.completion_list.count() - 1:
                    self.completion_list.setCurrentRow(current_row + 1)
                return
            elif event.key() == Qt.Key.Key_Return and not event.modifiers():
                # Select current item
                current_item = self.completion_list.currentItem()
                if current_item:
                    self.insert_completion(current_item)
                    return
            elif event.key() == Qt.Key.Key_Escape:
                # Hide completion list
                self.completion_list.hide()
                return
        
        if event.key() == Qt.Key.Key_Return and not event.modifiers():
            # Send message on Enter (only if completion list is not visible)
            if not self.completion_list.isVisible():
                self.send_message()
                return
        elif event.key() == Qt.Key.Key_Return and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            # New line on Shift+Enter
            super().keyPressEvent(event)
            return
        elif event.key() == Qt.Key.Key_Escape:
            # Hide completion list
            self.completion_list.hide()
            return
        
        super().keyPressEvent(event)
        
        # Check for @ mentions
        self.check_for_mentions()
    
    def check_for_mentions(self):
        """Check for @ mentions and show completion"""
        cursor = self.textCursor()
        text = self.toPlainText()
        pos = cursor.position()
        
        # Find @ symbol before cursor
        at_pos = text.rfind('@', 0, pos)
        if at_pos == -1:
            self.completion_list.hide()
            return
        
        # Get text after @
        query = text[at_pos + 1:pos]
        
        # Don't show completion if there's a space (mention is complete)
        if ' ' in query:
            self.completion_list.hide()
            return
        
        # Get completion items
        items = self.get_completion_items(query)
        
        if items:
            self.show_completion(items, at_pos)
        else:
            self.completion_list.hide()
    
    def get_completion_items(self, query):
        """Get completion items based on query"""
        items = []
        query_lower = query.lower()
        query_stripped = query.strip()
        
        # If query is empty or very short, show default options including dates
        show_defaults = len(query_stripped) <= 1
        
        # Tasks - filter by query
        all_tasks = []
        for category in ["today_must", "future_date", "long_term", "someday_maybe"]:
            tasks = self.data_manager.get_tasks_by_category(category)
            all_tasks.extend(tasks)
        
        for task in all_tasks:
            # Filter by query - if query is empty, show all; otherwise filter
            if not query_stripped or query_lower in task.title.lower():
                items.append({
                    'type': 'task',
                    'id': task.id,
                    'display': f"📋 {task.title}",
                    'completion': f"task:{task.id}",
                    'data': task
                })
        
        # Todo Lists - filter by query
        todolists = self.data_manager.get_setting("todolists", [])
        for todolist in todolists:
            # Filter by query
            if not query_stripped or query_lower in todolist.get('name', '').lower():
                items.append({
                    'type': 'todolist',
                    'id': todolist['id'],
                    'display': f"📚 {todolist.get('name', 'Unnamed')}",
                    'completion': f"todolist:{todolist['id']}",
                    'data': todolist
                })
        
        # People from social book - filter by query
        try:
            people = self.data_manager.get_all_people()
            if people:
                for person in people:
                    # Filter by query - check name
                    if not query_stripped or query_lower in person.name.lower():
                        items.append({
                            'type': 'person',
                            'id': person.id,
                            'display': f"👤 {person.name}",
                            'completion': f"person:{person.id}",
                            'data': person
                        })
        except Exception as e:
            # Social book might not be implemented yet, or error getting people
            import traceback
            print(f"Error getting people for mentions: {e}")
            traceback.print_exc()
        
        return items[:15]  # Limit to 15 items
    
    def show_completion(self, items, at_pos):
        """Show completion popup"""
        self.completion_list.clear()
        
        for item in items:
            list_item = QListWidgetItem(item['display'])
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.completion_list.addItem(list_item)
        
        # Select first item by default
        if self.completion_list.count() > 0:
            self.completion_list.setCurrentRow(0)
        
        # Position the completion list
        cursor = self.textCursor()
        cursor.setPosition(at_pos)
        rect = self.cursorRect(cursor)
        
        # Convert to global coordinates
        global_pos = self.mapToGlobal(rect.bottomLeft())
        self.completion_list.move(global_pos)
        self.completion_list.show()
        # Don't set focus on completion list - keep focus on input for typing
    
    def insert_completion(self, item):
        """Insert selected completion - insert friendly name but store code for parsing"""
        data = item.data(Qt.ItemDataRole.UserRole)
        
        cursor = self.textCursor()
        text = self.toPlainText()
        pos = cursor.position()
        
        # Find @ symbol before cursor
        at_pos = text.rfind('@', 0, pos)
        if at_pos == -1:
            return
        
        # Get friendly display name (remove emoji and format nicely)
        display_name = data['display']
        # Extract just the name part (after emoji)
        if ' - ' in display_name:
            # For dates: "📅 Calendar - Today (2024-01-15)" -> "Calendar Today"
            parts = display_name.split(' - ')
            if len(parts) > 1:
                display_name = parts[1].split(' (')[0]  # Remove date in parentheses
        elif ' ' in display_name:
            # For tasks/todolists: "📋 Task Name" -> "Task Name"
            display_name = display_name.split(' ', 1)[1]
        
        # Insert friendly name
        cursor.setPosition(at_pos)
        cursor.setPosition(pos, QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(f"@{display_name}")
        
        # Store mention data with both completion code and display name
        mention_key = data['completion']
        self.mentions[mention_key] = data
        # Also store by display name for reverse lookup
        self.mentions[f"display:{display_name}"] = data
        
        self.completion_list.hide()
    
    def send_message(self):
        """Send the message with mentions"""
        message = self.toPlainText().strip()
        if message:
            # Parse mentions in the message
            parsed_mentions = self.parse_mentions(message)
            
            # Emit signal
            self.message_ready.emit(message, parsed_mentions)
            
            # Clear input
            self.clear()
            self.mentions.clear()
    
    def parse_mentions(self, message):
        """Parse @ mentions in the message - supports both code format and friendly names"""
        mentions = {}
        
        # First try to find code format mentions (task:id, diary:date, etc.)
        pattern = r'@(task|todolist|person|diary|calendar|date):([^\s]+)'
        matches = re.findall(pattern, message)
        
        for mention_type, mention_id in matches:
            key = f"{mention_type}:{mention_id}"
            if key in self.mentions:
                mentions[key] = self.mentions[key]
        
        # Also find friendly name mentions (e.g., @Task Name, @Today, etc.)
        # Find all @mentions that are not in code format
        friendly_pattern = r'@([^\s@:]+)'
        friendly_matches = re.findall(friendly_pattern, message)
        
        for friendly_name in friendly_matches:
            # Skip if already matched as code format
            if any(f"{mention_type}:{mention_id}" == friendly_name for mention_type, mention_id in matches):
                continue
            
            # Try to find in mentions by display name
            display_key = f"display:{friendly_name}"
            if display_key in self.mentions:
                data = self.mentions[display_key]
                mention_key = data['completion']
                mentions[mention_key] = data
            else:
                # Try to match by partial name
                for key, data in self.mentions.items():
                    if key.startswith('display:'):
                        stored_name = key.replace('display:', '')
                        if friendly_name.lower() in stored_name.lower() or stored_name.lower() in friendly_name.lower():
                            mention_key = data['completion']
                            mentions[mention_key] = data
                            break
        
        return mentions
    
    def get_display_message(self, message, mentions):
        """Get display version of message with mention names"""
        display_message = message
        
        # Replace code format mentions with friendly names
        for mention_key, mention_data in mentions.items():
            # Try code format first
            mention_pattern = f"@{mention_key}"
            if mention_pattern in display_message:
                if mention_data['type'] == 'task':
                    display_name = f"@📋{mention_data['data'].title}"
                elif mention_data['type'] == 'todolist':
                    display_name = f"@📚{mention_data['data']['name']}"
                elif mention_data['type'] == 'person':
                    display_name = f"@👤{mention_data['data'].name}"
                elif mention_data['type'] == 'diary':
                    display_name = f"@📔Diary {mention_data['data']}"
                elif mention_data['type'] == 'calendar':
                    display_name = f"@📅Calendar {mention_data['data']}"
                elif mention_data['type'] == 'date':
                    display_name = f"@📅{mention_data['data']}"
                else:
                    display_name = mention_pattern
                
                display_message = display_message.replace(mention_pattern, display_name)
        
        # If message already contains friendly names, keep them as is
        # (they were inserted that way)
        
        return display_message
