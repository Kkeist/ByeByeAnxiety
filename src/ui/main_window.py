"""Main application window"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTabWidget, QLabel, QMessageBox,
                             QScrollArea, QLineEdit)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction

from src.utils import DataManager
from src.ui.floating_window import FloatingWindow
from src.ui.anxiety_killer_widget import AnxietyKillerWidget
from src.ui.ask_me_widget import AskMeWidget
from src.ui.todo_widget import TodoWidget
from src.ui.todolist_widget import TodoListWidget
from src.ui.focus_widget import FocusWidget
from src.ui.diary_widget import DiaryWidget
from src.ui.social_widget import SocialWidget
from src.ui.settings_dialog import SettingsDialog
from src.ui.calendar_widget import CalendarWidget


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        
        # Floating windows
        self.anxiety_killer_window = None
        self.ask_me_window = None
        
        # Widgets
        self.anxiety_killer_widget = None
        self.ask_me_widget = None
        
        self.setup_ui()
        self.setup_menu()
        self.initialize_agents()
        
        # Show floating windows by default
        self.show_anxiety_killer()
        self.show_ask_me()
    
    def setup_right_sidebar(self, main_layout):
        """Setup the right sidebar for todo lists"""
        sidebar = QWidget()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-left: 1px solid #dee2e6;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Header
        sidebar_header = QHBoxLayout()
        sidebar_title = QLabel("<h4>📚 Todo Lists</h4>")
        sidebar_title.setStyleSheet("color: #2c3e50; margin: 0; padding: 10px 0;")
        sidebar_header.addWidget(sidebar_title)
        
        # Add TodoList button
        add_todolist_btn = QPushButton("+ New List")
        add_todolist_btn.clicked.connect(self.create_quick_todolist)
        add_todolist_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        sidebar_header.addWidget(add_todolist_btn)
        sidebar_layout.addLayout(sidebar_header)
        
        # TodoLists scroll area
        self.sidebar_todolists_scroll = QScrollArea()
        self.sidebar_todolists_scroll.setWidgetResizable(True)
        self.sidebar_todolists_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.sidebar_todolists_container = QWidget()
        self.sidebar_todolists_container.setAcceptDrops(True)
        self.sidebar_todolists_layout = QVBoxLayout(self.sidebar_todolists_container)
        self.sidebar_todolists_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.sidebar_todolists_scroll.setWidget(self.sidebar_todolists_container)
        
        # Add drag/drop handlers for todolist
        self.sidebar_todolists_container.dragEnterEvent = self.sidebar_drag_enter
        self.sidebar_todolists_container.dragMoveEvent = self.sidebar_drag_move
        self.sidebar_todolists_container.dropEvent = self.sidebar_drop
        
        sidebar_layout.addWidget(self.sidebar_todolists_scroll)
        
        # Drop zone info
        drop_info = QLabel("💡 Drag tasks from Tasks tab, or drag TodoLists from Todo Lists tab to add them here")
        drop_info.setWordWrap(True)
        drop_info.setStyleSheet("""
            color: #7f8c8d; 
            font-size: 11px; 
            padding: 10px;
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            margin: 10px 0;
        """)
        sidebar_layout.addWidget(drop_info)
        
        # Initialize default todolists and load
        self.initialize_default_todolists()
        self.load_sidebar_todolists()
        
        main_layout.addWidget(sidebar, 1)  # Takes 1/4 of the space
    
    def sidebar_drag_enter(self, event):
        """Handle drag enter on sidebar"""
        if event.mimeData().hasFormat("application/x-todolist"):
            event.acceptProposedAction()
            self.sidebar_todolists_container.setStyleSheet("background-color: #e3f2fd;")
    
    def sidebar_drag_move(self, event):
        """Handle drag move on sidebar"""
        if event.mimeData().hasFormat("application/x-todolist"):
            event.acceptProposedAction()
    
    def sidebar_drop(self, event):
        """Handle drop on sidebar - add todolist to sidebar display"""
        if event.mimeData().hasFormat("application/x-todolist"):
            todolist_id = event.mimeData().data("application/x-todolist").data().decode()
            
            # Mark todolist as shown in sidebar
            todolists = self.data_manager.get_setting("todolists", [])
            for todolist in todolists:
                if todolist["id"] == todolist_id:
                    # Mark as sidebar item (not default, but shown in sidebar)
                    if todolist.get("is_default") not in ["daily", "longterm"]:
                        todolist["show_in_sidebar"] = True
                    break
            
            self.data_manager.save_setting("todolists", todolists)
            
            # Refresh sidebar to show the new todolist
            self.load_sidebar_todolists()
            
            event.acceptProposedAction()
        
        self.sidebar_todolists_container.setStyleSheet("")
    
    def create_quick_todolist(self):
        """Create a quick todo list"""
        from PyQt6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, 'New Todo List', 'Enter todo list name:')
        if ok and name.strip():
            from datetime import datetime
            
            todolist = {
                "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                "name": name.strip(),
                "description": "",
                "tasks": [],
                "created_at": datetime.now().isoformat()
            }
            
            # Save to data manager
            todolists = self.data_manager.get_setting("todolists", [])
            todolists.append(todolist)
            self.data_manager.save_setting("todolists", todolists)
            
            # Refresh displays
            self.load_sidebar_todolists()
            if hasattr(self, 'todolist_widget'):
                self.todolist_widget.load_todolists()
            
            # Show encouragement
            if self.anxiety_killer_widget and self.anxiety_killer_widget.agent:
                self.anxiety_killer_widget.add_system_message(
                    f"✨ Created new todo list '{name}'! Ready to organize your tasks!"
                )
    
    def load_sidebar_todolists(self):
        """Load todo lists in the sidebar"""
        # Clear existing items
        while self.sidebar_todolists_layout.count():
            item = self.sidebar_todolists_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Update default todolists first to ensure they have latest tasks
        self.update_default_todolists()
        
        # Load todo lists from data manager
        todolists = self.data_manager.get_setting("todolists", [])
        
        # Filter to show default todolists and those marked for sidebar
        sidebar_todolists = [
            tl for tl in todolists 
            if tl.get("is_default") in ["daily", "longterm"] or tl.get("show_in_sidebar", False)
        ]
        
        if not sidebar_todolists:
            no_lists = QLabel("No todo lists yet!\nCreate some to organize your tasks.")
            no_lists.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_lists.setStyleSheet("color: #95a5a6; font-style: italic; padding: 20px;")
            self.sidebar_todolists_layout.addWidget(no_lists)
        else:
            for todolist in sidebar_todolists:
                # Clean up deleted tasks from todolist
                self.clean_todolist_tasks(todolist)
                
                list_widget = self.create_sidebar_todolist_item(todolist)
                self.sidebar_todolists_layout.addWidget(list_widget)
        
        self.sidebar_todolists_layout.addStretch()
    
    def clean_todolist_tasks(self, todolist):
        """Remove deleted tasks from todolist"""
        task_ids = todolist.get("tasks", [])
        valid_task_ids = []
        
        for task_id in task_ids:
            task = self.data_manager.get_task(task_id)
            if task:  # Only keep tasks that still exist
                valid_task_ids.append(task_id)
        
        # Update todolist if tasks were removed
        if len(valid_task_ids) != len(task_ids):
            todolist["tasks"] = valid_task_ids
            # Save updated todolists
            todolists = self.data_manager.get_setting("todolists", [])
            for tl in todolists:
                if tl["id"] == todolist["id"]:
                    tl["tasks"] = valid_task_ids
                    break
            self.data_manager.save_setting("todolists", todolists)
    
    def create_sidebar_todolist_item(self, todolist):
        """Create a sidebar item for a todo list"""
        from src.ui.droppable_todolist_item import DroppableTodoListItem
        
        item = DroppableTodoListItem(todolist, self.data_manager)
        item.task_dropped.connect(self.on_task_dropped_to_todolist)
        item.todolist_clicked.connect(self.open_todolist_detail)
        
        return item
    
    def on_task_dropped_to_todolist(self, todolist_id: str, task_id: str, source_todolist_id: str = None):
        """Handle when a task is dropped onto a todolist"""
        # Add task to todolist
        todolists = self.data_manager.get_setting("todolists", [])
        
        # Remove from source todolist if moving from one to another
        if source_todolist_id and source_todolist_id != todolist_id:
            for todolist in todolists:
                if todolist["id"] == source_todolist_id:
                    if task_id in todolist["tasks"]:
                        todolist["tasks"].remove(task_id)
                    break
        
        # Find the target todolist and add task
        for todolist in todolists:
            if todolist["id"] == todolist_id:
                if task_id not in todolist["tasks"]:
                    todolist["tasks"].append(task_id)
                break
        
        # Save updated todolists
        self.data_manager.save_setting("todolists", todolists)
        
        # Refresh all displays
        self.refresh_all_todolists()
        
        # Show success message
        if self.anxiety_killer_widget and self.anxiety_killer_widget.agent:
            task = self.data_manager.get_task(task_id)
            todolist_name = next((tl['name'] for tl in todolists if tl['id'] == todolist_id), 'Unknown')
            if task:
                self.anxiety_killer_widget.add_system_message(
                    f"✨ Great! I moved '{task.title}' to your '{todolist_name}' list. Nice organization!"
                )
    
    def refresh_all_todolists(self):
        """Refresh all todolist displays"""
        # Clean up all todolists first
        todolists = self.data_manager.get_setting("todolists", [])
        for todolist in todolists:
            self.clean_todolist_tasks(todolist)
        
        # Update default todolists
        self.update_default_todolists()
        
        # Refresh sidebar
        self.load_sidebar_todolists()
        
        # Refresh main TodoList tab if it exists
        if hasattr(self, 'todolist_widget'):
            self.todolist_widget.load_todolists()
    
    def initialize_default_todolists(self):
        """Initialize default todolists (Daily and Long-term)"""
        todolists = self.data_manager.get_setting("todolists", [])
        
        # Check if default todolists exist
        daily_exists = any(tl.get("is_default") == "daily" for tl in todolists)
        longterm_exists = any(tl.get("is_default") == "longterm" for tl in todolists)
        
        from datetime import datetime
        
        if not daily_exists:
            daily_todolist = {
                "id": "default_daily",
                "name": "📅 Today's Tasks",
                "description": "Tasks that need to be done today",
                "tasks": [],
                "created_at": datetime.now().isoformat(),
                "is_default": "daily",
                "auto_managed": True
            }
            todolists.append(daily_todolist)
        
        if not longterm_exists:
            longterm_todolist = {
                "id": "default_longterm", 
                "name": "🎯 Daily Habits",
                "description": "Long-term goals and daily habits",
                "tasks": [],
                "created_at": datetime.now().isoformat(),
                "is_default": "longterm",
                "auto_managed": True
            }
            todolists.append(longterm_todolist)
        
        # Save updated todolists
        self.data_manager.save_setting("todolists", todolists)
        
        # Update with current tasks
        self.update_default_todolists()
    
    def update_default_todolists(self):
        """Update default todolists with current tasks"""
        todolists = self.data_manager.get_setting("todolists", [])
        
        # Get today's date
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get tasks by category
        today_tasks = self.data_manager.get_tasks_by_category("today_must")
        longterm_tasks = self.data_manager.get_tasks_by_category("long_term")
        
        # Update daily todolist
        for todolist in todolists:
            if todolist.get("is_default") == "daily":
                # Add today's tasks and future tasks due today
                task_ids = []
                for task in today_tasks:
                    task_ids.append(task.id)
                
                # Add future tasks due today
                future_tasks = self.data_manager.get_tasks_by_category("future_date")
                for task in future_tasks:
                    if task.due_date == today:
                        task_ids.append(task.id)
                
                todolist["tasks"] = list(set(task_ids))  # Remove duplicates
                
            elif todolist.get("is_default") == "longterm":
                # Add all long-term tasks
                task_ids = [task.id for task in longterm_tasks]
                todolist["tasks"] = task_ids
        
        # Save updated todolists
        self.data_manager.save_setting("todolists", todolists)
    
    def open_todolist_detail(self, todolist_data):
        """Open todolist detail popup"""
        from src.ui.todolist_detail_popup import TodoListDetailPopup
        
        popup = TodoListDetailPopup(todolist_data, self.data_manager, self)
        popup.todolist_updated.connect(self.refresh_all_todolists)
        popup.task_completed.connect(self.on_task_completed)
        popup.task_uncompleted.connect(self.on_task_uncompleted)
        
        # Position popup
        popup.move(self.x() + 50, self.y() + 50)
        popup.show()
        popup.raise_()
        popup.activateWindow()
    
    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("ByeByeAnxiety - ADHD Life Assistant")
        self.setMinimumSize(1200, 800)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("<h1>ByeByeAnxiety</h1>")
        title.setStyleSheet("color: #2c3e50;")
        header.addWidget(title)
        header.addStretch()
        
        # Settings button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.clicked.connect(self.show_settings)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        header.addWidget(settings_btn)
        
        layout.addLayout(header)
        
        # Info banner
        info = QLabel(
            "💙 Welcome! This app helps you manage daily tasks and reduce anxiety. "
            "Your AI assistants (Anxiety Killer & Ask Me) are floating windows you can move around."
        )
        info.setWordWrap(True)
        info.setStyleSheet("""
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            color: #1565c0;
        """)
        layout.addWidget(info)
        
        # Tab widget for main content
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 3px solid #3498db;
            }
        """)
        
        # Todo tab
        self.todo_widget = TodoWidget(self.data_manager)
        self.todo_widget.task_completed.connect(self.on_task_completed)
        self.todo_widget.task_uncompleted.connect(self.on_task_uncompleted)
        self.todo_widget.task_deleted.connect(self.on_task_deleted)
        tabs.addTab(self.todo_widget, "📋 Tasks")
        
        # TodoList tab
        self.todolist_widget = TodoListWidget(self.data_manager)
        tabs.addTab(self.todolist_widget, "📚 Todo Lists")
        
        # Calendar tab
        self.calendar_widget = CalendarWidget(self.data_manager)
        self.calendar_widget.task_scheduled.connect(self.on_task_scheduled)
        tabs.addTab(self.calendar_widget, "📅 Calendar")
        
        # Focus tab
        self.focus_widget = FocusWidget(self.data_manager)
        self.focus_widget.session_completed.connect(self.on_focus_completed)
        tabs.addTab(self.focus_widget, "⏱️ Focus")
        
        # Diary tab
        self.diary_widget = DiaryWidget(self.data_manager)
        self.diary_widget.ai_summary_requested.connect(self.request_diary_summary)
        tabs.addTab(self.diary_widget, "📔 Diary")
        
        # Social tab
        self.social_widget = SocialWidget(self.data_manager)
        tabs.addTab(self.social_widget, "👥 Social Book")
        
        # Create main content area with right sidebar
        main_content = QHBoxLayout()
        
        # Left side - tabs
        main_content.addWidget(tabs, 3)  # Takes 3/4 of the space
        
        # Right sidebar - Today's tasks
        self.setup_right_sidebar(main_content)
        
        layout.addLayout(main_content)
        
        # Footer with AI assistant buttons
        footer_layout = QVBoxLayout()
        
        # AI Assistant buttons
        ai_buttons_layout = QHBoxLayout()
        
        show_anxiety_btn = QPushButton("💙 Show Anxiety Killer")
        show_anxiety_btn.clicked.connect(self.show_anxiety_killer)
        show_anxiety_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        ai_buttons_layout.addWidget(show_anxiety_btn)
        
        show_askme_btn = QPushButton("💚 Show Ask Me")
        show_askme_btn.clicked.connect(self.show_ask_me)
        show_askme_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        ai_buttons_layout.addWidget(show_askme_btn)
        
        # Help button
        help_btn = QPushButton("😰 I can't do them")
        help_btn.clicked.connect(self.request_help)
        help_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        ai_buttons_layout.addWidget(help_btn)
        
        ai_buttons_layout.addStretch()
        footer_layout.addLayout(ai_buttons_layout)
        
        # Tip
        footer = QLabel(
            "💡 Tip: Use the AI assistants above for help anytime! "
            "Drag tasks to the right sidebar to add to today's list."
        )
        footer.setWordWrap(True)
        footer.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 10px;")
        footer_layout.addWidget(footer)
        
        layout.addLayout(footer_layout)
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        show_anxiety_killer = QAction("Show Anxiety Killer", self)
        show_anxiety_killer.triggered.connect(self.show_anxiety_killer)
        view_menu.addAction(show_anxiety_killer)
        
        show_ask_me = QAction("Show Ask Me", self)
        show_ask_me.triggered.connect(self.show_ask_me)
        view_menu.addAction(show_ask_me)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def initialize_agents(self):
        """Initialize AI agents with saved settings"""
        settings = self.data_manager.get_all_settings()
        
        provider = settings.get("active_ai_provider", "gemini")
        api_key = settings.get(f"{provider}_api_key", "")
        preferences = settings.get("user_preferences", "")
        askme_instructions = settings.get("askme_instructions", "")
        
        # Create widgets
        self.anxiety_killer_widget = AnxietyKillerWidget(self.data_manager)
        self.anxiety_killer_widget.proactive_message_received.connect(self.handle_proactive_message)
        self.ask_me_widget = AskMeWidget(self.data_manager)
        
        # Initialize if API key exists
        if api_key:
            self.anxiety_killer_widget.initialize_agent(api_key, provider, preferences)
            self.ask_me_widget.initialize_agent(api_key, provider, askme_instructions)
    
    def show_anxiety_killer(self):
        """Show Anxiety Killer floating window"""
        if not self.anxiety_killer_window:
            self.anxiety_killer_window = FloatingWindow("Anxiety Killer 💙", self)
            self.anxiety_killer_window.set_content(self.anxiety_killer_widget)
            self.anxiety_killer_window.resize(500, 600)
            
            # Position on left side
            self.anxiety_killer_window.move(50, 100)
        
        self.anxiety_killer_window.show()
        self.anxiety_killer_window.raise_()
    
    def show_ask_me(self):
        """Show Ask Me floating window"""
        if not self.ask_me_window:
            self.ask_me_window = FloatingWindow("Ask Me 💚", self)
            self.ask_me_window.set_content(self.ask_me_widget)
            self.ask_me_window.resize(600, 600)
            
            # Position on right side
            self.ask_me_window.move(self.width() - 650, 100)
        
        self.ask_me_window.show()
        self.ask_me_window.raise_()
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.data_manager, self)
        if dialog.exec():
            # Reinitialize agents with new settings
            settings = dialog.get_settings()
            
            if settings["api_key"]:
                self.anxiety_killer_widget.initialize_agent(
                    settings["api_key"],
                    settings["provider"],
                    settings["preferences"]
                )
                self.ask_me_widget.initialize_agent(
                    settings["api_key"],
                    settings["provider"],
                    settings["askme_instructions"]
                )
                
                QMessageBox.information(
                    self,
                    "Settings Saved",
                    "Your settings have been saved and AI agents have been reinitialized!"
                )
            else:
                QMessageBox.warning(
                    self,
                    "No API Key",
                    "Please configure your API key in Settings to use the AI assistants."
                )
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About ByeByeAnxiety",
            "<h2>ByeByeAnxiety</h2>"
            "<p>Version 1.0.0</p>"
            "<p>An AI-powered assistant designed to help individuals with ADHD "
            "manage their daily lives and reduce anxiety.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Anxiety Killer: Emotional support and task management</li>"
            "<li>Ask Me: ADHD-friendly learning assistant</li>"
            "<li>Task Management: Organize your todos</li>"
            "<li>Focus Timer: Stay on track with Pomodoro</li>"
            "<li>Diary: Track your progress</li>"
            "<li>Social Book: Remember important people</li>"
            "</ul>"
            "<p><small>Powered by Railtracks AI Framework</small></p>"
        )
    
    def on_task_completed(self, task_identifier: str):
        """Handle task completion - can be task_id or task_title"""
        # Try to get task by ID first, then by title
        task = None
        if len(task_identifier) > 10:  # Likely an ID (timestamp-based)
            task = self.data_manager.get_task(task_identifier)
        else:
            # Try to find by title
            all_tasks = []
            for category in ["today_must", "future_date", "long_term", "someday_maybe"]:
                tasks = self.data_manager.get_tasks_by_category(category)
                all_tasks.extend(tasks)
            task = next((t for t in all_tasks if t.title == task_identifier), None)
        
        if not task:
            return
        
        # Let AI generate a personalized praise message
        if self.anxiety_killer_widget and self.anxiety_killer_widget.agent:
            self.generate_task_completion_praise(task)
        
        # Check if any todolist is now complete
        self.check_todolist_completion(task.id)
    
    def on_task_uncompleted(self, task_identifier: str):
        """Handle task uncompletion - when user unchecks a completed task"""
        # Try to get task by ID first, then by title
        task = None
        if len(task_identifier) > 10:  # Likely an ID (timestamp-based)
            task = self.data_manager.get_task(task_identifier)
        else:
            # Try to find by title
            all_tasks = []
            for category in ["today_must", "future_date", "long_term", "someday_maybe"]:
                tasks = self.data_manager.get_tasks_by_category(category)
                all_tasks.extend(tasks)
            task = next((t for t in all_tasks if t.title == task_identifier), None)
        
        if not task:
            return
        
        # Let AI generate an encouraging message (not praise, but encouragement)
        if self.anxiety_killer_widget and self.anxiety_killer_widget.agent:
            self.generate_task_uncompletion_encouragement(task)
    
    def generate_task_completion_praise(self, task):
        """Generate AI praise for task completion"""
        import asyncio
        from PyQt6.QtCore import QTimer
        
        # Prepare context for AI
        praise_prompt = f"""The user just completed a task: "{task.title}"

Please generate a brief, warm, and personalized praise message (under 50 words) celebrating this achievement. 
Be specific about the task and make it feel genuine and encouraging. 
Use emojis if appropriate, but keep it natural and heartfelt."""

        # Use QTimer to schedule async call
        QTimer.singleShot(0, lambda: self._run_async_praise(task, praise_prompt))
    
    def generate_task_uncompletion_encouragement(self, task):
        """Generate AI encouragement for task uncompletion"""
        import asyncio
        from PyQt6.QtCore import QTimer
        
        # Prepare context for AI
        encouragement_prompt = f"""The user uncompleted a task: "{task.title}"

This is not a failure - they might need to adjust priorities, or the task needs more work. 
Please generate a brief, supportive, and encouraging message (under 50 words) that:
- Acknowledges it's okay to uncomplete tasks
- Offers gentle encouragement
- Doesn't judge or criticize
- Is warm and understanding

Use emojis if appropriate, but keep it natural and supportive."""

        # Use QTimer to schedule async call
        QTimer.singleShot(0, lambda: self._run_async_encouragement(task, encouragement_prompt))
    
    def _run_async_praise(self, task, prompt):
        """Helper to run async praise generation"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # If loop is running, create task
            asyncio.create_task(self._generate_ai_praise(task, prompt))
        else:
            # If loop is not running, run it
            loop.run_until_complete(self._generate_ai_praise(task, prompt))
    
    def _run_async_encouragement(self, task, prompt):
        """Helper to run async encouragement generation"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # If loop is running, create task
            asyncio.create_task(self._generate_ai_encouragement(task, prompt))
        else:
            # If loop is not running, run it
            loop.run_until_complete(self._generate_ai_encouragement(task, prompt))
    
    async def _generate_ai_praise(self, task, prompt):
        """Generate AI praise message"""
        try:
            if self.anxiety_killer_widget and self.anxiety_killer_widget.agent:
                response = await self.anxiety_killer_widget.agent.chat(prompt, context={})
                self.anxiety_killer_widget.send_proactive_message(response)
        except Exception as e:
            print(f"Error generating AI praise: {e}")
            # Fallback to simple message
            self.anxiety_killer_widget.send_proactive_message(
                f"🎉 Great job completing '{task.title}'! Every step forward counts!"
            )
    
    async def _generate_ai_encouragement(self, task, prompt):
        """Generate AI encouragement message"""
        try:
            if self.anxiety_killer_widget and self.anxiety_killer_widget.agent:
                response = await self.anxiety_killer_widget.agent.chat(prompt, context={})
                self.anxiety_killer_widget.send_proactive_message(response)
        except Exception as e:
            print(f"Error generating AI encouragement: {e}")
            # Fallback to simple message
            self.anxiety_killer_widget.send_proactive_message(
                f"💪 That's okay! You can always come back to '{task.title}' when you're ready. Take your time!"
            )
    
    def check_todolist_completion(self, task_id: str):
        """Check if any todolist is now complete after task completion"""
        todolists = self.data_manager.get_setting("todolists", [])
        
        for todolist in todolists:
            task_ids = todolist.get("tasks", [])
            if task_id not in task_ids:
                continue
            
            # Check if all tasks in this todolist are completed
            all_completed = True
            completed_tasks = []
            for tid in task_ids:
                task = self.data_manager.get_task(tid)
                if task:
                    if not task.completed:
                        all_completed = False
                        break
                    else:
                        completed_tasks.append(task.title)
            
            if all_completed and task_ids:  # Only if there are tasks
                # Let AI generate a personalized celebration message
                if self.anxiety_killer_widget and self.anxiety_killer_widget.agent:
                    self.generate_todolist_completion_praise(todolist, completed_tasks)
                break  # Only celebrate one at a time
    
    def generate_todolist_completion_praise(self, todolist, completed_tasks):
        """Generate AI praise for todolist completion"""
        import asyncio
        from PyQt6.QtCore import QTimer
        
        # Prepare context for AI
        tasks_list = ", ".join(completed_tasks[:5])  # First 5 tasks
        if len(completed_tasks) > 5:
            tasks_list += f", and {len(completed_tasks) - 5} more"
        
        praise_prompt = f"""The user just completed an entire todo list: "{todolist['name']}"

Completed tasks: {tasks_list}
Total tasks completed: {len(completed_tasks)}

Please generate a brief, enthusiastic, and personalized celebration message (under 60 words) that:
- Celebrates this major achievement
- Acknowledges the effort and dedication
- Is warm, encouraging, and genuine
- Makes the user feel proud of their accomplishment

Use emojis if appropriate, but keep it natural and heartfelt."""

        # Use QTimer to schedule async call
        QTimer.singleShot(0, lambda: self._run_async_todolist_praise(todolist, praise_prompt))
    
    def _run_async_todolist_praise(self, todolist, prompt):
        """Helper to run async todolist praise generation"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            asyncio.create_task(self._generate_ai_todolist_praise(todolist, prompt))
        else:
            loop.run_until_complete(self._generate_ai_todolist_praise(todolist, prompt))
    
    async def _generate_ai_todolist_praise(self, todolist, prompt):
        """Generate AI praise message for todolist completion"""
        try:
            if self.anxiety_killer_widget and self.anxiety_killer_widget.agent:
                response = await self.anxiety_killer_widget.agent.chat(prompt, context={})
                self.anxiety_killer_widget.send_proactive_message(response)
        except Exception as e:
            print(f"Error generating AI todolist praise: {e}")
            # Fallback to simple message
            self.anxiety_killer_widget.send_proactive_message(
                f"🎊🎉 Amazing! You've completed the entire '{todolist['name']}' list! You're absolutely crushing it! 🌟"
            )
    
    def on_task_deleted(self, task_id: str):
        """Handle task deletion - refresh all todolists"""
        # Refresh all todolist displays to remove deleted task
        self.refresh_all_todolists()
    
    def on_focus_completed(self, points: int):
        """Handle focus session completion"""
        # Show encouragement
        if self.anxiety_killer_widget and self.anxiety_killer_widget.agent:
            self.anxiety_killer_widget.send_proactive_message(
                f"🌟 Amazing focus session! You earned {points} points. "
                f"Your dedication is inspiring!"
            )
    
    def on_task_scheduled(self, task_id: str):
        """Handle task scheduling"""
        # Refresh other widgets
        self.todo_widget.load_tasks()
        
        # Show encouragement
        if self.anxiety_killer_widget and self.anxiety_killer_widget.agent:
            task = self.data_manager.get_task(task_id)
            if task:
                self.anxiety_killer_widget.add_system_message(
                    f"📅 Perfect! I scheduled '{task.title}' for you. Great planning ahead!"
                )
    
    def request_diary_summary(self, date: str, content: str):
        """Request AI summary for diary entry - summarizes diary content, chats, and activities"""
        if self.anxiety_killer_widget and self.anxiety_killer_widget.agent:
            # Get today's diary entry
            diary_entry = self.data_manager.get_diary_entry(date)
            diary_content = diary_entry.content if diary_entry and diary_entry.content else ""
            
            # Get today's chat history from both agents
            anxiety_killer_chats = self.data_manager.get_chat_history("anxiety_killer", date)
            ask_me_chats = self.data_manager.get_chat_history("ask_me", date)
            
            # Get tasks completed today
            all_tasks = []
            for category in ["today_must", "future_date", "long_term", "someday_maybe"]:
                tasks = self.data_manager.get_tasks_by_category(category)
                all_tasks.extend(tasks)
            
            completed_today = [task for task in all_tasks 
                             if task.completed and task.completed_at and task.completed_at.startswith(date)]
            
            # Get todolist operations (tasks added to todolists today)
            todolists = self.data_manager.get_setting("todolists", [])
            todolist_operations = []
            for todolist in todolists:
                # Check if todolist was created today or had tasks added today
                if todolist.get("created_at", "").startswith(date):
                    todolist_operations.append(f"Created todolist: {todolist.get('name', '')}")
            
            # Build summary context including diary content and chats
            summary_context = f"User's day on {date}:\n\n"
            
            # Add diary content (most important)
            if diary_content:
                summary_context += f"Diary entry:\n{diary_content}\n\n"
            else:
                summary_context += "Diary entry: (No diary content written today)\n\n"
            
            # Add completed tasks
            if completed_today:
                summary_context += f"Completed tasks ({len(completed_today)}):\n"
                summary_context += "\n".join([f"- {task.title}" for task in completed_today])
                summary_context += "\n\n"
            
            # Add Anxiety Killer conversations
            if anxiety_killer_chats:
                summary_context += "Anxiety Killer conversations:\n"
                for msg in anxiety_killer_chats:
                    role = msg.get('role', 'user')
                    msg_content = msg.get('content', '')[:300]  # Limit length
                    if role == 'user':
                        summary_context += f"User: {msg_content}\n"
                    elif role == 'assistant':
                        summary_context += f"AI: {msg_content}\n"
                summary_context += "\n"
            
            # Add Ask Me conversations
            if ask_me_chats:
                summary_context += "Ask Me questions and answers:\n"
                for msg in ask_me_chats:
                    role = msg.get('role', 'user')
                    msg_content = msg.get('content', '')[:300]  # Limit length
                    if role == 'user':
                        summary_context += f"User question: {msg_content}\n"
                    elif role == 'assistant':
                        summary_context += f"AI answer: {msg_content}\n"
                summary_context += "\n"
            
            # Add todolist operations
            if todolist_operations:
                summary_context += "TodoList operations:\n"
                summary_context += "\n".join([f"- {op}" for op in todolist_operations])
                summary_context += "\n\n"
            
            # Add summary instruction
            summary_context += "\nPlease create a brief, encouraging summary (under 150 words) that synthesizes the user's diary entry, completed tasks, conversations with AI, and activities. Focus on understanding the user's emotional state, achievements, and overall day experience."
            
            # Show message
            self.anxiety_killer_widget.add_system_message(
                f"📔 I'm analyzing your day on {date} - your tasks, chats, and activities. Let me create a summary for you..."
            )
            
            # Generate summary using AI
            # Use QTimer to schedule async call in event loop
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self._run_async_summary(date, summary_context))
    
    def _run_async_summary(self, date: str, context: str):
        """Helper to run async summary generation"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # If loop is running, create task
            asyncio.create_task(self.generate_diary_summary(date, context))
        else:
            # If loop is not running, run it
            loop.run_until_complete(self.generate_diary_summary(date, context))
    
    async def generate_diary_summary(self, date: str, context: str):
        """Generate diary summary using AI"""
        try:
            if self.anxiety_killer_widget and self.anxiety_killer_widget.agent:
                # Use the agent to generate summary
                summary = await self.anxiety_killer_widget.agent.generate_daily_summary("", context)
                
                # Set the summary in the diary widget
                self.diary_widget.set_summary(summary)
                
                # Show encouragement
                self.anxiety_killer_widget.add_system_message(
                    f"✨ I've created a summary of your day. You're doing great!"
                )
        except Exception as e:
            self.diary_widget.set_summary("Unable to generate summary at this time.")
            print(f"Error generating diary summary: {e}")
    
    def request_help(self):
        """Request help when user can't do their tasks"""
        # Show Anxiety Killer if not visible
        if not self.anxiety_killer_window or not self.anxiety_killer_window.isVisible():
            self.show_anxiety_killer()
        
        # Get today's tasks for context
        today_tasks = self.data_manager.get_tasks_by_category("today_must")
        incomplete_tasks = [task for task in today_tasks if not task.completed]
        
        # Calculate time remaining today
        from datetime import datetime, timedelta
        now = datetime.now()
        end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59)
        time_remaining = end_of_day - now
        hours_remaining = time_remaining.total_seconds() / 3600
        hours = int(hours_remaining)
        minutes = int((hours_remaining - hours) * 60)
        
        if self.anxiety_killer_widget and self.anxiety_killer_widget.agent:
            # Build comprehensive help message with guidance prompts
            help_prompts = [
                "Do I need to break down any of these tasks into smaller steps?",
                "What's the worst-case scenario if I can't complete these today?",
                "Can I accept that worst-case scenario?",
                "Are there any ways to mitigate or fix the situation?",
                "Can I do these tasks tomorrow instead?",
                f"Time check: There are {hours} hours and {minutes} minutes left until the end of today."
            ]
            
            if incomplete_tasks:
                task_list = "\n".join([f"- {task.title}" for task in incomplete_tasks[:10]])
                help_message = f"""I'm feeling overwhelmed and can't do my tasks today. Here's what I have:

{task_list}

Please help me think through this systematically. Consider these questions:
{chr(10).join([f"- {prompt}" for prompt in help_prompts])}

Let's work through this together step by step."""
            else:
                help_message = f"""I'm feeling overwhelmed and anxious about my tasks. 

Please help me think through this systematically. Consider these questions:
{chr(10).join([f"- {prompt}" for prompt in help_prompts])}

Let's work through this together step by step."""
            
            # Send the help request message
            self.anxiety_killer_widget.send_message_with_mentions(help_message, {})
            
            # Make sure the window is visible and on top
            self.anxiety_killer_window.raise_()
            self.anxiety_killer_window.activateWindow()
    
    def handle_proactive_message(self, message: str):
        """Handle proactive message from Anxiety Killer"""
        # Show Anxiety Killer window if not visible
        if not self.anxiety_killer_window or not self.anxiety_killer_window.isVisible():
            self.show_anxiety_killer()
        
        # Bring window to front and make it stay on top temporarily
        self.anxiety_killer_window.setWindowFlags(
            self.anxiety_killer_window.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
        )
        self.anxiety_killer_window.show()
        self.anxiety_killer_window.raise_()
        self.anxiety_killer_window.activateWindow()
        
        # Remove stay-on-top after a few seconds
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.remove_stay_on_top())
    
    def remove_stay_on_top(self):
        """Remove stay-on-top flag from Anxiety Killer window"""
        if self.anxiety_killer_window:
            self.anxiety_killer_window.setWindowFlags(
                self.anxiety_killer_window.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint
            )
            self.anxiety_killer_window.show()
