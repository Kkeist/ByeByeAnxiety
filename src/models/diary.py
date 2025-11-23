"""Diary data model"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime


@dataclass
class DiaryEntry:
    """Represents a diary entry for a specific date"""
    date: str  # YYYY-MM-DD format
    content: str = ""
    ai_summary: str = ""
    mood: Optional[str] = None
    completed_tasks: List[str] = field(default_factory=list)
    highlights: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert entry to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DiaryEntry':
        """Create entry from dictionary"""
        return cls(**data)
    
    def update_content(self, new_content: str):
        """Update diary content"""
        self.content = new_content
        self.updated_at = datetime.now().isoformat()
    
    def add_highlight(self, highlight: str):
        """Add a highlight to the day"""
        if highlight not in self.highlights:
            self.highlights.append(highlight)
            self.updated_at = datetime.now().isoformat()
    
    def set_summary(self, summary: str):
        """Set AI-generated summary"""
        self.ai_summary = summary
        self.updated_at = datetime.now().isoformat()
    
    def add_completed_task(self, task_title: str):
        """Record a completed task"""
        if task_title not in self.completed_tasks:
            self.completed_tasks.append(task_title)
            self.updated_at = datetime.now().isoformat()

