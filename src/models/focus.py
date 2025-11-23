"""Focus session data model"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime


@dataclass
class FocusSession:
    """Represents a focus/pomodoro session"""
    id: str
    start_time: str
    duration_minutes: int
    actual_duration_seconds: int = 0
    completed: bool = False
    points_earned: int = 0
    end_time: Optional[str] = None
    task_name: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert session to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FocusSession':
        """Create session from dictionary"""
        # Handle legacy data format
        if 'planned_duration' in data:
            data['duration_minutes'] = data.pop('planned_duration')
        if 'actual_duration' in data and 'actual_duration_seconds' not in data:
            data['actual_duration_seconds'] = data.pop('actual_duration')
        
        # Remove any unknown fields
        valid_fields = {
            'id', 'start_time', 'duration_minutes', 'actual_duration_seconds',
            'completed', 'points_earned', 'end_time', 'task_name'
        }
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    def complete(self, actual_seconds: int):
        """Mark session as complete"""
        self.completed = True
        self.actual_duration_seconds = actual_seconds
        self.end_time = datetime.now().isoformat()
        # Calculate points: 1 point per minute (even if stopped early)
        minutes = actual_seconds // 60
        self.points_earned = minutes


@dataclass
class FocusStats:
    """Statistics for focus sessions"""
    total_sessions: int = 0
    total_minutes: int = 0
    total_points: int = 0
    completion_rate: float = 0.0
    sessions_history: List[dict] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert stats to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FocusStats':
        """Create stats from dictionary"""
        return cls(**data)
    
    def add_session(self, session: FocusSession):
        """Add a completed session to stats"""
        self.total_sessions += 1
        self.total_minutes += session.actual_duration_seconds // 60
        self.total_points += session.points_earned
        self.sessions_history.append(session.to_dict())
        # Recalculate completion rate
        if self.total_sessions > 0:
            completed = sum(1 for s in self.sessions_history if s.get('completed', False))
            self.completion_rate = completed / self.total_sessions

