"""Task data model"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime
import json


@dataclass
class Task:
    """Represents a task/todo item"""
    id: str
    title: str
    description: str
    category: str  # today_must, future_date, long_term, someday_maybe
    completed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    due_date: Optional[str] = None
    start_date: Optional[str] = None
    completed_at: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    subtasks: List[str] = field(default_factory=list)
    order: int = 0
    
    def to_dict(self) -> dict:
        """Convert task to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create task from dictionary"""
        return cls(**data)
    
    def mark_complete(self):
        """Mark task as completed"""
        self.completed = True
        self.completed_at = datetime.now().isoformat()
    
    def mark_incomplete(self):
        """Mark task as incomplete"""
        self.completed = False
        self.completed_at = None
    
    def add_subtask(self, subtask: str):
        """Add a subtask"""
        if subtask not in self.subtasks:
            self.subtasks.append(subtask)
    
    def remove_subtask(self, subtask: str):
        """Remove a subtask"""
        if subtask in self.subtasks:
            self.subtasks.remove(subtask)


class TaskCategory:
    """Task category constants"""
    TODAY_MUST = "today_must"
    FUTURE_DATE = "future_date"
    LONG_TERM = "long_term"
    SOMEDAY_MAYBE = "someday_maybe"
    
    @classmethod
    def all_categories(cls) -> List[str]:
        """Get all category names"""
        return [cls.TODAY_MUST, cls.FUTURE_DATE, cls.LONG_TERM, cls.SOMEDAY_MAYBE]
    
    @classmethod
    def display_name(cls, category: str) -> str:
        """Get display name for category"""
        names = {
            cls.TODAY_MUST: "Today Must Do",
            cls.FUTURE_DATE: "Future Tasks",
            cls.LONG_TERM: "Long-term Goals",
            cls.SOMEDAY_MAYBE: "Someday/Maybe"
        }
        return names.get(category, category)

