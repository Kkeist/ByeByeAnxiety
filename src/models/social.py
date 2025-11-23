"""Social book data model"""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class Person:
    """Represents a person in the social book"""
    id: str
    name: str
    personal_info: str = ""
    birthday: Optional[str] = None  # YYYY-MM-DD format
    birthday_reminder: bool = False
    preferences: str = ""
    events: List[str] = field(default_factory=list)
    notes: str = ""
    custom_fields: Dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Convert person to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Person':
        """Create person from dictionary"""
        return cls(**data)
    
    def update_field(self, field_name: str, value: str):
        """Update a field"""
        if hasattr(self, field_name):
            setattr(self, field_name, value)
        else:
            self.custom_fields[field_name] = value
        self.updated_at = datetime.now().isoformat()
    
    def add_event(self, event: str):
        """Add an event"""
        self.events.append(event)
        self.updated_at = datetime.now().isoformat()
    
    def set_birthday_reminder(self, enabled: bool):
        """Enable or disable birthday reminder"""
        self.birthday_reminder = enabled
        self.updated_at = datetime.now().isoformat()

