"""Ask Me AI learning assistant widget"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QListWidget, QSplitter,
                             QLabel, QListWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QTextCursor
import asyncio
from datetime import datetime

from src.agents import AskMeAgent


class AskMeWorker(QThread):
    """Worker thread for async Ask Me operations"""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, agent, question, history=None):
        super().__init__()
        self.agent = agent
        self.question = question
        self.history = history
    
    def run(self):
        """Run the async operation"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                self.agent.ask(self.question, self.history)
            )
            loop.close()
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))


class AskMeWidget(QWidget):
    """Learning assistant interface"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.agent = None
        self.current_worker = None
        self.conversations = {}  # conversation_id -> messages
        self.current_conversation_id = None
        
        self.setup_ui()
        self.load_conversations()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QHBoxLayout(self)
        
        # Splitter for conversations list and chat
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Conversations list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("<b>Conversations</b>"))
        
        self.conversations_list = QListWidget()
        self.conversations_list.itemClicked.connect(self.load_conversation)
        self.conversations_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e9ecef;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        left_layout.addWidget(self.conversations_list)
        
        new_conv_btn = QPushButton("+ New Question")
        new_conv_btn.clicked.connect(self.new_conversation)
        new_conv_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        left_layout.addWidget(new_conv_btn)
        
        splitter.addWidget(left_panel)
        
        # Right panel - Chat area
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Instructions
        instructions = QLabel(
            "<b>Ask Me - Your Learning Assistant</b><br>"
            "<small>I break down complex topics into easy-to-understand explanations. "
            "Each question starts a new conversation you can return to later.</small>"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 10px; background-color: #e8f5e9; border-radius: 5px;")
        right_layout.addWidget(instructions)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(300)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        right_layout.addWidget(self.chat_display)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Ask me anything...")
        self.question_input.setMinimumHeight(35)
        self.question_input.returnPressed.connect(self.send_question)
        self.question_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #27ae60;
                border-radius: 5px;
                font-size: 13px;
            }
        """)
        input_layout.addWidget(self.question_input)
        
        self.ask_button = QPushButton("Ask")
        self.ask_button.setMinimumSize(80, 35)
        self.ask_button.clicked.connect(self.send_question)
        self.ask_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        input_layout.addWidget(self.ask_button)
        
        right_layout.addLayout(input_layout)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([200, 600])
        
        layout.addWidget(splitter)
    
    def initialize_agent(self, api_key: str, provider: str = "gemini", instructions: str = ""):
        """Initialize the AI agent"""
        try:
            self.agent = AskMeAgent(
                llm_provider=provider,
                api_key=api_key,
                custom_instructions=instructions
            )
            self.add_system_message("Ask Me is ready! What would you like to learn about?")
        except Exception as e:
            self.add_system_message(f"Error initializing agent: {str(e)}")
    
    def load_conversations(self):
        """Load conversation list"""
        conv_ids = self.data_manager.get_all_conversations("ask_me")
        self.conversations_list.clear()
        
        for conv_id in conv_ids:
            # Get first message as title
            messages = self.data_manager.get_chat_history("ask_me", conv_id, limit=1)
            if messages:
                title = messages[0]['content'][:50] + "..." if len(messages[0]['content']) > 50 else messages[0]['content']
                item = QListWidgetItem(title)
                item.setData(Qt.ItemDataRole.UserRole, conv_id)
                self.conversations_list.addItem(item)
    
    def new_conversation(self):
        """Start a new conversation"""
        self.current_conversation_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.conversations[self.current_conversation_id] = []
        self.chat_display.clear()
        self.add_system_message("New conversation started. What's your question?")
    
    def load_conversation(self, item: QListWidgetItem):
        """Load a conversation"""
        conv_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_conversation_id = conv_id
        
        # Load messages
        messages = self.data_manager.get_chat_history("ask_me", conv_id)
        self.conversations[conv_id] = messages
        
        # Display messages
        self.chat_display.clear()
        for msg in messages:
            if msg['role'] == 'user':
                self.add_user_message(msg['content'], save=False)
            elif msg['role'] == 'assistant':
                self.add_assistant_message(msg['content'], save=False)
    
    def send_question(self):
        """Send a question to the agent"""
        question = self.question_input.text().strip()
        if not question:
            return
        
        if not self.agent:
            self.add_system_message("Please configure your API key in Settings first!")
            return
        
        # Create new conversation if none exists
        if not self.current_conversation_id:
            self.new_conversation()
        
        # Clear input
        self.question_input.clear()
        
        # Add question to display
        self.add_user_message(question)
        
        # Disable input while processing
        self.ask_button.setEnabled(False)
        self.question_input.setEnabled(False)
        
        # Get conversation history
        history = self.conversations.get(self.current_conversation_id, [])
        
        # Start worker
        self.current_worker = AskMeWorker(self.agent, question, history)
        self.current_worker.response_ready.connect(self.handle_response)
        self.current_worker.error_occurred.connect(self.handle_error)
        self.current_worker.finished.connect(self.cleanup_worker)
        self.current_worker.start()
    
    def handle_response(self, response: str):
        """Handle agent response"""
        self.add_assistant_message(response)
        
        # Update conversations list if this is a new conversation
        if self.current_conversation_id not in [
            self.conversations_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.conversations_list.count())
        ]:
            self.load_conversations()
    
    def handle_error(self, error: str):
        """Handle error"""
        self.add_system_message(f"Error: {error}")
        self.ask_button.setEnabled(True)
        self.question_input.setEnabled(True)
    
    def cleanup_worker(self):
        """Cleanup after worker finishes"""
        self.ask_button.setEnabled(True)
        self.question_input.setEnabled(True)
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
            self.data_manager.save_chat_message("ask_me", "user", message, self.current_conversation_id)
            if self.current_conversation_id not in self.conversations:
                self.conversations[self.current_conversation_id] = []
            self.conversations[self.current_conversation_id].append({"role": "user", "content": message})
    
    def add_assistant_message(self, message: str, save: bool = True):
        """Add assistant message to chat"""
        timestamp = datetime.now().strftime("%H:%M")
        # Convert to markdown-style display
        formatted_message = self.format_markdown(message)
        self.chat_display.append(f'<div style="margin: 10px 0; background-color: #f1f8f4; '
                                f'padding: 10px; border-radius: 5px; border-left: 4px solid #27ae60; text-align: left;">'
                                f'<div style="margin-bottom: 5px;">'
                                f'<b style="color: #27ae60;">Ask Me</b> '
                                f'<span style="color: #95a5a6; font-size: 11px;">{timestamp}</span>'
                                f'</div>'
                                f'<div style="color: #263238; white-space: pre-wrap; font-family: monospace;">{formatted_message}</div>'
                                f'</div>')
        
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)
        
        if save:
            self.data_manager.save_chat_message("ask_me", "assistant", message, self.current_conversation_id)
            if self.current_conversation_id not in self.conversations:
                self.conversations[self.current_conversation_id] = []
            self.conversations[self.current_conversation_id].append({"role": "assistant", "content": message})
    
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
    
    def add_system_message(self, message: str):
        """Add system message to chat"""
        self.chat_display.append(f'<div style="margin: 10px 0; color: #7f8c8d; '
                                f'font-style: italic; text-align: center;">'
                                f'{message}'
                                f'</div>')
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)
