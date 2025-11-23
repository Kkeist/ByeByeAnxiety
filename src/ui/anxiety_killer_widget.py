"""Anxiety Killer AI assistant chat widget"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QComboBox, QScrollArea,
                             QLabel, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QTextCursor
import asyncio
from datetime import datetime

from src.agents import AnxietyKillerAgent
from src.ui.smart_input_widget import SmartInputWidget


class ChatWorker(QThread):
    """Worker thread for async chat operations"""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, agent, message, context=None):
        super().__init__()
        self.agent = agent
        self.message = message
        self.context = context
    
    def run(self):
        """Run the async chat operation"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                self.agent.chat(self.message, self.context)
            )
            loop.close()
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))


class AnxietyKillerWidget(QWidget):
    """Chat interface for Anxiety Killer agent"""
    
    task_created = pyqtSignal(dict)  # Emit when agent creates a task
    diary_updated = pyqtSignal(str)  # Emit when agent updates diary
    proactive_message_received = pyqtSignal(str)  # Emit when proactive message is sent
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.agent = None
        self.current_worker = None
        self.chat_history = []
        
        self.setup_ui()
        self.load_chat_history()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(300)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Message type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Message Type:"))
        
        self.message_type = QComboBox()
        self.message_type.addItems([
            "Free (AI decides)",
            "Chat (Diary entry)",
            "Inspiration (Save idea)",
            "Task (Add to calendar)"
        ])
        self.message_type.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ced4da;
                border-radius: 3px;
            }
        """)
        type_layout.addWidget(self.message_type)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.message_input = SmartInputWidget(self.data_manager)
        self.message_input.message_ready.connect(self.send_message_with_mentions)
        input_layout.addWidget(self.message_input)
        
        self.send_button = QPushButton("Send")
        self.send_button.setMinimumSize(80, 35)
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Info label
        info_label = QLabel("💡 Tip: I can help you manage tasks, provide emotional support, and organize your day!")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #6c757d; font-size: 11px; padding: 5px;")
        layout.addWidget(info_label)
    
    def initialize_agent(self, api_key: str, provider: str = "gemini", preferences: str = ""):
        """Initialize the AI agent"""
        try:
            self.agent = AnxietyKillerAgent(
                llm_provider=provider,
                api_key=api_key,
                user_preferences=preferences,
                data_manager=self.data_manager
            )
            self.add_system_message("Anxiety Killer is ready! I can help you create tasks, update your diary, and provide emotional support. How can I help you today? 😊")
        except Exception as e:
            self.add_system_message(f"Error initializing agent: {str(e)}")
    
    def load_chat_history(self):
        """Load chat history from database"""
        history = self.data_manager.get_chat_history("anxiety_killer", limit=50)
        for msg in history:
            if msg['role'] == 'user':
                self.add_user_message(msg['content'], save=False)
            elif msg['role'] == 'assistant':
                self.add_assistant_message(msg['content'], save=False)
    
    def send_message_with_mentions(self, message: str, mentions: dict):
        """Send a message with @ mentions to the agent"""
        if not message:
            return
        
        if not self.agent:
            self.add_system_message("Please configure your API key in Settings first!")
            return
        
        # Create display message with mention names
        display_message = self.message_input.get_display_message(message, mentions)
        
        # Add user message to display
        self.add_user_message(display_message)
        
        # Disable input while processing
        self.send_button.setEnabled(False)
        self.message_input.setEnabled(False)
        
        # Get message type
        msg_type = self.message_type.currentText()
        
        # Prepare context with mention information
        context = self.prepare_context()
        
        # Add mention information to context
        if mentions:
            context['mentions'] = {}
            for mention_key, mention_data in mentions.items():
                if mention_data['type'] == 'task':
                    task = mention_data['data']
                    context['mentions'][mention_key] = {
                        'type': 'task',
                        'title': task.title,
                        'id': task.id,
                        'category': task.category,
                        'due_date': task.due_date,
                        'description': task.description
                    }
                elif mention_data['type'] == 'todolist':
                    todolist = mention_data['data']
                    context['mentions'][mention_key] = {
                        'type': 'todolist',
                        'name': todolist['name'],
                        'id': todolist['id'],
                        'task_count': len(todolist.get('tasks', []))
                    }
                elif mention_data['type'] == 'person':
                    person = mention_data['data']
                    # Get full person information from social book
                    full_person = self.data_manager.get_person(person.id)
                    if full_person:
                        person = full_person
                    
                    context['mentions'][mention_key] = {
                        'type': 'person',
                        'name': person.name,
                        'id': person.id,
                        'personal_info': person.personal_info if hasattr(person, 'personal_info') else '',
                        'birthday': person.birthday if hasattr(person, 'birthday') else None,
                        'birthday_reminder': person.birthday_reminder if hasattr(person, 'birthday_reminder') else False,
                        'preferences': person.preferences if hasattr(person, 'preferences') else '',
                        'events': person.events if hasattr(person, 'events') else [],
                        'notes': person.notes if hasattr(person, 'notes') else '',
                        'custom_fields': person.custom_fields if hasattr(person, 'custom_fields') else {}
                    }
                elif mention_data['type'] == 'diary':
                    date = mention_data['data']
                    # Try to get diary entry for that date
                    diary_entry = self.data_manager.get_diary_entry(date)
                    context['mentions'][mention_key] = {
                        'type': 'diary',
                        'date': date,
                        'has_entry': diary_entry is not None,
                        'content_preview': diary_entry.content[:200] + "..." if diary_entry and diary_entry.content else "No entry yet"
                    }
                elif mention_data['type'] == 'calendar':
                    date = mention_data['data']
                    # Get all tasks for that date
                    tasks_on_date = []
                    for category in ["today_must", "future_date", "long_term", "someday_maybe"]:
                        tasks = self.data_manager.get_tasks_by_category(category)
                        for task in tasks:
                            if (task.start_date == date or task.due_date == date):
                                tasks_on_date.append({
                                    'title': task.title,
                                    'category': task.category,
                                    'completed': task.completed,
                                    'start_date': task.start_date,
                                    'due_date': task.due_date
                                })
                    
                    context['mentions'][mention_key] = {
                        'type': 'calendar',
                        'date': date,
                        'task_count': len(tasks_on_date),
                        'tasks': tasks_on_date[:10]  # Limit to first 10 tasks
                    }
                elif mention_data['type'] == 'date':
                    context['mentions'][mention_key] = {
                        'type': 'date',
                        'date': mention_data['data']
                    }
        
        # Add message type hint to the message
        if "Chat" in msg_type:
            message = f"[DIARY_ENTRY] {message}"
        elif "Inspiration" in msg_type:
            message = f"[SAVE_IDEA] {message}"
        elif "Task" in msg_type:
            message = f"[CREATE_TASK] {message}"
        
        # Start worker thread
        self.current_worker = ChatWorker(self.agent, message, context)
        self.current_worker.response_ready.connect(self.handle_response)
        self.current_worker.error_occurred.connect(self.handle_error)
        self.current_worker.finished.connect(self.cleanup_worker)
        self.current_worker.start()
    
    def send_message(self):
        """Legacy send message method for send button"""
        # Get text from smart input widget
        message = self.message_input.toPlainText().strip()
        if message:
            # Parse any mentions in the message
            mentions = self.message_input.parse_mentions(message)
            self.send_message_with_mentions(message, mentions)
    
    def prepare_context(self):
        """Prepare context for the agent"""
        context = {}
        
        # Get today's tasks
        today = datetime.now().strftime("%Y-%m-%d")
        tasks = self.data_manager.get_tasks_by_date(today)
        context['tasks'] = [
            {"title": t.title, "completed": t.completed}
            for t in tasks
        ]
        
        # Get recent diary
        diary_entry = self.data_manager.get_diary_entry(today)
        if diary_entry:
            context['recent_diary'] = diary_entry.content
        
        return context
    
    def handle_response(self, response: str):
        """Handle agent response"""
        self.add_assistant_message(response)
    
    def handle_error(self, error: str):
        """Handle error"""
        self.add_system_message(f"Error: {error}")
        self.send_button.setEnabled(True)
        self.message_input.setEnabled(True)
    
    def cleanup_worker(self):
        """Cleanup after worker finishes"""
        self.send_button.setEnabled(True)
        self.message_input.setEnabled(True)
        self.current_worker = None
    
    def add_user_message(self, message: str, save: bool = True):
        """Add user message to chat"""
        timestamp = datetime.now().strftime("%H:%M")
        # Convert to markdown-style display
        formatted_message = self.format_markdown(message)
        self.chat_display.append(f'<div style="margin: 10px 0; text-align: left;">'
                                f'<div style="margin-bottom: 5px;">'
                                f'<b style="color: #2c3e50;">You</b> '
                                f'<span style="color: #95a5a6; font-size: 11px;">{timestamp}</span>'
                                f'</div>'
                                f'<div style="color: #34495e; white-space: pre-wrap; font-family: monospace;">{formatted_message}</div>'
                                f'</div>')
        
        if save:
            self.data_manager.save_chat_message("anxiety_killer", "user", message)
            self.chat_history.append({"role": "user", "content": message})
    
    def add_assistant_message(self, message: str, save: bool = True):
        """Add assistant message to chat"""
        timestamp = datetime.now().strftime("%H:%M")
        # Convert to markdown-style display
        formatted_message = self.format_markdown(message)
        self.chat_display.append(f'<div style="margin: 10px 0; background-color: #e3f2fd; '
                                f'padding: 10px; border-radius: 5px; text-align: left;">'
                                f'<div style="margin-bottom: 5px;">'
                                f'<b style="color: #1976d2;">Anxiety Killer</b> '
                                f'<span style="color: #95a5a6; font-size: 11px;">{timestamp}</span>'
                                f'</div>'
                                f'<div style="color: #263238; white-space: pre-wrap; font-family: monospace;">{formatted_message}</div>'
                                f'</div>')
        
        # Scroll to bottom
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)
        
        if save:
            self.data_manager.save_chat_message("anxiety_killer", "assistant", message)
            self.chat_history.append({"role": "assistant", "content": message})
    
    def format_markdown(self, text: str) -> str:
        """Format text with basic markdown-like styling"""
        # Simple markdown formatting
        import re
        
        # Bold text **text**
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        
        # Italic text *text*
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        
        # Code blocks ```code```
        text = re.sub(r'```(.*?)```', r'<code style="background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px;">\1</code>', text, flags=re.DOTALL)
        
        # Inline code `code`
        text = re.sub(r'`(.*?)`', r'<code style="background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px;">\1</code>', text)
        
        # Lists - simple bullet points
        lines = text.split('\n')
        formatted_lines = []
        for line in lines:
            if line.strip().startswith('- '):
                formatted_lines.append(f'• {line.strip()[2:]}')
            elif line.strip().startswith('* '):
                formatted_lines.append(f'• {line.strip()[2:]}')
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def add_system_message(self, message: str, proactive: bool = False):
        """Add system message to chat"""
        if proactive:
            # Proactive messages have special styling
            timestamp = datetime.now().strftime("%H:%M")
            self.chat_display.append(f'<div style="margin: 10px 0; background-color: #e8f5e9; '
                                    f'padding: 15px; border-radius: 8px; border: 2px solid #4caf50;">'
                                    f'<b style="color: #2e7d32;">💙 Anxiety Killer</b> '
                                    f'<span style="color: #95a5a6; font-size: 11px;">{timestamp}</span><br>'
                                    f'<span style="color: #2e7d32; font-weight: 500;">{message}</span>'
                                    f'</div>')
        else:
            # Regular system messages
            self.chat_display.append(f'<div style="margin: 10px 0; color: #7f8c8d; '
                                    f'font-style: italic; text-align: center;">'
                                    f'{message}'
                                    f'</div>')
        
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)
        
        # If this is a proactive message, emit signal
        if proactive:
            self.proactive_message_received.emit(message)
    
    def send_proactive_message(self, message: str):
        """Send a proactive message from the AI"""
        self.add_system_message(message, proactive=True)
