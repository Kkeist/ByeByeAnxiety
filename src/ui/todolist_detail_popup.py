"""TodoList detail popup window"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QListWidgetItem, QPushButton,
                             QCheckBox, QWidget, QScrollArea, QFrame,
                             QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QFont, QDrag, QPainter


class TodoListDetailPopup(QDialog):
    """Popup window showing TodoList details and tasks"""
    
    todolist_updated = pyqtSignal(str)  # todolist_id
    task_completed = pyqtSignal(str)    # task_id
    
    def __init__(self, todolist_data, data_manager, parent=None):
        super().__init__(parent)
        self.todolist_data = todolist_data
        self.data_manager = data_manager
        
        self.setup_ui()
        self.load_tasks()
        
        # Make it stay on top
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
    
    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle(f"📚 {self.todolist_data['name']}")
        self.setMinimumSize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        
        # Title (editable for non-default lists)
        if not self.todolist_data.get("auto_managed", False):
            self.title_label = QPushButton(f"📚 {self.todolist_data['name']}")
            self.title_label.clicked.connect(self.edit_title)
            self.title_label.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    border: none;
                    background: transparent;
                    font-size: 18px;
                    font-weight: bold;
                    color: #2c3e50;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #f8f9fa;
                    border-radius: 3px;
                }
            """)
        else:
            self.title_label = QLabel(f"📚 {self.todolist_data['name']}")
            self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        
        header.addWidget(self.title_label)
        header.addStretch()
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.clicked.connect(self.close)
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        header.addWidget(close_btn)
        layout.addLayout(header)
        
        # Description
        if self.todolist_data.get("description"):
            desc_label = QLabel(self.todolist_data["description"])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #7f8c8d; font-style: italic; margin-bottom: 10px;")
            layout.addWidget(desc_label)
        
        # Task count
        self.task_count_label = QLabel()
        self.task_count_label.setStyleSheet("color: #95a5a6; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(self.task_count_label)
        
        # Tasks list
        self.tasks_scroll = QScrollArea()
        self.tasks_scroll.setWidgetResizable(True)
        self.tasks_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """)
        
        self.tasks_container = QWidget()
        self.tasks_container.setAcceptDrops(True)
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tasks_scroll.setWidget(self.tasks_container)
        
        layout.addWidget(self.tasks_scroll)
        
        # Action buttons (only for non-auto-managed lists)
        if not self.todolist_data.get("auto_managed", False):
            btn_layout = QHBoxLayout()
            
            delete_btn = QPushButton("🗑️ Delete List")
            delete_btn.clicked.connect(self.delete_todolist)
            delete_btn.setStyleSheet("""
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
            """)
            btn_layout.addWidget(delete_btn)
            
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
        
        # Info for auto-managed lists
        if self.todolist_data.get("auto_managed", False):
            info_label = QLabel("ℹ️ This is an automatically managed list. Tasks are added/removed based on their categories.")
            info_label.setWordWrap(True)
            info_label.setStyleSheet("""
                background-color: #e8f4fd;
                color: #1565c0;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #bbdefb;
                margin: 10px 0;
            """)
            layout.addWidget(info_label)
    
    def load_tasks(self):
        """Load and display tasks"""
        # Clear existing tasks
        while self.tasks_layout.count():
            item = self.tasks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        task_ids = self.todolist_data.get("tasks", [])
        valid_tasks = []
        
        # Load tasks and filter out deleted ones
        for task_id in task_ids:
            task = self.data_manager.get_task(task_id)
            if task:
                valid_tasks.append(task)
        
        # Update task count
        self.task_count_label.setText(f"📊 {len(valid_tasks)} tasks")
        
        if not valid_tasks:
            # Show empty state
            empty_label = QLabel("📝 No tasks in this list yet.\nTasks will appear here when you add them!")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    color: #95a5a6;
                    font-style: italic;
                    padding: 40px;
                    font-size: 14px;
                }
            """)
            self.tasks_layout.addWidget(empty_label)
        else:
            # Sort tasks: incomplete first, then completed
            valid_tasks.sort(key=lambda t: (t.completed, t.title))
            
            for task in valid_tasks:
                task_widget = self.create_task_widget(task)
                self.tasks_layout.addWidget(task_widget)
    
    def create_task_widget(self, task):
        """Create a widget for a task"""
        from src.ui.sortable_task_container import SortableTaskContainer
        
        # Create the container that handles drop events
        container = SortableTaskContainer(task.id)
        container.task_reordered.connect(self.reorder_tasks_in_todolist)
        container.setStyleSheet("""
            SortableTaskContainer {
                background-color: transparent;
            }
        """)
        # Make sure container can receive drops even when widget is on top
        container.setAttribute(Qt.WidgetAttribute.WA_AcceptDrops, True)
        
        # Create the actual task widget
        widget = QFrame()
        widget.task_id = task.id
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                margin: 2px 0;
                padding: 8px;
            }
            QFrame:hover {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)
        
        # Make widget draggable but don't block container's drop events
        widget.drag_start_position = None
        widget._task_id = task.id  # Store task_id
        widget.setAcceptDrops(False)  # Don't accept drops on widget itself
        widget.mousePressEvent = lambda e: self._task_mouse_press(e, widget)
        widget.mouseMoveEvent = lambda e: self._task_mouse_move(e, widget)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Checkbox
        checkbox = QCheckBox()
        checkbox.setChecked(task.completed)
        checkbox.stateChanged.connect(lambda state, t=task: self.toggle_task(t, state))
        layout.addWidget(checkbox)
        
        # Task info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # Title
        title_label = QLabel(f"<b>{task.title}</b>")
        title_label.setWordWrap(True)
        if task.completed:
            title_label.setStyleSheet("text-decoration: line-through; color: #95a5a6;")
        else:
            title_label.setStyleSheet("color: #2c3e50;")
        info_layout.addWidget(title_label)
        
        # Description and dates
        details = []
        if task.description:
            details.append(task.description[:100] + "..." if len(task.description) > 100 else task.description)
        if task.due_date:
            details.append(f"📅 Due: {task.due_date}")
        if task.start_date and task.start_date != task.due_date:
            details.append(f"🚀 Start: {task.start_date}")
        
        if details:
            details_label = QLabel(" | ".join(details))
            details_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
            details_label.setMaximumHeight(15)
            info_layout.addWidget(details_label)
        
        layout.addLayout(info_layout, 1)
        
        # Category badge
        category_colors = {
            "today_must": "#e74c3c",
            "future_date": "#3498db", 
            "long_term": "#27ae60",
            "someday_maybe": "#f39c12"
        }
        category_names = {
            "today_must": "Today",
            "future_date": "Future",
            "long_term": "Long-term", 
            "someday_maybe": "Maybe"
        }
        
        category_label = QLabel(category_names.get(task.category, task.category))
        category_label.setStyleSheet(f"""
            background-color: {category_colors.get(task.category, '#95a5a6')};
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
        """)
        category_label.setFixedHeight(20)
        layout.addWidget(category_label)
        
        # Drag handle
        drag_handle = QLabel("⋮⋮")
        drag_handle.setStyleSheet("""
            color: #bdc3c7;
            font-size: 16px;
            padding: 5px;
        """)
        drag_handle.setToolTip("Drag to reorder")
        layout.addWidget(drag_handle)
        
        # Put widget inside container
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(widget)
        
        return container
    
    def toggle_task(self, task, state):
        """Toggle task completion"""
        task.completed = (state == Qt.CheckState.Checked.value)
        if task.completed:
            task.mark_complete()
        else:
            task.mark_incomplete()
        
        self.data_manager.save_task(task)
        self.task_completed.emit(task.id)
        
        # Refresh display
        self.load_tasks()
    
    def edit_title(self):
        """Edit todolist title"""
        if self.todolist_data.get("auto_managed", False):
            return
        
        new_name, ok = QInputDialog.getText(
            self, 
            "Edit List Name", 
            "Enter new name:", 
            text=self.todolist_data["name"]
        )
        
        if ok and new_name.strip():
            # Update todolist name
            todolists = self.data_manager.get_setting("todolists", [])
            for todolist in todolists:
                if todolist["id"] == self.todolist_data["id"]:
                    todolist["name"] = new_name.strip()
                    self.todolist_data = todolist
                    break
            
            self.data_manager.save_setting("todolists", todolists)
            
            # Update UI
            self.setWindowTitle(f"📚 {new_name.strip()}")
            self.title_label.setText(f"📚 {new_name.strip()}")
            
            # Emit update signal
            self.todolist_updated.emit(self.todolist_data["id"])
    
    def delete_todolist(self):
        """Delete this todolist"""
        if self.todolist_data.get("auto_managed", False):
            QMessageBox.warning(self, "Cannot Delete", "This is an automatically managed list and cannot be deleted.")
            return
        
        reply = QMessageBox.question(
            self,
            "Delete TodoList",
            f"Are you sure you want to delete '{self.todolist_data['name']}'?\n\nThis will not delete the tasks themselves, just remove them from this list.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from todolists
            todolists = self.data_manager.get_setting("todolists", [])
            todolists = [tl for tl in todolists if tl["id"] != self.todolist_data["id"]]
            self.data_manager.save_setting("todolists", todolists)
            
            # Emit update signal and close
            self.todolist_updated.emit(self.todolist_data["id"])
            self.close()
    
    def _task_mouse_press(self, event, widget):
        """Handle mouse press for task drag"""
        if event.button() == Qt.MouseButton.LeftButton:
            widget.drag_start_position = event.position().toPoint()
    
    def _task_mouse_move(self, event, widget):
        """Handle mouse move for task drag"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        
        if not hasattr(widget, 'drag_start_position') or not widget.drag_start_position:
            return
        
        # Check if we've moved far enough to start a drag
        if ((event.position().toPoint() - widget.drag_start_position).manhattanLength() < 10):
            return
        
        # Start drag operation
        drag = QDrag(widget)
        mime_data = QMimeData()
        
        # Set the task ID as drag data
        mime_data.setText(widget._task_id)
        mime_data.setData("application/x-task", widget._task_id.encode())
        
        # Create drag pixmap
        pixmap = widget.grab()
        
        # Make it semi-transparent
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), Qt.GlobalColor.transparent)
        painter.setOpacity(0.7)
        painter.drawPixmap(0, 0, widget.grab())
        painter.end()
        
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(widget.drag_start_position)
        
        # Execute drag
        drag.exec(Qt.DropAction.MoveAction)
        widget.drag_start_position = None
    
    def reorder_tasks_in_todolist(self, dragged_task_id: str, target_task_id: str):
        """Reorder tasks within the todolist"""
        task_ids = self.todolist_data.get("tasks", [])
        
        # Find indices
        dragged_index = next((i for i, tid in enumerate(task_ids) if tid == dragged_task_id), -1)
        target_index = next((i for i, tid in enumerate(task_ids) if tid == target_task_id), -1)
        
        if dragged_index == -1 or target_index == -1 or dragged_index == target_index:
            return
        
        # Remove dragged task and reinsert at target position
        dragged_task_id = task_ids.pop(dragged_index)
        
        # Adjust target index if needed
        if dragged_index < target_index:
            target_index -= 1
        
        task_ids.insert(target_index, dragged_task_id)
        
        # Update todolist
        self.todolist_data["tasks"] = task_ids
        
        # Save to data manager
        todolists = self.data_manager.get_setting("todolists", [])
        for todolist in todolists:
            if todolist["id"] == self.todolist_data["id"]:
                todolist["tasks"] = task_ids
                break
        self.data_manager.save_setting("todolists", todolists)
        
        # Reload display
        self.load_tasks()
    
    def refresh_data(self):
        """Refresh todolist data and display"""
        # Reload todolist data
        todolists = self.data_manager.get_setting("todolists", [])
        for todolist in todolists:
            if todolist["id"] == self.todolist_data["id"]:
                self.todolist_data = todolist
                break
        
        # Reload tasks
        self.load_tasks()
